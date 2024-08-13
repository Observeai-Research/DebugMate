from langchain.tools import BaseTool
import agents.debugmate_agent
import json


class ToTTool(BaseTool):
    name = "ToT_tool"
    description = (
        "This tool searches for relevant code going deeper into multiple functions mentioned in the prompt."
        "Input a list of queries to retrieve most relevant code with reasons for error."
        "Do not use this tool for only one query. For only one query, use CodeSearch tool instead."
        'Format: input should be in JSON format: {"prompt": "<detailed explanation of the original problem being solved>", "query 1": "<query>", "query 2": "<query>", "query 3": "<query>", ...}'
        'Example input: {"prompt": "<original prompt>", "query 1": "<class1>.<function1>", "query 2": "<class2>.<function2>", "query 3": "<class3>.<function3>", ...}'
        "All quotes in the query should be double quotes which can be formatted in JSON; DO NOT USE SINGLE QUOTES."
        "Each query should be detailed like above for ALL functions or classes that could be related to the issue."
    )

    def __init__(self):
        super().__init__()

    def _run(self, query: str):
        """Executes a search deeper into code."""
        eval_prompt = """
            When you reach a final answer, you should evaluate whether a good conclusion of the issue was reached with a good solution.
            If a strong conclusion was reached, you want the parent agent to stop searching the code and conclude.
            If not, you want the parent agent to continue searching for a more likely error.
            Your final answer should either include "parent node should continue" or "parent node should conclude" at the end of the final thought.
        """
        query = json.loads(query)
        if len(query) == 2:
            return "For only one single query, use CodeSearch instead."
        print("\n\nTree of Thought Queries:")
        print(query["prompt"])
        for num in query:
            if num != "prompt":
                print("\t", f"{num}: {query[num]}")
        new_query = input("Add another query (ENTER if nothing to add): ")
        if new_query:
            query["user query"] = new_query
        result = []
        for num in query:
            if num == "prompt":
                continue
            prompt = query[num]
            print("ToT new_tree query prompt:", prompt)
            user_input = input("S to skip: ")
            if user_input == "S":
                continue
            agent = agents.debugmate_agent.MongoAgent(
                model="gpt-4-0613", temp=0.1, streaming=False
            )
            prompt = query["prompt"] + "\n\n" + prompt + "\n\n" + eval_prompt
            response = agent.run(prompt)
            result.append(response)
            if "parent node should conclude" in response:
                break
        return "\n".join(result)
