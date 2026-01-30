"""
API route definitions for reasoning service.
"""

import time

from app.config import get_settings
from app.llm_client import get_llm_client
from app.logging import get_audit_logger, get_logger
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    ReasoningRequest,
    ReasoningResponse,
)
from fastapi import APIRouter, HTTPException
from httpx import HTTPError

router = APIRouter()
logger = get_logger(__name__)
audit = get_audit_logger()


@router.post(
    "/reason",
    response_model=ReasoningResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def reason(request: ReasoningRequest) -> ReasoningResponse:
    """
    Execute AI reasoning on provided context.

    Accepts pre-retrieved context chunks and returns a citation-backed answer.
    """
    settings = get_settings()
    start_time = time.time()

    # Audit log the request
    audit.log_reasoning_request(
        tenant_id=request.tenant_id,
        query=request.query,
        strategy=request.strategy.value,
        chunk_count=len(request.context_chunks),
        user_id=request.user_id,
    )

    # Validate chunk count
    if len(request.context_chunks) > settings.max_context_chunks:
        raise HTTPException(
            status_code=400,
            detail={
                "type": "urn:waqedi:error:too-many-chunks",
                "title": "Too Many Context Chunks",
                "status": 400,
                "detail": f"Maximum {settings.max_context_chunks} chunks allowed",
            },
        )

    # Execute LLM reasoning
    llm = get_llm_client()

    try:
        result = await llm.reason(
            query=request.query,
            chunks=request.context_chunks,
            strategy=request.strategy,
        )
    except HTTPError as e:
        audit.log_llm_error(
            tenant_id=request.tenant_id,
            error=str(e),
            model=llm.model,
        )
        raise HTTPException(
            status_code=503,
            detail={
                "type": "urn:waqedi:error:llm-unavailable",
                "title": "LLM Service Unavailable",
                "status": 503,
                "detail": "Failed to communicate with LLM service",
            },
        )

    duration_ms = int((time.time() - start_time) * 1000)

    # Audit log the response
    audit.log_reasoning_response(
        tenant_id=request.tenant_id,
        confidence=result.confidence,
        citation_count=len(result.citations),
        model=result.model,
        duration_ms=duration_ms,
    )

    return ReasoningResponse(
        answer=result.answer,
        citations=result.citations,
        confidence=result.confidence,
        strategy=request.strategy,
        model=result.model,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness check."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.service_name,
        version=settings.service_version,
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Readiness check including LLM connectivity."""
    settings = get_settings()

    # Optionally check LLM health here
    # For now, just return ready

    return HealthResponse(
        status="ready",
        service=settings.service_name,
        version=settings.service_version,
    )
