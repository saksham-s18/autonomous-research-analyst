import pytest

from app.tools.evidence_ranking import (
    calculate_evidence_score,
    rank_evidence,
)


def test_calculate_evidence_score() -> None:
    score = calculate_evidence_score(
        relevance=0.90,
        confidence=0.80,
        source_quality=0.70,
    )

    expected = (
        0.40 * 0.90
        + 0.35 * 0.80
        + 0.25 * 0.70
    )

    assert score == pytest.approx(expected)


def test_perfect_evidence_gets_score_one() -> None:
    score = calculate_evidence_score(
        relevance=1.0,
        confidence=1.0,
        source_quality=1.0,
    )

    assert score == pytest.approx(1.0)


def test_zero_evidence_gets_score_zero() -> None:
    score = calculate_evidence_score(
        relevance=0.0,
        confidence=0.0,
        source_quality=0.0,
    )

    assert score == pytest.approx(0.0)


def test_rank_evidence_orders_highest_score_first() -> None:
    evidence = [
        {
            "subquestion": "Question",
            "claim": "Weak claim",
            "supporting_text": "Weak evidence",
            "source_url": "https://example.com/weak",
            "relevance": 0.60,
            "confidence": 0.60,
            "evidence_score": 0.60,
        },
        {
            "subquestion": "Question",
            "claim": "Strong claim",
            "supporting_text": "Strong evidence",
            "source_url": "https://example.com/strong",
            "relevance": 0.95,
            "confidence": 0.90,
            "evidence_score": 0.92,
        },
        {
            "subquestion": "Question",
            "claim": "Medium claim",
            "supporting_text": "Medium evidence",
            "source_url": "https://example.com/medium",
            "relevance": 0.80,
            "confidence": 0.75,
            "evidence_score": 0.78,
        },
    ]

    ranked = rank_evidence(evidence)

    assert ranked[0]["claim"] == "Strong claim"
    assert ranked[1]["claim"] == "Medium claim"
    assert ranked[2]["claim"] == "Weak claim"


def test_rank_evidence_does_not_modify_original_list() -> None:
    evidence = [
        {
            "subquestion": "Question",
            "claim": "First",
            "supporting_text": "Evidence",
            "source_url": "https://example.com/first",
            "relevance": 0.90,
            "confidence": 0.90,
            "evidence_score": 0.90,
        },
        {
            "subquestion": "Question",
            "claim": "Second",
            "supporting_text": "Evidence",
            "source_url": "https://example.com/second",
            "relevance": 0.50,
            "confidence": 0.50,
            "evidence_score": 0.50,
        },
    ]

    original = list(evidence)

    rank_evidence(evidence)

    assert evidence == original