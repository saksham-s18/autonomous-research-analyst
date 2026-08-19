from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.repositories.research_session import ResearchSessionRepository


@pytest_asyncio.fixture(autouse=True)
async def cleanup_database_engine():
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_create_research_session(
    db_session: AsyncSession,
) -> None:
    repository = ResearchSessionRepository(db_session)

    research_session = await repository.create(
        "How does AI affect software engineering jobs?"
    )

    assert research_session.id is not None
    assert research_session.question == (
        "How does AI affect software engineering jobs?"
    )
    assert research_session.status == "pending"

    await repository.delete(research_session.id)


@pytest.mark.asyncio
async def test_get_research_session_by_id(
    db_session: AsyncSession,
) -> None:
    repository = ResearchSessionRepository(db_session)

    created = await repository.create(
        "What are the economic effects of AI automation in India?"
    )

    result = await repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.question == (
        "What are the economic effects of AI automation in India?"
    )

    await repository.delete(created.id)


@pytest.mark.asyncio
async def test_get_missing_research_session(
    db_session: AsyncSession,
) -> None:
    repository = ResearchSessionRepository(db_session)

    result = await repository.get_by_id(
    UUID("00000000-0000-0000-0000-000000000000")
)

    assert result is None


@pytest.mark.asyncio
async def test_list_research_sessions(
    db_session: AsyncSession,
) -> None:
    repository = ResearchSessionRepository(db_session)

    first = await repository.create("First research question")
    second = await repository.create("Second research question")

    sessions = await repository.list()

    session_ids = {session.id for session in sessions}

    assert first.id in session_ids
    assert second.id in session_ids

    await repository.delete(first.id)
    await repository.delete(second.id)


@pytest.mark.asyncio
async def test_delete_research_session(
    db_session: AsyncSession,
) -> None:
    repository = ResearchSessionRepository(db_session)

    created = await repository.create("Question to delete")

    deleted = await repository.delete(created.id)

    assert deleted is True

    result = await repository.get_by_id(created.id)

    assert result is None