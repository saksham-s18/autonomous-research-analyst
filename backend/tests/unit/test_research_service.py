from app.models import research_session
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
    repository.get_by_id.return_value = research_session

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
        async def astream(self, initial_state, stream_mode):
            assert initial_state["research_id"] == research_session.id
            assert initial_state["question"] == (
                "What are the effects of AI automation?"
            )
            assert initial_state["status"] == "pending"
            assert initial_state["evidence"] == []
            assert initial_state["sources"] == []
            assert stream_mode == "values"

            yield {
                **initial_state,
                "status": "researching",
                "current_subquestion": "What are the main effects?",
            }

            yield expected_result

    monkeypatch.setattr(
        service,
        "_build_research_graph",
        lambda: FakeGraph(),
    )

    result = await service.run_research(
        research_session.id,
    )

    assert result is saved_session

    repository.get_by_id.assert_awaited_once_with(
        research_session.id,
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

    assert repository.save_checkpoint.await_count == 2

    first_checkpoint = repository.save_checkpoint.await_args_list[0].args[1]
    second_checkpoint = repository.save_checkpoint.await_args_list[1].args[1]

    assert first_checkpoint["status"] == "researching"
    assert first_checkpoint["current_subquestion"] == (
        "What are the main effects?"
    )

    assert second_checkpoint == expected_result

    assert all(
        call.args[0] == research_session.id
        for call in repository.save_checkpoint.await_args_list
    )

@pytest.mark.asyncio
async def test_save_research_checkpoint() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_id = ResearchSession(
        question="How does AI affect software engineering jobs?"
    ).id

    workflow_state = {
        "research_id": str(research_id),
        "question": "How does AI affect software engineering jobs?",
        "status": "researching",
        "current_subquestion": "What jobs are affected?",
        "completed_subquestions": [
            "What is the current state of AI adoption?"
        ],
        "research_iterations": 1,
    }

    expected = ResearchSession(
        question="How does AI affect software engineering jobs?",
        status="researching",
    )
    expected.workflow_state = workflow_state

    repository.save_checkpoint.return_value = expected

    result = await service.save_research_checkpoint(
        research_id,
        workflow_state,
    )

    assert result is expected

    repository.save_checkpoint.assert_awaited_once_with(
        research_id,
        workflow_state,
    )


@pytest.mark.asyncio
async def test_get_research_checkpoint() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_id = ResearchSession(
        question="How does AI affect software engineering jobs?"
    ).id

    workflow_state = {
        "research_id": str(research_id),
        "question": "How does AI affect software engineering jobs?",
        "status": "researching",
        "current_subquestion": "What jobs are affected?",
        "completed_subquestions": [
            "What is the current state of AI adoption?"
        ],
        "research_iterations": 1,
    }

    repository.get_checkpoint.return_value = workflow_state

    result = await service.get_research_checkpoint(research_id)

    assert result == workflow_state

    repository.get_checkpoint.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_resume_research_uses_saved_checkpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_session = ResearchSession(
        question="What are the effects of AI automation?",
        status="researching",
    )

    checkpoint = {
        "research_id": research_session.id,
        "question": "What are the effects of AI automation?",
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the main aspects?",
                "What evidence exists?",
            ],
        },
        "current_subquestion": None,
        "completed_subquestions": [
            "What are the main aspects?",
        ],
        "follow_up_subquestions": [],
        "research_iterations": 1,
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

    expected_result = {
        **checkpoint,
        "status": "synthesizing",
        "completed_subquestions": [
            "What are the main aspects?",
            "What evidence exists?",
        ],
        "research_iterations": 2,
        "final_report": "Resumed research report",
        "confidence": 0.90,
    }

    repository.get_by_id.return_value = research_session
    repository.get_checkpoint.return_value = checkpoint

    saved_session = ResearchSession(
        question="What are the effects of AI automation?",
        status="synthesizing",
        final_report="Resumed research report",
    )
    repository.save_result.return_value = saved_session

    class FakeGraph:
        async def astream(self, initial_state, stream_mode):
            assert initial_state == checkpoint
            assert stream_mode == "values"

            yield expected_result

    monkeypatch.setattr(
        service,
        "_build_research_graph",
        lambda: FakeGraph(),
    )

    result = await service.resume_research(research_session.id)

    assert result is saved_session

    repository.get_by_id.assert_awaited_once_with(
        research_session.id,
    )

    repository.get_checkpoint.assert_awaited_once_with(
        research_session.id,
    )

    repository.save_checkpoint.assert_awaited_once_with(
        research_session.id,
        expected_result,
    )

    repository.save_result.assert_awaited_once_with(
        research_session.id,
        status="synthesizing",
        research_plan=checkpoint["research_plan"],
        sources=[],
        evidence=[],
        findings=None,
        citations=[],
        finding_citations=None,
        conflicts=[],
        sufficiency_score=None,
        sufficiency_reasons=[],
        confidence=0.90,
        final_report="Resumed research report",
    )


@pytest.mark.asyncio
async def test_get_research_status_without_checkpoint() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_session = ResearchSession(
        question="What are the effects of AI automation?",
        status="pending",
    )

    repository.get_by_id.return_value = research_session
    repository.get_checkpoint.return_value = None

    result = await service.get_research_status(research_session.id)

    assert result == {
        "id": research_session.id,
        "status": "pending",
        "progress": {
            "completed_subquestions": 0,
            "total_subquestions": 0,
            "research_iterations": 0,
            "max_research_iterations": 3,
        },
        "error": None,
    }

    repository.get_by_id.assert_awaited_once_with(
        research_session.id,
    )
    repository.get_checkpoint.assert_awaited_once_with(
        research_session.id,
    )


@pytest.mark.asyncio
async def test_get_research_status_from_checkpoint() -> None:
    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_session = ResearchSession(
        question="What are the effects of AI automation?",
        status="researching",
    )

    checkpoint = {
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the main effects?",
                "What evidence exists?",
                "What are the risks?",
                "What are the limitations?",
            ],
        },
        "completed_subquestions": [
            "What are the main effects?",
            "What evidence exists?",
        ],
        "research_iterations": 2,
        "max_research_iterations": 3,
        "error": None,
    }

    repository.get_by_id.return_value = research_session
    repository.get_checkpoint.return_value = checkpoint

    result = await service.get_research_status(research_session.id)

    assert result == {
        "id": research_session.id,
        "status": "researching",
        "progress": {
            "completed_subquestions": 2,
            "total_subquestions": 4,
            "research_iterations": 2,
            "max_research_iterations": 3,
        },
        "error": None,
    }

    repository.get_by_id.assert_awaited_once_with(
        research_session.id,
    )
    repository.get_checkpoint.assert_awaited_once_with(
        research_session.id,
    )


@pytest.mark.asyncio
async def test_run_research_logs_lifecycle_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import patch

    repository = AsyncMock(spec=ResearchSessionRepository)
    service = ResearchService(repository)

    research_session = ResearchSession(
        question="What are the effects of AI automation?",
    )
    repository.get_by_id.return_value = research_session
    repository.save_result.return_value = research_session

    class FakeGraph:
        async def astream(self, initial_state, stream_mode):
            yield {
                **initial_state,
                "status": "synthesizing",
                "research_plan": {"goal": "test", "subquestions": []},
                "sources": [],
                "evidence": [],
                "citations": [],
                "conflicts": [],
                "sufficiency_score": 1.0,
                "sufficiency_reasons": [],
                "confidence": 0.95,
                "final_report": "report",
            }

    monkeypatch.setattr(
        service,
        "_build_research_graph",
        lambda: FakeGraph(),
    )

    with patch("app.services.research.logger") as mock_logger:
        await service.run_research(research_session.id)

    mock_logger.info.assert_any_call(
        "research_run_started",
        extra={"research_id": str(research_session.id)},
    )
    mock_logger.info.assert_any_call(
        "research_run_completed",
        extra={
            "research_id": str(research_session.id),
            "status": "synthesizing",
            "confidence": 0.95,
        },
    )
