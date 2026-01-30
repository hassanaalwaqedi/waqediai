"""
Domain models for document ingestion and lifecycle.
"""

import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class DocumentStatus(str, Enum):
    """Document lifecycle states."""

    UPLOADED = "UPLOADED"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"
    DELETED = "DELETED"


class FileCategory(str, Enum):
    """File type categories for processing pipeline routing."""

    DOCUMENT = "DOCUMENT"  # PDF -> OCR
    IMAGE = "IMAGE"  # Vision analysis
    AUDIO = "AUDIO"  # Speech-to-text
    VIDEO = "VIDEO"  # Combined processing


# State machine: allowed transitions
ALLOWED_TRANSITIONS: dict[DocumentStatus, set[DocumentStatus]] = {
    DocumentStatus.UPLOADED: {DocumentStatus.VALIDATED, DocumentStatus.REJECTED},
    DocumentStatus.VALIDATED: {DocumentStatus.QUEUED},
    DocumentStatus.QUEUED: {DocumentStatus.PROCESSING},
    DocumentStatus.PROCESSING: {DocumentStatus.PROCESSED, DocumentStatus.FAILED},
    DocumentStatus.PROCESSED: {DocumentStatus.ARCHIVED, DocumentStatus.DELETED},
    DocumentStatus.FAILED: {DocumentStatus.QUEUED},
    DocumentStatus.ARCHIVED: {DocumentStatus.DELETED},
    DocumentStatus.REJECTED: set(),  # Terminal
    DocumentStatus.DELETED: set(),  # Terminal
}


class IllegalStateTransition(Exception):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, from_status: DocumentStatus, to_status: DocumentStatus):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(
            f"Cannot transition from {from_status.value} to {to_status.value}"
        )


class LegalHoldViolation(Exception):
    """Raised when trying to delete a document under legal hold."""

    def __init__(self, document_id: str):
        self.document_id = document_id
        super().__init__(f"Document {document_id} is under legal hold and cannot be deleted")


def generate_document_id() -> str:
    """
    Generate a unique, time-ordered document ID.

    Format: doc_{timestamp_base32}_{random}
    """
    # Timestamp component for ordering (milliseconds since epoch)
    ts = int(time.time() * 1000)
    ts_part = format(ts, 'x')  # Hex encoding

    # Random component for uniqueness
    random_part = secrets.token_hex(8)

    return f"doc_{ts_part}_{random_part}"


@dataclass
class Document:
    """
    Core document entity.

    Represents a document throughout its lifecycle.
    """

    # Identity
    id: str
    tenant_id: UUID

    # Ownership
    uploaded_by: UUID
    department_id: UUID | None = None
    collection_id: UUID | None = None

    # File Properties
    filename: str = ""
    content_type: str = ""
    size_bytes: int = 0
    checksum_sha256: str = ""

    # Classification
    file_category: FileCategory = FileCategory.DOCUMENT
    language: str | None = None

    # Lifecycle
    status: DocumentStatus = DocumentStatus.UPLOADED
    retention_policy: str = "standard"
    legal_hold: bool = False

    # Storage
    storage_bucket: str = ""
    storage_key: str = ""

    # Timestamps
    uploaded_at: datetime | None = None
    validated_at: datetime | None = None
    processed_at: datetime | None = None
    archived_at: datetime | None = None
    deleted_at: datetime | None = None
    expires_at: datetime | None = None

    # Custom metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def can_transition_to(self, new_status: DocumentStatus) -> bool:
        """Check if transition to new status is allowed."""
        allowed = ALLOWED_TRANSITIONS.get(self.status, set())
        return new_status in allowed

    def transition_to(self, new_status: DocumentStatus) -> None:
        """
        Transition to a new status.

        Raises:
            IllegalStateTransition: If transition is not allowed.
            LegalHoldViolation: If deleting a held document.
        """
        if not self.can_transition_to(new_status):
            raise IllegalStateTransition(self.status, new_status)

        if new_status == DocumentStatus.DELETED and self.legal_hold:
            raise LegalHoldViolation(self.id)

        self.status = new_status

        # Update relevant timestamps
        now = datetime.utcnow()
        if new_status == DocumentStatus.VALIDATED:
            self.validated_at = now
        elif new_status == DocumentStatus.PROCESSED:
            self.processed_at = now
        elif new_status == DocumentStatus.ARCHIVED:
            self.archived_at = now
        elif new_status == DocumentStatus.DELETED:
            self.deleted_at = now

    @property
    def is_terminal(self) -> bool:
        """Check if document is in a terminal state."""
        return self.status in {DocumentStatus.REJECTED, DocumentStatus.DELETED}

    @property
    def is_processable(self) -> bool:
        """Check if document can be processed."""
        return self.status in {DocumentStatus.QUEUED, DocumentStatus.FAILED}


# MIME type to category mapping
MIME_TO_CATEGORY: dict[str, FileCategory] = {
    "application/pdf": FileCategory.DOCUMENT,
    "image/png": FileCategory.IMAGE,
    "image/jpeg": FileCategory.IMAGE,
    "audio/mpeg": FileCategory.AUDIO,
    "audio/wav": FileCategory.AUDIO,
    "video/mp4": FileCategory.VIDEO,
}


# Allowed MIME types with size limits (MB)
ALLOWED_MIME_TYPES: dict[str, int] = {
    "application/pdf": 100,
    "image/png": 50,
    "image/jpeg": 50,
    "audio/mpeg": 500,
    "audio/wav": 500,
    "video/mp4": 2048,
}


def get_file_category(content_type: str) -> FileCategory:
    """Get file category from MIME type."""
    return MIME_TO_CATEGORY.get(content_type, FileCategory.DOCUMENT)


def is_allowed_content_type(content_type: str) -> bool:
    """Check if content type is allowed."""
    return content_type in ALLOWED_MIME_TYPES


def get_max_size_bytes(content_type: str) -> int:
    """Get maximum file size in bytes for content type."""
    mb = ALLOWED_MIME_TYPES.get(content_type, 100)
    return mb * 1024 * 1024
