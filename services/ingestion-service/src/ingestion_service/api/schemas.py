"""
Pydantic schemas for Ingestion API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response after successful upload."""

    document_id: str = Field(..., description="Unique document identifier")
    status: str = Field(..., description="Current document status")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., description="File size in bytes")
    file_category: str = Field(..., description="Document category")
    uploaded_at: datetime = Field(..., description="Upload timestamp")


class DocumentResponse(BaseModel):
    """Full document details response."""

    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    file_category: str
    status: str
    language: str | None = None
    retention_policy: str
    legal_hold: bool
    uploaded_by: UUID
    department_id: UUID | None = None
    collection_id: UUID | None = None
    uploaded_at: datetime
    validated_at: datetime | None = None
    processed_at: datetime | None = None

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    """Document item in list response."""

    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    file_category: str
    status: str
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    """Paginated document list response."""

    items: list[DocumentListItem]
    next_cursor: str | None = None
    total_count: int | None = None


class DeleteResponse(BaseModel):
    """Deletion request response."""

    document_id: str
    status: str = "DELETION_SCHEDULED"
    message: str = "Document deletion has been scheduled"


class ProblemDetail(BaseModel):
    """RFC 7807 error response."""

    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
