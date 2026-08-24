"""Research sufficiency evaluation utilities."""

from dataclasses import dataclass

from app.graph.state import Evidence, SourceFailure


@dataclass(frozen=True)
class SufficiencyResult:
    """Result of evaluating research sufficiency."""

    sufficient: bool
    score: float
    reasons: tuple[str, ...]


def evaluate_research_sufficiency(
    evidence: list[Evidence],
    source_failures: list[SourceFailure],
    expected_subquestions: int,
    conflicts: int,
) -> SufficiencyResult:
    """Determine whether collected research is sufficient."""

    if expected_subquestions <= 0:
        return SufficiencyResult(
            sufficient=False,
            score=0.0,
            reasons=("No research subquestions are defined.",),
        )

    if not evidence:
        return SufficiencyResult(
            sufficient=False,
            score=0.0,
            reasons=("No evidence was collected.",),
        )

    evidence_count_score = min(
        len(evidence) / expected_subquestions,
        1.0,
    )

    average_evidence_score = sum(
        item["evidence_score"]
        for item in evidence
    ) / len(evidence)

    failed_source_count = len(source_failures)

    failure_penalty = min(
        failed_source_count * 0.05,
        0.25,
    )

    conflict_penalty = min(
        conflicts * 0.05,
        0.25,
    )

    score = (
        0.35 * evidence_count_score
        + 0.45 * average_evidence_score
        + 0.20
    )

    score -= failure_penalty
    score -= conflict_penalty

    score = max(0.0, min(score, 1.0))

    reasons = []

    if evidence_count_score < 1.0:
        reasons.append("Evidence coverage is incomplete.")

    if average_evidence_score < 0.70:
        reasons.append("Average evidence quality is below the target.")

    if failed_source_count > 0:
        reasons.append(
            f"{failed_source_count} source failure(s) were recorded."
        )

    if conflicts > 0:
        reasons.append(
            f"{conflicts} evidence conflict(s) require consideration."
        )

    if not reasons:
        reasons.append("Evidence meets the sufficiency criteria.")

    return SufficiencyResult(
        sufficient=score >= 0.70,
        score=round(score, 4),
        reasons=tuple(reasons),
    )