from app.tools.research_sufficiency import (
    evaluate_research_sufficiency,
)


def make_evidence(score: float) -> dict:
    """Create deterministic evidence."""

    return {
        "subquestion": "Question",
        "claim": "Claim",
        "supporting_text": "Supporting text",
        "source_url": "https://example.com",
        "relevance": score,
        "confidence": score,
        "evidence_score": score,
    }


def test_strong_complete_research_is_sufficient() -> None:
    result = evaluate_research_sufficiency(
        evidence=[
            make_evidence(0.90),
            make_evidence(0.90),
            make_evidence(0.90),
        ],
        source_failures=[],
        expected_subquestions=3,
        conflicts=0,
    )

    assert result.sufficient is True
    assert result.score >= 0.70
    assert result.reasons == (
        "Evidence meets the sufficiency criteria.",
    )


def test_no_evidence_is_insufficient() -> None:
    result = evaluate_research_sufficiency(
        evidence=[],
        source_failures=[],
        expected_subquestions=3,
        conflicts=0,
    )

    assert result.sufficient is False
    assert result.score == 0.0
    assert result.reasons == (
        "No evidence was collected.",
    )


def test_low_quality_evidence_is_insufficient() -> None:
    result = evaluate_research_sufficiency(
        evidence=[
            make_evidence(0.30),
            make_evidence(0.30),
            make_evidence(0.30),
        ],
        source_failures=[],
        expected_subquestions=3,
        conflicts=0,
    )

    assert result.sufficient is False
    assert "Average evidence quality is below the target." in result.reasons


def test_source_failures_reduce_score() -> None:
    failures = [
        {
            "url": "https://example.com/a",
            "stage": "fetch",
            "error_type": "http_403",
            "error_message": "Source returned HTTP 403 Forbidden.",
            "retryable": False,
        },
        {
            "url": "https://example.com/b",
            "stage": "fetch",
            "error_type": "timeout",
            "error_message": "Source request timed out.",
            "retryable": True,
        },
    ]

    result = evaluate_research_sufficiency(
        evidence=[
            make_evidence(0.90),
            make_evidence(0.90),
            make_evidence(0.90),
        ],
        source_failures=failures,
        expected_subquestions=3,
        conflicts=0,
    )

    assert result.score < 0.95
    assert "2 source failure(s) were recorded." in result.reasons


def test_conflicts_reduce_score() -> None:
    result = evaluate_research_sufficiency(
        evidence=[
            make_evidence(0.90),
            make_evidence(0.90),
            make_evidence(0.90),
        ],
        source_failures=[],
        expected_subquestions=3,
        conflicts=2,
    )

    assert result.score < 0.95
    assert "2 evidence conflict(s) require consideration." in result.reasons


def test_invalid_subquestion_count_is_insufficient() -> None:
    result = evaluate_research_sufficiency(
        evidence=[make_evidence(0.90)],
        source_failures=[],
        expected_subquestions=0,
        conflicts=0,
    )

    assert result.sufficient is False
    assert result.score == 0.0