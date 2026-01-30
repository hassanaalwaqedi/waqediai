"""
Document events for async processing.
"""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ingestion_service.domain.models import FileCategory


@dataclass
class DocumentEvent:
    """Base class for document events."""

    event_id: str
    event_type: str
    timestamp: str
    tenant_id: str
    correlation_id: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_event(
    event_type: str,
    tenant_id: str,
    correlation_id: str,
    payload: dict[str, Any],
) -> DocumentEvent:
    """Create a new document event."""
    return DocumentEvent(
        event_id=f"evt_{uuid4().hex[:24]}",
        event_type=event_type,
        timestamp=datetime.now(UTC).isoformat(),
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload=payload,
    )


def document_uploaded_event(
    document_id: str,
    tenant_id: str,
    correlation_id: str,
    file_category: FileCategory,
    content_type: str,
    size_bytes: int,
) -> DocumentEvent:
    """Create document.uploaded event."""
    return create_event(
        event_type="document.uploaded",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload={
            "document_id": document_id,
            "file_category": file_category.value,
            "content_type": content_type,
            "size_bytes": size_bytes,
        },
    )


def document_validated_event(
    document_id: str,
    tenant_id: str,
    correlation_id: str,
) -> DocumentEvent:
    """Create document.validated event."""
    return create_event(
        event_type="document.validated",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload={"document_id": document_id},
    )


def document_queued_event(
    document_id: str,
    tenant_id: str,
    correlation_id: str,
    priority: int = 0,
) -> DocumentEvent:
    """Create document.queued event."""
    return create_event(
        event_type="document.queued",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload={
            "document_id": document_id,
            "priority": priority,
        },
    )


def document_processed_event(
    document_id: str,
    tenant_id: str,
    correlation_id: str,
    chunks_count: int = 0,
) -> DocumentEvent:
    """Create document.processed event."""
    return create_event(
        event_type="document.processed",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload={
            "document_id": document_id,
            "chunks_count": chunks_count,
        },
    )


def document_failed_event(
    document_id: str,
    tenant_id: str,
    correlation_id: str,
    error_code: str,
    error_message: str,
) -> DocumentEvent:
    """Create document.failed event."""
    return create_event(
        event_type="document.failed",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload={
            "document_id": document_id,
            "error_code": error_code,
            "error_message": error_message,
        },
    )


def document_deleted_event(
    document_id: str,
    tenant_id: str,
    correlation_id: str,
    deleted_by: str,
) -> DocumentEvent:
    """Create document.deleted event."""
    return create_event(
        event_type="document.deleted",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        payload={
            "document_id": document_id,
            "deleted_by": deleted_by,
        },
    )
