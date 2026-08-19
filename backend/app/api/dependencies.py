from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.research_session import ResearchSessionRepository
from app.services.research import ResearchService


async def get_research_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> ResearchService:
    """Provide a research service for the current request."""

    repository = ResearchSessionRepository(session)

    return ResearchService(repository)