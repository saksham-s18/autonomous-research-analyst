"""Utilities for formatting final research reports."""

from app.graph.state import Citation


def format_report_with_citations(
    report: str,
    citations: list[Citation],
    finding_citations: list[list[int]] | None = None,
    findings: list[str] | None = None,
) -> str:
    """Format a research report with claim-level citations."""

    formatted_report = report

    if findings:
        formatted_report += "\n\nKey Findings:\n"

        for index, finding in enumerate(findings):
            citation_ids = (
                finding_citations[index]
                if finding_citations and index < len(finding_citations)
                else []
            )

            citation_text = ""

            if citation_ids:
                citation_text = " " + " ".join(
                    f"[{citation_id}]"
                    for citation_id in citation_ids
                )

            formatted_report += (
                f"{index + 1}. {finding}{citation_text}\n"
            )

        formatted_report = formatted_report.rstrip()

    elif finding_citations:
        lines = formatted_report.splitlines()

        for index, citation_ids in enumerate(finding_citations):
            if index >= len(lines):
                break

            if not citation_ids:
                continue

            citation_text = " ".join(
                f"[{citation_id}]"
                for citation_id in citation_ids
            )

            lines[index] = f"{lines[index]} {citation_text}"

        formatted_report = "\n".join(lines)

    if not citations:
        return formatted_report

    sources = "\n\nSources:\n" + "\n".join(
        f"[{citation['citation_id']}] {citation['url']}"
        for citation in citations
    )

    return formatted_report + sources