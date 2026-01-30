"""
Structured, tenant-aware logging.

Provides consistent logging with tenant context for audit and tracing.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from uuid import UUID

from app.config import get_settings


class TenantAwareFormatter(logging.Formatter):
    """JSON formatter with tenant context."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "reasoning-service",
        }

        # Add tenant context if available
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = str(record.tenant_id)
        if hasattr(record, "user_id"):
            log_data["user_id"] = str(record.user_id)
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging() -> None:
    """Configure structured logging for the service."""
    settings = get_settings()

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        handler.setFormatter(TenantAwareFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )
        )

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class AuditLogger:
    """Logger for audit events with tenant context."""

    def __init__(self):
        self.logger = logging.getLogger("audit.reasoning")

    def log_reasoning_request(
        self,
        tenant_id: UUID,
        query: str,
        strategy: str,
        chunk_count: int,
        user_id: UUID | None = None,
    ) -> None:
        """Log incoming reasoning request."""
        extra = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "extra_data": {
                "event": "reasoning.request",
                "strategy": strategy,
                "chunk_count": chunk_count,
                "query_length": len(query),
            },
        }
        self.logger.info("Reasoning request received", extra=extra)

    def log_reasoning_response(
        self,
        tenant_id: UUID,
        confidence: float,
        citation_count: int,
        model: str,
        duration_ms: int,
    ) -> None:
        """Log reasoning response."""
        extra = {
            "tenant_id": tenant_id,
            "extra_data": {
                "event": "reasoning.response",
                "confidence": confidence,
                "citation_count": citation_count,
                "model": model,
                "duration_ms": duration_ms,
            },
        }
        self.logger.info("Reasoning response generated", extra=extra)

    def log_llm_error(
        self,
        tenant_id: UUID,
        error: str,
        model: str,
    ) -> None:
        """Log LLM error."""
        extra = {
            "tenant_id": tenant_id,
            "extra_data": {
                "event": "reasoning.error",
                "error": error,
                "model": model,
            },
        }
        self.logger.error("LLM error occurred", extra=extra)


def get_audit_logger() -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger()
