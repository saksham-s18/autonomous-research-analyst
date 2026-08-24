"""Utilities for classifying source processing failures."""

import httpx


def classify_source_failure(
    stage: str,
    exc: Exception,
) -> tuple[str, str, bool]:
    """Return error type, message, and retryability."""

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code

        if status_code == 403:
            return (
                "http_403",
                "Source returned HTTP 403 Forbidden.",
                False,
            )

        if status_code == 404:
            return (
                "http_404",
                "Source returned HTTP 404 Not Found.",
                False,
            )

        if status_code >= 500:
            return (
                "http_server_error",
                f"Source returned HTTP {status_code}.",
                True,
            )

        return (
            "http_error",
            f"Source returned HTTP {status_code}.",
            False,
        )

    if isinstance(exc, httpx.TimeoutException):
        return (
            "timeout",
            "Source request timed out.",
            True,
        )

    if isinstance(exc, httpx.RequestError):
        return (
            "request_error",
            "Source request failed.",
            True,
        )

    if isinstance(exc, RuntimeError):
        return (
            "extraction_error",
            "Evidence extraction failed.",
            True,
        )

    return (
        "unknown_error",
        "Source processing failed.",
        False,
    )