"""
Pydantic schemas for chunking service.
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    """Chunking strategy types."""
    SEMANTIC = "semantic"
    PARAGRAPH = "paragraph"
    SLIDING_WINDOW = "sliding_window"
    SENTENCE = "sentence"


class TextSegment(BaseModel):
    """Input text segment from language service."""
    text: str = Field(..., min_length=1)
    language: str = Field(default="en")
    page_number: int | None = None
    segment_index: int = 0


class ChunkRequest(BaseModel):
    """Request to chunk a document."""
    tenant_id: UUID
    document_id: str
    segments: list[TextSegment]
    strategy: ChunkingStrategy = Field(default=ChunkingStrategy.SEMANTIC)
    chunk_size: int = Field(default=512, ge=100, le=2048)
    overlap: int = Field(default=50, ge=0, le=200)


class ChunkOutput(BaseModel):
    """A single output chunk."""
    chunk_id: str
    text: str
    language: str
    page_number: int | None
    chunk_index: int
    token_count: int


class ChunkResponse(BaseModel):
    """Response after chunking."""
    document_id: str
    chunks: list[ChunkOutput]
    total_chunks: int
    strategy: ChunkingStrategy


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
