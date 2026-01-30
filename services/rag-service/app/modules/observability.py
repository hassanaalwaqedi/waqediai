"""
Observability and audit logging module.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.config import get_settings
from app.models import (
    ContextWindow,
    EnrichedQuery,
    RAGQuery,
    RAGResponse,
    ReasoningTrace,
)


class TenantFormatter(logging.Formatter):
    """JSON formatter with tenant context."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "rag-service",
        }
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = str(record.tenant_id)
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def configure_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level.upper()))
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(TenantFormatter())
    root.addHandler(handler)


class AuditLogger:
    """
    Audit logging for RAG operations.
    """

    def __init__(self):
        self.logger = logging.getLogger("audit.rag")
        self._traces: dict[UUID, list[ReasoningTrace]] = {}

    def log_query(self, query: RAGQuery, enriched: EnrichedQuery) -> str:
        """Log query processing."""
        trace_id = f"trace_{uuid4().hex[:12]}"

        self.logger.info(
            "Query processed",
            extra={
                "tenant_id": query.tenant_id,
                "extra": {
                    "event": "rag.query",
                    "trace_id": trace_id,
                    "language": enriched.language,
                    "intent": enriched.intent.value,
                    "keywords": enriched.keywords,
                },
            },
        )
        return trace_id

    def log_retrieval(
        self,
        trace_id: str,
        tenant_id: UUID,
        context: ContextWindow,
    ) -> None:
        """Log retrieval results."""
        self.logger.info(
            "Retrieval completed",
            extra={
                "tenant_id": tenant_id,
                "extra": {
                    "event": "rag.retrieval",
                    "trace_id": trace_id,
                    "chunks": len(context.chunks),
                    "tokens": context.total_tokens,
                    "documents": len(context.document_ids),
                },
            },
        )

    def log_generation(
        self,
        trace_id: str,
        tenant_id: UUID,
        response: RAGResponse,
        latency_ms: int,
    ) -> None:
        """Log generation results."""
        self.logger.info(
            "Answer generated",
            extra={
                "tenant_id": tenant_id,
                "extra": {
                    "event": "rag.generation",
                    "trace_id": trace_id,
                    "citations": len(response.citations),
                    "confidence": response.confidence,
                    "answer_type": response.answer_type.value,
                    "latency_ms": latency_ms,
                },
            },
        )

    def create_trace(
        self,
        trace_id: str,
        tenant_id: UUID,
        query: str,
        context: ContextWindow,
        response: RAGResponse,
        latency_ms: int,
    ) -> ReasoningTrace:
        """Create full reasoning trace for audit."""
        trace = ReasoningTrace(
            trace_id=trace_id,
            tenant_id=tenant_id,
            query=query,
            retrieved_chunks=[c.chunk_id for c in context.chunks],
            context_tokens=context.total_tokens,
            prompt_tokens=context.total_tokens + len(query) // 4,
            answer=response.answer,
            citations=[c.chunk_id for c in response.citations],
            latency_ms=latency_ms,
            timestamp=datetime.now(UTC),
        )

        # Store trace
        if tenant_id not in self._traces:
            self._traces[tenant_id] = []
        self._traces[tenant_id].append(trace)

        # Keep only last 100 traces per tenant
        if len(self._traces[tenant_id]) > 100:
            self._traces[tenant_id] = self._traces[tenant_id][-100:]

        return trace


def get_audit_logger() -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger()
