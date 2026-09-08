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

    async def save_result(
        self,
        research_id: UUID,
        *,
        status: str,
        research_plan: dict | None,
        sources: list | None,
        evidence: list | None,
        findings: list | None,
        citations: list | None,
        finding_citations: list | None,
        conflicts: list | None,
        sufficiency_score: float | None,
        sufficiency_reasons: list | None,
        confidence: float | None,
        final_report: str | None,
    ) -> ResearchSession | None:
        """Persist the result of a research workflow."""

        research_session = await self.get_by_id(research_id)

        if research_session is None:
            return None

        research_session.status = status
        research_session.research_plan = research_plan
        research_session.sources = sources
        research_session.evidence = evidence
        research_session.findings = findings
        research_session.citations = citations
        research_session.finding_citations = finding_citations
        research_session.conflicts = conflicts
        research_session.sufficiency_score = sufficiency_score
        research_session.sufficiency_reasons = sufficiency_reasons
        research_session.confidence = confidence
        research_session.final_report = final_report

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