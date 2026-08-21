"""Shared state for the research workflow."""

from typing import TypedDict
from uuid import UUID


class ResearchState(TypedDict):
    """State shared across the autonomous research workflow."""

    research_id: UUID
    question: str
    status: str

    research_plan: list[str]

    current_subquestion: str | None
    completed_subquestions: list[str]

    evidence: list[dict[str, object]]
    sources: list[dict[str, object]]
    conflicts: list[dict[str, object]]

    research_iterations: int
    max_research_iterations: int

    draft_report: str | None
    final_report: str | None

    confidence: float | None

    error: str | None