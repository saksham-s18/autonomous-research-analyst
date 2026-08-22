import pytest

from app.tools.search import SearchResult, SearchTool


class FakeSearchTool(SearchTool):
    """Deterministic search implementation for tests."""

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        return [
            {
                "title": "AI Automation in India",
                "url": "https://example.com/ai",
                "snippet": "Research about AI automation.",
            }
        ]


@pytest.mark.asyncio
async def test_search_tool_returns_search_results() -> None:
    tool = FakeSearchTool()

    results = await tool.search(
        "economic effects of AI automation in India"
    )

    assert len(results) == 1
    assert results[0]["title"] == "AI Automation in India"
    assert results[0]["url"] == "https://example.com/ai"