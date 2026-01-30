"""
Structured logging configuration for WaqediAI services.

Provides JSON-formatted logs with correlation IDs and
standard fields for observability.
"""

import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

import json

# Context variable for request-scoped fields
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})


def set_log_context(**kwargs: Any) -> None:
    """Set request-scoped log context fields."""
    current = _log_context.get().copy()
    current.update(kwargs)
    _log_context.set(current)


def clear_log_context() -> None:
    """Clear request-scoped log context."""
    _log_context.set({})


class JsonFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging.

    Produces logs in the format:
    {
        "timestamp": "2026-01-08T23:40:00Z",
        "level": "INFO",
        "service": "query-orchestrator",
        "message": "Query processed",
        ...context fields
    }
    """

    def __init__(self, service_name: str) -> None:
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context fields
        log_data.update(_log_context.get())

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "taskName",
                "message",
            ):
                log_data[key] = value

        return json.dumps(log_data, default=str)


def configure_logging(
    service_name: str,
    level: str = "INFO",
    format_type: str = "json",
) -> None:
    """
    Configure logging for a service.

    Args:
        service_name: Name of the service for log tagging.
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_type: 'json' for structured logs, 'text' for human-readable.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add new handler
    handler = logging.StreamHandler(sys.stdout)

    if format_type == "json":
        handler.setFormatter(JsonFormatter(service_name))
    else:
        handler.setFormatter(
            logging.Formatter(
                f"%(asctime)s | {service_name} | %(levelname)s | %(name)s | %(message)s"
            )
        )

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
