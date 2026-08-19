from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.research_session import ResearchSession


class ResearchSessionRepository:
    """Database operations for research sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        question: str,
    ) -> ResearchSession:
        """Create and persist a new research session."""

        research_session = ResearchSession(
            question=question,
        )

        self.session.add(research_session)
        await self.session.commit()
        await self.session.refresh(research_session)

        return research_session

    async def get_by_id(
        self,
        research_id: UUID,
    ) -> ResearchSession | None:
        """Return a research session by ID."""

        result = await self.session.execute(
            select(ResearchSession).where(
                ResearchSession.id == research_id,
            )
        )

        return result.scalar_one_or_none()

    async def list(
        self,
    ) -> list[ResearchSession]:
        """Return all research sessions."""

        result = await self.session.execute(
            select(ResearchSession).order_by(
                ResearchSession.created_at.desc(),
            )
        )

        return list(result.scalars().all())

    async def delete(
        self,
        research_id: UUID,
    ) -> bool:
        """Delete a research session and return whether it existed."""

        result = await self.session.execute(
            delete(ResearchSession).where(
                ResearchSession.id == research_id,
            )
        )

        await self.session.commit()

        return result.rowcount > 0