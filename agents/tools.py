import langchain.agents
from langchain.base_language import BaseLanguageModel

import tools.stackoverflowtool
import tools.confluence_tool
import tools.code_tool
import agents.ToT_tool


def make_tools(llm: BaseLanguageModel, api_keys: dict = {}, verbose=True):
    all_tools = langchain.agents.load_tools([])

    stack_overflow_tool = tools.stackoverflowtool.StackOverflowTool()
    confluence_tool = tools.confluence_tool.ConfluenceTool()
    code_tool = tools.code_tool.CodeTool()
    tot_tool = agents.ToT_tool.ToTTool()

    all_tools += [stack_overflow_tool]
    all_tools += [confluence_tool]
    all_tools += [code_tool]
    all_tools += [tot_tool]

    return all_tools
