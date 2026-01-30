"""
API route definitions for retrieval service.
"""

import time

from app.config import get_settings
from app.logging import get_audit_logger, get_logger
from app.qdrant_client import get_qdrant_service
from app.schemas import (
    DeleteRequest,
    DeleteResponse,
    HealthResponse,
    IndexRequest,
    IndexResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from fastapi import APIRouter, HTTPException

router = APIRouter()
logger = get_logger(__name__)
audit = get_audit_logger()


@router.post("/index", response_model=IndexResponse, status_code=201)
async def index_chunks(request: IndexRequest) -> IndexResponse:
    """
    Index knowledge chunks for semantic search.

    Generates embeddings and stores in Qdrant.
    """
    settings = get_settings()
    start_time = time.time()

    # Validate chunk count
    if len(request.chunks) > settings.max_chunks_per_request:
        raise HTTPException(
            status_code=400,
            detail={
                "type": "urn:waqedi:error:too-many-chunks",
                "title": "Too Many Chunks",
                "status": 400,
                "detail": f"Maximum {settings.max_chunks_per_request} chunks per request",
            },
        )

    # Validate chunk lengths
    for chunk in request.chunks:
        if len(chunk.text) > settings.max_chunk_length:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "urn:waqedi:error:chunk-too-long",
                    "title": "Chunk Too Long",
                    "status": 400,
                    "detail": f"Chunk {chunk.chunk_id} exceeds max length",
                },
            )

    # Index chunks
    qdrant = get_qdrant_service()
    chunks_data = [
        {
            "chunk_id": c.chunk_id,
            "text": c.text,
            "language": c.language,
            "page_number": c.page_number,
        }
        for c in request.chunks
    ]

    indexed_count = qdrant.index_chunks(
        tenant_id=request.tenant_id,
        document_id=request.document_id,
        chunks=chunks_data,
    )

    duration_ms = int((time.time() - start_time) * 1000)

    audit.log_index(
        tenant_id=request.tenant_id,
        document_id=request.document_id,
        chunk_count=indexed_count,
        duration_ms=duration_ms,
    )

    return IndexResponse(
        indexed_count=indexed_count,
        document_id=request.document_id,
        collection=qdrant.collection_name,
    )


@router.post("/search", response_model=SearchResponse)
async def search_chunks(request: SearchRequest) -> SearchResponse:
    """
    Semantic search for relevant chunks.

    Returns ranked results with relevance scores.
    """
    start_time = time.time()

    qdrant = get_qdrant_service()
    hits = qdrant.search(
        tenant_id=request.tenant_id,
        query=request.query,
        top_k=request.top_k,
        language=request.language,
        min_score=request.min_score,
    )

    duration_ms = int((time.time() - start_time) * 1000)
    top_score = hits[0].score if hits else None

    audit.log_search(
        tenant_id=request.tenant_id,
        query_length=len(request.query),
        result_count=len(hits),
        top_score=top_score,
        duration_ms=duration_ms,
    )

    results = [
        SearchResult(
            chunk_id=h.chunk_id,
            document_id=h.document_id,
            text=h.text,
            language=h.language,
            score=h.score,
        )
        for h in hits
    ]

    return SearchResponse(
        results=results,
        query=request.query,
        total_found=len(results),
    )


@router.post("/delete", response_model=DeleteResponse)
async def delete_document(request: DeleteRequest) -> DeleteResponse:
    """
    Delete all vectors for a document.
    """
    qdrant = get_qdrant_service()
    deleted_count = qdrant.delete_document(
        tenant_id=request.tenant_id,
        document_id=request.document_id,
    )

    audit.log_delete(
        tenant_id=request.tenant_id,
        document_id=request.document_id,
        deleted_count=deleted_count,
    )

    return DeleteResponse(
        deleted_count=deleted_count,
        document_id=request.document_id,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness check."""
    settings = get_settings()
    qdrant = get_qdrant_service()

    return HealthResponse(
        status="healthy",
        service=settings.service_name,
        version=settings.service_version,
        qdrant_connected=qdrant.health_check(),
    )
