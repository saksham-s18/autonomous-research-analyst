"""Utilities for formatting final research reports."""

from app.graph.state import Citation


def format_report_with_citations(
    report: str,
    citations: list[Citation],
) -> str:
    """Append a deterministic sources section to a research report."""

    if not citations:
        return report

    sources = "\n\nSources:\n" + "\n".join(
        f"[{citation['citation_id']}] {citation['url']}"
        for citation in citations
    )

    return report + sources