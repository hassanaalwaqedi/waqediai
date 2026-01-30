"""
Pydantic schemas for reasoning API.

Defines strict input/output contracts for AI reasoning requests.
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReasoningStrategy(str, Enum):
    """Reasoning strategy types."""
    QA = "qa"
    SUMMARY = "summary"
    EXPLAIN = "explain"


class ContextChunk(BaseModel):
    """A context chunk from vector retrieval."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    text: str = Field(..., min_length=1, description="Chunk text content")
    language: str = Field(default="en", description="ISO 639-1 language code")
    relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)

    @field_validator("text")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize input text."""
        return v.strip()


class ReasoningRequest(BaseModel):
    """Request for AI reasoning."""

    tenant_id: UUID = Field(..., description="Tenant context")
    query: str = Field(..., min_length=1, max_length=4096, description="User query")
    context_chunks: list[ContextChunk] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Pre-retrieved context chunks",
    )
    strategy: ReasoningStrategy = Field(
        default=ReasoningStrategy.QA,
        description="Reasoning strategy",
    )
    user_id: UUID | None = Field(default=None, description="Optional user context")

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """Sanitize query input."""
        return v.strip()


class Citation(BaseModel):
    """Citation reference to source chunk."""

    chunk_id: str = Field(..., description="Referenced chunk identifier")
    document_id: str = Field(..., description="Referenced document identifier")


class ReasoningResponse(BaseModel):
    """Response from AI reasoning."""

    answer: str = Field(..., description="Generated answer text")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Citations backing the answer",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score",
    )
    strategy: ReasoningStrategy = Field(..., description="Strategy used")
    model: str = Field(..., description="LLM model used")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    """Error response following RFC 7807."""

    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
