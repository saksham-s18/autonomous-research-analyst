"""Research agent implementation."""

from app.tools.search import SearchResult, SearchTool


class ResearchAgent:
    """Research a single subquestion using a search tool."""

    def __init__(self, search_tool: SearchTool) -> None:
        self.search_tool = search_tool

    async def research(
        self,
        subquestion: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Search for evidence relevant to a subquestion."""

        return await self.search_tool.search(
            subquestion,
            max_results=max_results,
        )