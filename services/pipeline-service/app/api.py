"""
API routes for pipeline service.
"""

import logging
from uuid import UUID

from app.config import get_settings
from app.models import DocumentInput
from app.pipeline import get_pipeline
from app.stages import get_vector_store
from fastapi import APIRouter, Form, HTTPException, UploadFile
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class IngestResponse(BaseModel):
    """Response from document ingestion."""
    document_id: str
    status: str
    chunks_created: int
    vectors_stored: int
    language: str
    document_type: str | None
    processing_time_ms: int
    error: str | None = None


class DeleteRequest(BaseModel):
    """Request to delete a document."""
    tenant_id: UUID
    document_id: str


class DeleteResponse(BaseModel):
    """Response from deletion."""
    success: bool
    document_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    qdrant_connected: bool


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile,
    tenant_id: str = Form(...),
    document_id: str = Form(...),
) -> IngestResponse:
    """
    Ingest a document through the full pipeline.

    Accepts: PDF, images (PNG/JPG), text files
    """
    settings = get_settings()

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    extension = "." + file.filename.rsplit(".", 1)[-1].lower()
    if extension not in settings.supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {settings.supported_extensions}",
        )

    # Read content
    content = await file.read()
    max_size = settings.max_document_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max: {settings.max_document_size_mb}MB",
        )

    # Create document input
    doc_input = DocumentInput(
        tenant_id=UUID(tenant_id),
        document_id=document_id,
        filename=file.filename,
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )

    # Process through pipeline
    pipeline = get_pipeline()
    result = pipeline.process(doc_input)

    return IngestResponse(
        document_id=result.document_id,
        status=result.status.value,
        chunks_created=result.chunks_created,
        vectors_stored=result.vectors_stored,
        language=result.language,
        document_type=result.document_type.value if result.document_type else None,
        processing_time_ms=result.processing_time_ms,
        error=result.error,
    )


@router.post("/delete", response_model=DeleteResponse)
async def delete_document(request: DeleteRequest) -> DeleteResponse:
    """Delete a document from the vector store."""
    pipeline = get_pipeline()
    success = pipeline.delete_document(str(request.tenant_id), request.document_id)

    return DeleteResponse(
        success=success,
        document_id=request.document_id,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check with Qdrant connectivity."""
    settings = get_settings()
    store = get_vector_store()

    return HealthResponse(
        status="healthy",
        service=settings.service_name,
        version=settings.service_version,
        qdrant_connected=store.health_check(),
    )
