from app.tools.citations import (
    build_citations,
    map_findings_to_citations,
)

def test_build_citations_deduplicates_source_urls() -> None:
    evidence = [
        {
            "source_url": "https://example.com/a",
        },
        {
            "source_url": "https://example.com/a",
        },
        {
            "source_url": "https://example.com/b",
        },
    ]

    citations = build_citations(evidence)

    assert citations == [
        {
            "citation_id": 1,
            "url": "https://example.com/a",
        },
        {
            "citation_id": 2,
            "url": "https://example.com/b",
        },
    ]


def test_build_citations_returns_empty_for_no_evidence() -> None:
    assert build_citations([]) == []


def test_map_findings_to_citations() -> None:
    evidence = [
        {
            "evidence_id": "E1",
            "source_url": "https://example.com/source-a",
        },
        {
            "evidence_id": "E2",
            "source_url": "https://example.com/source-b",
        },
        {
            "evidence_id": "E3",
            "source_url": "https://example.com/source-a",
        },
    ]

    findings = [
        {
            "claim": "Finding one",
            "evidence_ids": ["E1", "E2"],
        },
        {
            "claim": "Finding two",
            "evidence_ids": ["E3"],
        },
    ]

    citations = build_citations(evidence)

    result = map_findings_to_citations(
        findings,
        evidence,
        citations,
    )

    assert result == [
        [1, 2],
        [1],
    ]