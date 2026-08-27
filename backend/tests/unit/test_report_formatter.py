from app.tools.report_formatter import format_report_with_citations


def test_format_report_with_citations() -> None:
    report = "AI automation affects employment."

    citations = [
        {
            "citation_id": 1,
            "url": "https://example.com/source",
        },
        {
            "citation_id": 2,
            "url": "https://example.com/source2",
        },
    ]

    result = format_report_with_citations(
        report,
        citations,
    )

    assert result == (
        "AI automation affects employment."
        "\n\nSources:\n"
        "[1] https://example.com/source\n"
        "[2] https://example.com/source2"
    )


def test_format_report_without_citations() -> None:
    report = "AI automation affects employment."

    assert format_report_with_citations(report, []) == report