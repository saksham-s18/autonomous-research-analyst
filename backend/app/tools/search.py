"""Search tool abstractions and Tavily implementation."""

from abc import ABC, abstractmethod
from typing import TypedDict

from tavily import AsyncTavilyClient


class SearchResult(TypedDict):
    """A single web search result."""

    title: str
    url: str
    snippet: str


class SearchTool(ABC):
    """Abstract interface for web search."""

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Search the web and return relevant results."""
        raise NotImplementedError


class TavilySearchTool(SearchTool):
    """Search the web using Tavily."""

    def __init__(self, api_key: str) -> None:
        self.client = AsyncTavilyClient(api_key=api_key)

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Search Tavily and normalize the results."""

        response = await self.client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
        )

        return [
            {
                "title": result["title"],
                "url": result["url"],
                "snippet": result.get("content", ""),
            }
            for result in response["results"]
        ]