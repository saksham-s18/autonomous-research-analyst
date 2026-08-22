from uuid import uuid4

import pytest

from app.agents.evidence import EvidenceOutput
from app.agents.planner import ResearchPlanOutput
from app.graph import nodes
from app.graph.workflow import build_research_graph
from app.tools.search import SearchResult


class FakePlanner:
    """Fake planner used to keep workflow tests offline."""

    async def create_plan(self, question: str) -> ResearchPlanOutput:
        return ResearchPlanOutput(
            goal=question,
            subquestions=[
                "What are the main aspects?",
                "What evidence exists?",
                "What are the benefits and risks?",
            ],
        )


class FakeResearchAgent:
    """Fake researcher used to keep workflow tests offline."""

    async def research(
        self,
        subquestion: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        return [
            {
                "title": f"Research source for {subquestion}",
                "url": "https://example.com/source",
                "snippet": f"Evidence about: {subquestion}",
            }
        ]


class FakeFetcher:
    """Fake source fetcher used in workflow tests."""

    async def fetch(self, url: str) -> str:
        return f"Source content for {url}"


class FakeEvidenceAgent:
    """Fake evidence agent used in workflow tests."""

    async def extract(
        self,
        subquestion: str,
        source_url: str,
        content: str,
    ) -> EvidenceOutput:
        return EvidenceOutput(
            claim=f"Evidence about {subquestion}",
            supporting_text=content,
            relevance=0.95,
            confidence=0.90,
        )


@pytest.mark.asyncio
async def test_research_workflow_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Replace real external dependencies with deterministic fakes.
    monkeypatch.setattr(
        nodes,
        "create_planner_agent",
        lambda: FakePlanner(),
    )

    monkeypatch.setattr(
        nodes,
        "create_research_agent",
        lambda: FakeResearchAgent(),
    )

    monkeypatch.setattr(
        nodes,
        "HttpSourceFetcher",
        FakeFetcher,
    )

    monkeypatch.setattr(
        nodes,
        "create_evidence_agent",
        lambda: FakeEvidenceAgent(),
    )

    graph = build_research_graph()

    state = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "pending",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [],
        },
        "current_subquestion": None,
        "completed_subquestions": [],
        "evidence": [],
        "sources": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    result = await graph.ainvoke(state)

    assert result["status"] == "synthesizing"
    assert result["question"] == "What are the effects of AI automation?"

    assert result["research_plan"]["goal"] == (
        "What are the effects of AI automation?"
    )
    assert len(result["research_plan"]["subquestions"]) == 3

    assert len(result["completed_subquestions"]) == 3
    assert len(result["sources"]) == 3
    assert len(result["evidence"]) == 3

    assert all(
        item["source_url"] == "https://example.com/source"
        for item in result["evidence"]
    )

    assert all(
        item["claim"].startswith("Evidence about")
        for item in result["evidence"]
    )

    assert all(
        item["supporting_text"].startswith("Source content")
        for item in result["evidence"]
    )

    assert all(
        item["relevance"] == 0.95
        for item in result["evidence"]
    )

    assert all(
        item["confidence"] == 0.90
        for item in result["evidence"]
    )

    assert all(
        item["subquestion"] in result["completed_subquestions"]
        for item in result["evidence"]
    )

    assert result["current_subquestion"] is None