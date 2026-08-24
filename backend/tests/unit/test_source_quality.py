import pytest

from app.tools.source_quality import assess_source_quality


def test_government_source_has_high_quality() -> None:
    result = assess_source_quality(
        "https://www.gov.in/report"
    )

    assert result.category == "government"
    assert result.score == pytest.approx(0.95)
    assert "Government domain." in result.reasons


def test_academic_source_has_high_quality() -> None:
    result = assess_source_quality(
        "https://research.example.edu/paper"
    )

    assert result.category == "academic"
    assert result.score == pytest.approx(0.90)


def test_academic_country_domain_is_detected() -> None:
    result = assess_source_quality(
        "https://university.example.ac.uk/paper"
    )

    assert result.category == "academic"


def test_research_institution_is_detected() -> None:
    result = assess_source_quality(
        "https://www.research-institute.example/reports"
    )

    assert result.category == "research_institution"
    assert result.score == pytest.approx(0.85)


def test_official_organization_is_detected() -> None:
    result = assess_source_quality(
        "https://example.org/report"
    )

    assert result.category == "official_organization"
    assert result.score == pytest.approx(0.75)


def test_social_media_has_low_quality() -> None:
    result = assess_source_quality(
        "https://www.linkedin.com/posts/example"
    )

    assert result.category == "social_media"
    assert result.score == pytest.approx(0.20)


def test_general_web_source_gets_neutral_score() -> None:
    result = assess_source_quality(
        "https://example.com/article"
    )

    assert result.category == "general_web"
    assert result.score == pytest.approx(0.50)


def test_invalid_url_gets_zero_quality() -> None:
    result = assess_source_quality(
        "not-a-valid-url"
    )

    assert result.category == "unknown"
    assert result.score == pytest.approx(0.0)