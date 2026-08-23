"""Utilities for normalizing and deduplicating source URLs."""

from urllib.parse import urlsplit, urlunsplit

from app.tools.search import SearchResult


def normalize_url(url: str) -> str:
    """Normalize a URL for safe deduplication.

    The normalization is intentionally conservative:
    - lowercase the scheme and hostname
    - remove URL fragments
    - remove a trailing slash from non-root paths
    - preserve query parameters
    - preserve meaningful URL structure
    """

    parsed = urlsplit(url)

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower() if parsed.hostname else ""

    if parsed.port is not None:
        hostname = f"{hostname}:{parsed.port}"

    path = parsed.path

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return urlunsplit(
        (
            scheme,
            hostname,
            path,
            parsed.query,
            "",
        )
    )


def deduplicate_search_results(
    results: list[SearchResult],
) -> list[SearchResult]:
    """Remove duplicate search results using normalized URLs."""

    seen_urls: set[str] = set()
    unique_results: list[SearchResult] = []

    for result in results:
        normalized_url = normalize_url(result["url"])

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)

        unique_results.append(
            {
                **result,
                "url": normalized_url,
            }
        )

    return unique_results