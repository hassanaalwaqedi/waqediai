"""
Structured, tenant-aware logging for retrieval service.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from uuid import UUID

from app.config import get_settings


class TenantAwareFormatter(logging.Formatter):
    """JSON formatter with tenant context."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "retrieval-service",
        }

        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = str(record.tenant_id)
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_format == "json":
        handler.setFormatter(TenantAwareFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class AuditLogger:
    """Audit logger for retrieval operations."""

    def __init__(self):
        self.logger = logging.getLogger("audit.retrieval")

    def log_index(
        self,
        tenant_id: UUID,
        document_id: str,
        chunk_count: int,
        duration_ms: int,
    ) -> None:
        extra = {
            "tenant_id": tenant_id,
            "extra_data": {
                "event": "retrieval.index",
                "document_id": document_id,
                "chunk_count": chunk_count,
                "duration_ms": duration_ms,
            },
        }
        self.logger.info("Indexed document chunks", extra=extra)

    def log_search(
        self,
        tenant_id: UUID,
        query_length: int,
        result_count: int,
        top_score: float | None,
        duration_ms: int,
    ) -> None:
        extra = {
            "tenant_id": tenant_id,
            "extra_data": {
                "event": "retrieval.search",
                "query_length": query_length,
                "result_count": result_count,
                "top_score": top_score,
                "duration_ms": duration_ms,
            },
        }
        self.logger.info("Search completed", extra=extra)

    def log_delete(
        self,
        tenant_id: UUID,
        document_id: str,
        deleted_count: int,
    ) -> None:
        extra = {
            "tenant_id": tenant_id,
            "extra_data": {
                "event": "retrieval.delete",
                "document_id": document_id,
                "deleted_count": deleted_count,
            },
        }
        self.logger.info("Document deleted from index", extra=extra)


def get_audit_logger() -> AuditLogger:
    return AuditLogger()
