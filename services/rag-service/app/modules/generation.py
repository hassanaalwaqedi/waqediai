"""
Answer generation module.

Generates citation-backed answers using Ollama/Qwen.
"""

import logging
import re

import httpx
from app.config import get_settings
from app.models import (
    AnswerType,
    Citation,
    ContextWindow,
    QueryIntent,
    RAGResponse,
    RankedChunk,
)

logger = logging.getLogger(__name__)


class Generator:
    """
    LLM-based answer generation.

    Uses Ollama with Qwen for citation-enforced generation.
    """

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens

    async def generate(
        self,
        prompt: dict,
        context: ContextWindow,
        query_intent: QueryIntent,
        language: str,
    ) -> RAGResponse:
        """
        Generate answer from LLM.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

            answer = result.get("message", {}).get("content", "")

        except httpx.HTTPError as e:
            logger.error(f"LLM request failed: {e}")
            return RAGResponse(
                answer="I am unable to generate a response at this time.",
                citations=[],
                confidence=0.0,
                answer_type=AnswerType.DIRECT,
                language=language,
                metadata={"error": str(e)},
            )

        # Extract citations from answer
        citations = self._extract_citations(answer, context.chunks)

        # Calculate confidence
        confidence = self._calculate_confidence(answer, citations, context)

        # Determine answer type
        answer_type = self._detect_answer_type(answer, query_intent)

        logger.info(
            f"Generated answer: {len(answer)} chars, "
            f"{len(citations)} citations, confidence={confidence:.2f}"
        )

        return RAGResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            answer_type=answer_type,
            language=language,
            metadata={
                "model": self.model,
                "chunks_used": len(context.chunks),
            },
        )

    def _extract_citations(
        self,
        answer: str,
        chunks: list[RankedChunk],
    ) -> list[Citation]:
        """Extract citations from answer text."""
        citations = []
        seen = set()

        # Find [chunk_id] patterns
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, answer)

        # Map chunk_ids to chunks
        chunk_map = {c.chunk_id: c for c in chunks}

        for match in matches:
            chunk_id = match.strip()
            if chunk_id in chunk_map and chunk_id not in seen:
                chunk = chunk_map[chunk_id]
                citations.append(Citation(
                    chunk_id=chunk_id,
                    document_id=chunk.document_id,
                    text_excerpt=chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text,
                ))
                seen.add(chunk_id)

        return citations

    def _calculate_confidence(
        self,
        answer: str,
        citations: list[Citation],
        context: ContextWindow,
    ) -> float:
        """Calculate answer confidence score."""
        if not citations:
            # No citations = low confidence
            return 0.3

        # Base confidence on citation coverage
        citation_ratio = len(citations) / max(len(context.chunks), 1)

        # Check for refusal patterns
        refusal_patterns = [
            "cannot find",
            "not available",
            "no information",
            "لا أجد",
            "غير متاحة",
        ]
        is_refusal = any(p in answer.lower() for p in refusal_patterns)

        if is_refusal:
            return 0.9  # High confidence in honest refusal

        # Score based on citations and answer quality
        base_score = min(citation_ratio * 0.8 + 0.2, 0.95)

        return round(base_score, 2)

    def _detect_answer_type(
        self,
        answer: str,
        intent: QueryIntent,
    ) -> AnswerType:
        """Detect the format of the answer."""
        # Check for list patterns
        list_patterns = [
            r'^\s*[-•*]\s',
            r'^\s*\d+\.',
            r'^\s*\d+\)',
        ]
        lines = answer.split('\n')
        list_lines = sum(1 for line in lines if any(re.match(p, line) for p in list_patterns))

        if list_lines >= 3:
            if intent == QueryIntent.PROCEDURAL:
                return AnswerType.STEPS
            return AnswerType.LIST

        if intent == QueryIntent.SUMMARY or len(answer) > 500:
            return AnswerType.EXPLANATION

        return AnswerType.DIRECT


def get_generator() -> Generator:
    """Get generator instance."""
    return Generator()
