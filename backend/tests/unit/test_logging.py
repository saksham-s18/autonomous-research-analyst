import json
import logging
from app.core.logging import JsonFormatter


def test_json_formatter_basic_fields() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["message"] == "test message"
    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert "timestamp" in data


def test_json_formatter_extra_fields() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="research event",
        args=(),
        exc_info=None,
    )
    record.research_id = "test-uuid-1234"
    record.status = "planning"
    record.duration_ms = 42.5

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["message"] == "research event"
    assert data["research_id"] == "test-uuid-1234"
    assert data["status"] == "planning"
    assert data["duration_ms"] == 42.5


def test_json_formatter_exception_handling() -> None:
    formatter = JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=10,
        msg="error occurred",
        args=(),
        exc_info=exc_info,
    )

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["message"] == "error occurred"
    assert "exception" in data
    assert "ValueError: boom" in data["exception"]
