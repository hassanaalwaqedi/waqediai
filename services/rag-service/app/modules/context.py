"""
Reranking and context assembly module.

Selects and orders chunks for optimal LLM context.
"""

import logging
from difflib import SequenceMatcher

from app.config import get_settings
from app.models import ContextWindow, RankedChunk, RetrievedChunk

logger = logging.getLogger(__name__)


class ContextAssembler:
    """
    Context ranking and assembly.

    Performs:
    1. Relevance-based reranking
    2. Diversity scoring (avoid redundancy)
    3. Token budget enforcement
    4. Deduplication
    """

    def __init__(self):
        settings = get_settings()
        self.max_tokens = settings.max_context_tokens
        self.max_chunks = settings.max_chunks_per_query
        self.dedup_threshold = settings.deduplication_threshold

    def assemble(
        self,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> ContextWindow:
        """
        Assemble context window from retrieved chunks.
        """
        if not chunks:
            return ContextWindow(
                chunks=[],
                total_tokens=0,
                languages=[],
                document_ids=[],
            )

        # Step 1: Deduplicate
        unique_chunks = self._deduplicate(chunks)

        # Step 2: Score for diversity and relevance
        scored_chunks = self._score_chunks(unique_chunks)

        # Step 3: Select top chunks within token budget
        selected = self._select_within_budget(scored_chunks, top_k)

        # Collect metadata
        languages = list({c.language for c in selected})
        doc_ids = list({c.document_id for c in selected})
        total_tokens = sum(self._estimate_tokens(c.text) for c in selected)

        logger.info(
            f"Assembled context: {len(selected)} chunks, "
            f"{total_tokens} tokens, {len(doc_ids)} documents"
        )

        return ContextWindow(
            chunks=selected,
            total_tokens=total_tokens,
            languages=languages,
            document_ids=doc_ids,
        )

    def _deduplicate(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Remove near-duplicate chunks."""
        unique = []

        for chunk in chunks:
            is_duplicate = False
            for existing in unique:
                similarity = self._text_similarity(chunk.text, existing.text)
                if similarity > self.dedup_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(chunk)

        if len(unique) < len(chunks):
            logger.info(f"Deduplicated: {len(chunks)} → {len(unique)} chunks")

        return unique

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity ratio."""
        return SequenceMatcher(None, text1[:500], text2[:500]).ratio()

    def _score_chunks(self, chunks: list[RetrievedChunk]) -> list[RankedChunk]:
        """Score chunks for relevance and diversity."""
        if not chunks:
            return []

        scored = []
        seen_docs = set()

        for i, chunk in enumerate(chunks):
            # Relevance score from retrieval
            relevance = chunk.score

            # Diversity bonus for new documents
            diversity = 1.0 if chunk.document_id not in seen_docs else 0.7
            seen_docs.add(chunk.document_id)

            # Combined score
            final_score = 0.7 * relevance + 0.3 * diversity

            scored.append(RankedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                language=chunk.language,
                relevance_score=relevance,
                diversity_score=diversity,
                final_score=final_score,
                rank=i + 1,
            ))

        # Sort by final score
        scored.sort(key=lambda x: x.final_score, reverse=True)

        # Update ranks
        for i, chunk in enumerate(scored):
            chunk.rank = i + 1

        return scored

    def _select_within_budget(
        self,
        chunks: list[RankedChunk],
        top_k: int,
    ) -> list[RankedChunk]:
        """Select chunks within token budget."""
        selected = []
        current_tokens = 0

        for chunk in chunks:
            if len(selected) >= min(top_k, self.max_chunks):
                break

            chunk_tokens = self._estimate_tokens(chunk.text)

            if current_tokens + chunk_tokens <= self.max_tokens:
                selected.append(chunk)
                current_tokens += chunk_tokens

        return selected

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approx 4 chars per token)."""
        return max(1, len(text) // 4)


def get_context_assembler() -> ContextAssembler:
    """Get context assembler instance."""
    return ContextAssembler()
