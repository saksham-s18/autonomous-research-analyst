import pytest
import pytest_asyncio
from sqlalchemy import select, text

from app.db.session import AsyncSessionLocal, engine
from app.models import ResearchSession


@pytest_asyncio.fixture(autouse=True)
async def cleanup_database_engine():
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_database_connection() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_create_research_session() -> None:
    async with AsyncSessionLocal() as session:
        research_session = ResearchSession(
            question="How does AI affect software engineering jobs?",
        )

        session.add(research_session)
        await session.commit()
        await session.refresh(research_session)

        assert research_session.id is not None
        assert research_session.status == "pending"

        result = await session.execute(
            select(ResearchSession).where(
                ResearchSession.id == research_session.id
            )
        )

        saved_session = result.scalar_one()

        assert saved_session.question == (
            "How does AI affect software engineering jobs?"
        )

        await session.delete(saved_session)
        await session.commit()