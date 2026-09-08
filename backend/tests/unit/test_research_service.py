from unittest.mock import AsyncMock

import pytest

from app.models.research_session import ResearchSession
from app.repositories.research_session import ResearchSessionRepository
from app.services.research import ResearchService


@pytest.mark.asyncio
async def test_create_research_session() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    expected = ResearchSession(
        question="How does AI affect software engineering jobs?",
    )

    repository.create.return_value = expected

    result = await service.create_research_session(
        "How does AI affect software engineering jobs?"
    )

    assert result is expected

    repository.create.assert_awaited_once_with(
        "How does AI affect software engineering jobs?"
    )


@pytest.mark.asyncio
async def test_get_research_session() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    expected = ResearchSession(
        question="What are the economic effects of AI?"
    )

    repository.get_by_id.return_value = expected

    research_id = expected.id

    result = await service.get_research_session(research_id)

    assert result is expected

    repository.get_by_id.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_get_missing_research_session() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    repository.get_by_id.return_value = None

    research_id = ResearchSession(
        question="Missing session"
    ).id

    result = await service.get_research_session(research_id)

    assert result is None

    repository.get_by_id.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_list_research_sessions() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    expected = [
        ResearchSession(question="First question"),
        ResearchSession(question="Second question"),
    ]

    repository.list.return_value = expected

    result = await service.list_research_sessions()

    assert result == expected

    repository.list.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_research_session() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    repository.delete.return_value = True

    research_id = ResearchSession(
        question="Question to delete"
    ).id

    result = await service.delete_research_session(research_id)

    assert result is True

    repository.delete.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_run_research_persists_workflow_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_session = ResearchSession(
        question="What are the effects of AI automation?",
    )
    repository.create.return_value = research_session

    saved_session = ResearchSession(
        question="What are the effects of AI automation?",
        status="synthesizing",
        final_report="Research report",
    )
    repository.save_result.return_value = saved_session

    expected_result = {
        "status": "synthesizing",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": ["What are the main effects?"],
        },
        "sources": [],
        "evidence": [],
        "findings": [
            {
                "claim": "AI affects employment.",
                "evidence_ids": ["E1"],
            }
        ],
        "finding_citations": [[1]],
        "citations": [
            {
                "citation_id": 1,
                "url": "https://example.com/source",
            }
        ],
        "conflicts": [],
        "sufficiency_score": 0.80,
        "sufficiency_reasons": [],
        "confidence": 0.90,
        "final_report": "Research report",
    }

    class FakeGraph:
        async def ainvoke(self, initial_state):
            assert initial_state["research_id"] == research_session.id
            assert initial_state["question"] == (
                "What are the effects of AI automation?"
            )
            assert initial_state["status"] == "pending"
            assert initial_state["evidence"] == []
            assert initial_state["sources"] == []

            return expected_result

    monkeypatch.setattr(
        service,
        "_build_research_graph",
        lambda: FakeGraph(),
    )

    result = await service.run_research(
        "What are the effects of AI automation?"
    )

    assert result is saved_session

    repository.create.assert_awaited_once_with(
        "What are the effects of AI automation?"
    )

    repository.save_result.assert_awaited_once_with(
        research_session.id,
        status="synthesizing",
        research_plan=expected_result["research_plan"],
        sources=[],
        evidence=[],
        findings=expected_result["findings"],
        citations=expected_result["citations"],
        finding_citations=expected_result["finding_citations"],
        conflicts=[],
        sufficiency_score=0.80,
        sufficiency_reasons=[],
        confidence=0.90,
        final_report="Research report",
    )