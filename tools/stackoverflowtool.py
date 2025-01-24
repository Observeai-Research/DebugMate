from langchain.tools import BaseTool

import requests
from bs4 import BeautifulSoup
from googlesearch import search

class StackOverflowTool(BaseTool):
    name = "StackOverflowSearch"
    description = (
        "Input a query string and returns an answer from stack overflow"
        "Search Stack Overflow to find relevant similar questions and fetch the answers"
    )
    max_answers = 10

    def __init__(self, max_answers=10):
        super().__init__()
        self.max_answers = max_answers

    def _run(self, query: str):
        """Executes a search on Stack Overflow based on the query."""
        search_results = list(
            search(
                "site:stackoverflow.com " + query, num_results=1
            )
        )
        # most_relevant_question_link = self.search_stack_overflow(query)
        most_relevant_question_link = search_results[0]
        if most_relevant_question_link == "Error":
            return "Didn't find any relevant information on Stack Overflow, use some other tool"
        question_content = self.fetch_question_content(most_relevant_question_link)
        answer_string = self.parse_stack_overflow_get_answer(question_content)["answer"]
        return answer_string

    def search_stack_overflow(self, query: str):
        base_url = "https://api.stackexchange.com/2.3/search"
        params = {
            "site": "stackoverflow",
            "intitle": query,  # Search query
            "sort": "relevance",  # Sort by relevance
            "order": "desc",  # Order in descending order
            "pagesize": 1,  # Number of results per page
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["items"]:
                return data["items"][0][
                    "link"
                ]  # Return the link to the most relevant question
            else:
                return "Error"
        else:
            return "Error"

    def fetch_question_content(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            question_title = soup.find("a", class_="question-hyperlink").text.strip()
            question_body = (
                soup.find("div", class_="question")
                .find("div", class_="js-post-body")
                .text.strip()
            )
            answers = soup.find_all("div", class_="answer")
            if not answers:
                answers = soup.find_all("span", class_="comment-copy")
                answer_texts = [answer.text.strip() for answer in answers]
            else:
                answer_texts = [
                    answer.find("div", class_="js-post-body").text.strip()
                    for answer in answers
                ]
            return {
                "title": question_title,
                "body": question_body,
                "answers": " next answer: ".join(answer_texts[: self.max_answers]),
            }
        else:
            return {
                "title": "Error fetching question title.",
                "body": "Error fetching question content.",
                "answers": "could not fetch, invalid url specified",
            }

    def parse_stack_overflow_get_answer(self, content):
        return {"answer": content["answers"]}
