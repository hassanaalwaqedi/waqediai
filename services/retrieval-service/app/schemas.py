"""
Pydantic schemas for retrieval API.

Strict input/output contracts for indexing and search.
"""

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChunkInput(BaseModel):
    """A text chunk to index."""

    chunk_id: str = Field(..., min_length=1, description="Unique chunk identifier")
    text: str = Field(..., min_length=1, description="Chunk text content")
    language: str = Field(default="en", description="ISO 639-1 language code")
    page_number: int | None = Field(default=None, description="Source page number")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        return v.strip()


class IndexRequest(BaseModel):
    """Request to index knowledge chunks."""

    tenant_id: UUID = Field(..., description="Tenant context")
    document_id: str = Field(..., min_length=1, description="Parent document ID")
    chunks: list[ChunkInput] = Field(
        ...,
        min_length=1,
        description="Chunks to index",
    )


class IndexResponse(BaseModel):
    """Response after indexing."""

    indexed_count: int = Field(..., description="Number of chunks indexed")
    document_id: str = Field(..., description="Document ID")
    collection: str = Field(..., description="Qdrant collection used")


class SearchRequest(BaseModel):
    """Request for semantic search."""

    tenant_id: UUID = Field(..., description="Tenant context for isolation")
    query: str = Field(..., min_length=1, max_length=4096, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    language: str | None = Field(default=None, description="Filter by language")
    min_score: float | None = Field(default=None, ge=0.0, le=1.0)

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        return v.strip()


class SearchResult(BaseModel):
    """A single search result."""

    chunk_id: str = Field(..., description="Chunk identifier")
    document_id: str = Field(..., description="Parent document ID")
    text: str = Field(..., description="Chunk text content")
    language: str = Field(..., description="Chunk language")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")


class SearchResponse(BaseModel):
    """Response from semantic search."""

    results: list[SearchResult] = Field(default_factory=list)
    query: str = Field(..., description="Original query")
    total_found: int = Field(..., description="Total matches found")


class DeleteRequest(BaseModel):
    """Request to delete document vectors."""

    tenant_id: UUID = Field(..., description="Tenant context")
    document_id: str = Field(..., description="Document to delete")


class DeleteResponse(BaseModel):
    """Response after deletion."""

    deleted_count: int = Field(..., description="Vectors deleted")
    document_id: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str
    qdrant_connected: bool


class ErrorResponse(BaseModel):
    """Error response following RFC 7807."""

    type: str
    title: str
    status: int
    detail: str
