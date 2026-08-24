"""Source quality assessment utilities."""

from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class SourceQuality:
    """Quality assessment for a research source."""

    score: float
    category: str
    reasons: tuple[str, ...]


def assess_source_quality(url: str) -> SourceQuality:
    """Assess source quality using conservative URL-based signals."""

    hostname = (urlsplit(url).hostname or "").lower()

    if not hostname:
        return SourceQuality(
            score=0.0,
            category="unknown",
            reasons=("URL does not contain a valid hostname.",),
        )

    if _is_social_media(hostname):
        return SourceQuality(
            score=0.20,
            category="social_media",
            reasons=("Social media source.",),
        )

    if _is_government(hostname):
        return SourceQuality(
            score=0.95,
            category="government",
            reasons=("Government domain.",),
        )

    if _is_academic(hostname):
        return SourceQuality(
            score=0.90,
            category="academic",
            reasons=("Academic domain.",),
        )

    if _is_research_institution(hostname):
        return SourceQuality(
            score=0.85,
            category="research_institution",
            reasons=("Research or institutional domain.",),
        )

    if _is_official_organization(hostname):
        return SourceQuality(
            score=0.75,
            category="official_organization",
            reasons=("Organization or institutional website.",),
        )

    return SourceQuality(
        score=0.50,
        category="general_web",
        reasons=("General web source.",),
    )


def _is_government(hostname: str) -> bool:
    """Return whether a hostname appears to be governmental."""

    return hostname.endswith((".gov", ".gov.in")) or ".gov." in hostname


def _is_academic(hostname: str) -> bool:
    """Return whether a hostname appears to be academic."""

    return hostname.endswith((".edu", ".ac")) or ".edu." in hostname or ".ac." in hostname


def _is_research_institution(hostname: str) -> bool:
    """Return whether a hostname appears to belong to a research institution."""

    research_terms = (
        "research",
        "institute",
        "university",
        "foundation",
        "laboratory",
        "lab",
    )

    return any(term in hostname for term in research_terms)


def _is_official_organization(hostname: str) -> bool:
    """Return whether a hostname appears to belong to an organization."""

    return hostname.endswith(".org") or ".org." in hostname


def _is_social_media(hostname: str) -> bool:
    """Return whether a hostname belongs to a social platform."""

    social_domains = {
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "reddit.com",
        "tiktok.com",
        "x.com",
        "twitter.com",
        "youtube.com",
    }

    return hostname in social_domains or any(hostname.endswith(f".{domain}") for domain in social_domains)