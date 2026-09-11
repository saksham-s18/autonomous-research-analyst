from uuid import UUID

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.research_session import ResearchSessionRepository
from app.services.research import ResearchService

logger = get_logger(__name__)


async def run_research_in_background(
    research_id: UUID,
) -> None:
    """Run research with a background-task-owned database session."""

    logger.info(
        "background_research_started",
        extra={"research_id": str(research_id)},
    )

    try:
        async with AsyncSessionLocal() as session:
            repository = ResearchSessionRepository(session)
            service = ResearchService(repository)

            await service.run_research(research_id)

        logger.info(
            "background_research_completed",
            extra={"research_id": str(research_id)},
        )
    except Exception:
        logger.exception(
            "background_research_failed",
            extra={"research_id": str(research_id)},
        )
        raise
