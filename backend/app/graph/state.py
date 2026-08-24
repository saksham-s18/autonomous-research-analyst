"""Shared state for the research workflow."""

from typing import TypedDict
from uuid import UUID


class ResearchPlan(TypedDict):
    """Structured research plan generated from a research question."""

    goal: str
    subquestions: list[str]


class Source(TypedDict):
    """A source discovered during research."""

    title: str
    url: str
    publisher: str | None
    published_at: str | None
    quality_score: float
    quality_category: str
    quality_reasons: list[str]


class Evidence(TypedDict):
    """Evidence extracted from a research source."""

    subquestion: str
    claim: str
    supporting_text: str
    source_url: str
    relevance: float
    confidence: float
    evidence_score: float


class Conflict(TypedDict):
    """A disagreement between pieces of research evidence."""

    topic: str
    claims: list[str]
    explanation: str
    conflict_type: str
    severity: float
    confidence: float


class SourceFailure(TypedDict):
    """A failure encountered while processing a research source."""

    url: str
    stage: str
    error_type: str
    error_message: str
    retryable: bool


class ResearchState(TypedDict):
    """State shared across the autonomous research workflow."""

    research_id: UUID
    question: str
    status: str

    research_plan: ResearchPlan

    current_subquestion: str | None
    completed_subquestions: list[str]

    evidence: list[Evidence]
    sources: list[Source]
    source_failures: list[SourceFailure]
    conflicts: list[Conflict]

    draft_report: str | None
    final_report: str | None

    confidence: float | None

    sufficiency_score: float | None
    sufficiency_reasons: list[str]

    error: str | None