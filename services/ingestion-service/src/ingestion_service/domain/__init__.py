"""Domain models package."""

from ingestion_service.domain.events import (
    DocumentEvent,
    document_deleted_event,
    document_failed_event,
    document_processed_event,
    document_queued_event,
    document_uploaded_event,
    document_validated_event,
)
from ingestion_service.domain.models import (
    ALLOWED_MIME_TYPES,
    Document,
    DocumentStatus,
    FileCategory,
    IllegalStateTransition,
    LegalHoldViolation,
    generate_document_id,
    get_file_category,
    get_max_size_bytes,
    is_allowed_content_type,
)

__all__ = [
    "Document",
    "DocumentStatus",
    "FileCategory",
    "IllegalStateTransition",
    "LegalHoldViolation",
    "generate_document_id",
    "get_file_category",
    "is_allowed_content_type",
    "get_max_size_bytes",
    "ALLOWED_MIME_TYPES",
    "DocumentEvent",
    "document_uploaded_event",
    "document_validated_event",
    "document_queued_event",
    "document_processed_event",
    "document_failed_event",
    "document_deleted_event",
]
