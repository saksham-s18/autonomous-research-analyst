from app.tools.citations import build_citations


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