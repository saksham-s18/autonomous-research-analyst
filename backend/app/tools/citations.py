"""Citation utilities for research reports."""

from typing import TypedDict


class Citation(TypedDict):
    """A citation associated with a research source."""

    citation_id: int
    url: str


def build_citations(evidence: list[dict]) -> list[Citation]:
    """Build deterministic citations from evidence source URLs."""

    citations: list[Citation] = []
    seen_urls: set[str] = set()

    for item in evidence:
        url = item["source_url"]

        if url in seen_urls:
            continue

        seen_urls.add(url)

        citations.append(
            {
                "citation_id": len(citations) + 1,
                "url": url,
            }
        )

    return citations