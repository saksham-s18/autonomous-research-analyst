"""Citation utilities for research reports."""

from typing import TypedDict


class Citation(TypedDict):
    """A citation associated with a research source."""

    citation_id: int
    url: str

class FindingCitation(TypedDict):
    """Citation IDs associated with a synthesized finding."""

    evidence_id: str
    citation_ids: list[int]

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


def map_findings_to_citations(
    findings: list[dict],
    evidence: list[dict],
    citations: list[Citation],
) -> list[list[int]]:
    """Map each finding to its deterministic citation IDs."""

    evidence_by_id = {
        item["evidence_id"]: item
        for item in evidence
    }

    citation_by_url = {
        citation["url"]: citation["citation_id"]
        for citation in citations
    }

    finding_citations: list[list[int]] = []

    for finding in findings:
        citation_ids: list[int] = []

        for evidence_id in finding["evidence_ids"]:
            evidence_item = evidence_by_id[evidence_id]
            citation_id = citation_by_url[evidence_item["source_url"]]

            if citation_id not in citation_ids:
                citation_ids.append(citation_id)

        finding_citations.append(citation_ids)

    return finding_citations