"""Utilities for scoring and ranking research evidence."""

from app.graph.state import Evidence

RELEVANCE_WEIGHT = 0.40
CONFIDENCE_WEIGHT = 0.35
SOURCE_QUALITY_WEIGHT = 0.25


def calculate_evidence_score(
    relevance: float,
    confidence: float,
    source_quality: float,
) -> float:
    """Calculate a normalized evidence quality score."""

    score = (
        RELEVANCE_WEIGHT * relevance
        + CONFIDENCE_WEIGHT * confidence
        + SOURCE_QUALITY_WEIGHT * source_quality
    )

    return round(score, 4)


def rank_evidence(
    evidence: list[Evidence],
) -> list[Evidence]:
    """Return evidence ordered from strongest to weakest."""

    return sorted(
        evidence,
        key=lambda item: item["evidence_score"],
        reverse=True,
    )