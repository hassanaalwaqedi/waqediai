"""
API routes for chunking service.
"""

from uuid import uuid4

from app.chunker import get_chunker
from app.config import get_settings
from app.schemas import (
    ChunkOutput,
    ChunkRequest,
    ChunkResponse,
    HealthResponse,
)
from fastapi import APIRouter

router = APIRouter()


@router.post("/chunk", response_model=ChunkResponse)
async def chunk_document(request: ChunkRequest) -> ChunkResponse:
    """
    Chunk a document into semantic pieces.
    """
    chunker = get_chunker()
    all_chunks = []
    chunk_index = 0

    for segment in request.segments:
        results = chunker.chunk(
            text=segment.text,
            strategy=request.strategy,
            chunk_size=request.chunk_size,
            overlap=request.overlap,
            page_number=segment.page_number,
            source_index=segment.segment_index,
        )

        for result in results:
            all_chunks.append(ChunkOutput(
                chunk_id=f"chunk_{uuid4().hex[:12]}",
                text=result.text,
                language=segment.language,
                page_number=result.page_number,
                chunk_index=chunk_index,
                token_count=result.token_count,
            ))
            chunk_index += 1

    return ChunkResponse(
        document_id=request.document_id,
        chunks=all_chunks,
        total_chunks=len(all_chunks),
        strategy=request.strategy,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.service_name,
        version=settings.service_version,
    )
