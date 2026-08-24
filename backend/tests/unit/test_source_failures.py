import httpx

from app.tools.source_failures import classify_source_failure


def test_403_is_not_retryable() -> None:
    request = httpx.Request(
        "GET",
        "https://example.com/protected",
    )
    response = httpx.Response(
        403,
        request=request,
    )
    error = httpx.HTTPStatusError(
        "Forbidden",
        request=request,
        response=response,
    )

    error_type, message, retryable = classify_source_failure(
        "fetch",
        error,
    )

    assert error_type == "http_403"
    assert message == "Source returned HTTP 403 Forbidden."
    assert retryable is False


def test_404_is_not_retryable() -> None:
    request = httpx.Request(
        "GET",
        "https://example.com/missing",
    )
    response = httpx.Response(
        404,
        request=request,
    )
    error = httpx.HTTPStatusError(
        "Not found",
        request=request,
        response=response,
    )

    error_type, _message, retryable = classify_source_failure(
        "fetch",
        error,
    )

    assert error_type == "http_404"
    assert retryable is False


def test_server_error_is_retryable() -> None:
    request = httpx.Request(
        "GET",
        "https://example.com/server",
    )
    response = httpx.Response(
        503,
        request=request,
    )
    error = httpx.HTTPStatusError(
        "Service unavailable",
        request=request,
        response=response,
    )

    error_type, _message, retryable = classify_source_failure(
        "fetch",
        error,
    )

    assert error_type == "http_server_error"
    assert retryable is True


def test_timeout_is_retryable() -> None:
    error = httpx.ReadTimeout(
        "Request timed out.",
    )

    error_type, _message, retryable = classify_source_failure(
        "fetch",
        error,
    )

    assert error_type == "timeout"
    assert retryable is True


def test_request_error_is_retryable() -> None:
    error = httpx.RequestError(
        "Connection failed.",
    )

    error_type, _message, retryable = classify_source_failure(
        "fetch",
        error,
    )

    assert error_type == "request_error"
    assert retryable is True


def test_runtime_error_is_extraction_failure() -> None:
    error = RuntimeError("LLM extraction failed.")

    error_type, _message, retryable = classify_source_failure(
        "extract",
        error,
    )

    assert error_type == "extraction_error"
    assert retryable is True


def test_unknown_error_is_not_retryable() -> None:
    error = ValueError("Unexpected problem.")

    error_type, _message, retryable = classify_source_failure(
        "fetch",
        error,
    )

    assert error_type == "unknown_error"
    assert retryable is False