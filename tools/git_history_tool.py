from langchain.tools import BaseTool
import os
import json
import requests
import git
import openai


class GitHistoryTool(BaseTool):
    name = "GitHistorySearch"
    description = (
        "This tool retrieves Git History from the codebase."
        "Returns names of all relevant files changed and individual file changes when specified in query."
        "Input your query to retrieve context"
    )

    def __init__(self):
        super().__init__()

    def getFromBitBucket(self, url):
        bitbucket_key = os.getenv("BITBUCKET_API_KEY")
        headers = {
            "Authorization": f"Bearer {bitbucket_key}",
            "Content-Type": "application/json",
        }

        # diff between any two commits
        data = json.loads(requests.request("GET", url, headers=headers).text)
        return data

    def getChangedFiles(self, commit1, commit2):
        """Returns str of files changed in the latest commits"""
        result = ""
        path = os.getenv("CODE_PATH_LOCAL")
        repo = git.Repo(path)
        commits_touching_path = list(repo.iter_commits(paths=path))
        c1 = c2 = None
        for i in range(len(commits_touching_path)):
            commit = commits_touching_path[i]
            if commit1 in str(commit):
                c1 = i
                print("c1", i)
            if commit2 in str(commit):
                c2 = i
                print("c2", i)
        changes = repo.git.diff(
            commits_touching_path[c1], commits_touching_path[c2], path
        )
        print("Length:", len(changes.split("\n")))
        for line in changes.split("\n"):
            if "diff" in line:
                result += line + "\n"
        return result

    def ranking(self, query, diff_list):
        final_list = []
        openai_client = openai.OpenAI()
        model = "gpt-3.5-turbo"
        for i in range(0, len(diff_list), 20):
            diff_chunk = diff_list[i, i + 20]
            prompt = (
                """Select the five most likely changes that could be related to the following issue.
            Your answer should only contain the five changes that you think are most likely related to the issue.
            """
                + query
                + "\n".join(diff_chunk)
            )
            messages = [
                {"role": "user", "content": prompt},
            ]
            response = openai_client.chat.completions.create(
                model=model, messages=messages
            )
            final_list.append(response.choices[0].message.content)
        prompt = (
            """Select the five most likely changes that could be related to the following issue.
        Your answer should only contain the five changes that you think are most likely related to the issue.
        """
            + query
            + "\n".join(diff_chunk)
        )
        messages = [
            {"role": "user", "content": prompt},
        ]
        response = openai_client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content

    def _run(self, query: str):
        """Returns latest code differences based on the query."""
        path = os.getenv("CODE_PATH_LOCAL")
        result = ""
        repo = git.Repo(path)
        commits_touching_path = list(repo.iter_commits(paths=path))
        changes = repo.git.diff(
            commits_touching_path[0], commits_touching_path[5], path
        )
        start = False
        for line in changes.split("\n"):
            if query in line:
                start = True
            elif start and "diff" in line:
                print("line:", line)
                result += line + "\n"
                break
            if start:
                result += line + "\n"
        return result
