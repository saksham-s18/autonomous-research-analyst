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
        initial_subquestions = [
            "What are the main aspects?",
            "What evidence exists?",
            "What are the benefits and risks?",
        ]
        suffix = "" if subquestion in initial_subquestions else "2"

        return [
            {
                "title": f"Research source for {subquestion}",
                "url": f"https://example.com/source{suffix}",
                "snippet": f"Evidence about: {subquestion}",
            }
        ]


class FakeFetcher:
    """Fake source fetcher used in workflow tests."""

    async def fetch(self, url: str) -> str:
        return f"Source content for {url}"


class FakeEvidenceAgent:
    """Fake evidence agent used in workflow tests."""

    def __init__(
        self,
        relevance: float = 0.95,
        confidence: float = 0.90,
    ) -> None:
        self.relevance = relevance
        self.confidence = confidence

    async def extract(
        self,
        subquestion: str,
        source_url: str,
        content: str,
    ) -> EvidenceOutput:
        return EvidenceOutput(
            claim=f"Evidence about {subquestion}",
            supporting_text=content,
            relevance=self.relevance,
            confidence=self.confidence,
        )

class FakeSynthesisAgent:
    """Fake synthesis agent used in workflow tests."""

    async def synthesize(
        self,
        question: str,
        evidence: list,
        conflicts: list,
    ):
        from app.agents.synthesis import SynthesisOutput

        return SynthesisOutput(
            title="Effects of AI Automation",
            executive_summary="Synthesized research report.",
            key_findings=[
                "AI automation affects employment.",
            ],
            detailed_analysis=(
                "AI automation can change employment patterns."
            ),
            conflicting_evidence=[],
            limitations=[
                "The research evidence is limited.",
            ],
            conclusion=(
                "AI automation has both benefits and risks."
            ),
            confidence=0.91,
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
        lambda: FakeEvidenceAgent(
            relevance=0.50,
            confidence=0.50,
        ),
    )

    monkeypatch.setattr(
        nodes,
        "create_synthesis_agent",
        lambda: FakeSynthesisAgent(),
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
        "follow_up_subquestions": [],
        "research_iterations": 0,
        "max_research_iterations": 3,
        "evidence": [],
        "sources": [],
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
        "error": None,
    }

    result = await graph.ainvoke(state)

    assert result["status"] == "synthesizing"
    assert result["question"] == "What are the effects of AI automation?"

    assert result["research_plan"]["goal"] == (
        "What are the effects of AI automation?"
    )
    assert result["research_iterations"] == 3
    assert result["max_research_iterations"] == 3
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
        item["relevance"] == 0.50
        for item in result["evidence"]
    )

    assert all(
        item["confidence"] == 0.50
        for item in result["evidence"]
    )

    assert all(
        item["evidence_score"] == 0.50
        for item in result["evidence"]
    )

    assert all(
        item["subquestion"] in result["completed_subquestions"]
        for item in result["evidence"]
    )

    assert result["current_subquestion"] is None

    assert result["conflicts"] == []
    assert result["sufficiency_score"] is not None
    assert result["sufficiency_score"] >= 0.70


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

    monkeypatch.setattr(
        nodes,
        "create_synthesis_agent",
        lambda: FakeSynthesisAgent(),
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
        "follow_up_subquestions": [],
        "research_iterations": 0,
        "max_research_iterations": 3,
        "evidence": [],
        "sources": [],
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
        "error": None,
    }

    result = await graph.ainvoke(state)

    assert result["status"] == "synthesizing"
    assert len(result["sources"]) == 4
    assert len(result["evidence"]) == 0
    assert len(result["source_failures"]) == 4

    assert len(result["follow_up_subquestions"]) == 1
    assert result["follow_up_subquestions"][0].startswith(
        "What additional evidence"
    )

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
        "research_iterations": 0,
        "max_research_iterations": 3,
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
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
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


@pytest.mark.asyncio
async def test_synthesis_marks_insufficient_research() -> None:
    """Synthesis should record insufficient research."""

    state = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the employment effects of AI?",
                "What are the productivity effects of AI?",
                "What are the risks of AI automation?",
            ],
        },
        "current_subquestion": None,
        "completed_subquestions": [],
        "research_iterations": 0,
        "max_research_iterations": 3,
        "evidence": [],
        "sources": [],
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
        "error": None,
    }

    result = await nodes.synthesis_node(state)

    assert result["sufficiency_score"] == 0.0
    assert result["sufficiency_reasons"] == [
        "No evidence was collected.",
    ]
    assert result["conflicts"] == []

@pytest.mark.asyncio
async def test_research_workflow_generates_follow_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workflow should generate follow-up research when needed."""

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
        lambda: FakeEvidenceAgent(
            relevance=0.20,
            confidence=0.20,
        ),
    )

    monkeypatch.setattr(
        nodes,
        "create_synthesis_agent",
        lambda: FakeSynthesisAgent(),
    )

    monkeypatch.setattr(
        nodes,
        "create_conflict_agent",
        lambda: FakeConflictAgent(),
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
        "follow_up_subquestions": [],
        "research_iterations": 0,
        "max_research_iterations": 3,
        "evidence": [],
        "sources": [],
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
        "error": None,
    }

    result = await graph.ainvoke(state)

    assert result["status"] == "synthesizing"

    assert result["draft_report"] == "Synthesized research report."
    assert result["final_report"] == (
        "Synthesized research report."
        "\n\nSources:\n"
        "[1] https://example.com/source\n"
        "[2] https://example.com/source2"
    )
    assert result["confidence"] == 0.91

    assert result["citations"] == [
        {
            "citation_id": 1,
            "url": "https://example.com/source",
        },
        {
            "citation_id": 2,
            "url": "https://example.com/source2",
        },
    ]

    assert result["research_iterations"] == 4
    assert result["max_research_iterations"] == 3

    assert len(result["follow_up_subquestions"]) == 1

    assert result["follow_up_subquestions"][0].startswith(
        "What additional evidence"
    )                   

    assert result["sufficiency_score"] is not None
    assert result["sufficiency_score"] < 0.70


@pytest.mark.asyncio
async def test_synthesis_node_persists_generated_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Synthesis node should persist the generated research report."""

    monkeypatch.setattr(
        nodes,
        "create_conflict_agent",
        lambda: FakeConflictAgent(),
    )

    monkeypatch.setattr(
        nodes,
        "create_synthesis_agent",
        lambda: FakeSynthesisAgent(),
    )

    state = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the employment effects?",
            ],
        },
        "current_subquestion": None,
        "completed_subquestions": [
            "What are the employment effects?",
        ],
        "follow_up_subquestions": [],
        "research_iterations": 1,
        "max_research_iterations": 3,
        "evidence": [
            {
                "subquestion": "What are the employment effects?",
                "claim": "AI can automate routine tasks.",
                "supporting_text": (
                    "Automation can replace some routine activities."
                ),
                "source_url": "https://example.com/source",
                "relevance": 0.90,
                "confidence": 0.85,
                "evidence_score": 0.87,
            },
            {
                "subquestion": "What are the employment effects?",
                "claim": "AI can create new jobs.",
                "supporting_text": (
                    "New roles can emerge around AI systems."
                ),
                "source_url": "https://example.com/source2",
                "relevance": 0.85,
                "confidence": 0.80,
                "evidence_score": 0.82,
            },
        ],
        "sources": [],
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
        "error": None,
    }

    result = await nodes.synthesis_node(state)

    assert result["status"] == "synthesizing"
    assert result["draft_report"] == "Synthesized research report."
    assert result["final_report"] == (
        "Synthesized research report."
        "\n\nSources:\n"
        "[1] https://example.com/source\n"
        "[2] https://example.com/source2"
    )
    assert result["confidence"] == 0.91
    assert result["error"] is None
    assert result["conflicts"] is not None

@pytest.mark.asyncio
async def test_synthesis_node_handles_synthesis_agent_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Synthesis failures should be recorded instead of crashing."""

    class FailingSynthesisAgent:
        async def synthesize(
            self,
            question: str,
            evidence: list,
            conflicts: list,
        ):
            raise RuntimeError("Synthesis generation failed")

    monkeypatch.setattr(
        nodes,
        "create_conflict_agent",
        lambda: FakeConflictAgent(),
    )

    monkeypatch.setattr(
        nodes,
        "create_synthesis_agent",
        lambda: FailingSynthesisAgent(),
    )

    state = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the employment effects?",
            ],
        },
        "current_subquestion": None,
        "completed_subquestions": [
            "What are the employment effects?",
        ],
        "follow_up_subquestions": [],
        "research_iterations": 1,
        "max_research_iterations": 3,
        "evidence": [
            {
                "subquestion": "What are the employment effects?",
                "claim": "AI can automate routine tasks.",
                "supporting_text": (
                    "Automation can replace some routine activities."
                ),
                "source_url": "https://example.com/source",
                "relevance": 0.90,
                "confidence": 0.85,
                "evidence_score": 0.87,
            },
            {
                "subquestion": "What are the employment effects?",
                "claim": "AI can create new jobs.",
                "supporting_text": (
                    "New roles can emerge around AI systems."
                ),
                "source_url": "https://example.com/source2",
                "relevance": 0.85,
                "confidence": 0.80,
                "evidence_score": 0.82,
            },
        ],
        "sources": [],
        "citations": [],
        "source_failures": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "sufficiency_score": None,
        "sufficiency_reasons": [],
        "error": None,
    }

    result = await nodes.synthesis_node(state)

    assert result["status"] == "synthesis_failed"
    assert result["draft_report"] is None
    assert result["final_report"] is None
    assert result["confidence"] is None
    assert result["error"] == "Synthesis generation failed"
    assert result["current_subquestion"] is None
    assert result["conflicts"] is not None
    assert result["sufficiency_score"] is not None