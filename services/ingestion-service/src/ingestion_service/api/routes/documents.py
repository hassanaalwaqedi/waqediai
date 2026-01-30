"""
Document API routes.

Handles upload, listing, details, and deletion of documents.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from fastapi.responses import JSONResponse

from ingestion_service.api.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentListItem,
    DeleteResponse,
    ProblemDetail,
)
from ingestion_service.adapters import get_session, DocumentRepository
from ingestion_service.domain import DocumentStatus, LegalHoldViolation
from ingestion_service.services import (
    UploadService,
    UnsupportedMediaType,
    FileTooLarge,
    QuotaExceeded,
)
from ingestion_service.middleware.auth import get_current_user, TenantContext

router = APIRouter(prefix="/documents", tags=["Documents"])


def _doc_to_response(doc) -> DocumentResponse:
    """Convert domain document to response schema."""
    return DocumentResponse(
        document_id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        file_category=doc.file_category.value,
        status=doc.status.value,
        language=doc.language,
        retention_policy=doc.retention_policy,
        legal_hold=doc.legal_hold,
        uploaded_by=doc.uploaded_by,
        department_id=doc.department_id,
        collection_id=doc.collection_id,
        uploaded_at=doc.uploaded_at,
        validated_at=doc.validated_at,
        processed_at=doc.processed_at,
    )


def _doc_to_list_item(doc) -> DocumentListItem:
    """Convert domain document to list item."""
    return DocumentListItem(
        document_id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        file_category=doc.file_category.value,
        status=doc.status.value,
        uploaded_at=doc.uploaded_at,
    )


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=201,
    responses={
        413: {"model": ProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        429: {"model": ProblemDetail, "description": "Quota exceeded"},
    },
)
async def upload_document(
    request: Request,
    file: Annotated[UploadFile, File(description="File to upload")],
    context: Annotated[TenantContext, Depends(get_current_user)],
    collection_id: UUID | None = None,
) -> DocumentUploadResponse:
    """
    Upload a new document.
    
    Accepts PDF, images (PNG, JPG), audio (MP3, WAV), and video (MP4).
    """
    # Read file content
    file_content = await file.read()

    upload_service = UploadService()

    try:
        document = await upload_service.upload(
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            file_data=file_content,
            department_id=context.department_id,
            collection_id=collection_id,
            correlation_id=getattr(request.state, "correlation_id", ""),
        )

        return DocumentUploadResponse(
            document_id=document.id,
            status=document.status.value,
            filename=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            file_category=document.file_category.value,
            uploaded_at=document.uploaded_at,
        )

    except UnsupportedMediaType as e:
        raise HTTPException(
            status_code=415,
            detail={
                "type": "urn:waqedi:error:unsupported-media-type",
                "title": "Unsupported Media Type",
                "status": 415,
                "detail": e.message,
            },
        )
    except FileTooLarge as e:
        raise HTTPException(
            status_code=413,
            detail={
                "type": "urn:waqedi:error:file-too-large",
                "title": "File Too Large",
                "status": 413,
                "detail": e.message,
            },
        )
    except QuotaExceeded as e:
        raise HTTPException(
            status_code=429,
            detail={
                "type": "urn:waqedi:error:quota-exceeded",
                "title": "Quota Exceeded",
                "status": 429,
                "detail": e.message,
            },
        )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    context: Annotated[TenantContext, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
    status: str | None = Query(None, pattern="^(UPLOADED|VALIDATED|QUEUED|PROCESSING|PROCESSED|FAILED|ARCHIVED)$"),
    file_category: str | None = Query(None, pattern="^(DOCUMENT|IMAGE|AUDIO|VIDEO)$"),
    collection_id: UUID | None = None,
) -> DocumentListResponse:
    """
    List documents in the current tenant.
    
    Returns cursor-based paginated results.
    """
    async with get_session() as session:
        repo = DocumentRepository(session, context.tenant_id)

        doc_status = DocumentStatus(status) if status else None

        documents, next_cursor = await repo.list_documents(
            limit=limit,
            cursor=cursor,
            status=doc_status,
            file_category=file_category,
            collection_id=collection_id,
        )

        return DocumentListResponse(
            items=[_doc_to_list_item(d) for d in documents],
            next_cursor=next_cursor,
        )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    responses={404: {"model": ProblemDetail}},
)
async def get_document(
    document_id: str,
    context: Annotated[TenantContext, Depends(get_current_user)],
) -> DocumentResponse:
    """Get document details by ID."""
    async with get_session() as session:
        repo = DocumentRepository(session, context.tenant_id)
        document = await repo.get_by_id(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail={
                    "type": "urn:waqedi:error:document-not-found",
                    "title": "Document Not Found",
                    "status": 404,
                    "detail": f"Document {document_id} not found",
                },
            )

        return _doc_to_response(document)


@router.delete(
    "/{document_id}",
    response_model=DeleteResponse,
    status_code=202,
    responses={
        404: {"model": ProblemDetail},
        409: {"model": ProblemDetail, "description": "Legal hold prevents deletion"},
    },
)
async def delete_document(
    document_id: str,
    context: Annotated[TenantContext, Depends(get_current_user)],
) -> DeleteResponse:
    """
    Request document deletion (soft delete).
    
    Returns 202 Accepted. Actual deletion is asynchronous.
    """
    async with get_session() as session:
        repo = DocumentRepository(session, context.tenant_id)
        document = await repo.get_by_id(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail={
                    "type": "urn:waqedi:error:document-not-found",
                    "title": "Document Not Found",
                    "status": 404,
                    "detail": f"Document {document_id} not found",
                },
            )

        # Check legal hold
        if document.legal_hold:
            raise HTTPException(
                status_code=409,
                detail={
                    "type": "urn:waqedi:error:legal-hold",
                    "title": "Legal Hold Active",
                    "status": 409,
                    "detail": f"Document {document_id} is under legal hold",
                },
            )

        # Soft delete
        await repo.soft_delete(document_id)

        return DeleteResponse(
            document_id=document_id,
            status="DELETED",
            message="Document has been marked for deletion",
        )
