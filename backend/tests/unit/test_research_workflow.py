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

class FakeConflictAgent:
    """Fake conflict agent used in workflow tests."""

    async def detect(
        self,
        subquestion: str,
        evidence: list,
    ) -> list:
        return []


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
        "create_conflict_agent",
        lambda: FakeConflictAgent(),
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
        "source_failures": [],
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
        source["quality_score"] == 0.50
        for source in result["sources"]
    )

    assert all(
        source["quality_category"] == "general_web"
        for source in result["sources"]
    )

    assert all(
        source["quality_reasons"] == ["General web source."]
        for source in result["sources"]
    )

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
        item["evidence_score"] == 0.82
        for item in result["evidence"]
    )

    assert all(
        item["subquestion"] in result["completed_subquestions"]
        for item in result["evidence"]
    )

    assert result["current_subquestion"] is None

    assert result["conflicts"] == []


@pytest.mark.asyncio
async def test_research_workflow_handles_evidence_agent_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Evidence extraction errors should be caught and recorded."""

    class FailingEvidenceAgent:
        async def extract(
            self,
            subquestion: str,
            source_url: str,
            content: str,
        ) -> EvidenceOutput:
            raise RuntimeError("Failed to parse evidence")

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
        lambda: FailingEvidenceAgent(),
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
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    result = await graph.ainvoke(state)

    assert result["status"] == "synthesizing"
    assert len(result["sources"]) == 3
    assert len(result["evidence"]) == 0
    assert len(result["source_failures"]) == 3

    assert all(
        failure["stage"] == "extract"
        for failure in result["source_failures"]
    )

    assert all(
        failure["error_type"] == "extraction_error"
        for failure in result["source_failures"]
    )

    assert all(
        failure["retryable"] is True
        for failure in result["source_failures"]
    )

    assert all(
        failure["error_message"] == "Evidence extraction failed."
        for failure in result["source_failures"]
    )


@pytest.mark.asyncio
async def test_synthesis_detects_conflicts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Synthesis should persist conflicts returned by the agent."""

    class ConflictProducingAgent:
        async def detect(
            self,
            subquestion: str,
            evidence: list,
        ) -> list:
            from app.agents.conflict import ConflictOutput

            return [
                ConflictOutput(
                    topic="AI employment",
                    evidence_a="AI creates jobs.",
                    evidence_b="AI displaces jobs.",
                    conflict_type="contextual",
                    explanation=(
                        "The evidence describes different employment "
                        "effects of automation."
                    ),
                    severity=0.60,
                    confidence=0.90,
                )
            ]

    monkeypatch.setattr(
        nodes,
        "create_conflict_agent",
        lambda: ConflictProducingAgent(),
    )

    state = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the employment effects of AI?"
            ],
        },
        "current_subquestion": None,
        "completed_subquestions": [
            "What are the employment effects of AI?"
        ],
        "evidence": [
            {
                "subquestion": "What are the employment effects of AI?",
                "claim": "AI creates jobs.",
                "supporting_text": "New AI roles are emerging.",
                "source_url": "https://example.com/a",
                "relevance": 0.90,
                "confidence": 0.85,
                "evidence_score": 0.90,
            },
            {
                "subquestion": "What are the employment effects of AI?",
                "claim": "AI displaces jobs.",
                "supporting_text": "Some existing roles are automated.",
                "source_url": "https://example.com/b",
                "relevance": 0.90,
                "confidence": 0.85,
                "evidence_score": 0.85,
            },
        ],
        "sources": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    result = await nodes.synthesis_node(state)

    assert result["status"] == "synthesizing"
    assert len(result["conflicts"]) == 1

    conflict = result["conflicts"][0]

    assert conflict["topic"] == "AI employment"
    assert conflict["claims"] == [
        "AI creates jobs.",
        "AI displaces jobs.",
    ]
    assert conflict["conflict_type"] == "contextual"
    assert conflict["severity"] == 0.60
    assert conflict["confidence"] == 0.90