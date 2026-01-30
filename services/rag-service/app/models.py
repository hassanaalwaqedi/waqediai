"""
Data models for Advanced RAG Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class QueryIntent(str, Enum):
    """Query intent types."""
    FACTUAL = "factual"
    SUMMARY = "summary"
    COMPARISON = "comparison"
    PROCEDURAL = "procedural"
    CLARIFICATION = "clarification"


class AnswerType(str, Enum):
    """Answer format types."""
    DIRECT = "direct"
    LIST = "list"
    STEPS = "steps"
    EXPLANATION = "explanation"


@dataclass
class RAGQuery:
    """Input query for RAG processing."""
    tenant_id: UUID
    user_id: UUID | None
    query: str
    conversation_id: str | None = None
    language: str | None = None
    top_k: int = 5
    filters: dict = field(default_factory=dict)


@dataclass
class EnrichedQuery:
    """Query after understanding and enrichment."""
    original_query: str
    normalized_query: str
    language: str
    intent: QueryIntent
    keywords: list[str]
    conversation_context: list[str]


@dataclass
class RetrievedChunk:
    """A chunk retrieved from vector store."""
    chunk_id: str
    document_id: str
    text: str
    language: str
    score: float
    metadata: dict = field(default_factory=dict)


@dataclass
class RankedChunk:
    """A chunk after re-ranking."""
    chunk_id: str
    document_id: str
    text: str
    language: str
    relevance_score: float
    diversity_score: float
    final_score: float
    rank: int


@dataclass
class ContextWindow:
    """Assembled context for LLM."""
    chunks: list[RankedChunk]
    total_tokens: int
    languages: list[str]
    document_ids: list[str]


@dataclass
class Citation:
    """A citation reference."""
    chunk_id: str
    document_id: str
    text_excerpt: str


@dataclass
class RAGResponse:
    """Final RAG response."""
    answer: str
    citations: list[Citation]
    confidence: float
    answer_type: AnswerType
    language: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ReasoningTrace:
    """Audit trace for reasoning."""
    trace_id: str
    tenant_id: UUID
    query: str
    retrieved_chunks: list[str]
    context_tokens: int
    prompt_tokens: int
    answer: str
    citations: list[str]
    latency_ms: int
    timestamp: datetime
