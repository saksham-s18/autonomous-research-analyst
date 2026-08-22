import pytest

from app.agents.researcher import ResearchAgent
from app.tools.search import SearchResult, SearchTool


class FakeSearchTool(SearchTool):
    """Deterministic search tool for tests."""

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        return [
            {
                "title": "AI Employment Research",
                "url": "https://example.com/employment",
                "snippet": "AI affects employment in multiple sectors.",
            },
            {
                "title": "AI Productivity Research",
                "url": "https://example.com/productivity",
                "snippet": "AI can influence productivity.",
            },
        ]


@pytest.mark.asyncio
async def test_research_agent_searches_subquestion() -> None:
    agent = ResearchAgent(FakeSearchTool())

    results = await agent.research(
        "What are the employment effects of AI automation?"
    )

    assert len(results) == 2
    assert results[0]["title"] == "AI Employment Research"
    assert results[1]["title"] == "AI Productivity Research"