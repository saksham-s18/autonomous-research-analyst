from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.repositories.research_session import ResearchSessionRepository
from app.services.research import ResearchService


async def run_research_in_background(
    research_id: UUID,
) -> None:
    """Run research with a background-task-owned database session."""

    async with AsyncSessionLocal() as session:
        repository = ResearchSessionRepository(session)
        service = ResearchService(repository)

        await service.run_research(research_id)
