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


@pytest.mark.asyncio
async def test_save_research_result(
    db_session: AsyncSession,
) -> None:
    repository = ResearchSessionRepository(db_session)

    created = await repository.create(
        "How does AI affect software engineering jobs?"
    )

    result = await repository.save_result(
        created.id,
        status="completed",
        research_plan={
            "goal": "Understand the impact of AI on software engineering jobs",
            "subquestions": ["What jobs are affected?"],
        },
        sources=[
            {
                "title": "Example source",
                "url": "https://example.com/source",
            }
        ],
        evidence=[
            {
                "evidence_id": "E1",
                "subquestion": "What jobs are affected?",
                "claim": "AI changes software engineering workflows.",
                "supporting_text": "Example supporting text",
                "source_url": "https://example.com/source",
                "relevance": 0.9,
                "confidence": 0.8,
                "evidence_score": 0.85,
            }
        ],
        findings=[
            {
                "claim": "AI changes software engineering workflows.",
                "evidence_ids": ["E1"],
            }
        ],
        citations=[
            {
                "citation_id": 1,
                "url": "https://example.com/source",
            }
        ],
        finding_citations=[[1]],
        conflicts=[],
        sufficiency_score=0.9,
        sufficiency_reasons=["Evidence sufficiently covers the question."],
        confidence=0.85,
        final_report="AI is changing software engineering workflows.",
    )

    assert result is not None
    assert result.id == created.id
    assert result.status == "completed"
    assert result.research_plan is not None
    assert result.evidence is not None
    assert result.evidence[0]["evidence_id"] == "E1"
    assert result.findings is not None
    assert result.findings[0]["evidence_ids"] == ["E1"]
    assert result.citations is not None
    assert result.citations[0]["citation_id"] == 1
    assert result.finding_citations == [[1]]
    assert result.sufficiency_score == 0.9
    assert result.confidence == 0.85
    assert result.final_report == (
        "AI is changing software engineering workflows."
    )

    await repository.delete(created.id)