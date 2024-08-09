import os
from langchain.tools import BaseTool
from langchain_community.graphs import Neo4jGraph
from openai import OpenAI
from langchain.chains import GraphCypherQAChain
from langchain_openai import ChatOpenAI

url = os.environ.get("NEO4J_URL")
username = "neo4j"
password = os.environ.get("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

graph = Neo4jGraph(url=url, username=username, password=password)

graph.refresh_schema()

cypher_chain = GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(temperature=0, model_name="gpt-4"),
    qa_llm=ChatOpenAI(temperature=0),
    graph=graph,
    verbose=True,
    return_intermediate_steps=True,
)

Graph_understanding_prompt = """Your task is to answer the following question using the graph representing the organization's architecture.
[{question}]
You have executed the following cypher query
[{cypher_query}]
and the answer is
[{cypher_answer}]
Analyse it and provide an answer to the question.
If you feel the cypher does not appropriately answer the question, your answer should be 'the graph does not contain the information needed to answer the question'.
"""


class GraphUnderstandingTool(BaseTool):
    name = "GraphUnderstandingTool"
    description = (
        "This tool queries the organization's architecture graph and returns answers about relationships, nodes and properties"
        "Input the question/query and it will provide an answer "
    )
    query: str = None
    graph: Neo4jGraph = None

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run_graph_cypher_chain(self, question: str):
        cypher_prompt = """
            The 'relationship type' defines the relationship between two nodes:
                CONNECTED: Direct interaction between services.
                CONSUMES: Service uses data from another service.
                Call Sync: Synchronous call between services.
                Call Sync backfill: Sync call for backfilling data.
                PUBLISHES: Service sends data for others to subscribe.
                SUBSCRIBES: Service listens to data from another service.
                USES: Service utilizes another service's functionality.
            Note: 'node 1 USES node 2' and 'node 2 USES node 1' will result in different answers. The first has an arrow from node 1 to node 2, while the second has an arrow from node 2 to node 1. "USES" could be any relationship type (CONNECTED, CONSUMES, Call Sync, etc.). Keep this in mind for making a Cypher query.
            Using the description above, answer the following question:
        """
        result = cypher_chain.invoke(cypher_prompt + question)
        return result

    def get_graph_understanding_prompt(self, question: str):
        result = self.run_graph_cypher_chain(question)
        cypher_query = result["intermediate_steps"][0]["query"]
        cypher_answer = result["intermediate_steps"][1]["context"]
        return Graph_understanding_prompt.format(
            question=question, cypher_query=cypher_query, cypher_answer=cypher_answer
        )

    def query_llm(self, message: str):
        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Answer the following question with all provided resources.",
                },
                {"role": "user", "content": message},
            ],
        )

        return completion.choices[0].message.content

    def _run(self, question: str) -> str:
        llm_prompt = self.get_graph_understanding_prompt(question)
        response = self.query_llm(llm_prompt)
        return response
