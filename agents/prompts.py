# flake8: noqa
PREFIX = """
You are a debugging agent and your task is to respond to the question or
solve the problem to the best of your ability using the provided tools.
"""

FORMAT_INSTRUCTIONS = """
You can only respond with a single complete
"Thought, Action, Action Input" format
OR a single "Final Answer" format.

Complete format:

Thought: (reflect on your progress and decide what to do next)
Action: (the action name, should be one of [{tool_names}])
Action Input: (the input string to the action)

OR

Final Answer: (the final answer to the original user query along with a confidence score of how effective each
hypothesis is in solving the problem and how likely the interpretation is correct out of 100.)
"""

QUESTION_PROMPT = """
Answer the question below using the following tools:

{tool_strings}

From the tools provided, select the best tool available for each action.

IMPORTANT: Your first step is to check the following, and plan your steps accordingly:
1. Use the code search tool to ask for a specific function referenced that may be useful for debugging.
2. If multiple functions called in the code output could be related to the issue, use ToT_tool and input all the
possible related functions with a description.
3. From the ToT_tool output, make a list of multiple possible explanations with solutions when needed.
4. Check if the problem to be solved needs code or implementation details of the code; if so look for the code base,
official documentation, or developer forums.
5. If stack trace is not provided and no function or class names are mentioned, use other tools such as StackOverflow or
Confluence tool.
6. Don't only check the current function, check all the functions it is calling that you think could have caused the issue.
7. Do not stop until you find the exact lines causing the issue.
8. Your output should include a confidence score of the answer you are suggesting along with a detailed explanation of
the reason for the score.

Do not skip these steps.
Do not finish the chain if you have suggestions for user to debug one or many functions. If so, use the code tool or
ToT_tool and continue the debugging process.
Do not finish chain until you find exact lines that caused the error and can give the user at least one specific solution.
Do not use a naming convention to search for classes using CodeSearch, your input needs to be definitive.
If the exact class you want to search for is not present in the output of CodeSearch, StackOverFlow search, or the prompt,
DO NOT use CodeSearch. Instead use another tool like Stackoverflow or Confluence to search for other ways to find a solution.
Final answer should contain a list of hypothesis if there are multiple possible reasons for the error.
Question: {input}
Your final answer should contain all information necessary to answer the question and subquestions.
"""

SUFFIX = """
Thought: {agent_scratchpad}
"""
FINAL_ANSWER_ACTION = "Final Answer:"

REPHRASE_TEMPLATE = """In this exercise you will assume the role of a software engineer assistant. Your task is to answer
the provided question as best as you can, based on the provided solution draft.
The solution draft follows the format "Thought, Action, Action Input, Observation", where the 'Thought' statements describe
a reasoning sequence. The rest of the text is information obtained to complement the reasoning sequence, and it is 100% accurate.
Your task is to write an answer to the question based on the solution draft, based on the following guidelines:
The text should have an educative and assistant-like tone, be accurate, follow the same reasoning sequence as the solution
draft and explain how any conclusion is reached.
Question: {question}

Solution draft: {agent_ans}

Answer:
"""

MRKL_NEXT_STEP_INPUT = """
Given the following list of intermediate steps, follow these guidelines:

    1. **Read the intermediate steps**:
        - Go through each tuple in the list.
        - Focus on the second element in each tuple (the 'content' field).

    2. **Modify the code content**:
        - Discard only parts of the code that are absolutely irrelevant to the main idea of the thought process.
        - Ensure to retain all information that is relevant to the query and may be useful later.
        - Remove duplicated code, boilerplate, or comments that do not add value to understanding the essential functionality.
        - Maintain import statements, crucial functions, logic, and operations necessary for the task.
        - Specifically keep all import statements, the entire function or class that is being referenced in the input, and implementations of them if present.

    3. **Explain modifications**:
        - Clearly mention which parts are deleted and why.
        - Ensure the agent does not request the same unnecessary information again.

    4. Your output should only include a modified version of the code in the last tuple of the list.

    5. Most importantly, do not remove import statements or package definitions.
The agent's current thought for what it expects as code output: {log}.
The agent's prompt to code RAG tool: {tool_input}
"""

BRANCHING_INSTRUCTIONS = """
I have been instructed by user input that the issue is specifically in the following.
{prompt_input}. Understand the function, write a description of what it does and how it could potentially
be related to the problem and then go deeper into function calls as required.
From there, repeat the process of using tools to continue debugging the issue."""


BRANCHING_INSTRUCTIONS = "Next Action: {prompt_input}"
