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