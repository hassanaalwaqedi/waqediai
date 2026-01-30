"""
Ollama HTTP adapter for LLM reasoning.

Provides a clean interface to Ollama API with citation-enforced prompting.
"""

import re
from dataclasses import dataclass

import httpx
from app.config import get_settings
from app.logging import get_logger
from app.schemas import Citation, ContextChunk, ReasoningStrategy

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM."""
    answer: str
    citations: list[Citation]
    confidence: float
    model: str


class OllamaClient:
    """
    HTTP client for Ollama API.

    Enforces citation-based answering and context-only responses.
    """

    SYSTEM_PROMPT = """You are a precise enterprise AI assistant. Follow these rules strictly:

1. ONLY use information from the provided context chunks
2. NEVER make claims not directly supported by the context
3. ALWAYS cite your sources using [chunk_id] format
4. If the context doesn't contain enough information, say so clearly
5. Be concise and professional

For each claim you make, include a citation like [chunk_123] referencing the source chunk."""

    STRATEGY_PROMPTS = {
        ReasoningStrategy.QA: "Answer the following question based strictly on the provided context. Cite every claim.",
        ReasoningStrategy.SUMMARY: "Summarize the key information from the provided context. Cite the sources for each point.",
        ReasoningStrategy.EXPLAIN: "Explain the concepts in the provided context clearly. Cite all references.",
    }

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.max_tokens = settings.ollama_max_tokens
        self.temperature = settings.ollama_temperature

    def _build_context_block(self, chunks: list[ContextChunk]) -> str:
        """Build formatted context block from chunks."""
        context_parts = []
        for chunk in chunks:
            context_parts.append(
                f"[{chunk.chunk_id}] (Document: {chunk.document_id}, Language: {chunk.language})\n{chunk.text}"
            )
        return "\n\n---\n\n".join(context_parts)

    def _build_prompt(
        self,
        query: str,
        chunks: list[ContextChunk],
        strategy: ReasoningStrategy,
    ) -> str:
        """Build the full prompt with context and instructions."""
        context_block = self._build_context_block(chunks)
        strategy_instruction = self.STRATEGY_PROMPTS[strategy]

        return f"""## Context Chunks

{context_block}

## Task

{strategy_instruction}

## User Query

{query}

## Your Response (with citations)"""

    def _extract_citations(
        self,
        answer: str,
        available_chunks: list[ContextChunk],
    ) -> list[Citation]:
        """Extract citations from answer text."""
        citations = []
        seen_chunk_ids = set()

        # Find all [chunk_id] patterns
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, answer)

        # Map chunk_ids to documents
        chunk_to_doc = {c.chunk_id: c.document_id for c in available_chunks}

        for match in matches:
            chunk_id = match.strip()
            if chunk_id in chunk_to_doc and chunk_id not in seen_chunk_ids:
                citations.append(Citation(
                    chunk_id=chunk_id,
                    document_id=chunk_to_doc[chunk_id],
                ))
                seen_chunk_ids.add(chunk_id)

        return citations

    def _calculate_confidence(
        self,
        citations: list[Citation],
        chunk_count: int,
        answer_length: int,
    ) -> float:
        """Calculate confidence score based on citation coverage."""
        if not citations:
            return 0.3  # Low confidence without citations

        # Base confidence on citation ratio
        citation_ratio = min(len(citations) / max(chunk_count, 1), 1.0)

        # Penalize very short or very long answers
        length_factor = 1.0
        if answer_length < 50:
            length_factor = 0.7
        elif answer_length > 2000:
            length_factor = 0.9

        confidence = citation_ratio * length_factor * 0.9 + 0.1
        return round(min(confidence, 1.0), 2)

    async def reason(
        self,
        query: str,
        chunks: list[ContextChunk],
        strategy: ReasoningStrategy,
    ) -> LLMResponse:
        """
        Execute reasoning with the LLM.

        Args:
            query: User query.
            chunks: Context chunks for grounding.
            strategy: Reasoning strategy.

        Returns:
            LLMResponse with answer, citations, and confidence.

        Raises:
            httpx.HTTPError: On LLM communication failure.
        """
        prompt = self._build_prompt(query, chunks, strategy)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

        answer = result.get("message", {}).get("content", "")

        citations = self._extract_citations(answer, chunks)
        confidence = self._calculate_confidence(
            citations, len(chunks), len(answer)
        )

        logger.info(
            f"LLM response generated: {len(answer)} chars, {len(citations)} citations"
        )

        return LLMResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            model=self.model,
        )


def get_llm_client() -> OllamaClient:
    """Get LLM client instance."""
    return OllamaClient()
