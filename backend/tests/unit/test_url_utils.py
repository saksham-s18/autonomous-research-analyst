from app.tools.url_utils import (
    deduplicate_search_results,
    normalize_url,
)


def test_normalize_url_removes_fragment() -> None:
    url = "https://example.com/article#section-2"

    assert normalize_url(url) == "https://example.com/article"


def test_normalize_url_removes_trailing_slash() -> None:
    url = "https://example.com/article/"

    assert normalize_url(url) == "https://example.com/article"


def test_normalize_url_preserves_root_slash() -> None:
    url = "https://example.com/"

    assert normalize_url(url) == "https://example.com/"


def test_normalize_url_lowercases_scheme_and_hostname() -> None:
    url = "HTTPS://EXAMPLE.COM/article"

    assert normalize_url(url) == "https://example.com/article"


def test_normalize_url_preserves_query_parameters() -> None:
    url = "https://example.com/article?page=2"

    assert normalize_url(url) == "https://example.com/article?page=2"


def test_deduplicate_search_results_removes_duplicate_urls() -> None:
    results = [
        {
            "title": "First result",
            "url": "https://example.com/article",
            "snippet": "First",
        },
        {
            "title": "Duplicate result",
            "url": "https://example.com/article#section",
            "snippet": "Duplicate",
        },
    ]

    unique_results = deduplicate_search_results(results)

    assert len(unique_results) == 1
    assert unique_results[0]["title"] == "First result"
    assert unique_results[0]["url"] == "https://example.com/article"


def test_deduplicate_search_results_keeps_different_urls() -> None:
    results = [
        {
            "title": "Article one",
            "url": "https://example.com/article-one",
            "snippet": "First",
        },
        {
            "title": "Article two",
            "url": "https://example.com/article-two",
            "snippet": "Second",
        },
    ]

    unique_results = deduplicate_search_results(results)

    assert len(unique_results) == 2


def test_deduplicate_search_results_keeps_different_query_parameters() -> None:
    results = [
        {
            "title": "Page one",
            "url": "https://example.com/article?page=1",
            "snippet": "First",
        },
        {
            "title": "Page two",
            "url": "https://example.com/article?page=2",
            "snippet": "Second",
        },
    ]

    unique_results = deduplicate_search_results(results)

    assert len(unique_results) == 2


def test_deduplication_uses_normalized_url() -> None:
    results = [
        {
            "title": "First",
            "url": "HTTPS://EXAMPLE.COM/report/",
            "snippet": "First",
        },
        {
            "title": "Second",
            "url": "https://example.com/report#summary",
            "snippet": "Second",
        },
    ]

    unique_results = deduplicate_search_results(results)

    assert len(unique_results) == 1
    assert unique_results[0]["url"] == "https://example.com/report"