from langchain.tools import BaseTool
from tools.help_desk import HelpDesk


class ConfluenceTool(BaseTool):
    name = "ConfluenceSearch"
    description = (
        "The tool retrieves information about all organizational services"
        "Input your query to retrieve internal context"
    )

    def __init__(self):
        super().__init__()

    def _run(self, query: str):
        """Executes a search on Confluence based on the query."""
        model = HelpDesk(new_db=False)
        # result = model.retrieval_qa_inference(query)
        result = model.get_text(query)
        return result
