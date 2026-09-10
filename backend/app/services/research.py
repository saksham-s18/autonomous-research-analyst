from uuid import UUID

from app.graph.state import create_initial_research_state
from app.models.research_session import ResearchSession
from app.repositories.research_session import ResearchSessionRepository

class ResearchService:
    """Application logic for research sessions."""

    def __init__(
        self,
        repository: ResearchSessionRepository,
    ) -> None:
        self.repository = repository


    def _build_research_graph(self):
        """Build the research workflow."""

        from app.graph.workflow import build_research_graph

        return build_research_graph()


    async def create_research_session(
        self,
        question: str,
    ) -> ResearchSession:
        """Create a new research session."""

        return await self.repository.create(question)


    async def run_research(
        self,
        question: str,
    ) -> ResearchSession | None:
        """Run a research workflow and persist its result."""

        research_session = await self.create_research_session(question)

        initial_state = create_initial_research_state(
            research_session.id,
            question,
        )

        graph = self._build_research_graph()

        result = None

        async for state in graph.astream(
            initial_state,
            stream_mode="values",
        ):
            result = state

            await self.save_research_checkpoint(
                research_session.id,
                dict(state),
            )

        if result is None:
            return None

        return await self.save_research_result(
            research_session.id,
            status=result["status"],
            research_plan=result["research_plan"],
            sources=result["sources"],
            evidence=result["evidence"],
            findings=result.get("findings"),
            citations=result["citations"],
            finding_citations=result.get("finding_citations"),
            conflicts=result["conflicts"],
            sufficiency_score=result["sufficiency_score"],
            sufficiency_reasons=result["sufficiency_reasons"],
            confidence=result["confidence"],
            final_report=result["final_report"],
        )


    async def resume_research(
        self,
        research_id: UUID,
    ) -> ResearchSession | None:
        """Resume a research workflow from its latest persisted checkpoint."""

        research_session = await self.get_research_session(research_id)

        if research_session is None:
            return None

        checkpoint = await self.get_research_checkpoint(research_id)

        if checkpoint is None:
            return research_session

        graph = self._build_research_graph()

        result = None

        async for state in graph.astream(
            checkpoint,
            stream_mode="values",
        ):
            result = state

            await self.save_research_checkpoint(
                research_id,
                dict(state),
            )

        if result is None:
            return research_session

        return await self.save_research_result(
            research_id,
            status=result["status"],
            research_plan=result["research_plan"],
            sources=result["sources"],
            evidence=result["evidence"],
            findings=result.get("findings"),
            citations=result["citations"],
            finding_citations=result.get("finding_citations"),
            conflicts=result["conflicts"],
            sufficiency_score=result["sufficiency_score"],
            sufficiency_reasons=result["sufficiency_reasons"],
            confidence=result["confidence"],
            final_report=result["final_report"],
        )

    async def save_research_result(
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

        return await self.repository.save_result(
            research_id,
            status=status,
            research_plan=research_plan,
            sources=sources,
            evidence=evidence,
            findings=findings,
            citations=citations,
            finding_citations=finding_citations,
            conflicts=conflicts,
            sufficiency_score=sufficiency_score,
            sufficiency_reasons=sufficiency_reasons,
            confidence=confidence,
            final_report=final_report,
        )


    async def save_research_checkpoint(
        self,
        research_id: UUID,
        workflow_state: dict,
    ) -> ResearchSession | None:
        """Persist the current workflow state for a research session."""

        return await self.repository.save_checkpoint(
            research_id,
            workflow_state,
        )

    async def get_research_checkpoint(
        self,
        research_id: UUID,
    ) -> dict | None:
        """Retrieve the persisted workflow state for a research session."""

        return await self.repository.get_checkpoint(research_id)

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
        