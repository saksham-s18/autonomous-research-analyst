import json
import logging
import sys
from datetime import UTC, datetime

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging() -> None:
    """Configure application-wide structured logging."""

    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers if configuration is called again.
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    root_logger.setLevel(settings.log_level.upper())


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module."""
    return logging.getLogger(name)