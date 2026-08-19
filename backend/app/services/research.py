from uuid import UUID

from app.models.research_session import ResearchSession
from app.repositories.research_session import ResearchSessionRepository


class ResearchService:
    """Application logic for research sessions."""

    def __init__(
        self,
        repository: ResearchSessionRepository,
    ) -> None:
        self.repository = repository

    async def create_research_session(
        self,
        question: str,
    ) -> ResearchSession:
        """Create a new research session."""

        return await self.repository.create(question)

    async def get_research_session(
        self,
        research_id: UUID,
    ) -> ResearchSession | None:
        """Retrieve a research session by ID."""

        return await self.repository.get_by_id(research_id)

    async def list_research_sessions(self) -> list[ResearchSession]:
        """Retrieve all research sessions."""

        return await self.repository.list()

    async def delete_research_session(
        self,
        research_id: UUID,
    ) -> bool:
        """Delete a research session."""

        return await self.repository.delete(research_id)