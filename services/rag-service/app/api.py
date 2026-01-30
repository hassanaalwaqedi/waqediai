"""
API routes for RAG service.
"""

import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models import RAGQuery, AnswerType
from app.engine import get_rag_engine
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Default tenant for guest mode (public knowledge base)
GUEST_TENANT_ID = UUID("00000000-0000-0000-0000-000000000000")


class QueryRequest(BaseModel):
    """RAG query request supporting both guest and authenticated modes."""
    tenant_id: UUID | None = None  # Optional for guest mode
    user_id: UUID | None = None
    query: str = Field(..., min_length=1, max_length=4096)
    conversation_id: str | None = None
    session_id: str | None = None  # For guest session tracking
    top_k: int = Field(default=5, ge=1, le=20)
    language: str | None = None
    mode: Literal["guest", "authenticated"] = Field(default="guest")
    filters: dict = Field(default_factory=dict)


class CitationSchema(BaseModel):
    """Citation in response."""
    chunk_id: str
    document_id: str
    text_excerpt: str


class QueryResponse(BaseModel):
    """RAG query response."""
    answer: str
    citations: list[CitationSchema]
    confidence: float
    answer_type: str
    language: str
    trace_id: str | None = None
    latency_ms: int | None = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Execute an Advanced RAG query.
    
    Supports both guest mode (public knowledge) and authenticated mode (tenant-scoped).
    Returns a citation-backed answer grounded in retrieved context.
    """
    # Resolve tenant: use provided tenant_id or fall back to guest tenant
    effective_tenant = request.tenant_id if request.tenant_id else GUEST_TENANT_ID
    
    logger.info(
        f"RAG query: mode={request.mode}, tenant={effective_tenant}, "
        f"query_length={len(request.query)}"
    )
    
    engine = get_rag_engine()

    rag_query = RAGQuery(
        tenant_id=effective_tenant,
        user_id=request.user_id,
        query=request.query,
        conversation_id=request.conversation_id or request.session_id,
        language=request.language,
        top_k=request.top_k,
        filters=request.filters,
    )

    response = await engine.query(rag_query)

    return QueryResponse(
        answer=response.answer,
        citations=[
            CitationSchema(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                text_excerpt=c.text_excerpt,
            )
            for c in response.citations
        ],
        confidence=response.confidence,
        answer_type=response.answer_type.value if hasattr(response.answer_type, 'value') else str(response.answer_type),
        language=response.language,
        trace_id=response.metadata.get("trace_id"),
        latency_ms=response.metadata.get("latency_ms"),
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
