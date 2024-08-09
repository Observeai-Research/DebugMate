import tools.load_db as load_db
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_core.callbacks import CallbackManagerForChainRun
import openai


class HelpDesk:
    """Create the necessary objects to create a QARetrieval chain"""

    def __init__(self, new_db=False):
        self.new_db = new_db
        self.template = self.get_template()
        self.embeddings = self.get_embeddings()
        self.llm = self.get_llm()
        self.prompt = self.get_prompt()

        if self.new_db:
            self.db = load_db.DataLoader().set_db(self.embeddings)
        else:
            self.db = load_db.DataLoader().get_db(self.embeddings)

        self.retriever = self.db.as_retriever()
        self.retrieval_qa_chain = self.get_retrieval_qa()

    def get_template(self):
        template = """
        Given this text extracts:
        -----
        {context}
        -----
        Please answer with to the following question:
        Question: {question}
        Helpful Answer:
        """
        return template

    def get_prompt(self) -> PromptTemplate:
        prompt = PromptTemplate(
            template=self.template, input_variables=["context", "question"]
        )
        return prompt

    def get_embeddings(self) -> OpenAIEmbeddings:
        embeddings = OpenAIEmbeddings()
        return embeddings

    def get_llm(self):
        llm = OpenAI()
        return llm

    def get_retrieval_qa(self):
        chain_type_kwargs = {"prompt": self.prompt}
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs=chain_type_kwargs,
        )
        return qa

    def retrieval_qa_inference(self, question, verbose=True):
        query = {"query": question}
        answer = self.retrieval_qa_chain(query)
        return answer["result"]

    def get_text(self, question, expand_query=False):
        if expand_query:
            question = question + expand_query(question)
        run_manager = CallbackManagerForChainRun.get_noop_manager()
        answers = self.retriever.invoke(
            question, config={"callbacks": run_manager.get_child()}
        )
        result = ""
        for answer in answers:
            result += answer.dict()["page_content"] + "\n"
        return result

    def expand_query(self, question):
        messages = [
            {
                "role": "system",
                "content": "You are an expert debugging assistant. Provide an example answer that is likely to be found in the organization's internal documentation.",
            },
            {"role": "user", "content": question},
        ]
        openai_client = openai.OpenAI()
        model = "gpt-3.5-turbo"
        response = openai_client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content
