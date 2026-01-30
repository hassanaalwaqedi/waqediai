"""
Semantic chunking implementation.

Provides multiple chunking strategies for document processing.
"""

import re
from dataclasses import dataclass

from app.config import get_settings
from app.schemas import ChunkingStrategy


@dataclass
class ChunkResult:
    """Internal chunk result."""
    text: str
    token_count: int
    page_number: int | None
    source_index: int


class TextChunker:
    """
    Text chunking with multiple strategies.
    """

    def __init__(self):
        settings = get_settings()
        self.default_size = settings.default_chunk_size
        self.max_size = settings.max_chunk_size
        self.min_size = settings.min_chunk_size
        self.overlap = settings.overlap_tokens

    def chunk(
        self,
        text: str,
        strategy: ChunkingStrategy,
        chunk_size: int = 512,
        overlap: int = 50,
        page_number: int | None = None,
        source_index: int = 0,
    ) -> list[ChunkResult]:
        """
        Chunk text using specified strategy.
        """
        if strategy == ChunkingStrategy.SEMANTIC:
            return self._semantic_chunk(text, chunk_size, overlap, page_number, source_index)
        elif strategy == ChunkingStrategy.PARAGRAPH:
            return self._paragraph_chunk(text, page_number, source_index)
        elif strategy == ChunkingStrategy.SLIDING_WINDOW:
            return self._sliding_window_chunk(text, chunk_size, overlap, page_number, source_index)
        elif strategy == ChunkingStrategy.SENTENCE:
            return self._sentence_chunk(text, chunk_size, page_number, source_index)
        else:
            return self._semantic_chunk(text, chunk_size, overlap, page_number, source_index)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approx 4 chars per token)."""
        return len(text) // 4

    def _semantic_chunk(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
        page_number: int | None,
        source_index: int,
    ) -> list[ChunkResult]:
        """
        Semantic chunking that respects sentence boundaries.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)

            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(ChunkResult(
                    text=chunk_text,
                    token_count=self._estimate_tokens(chunk_text),
                    page_number=page_number,
                    source_index=source_index,
                ))

                # Keep overlap
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_chunk):
                    s_tokens = self._estimate_tokens(s)
                    if overlap_tokens + s_tokens <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break

                current_chunk = overlap_sentences
                current_tokens = overlap_tokens

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if self._estimate_tokens(chunk_text) >= self.min_size:
                chunks.append(ChunkResult(
                    text=chunk_text,
                    token_count=self._estimate_tokens(chunk_text),
                    page_number=page_number,
                    source_index=source_index,
                ))

        return chunks

    def _paragraph_chunk(
        self,
        text: str,
        page_number: int | None,
        source_index: int,
    ) -> list[ChunkResult]:
        """Chunk by paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []

        for para in paragraphs:
            para = para.strip()
            if para and self._estimate_tokens(para) >= self.min_size:
                chunks.append(ChunkResult(
                    text=para,
                    token_count=self._estimate_tokens(para),
                    page_number=page_number,
                    source_index=source_index,
                ))

        return chunks

    def _sliding_window_chunk(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
        page_number: int | None,
        source_index: int,
    ) -> list[ChunkResult]:
        """Fixed-size sliding window chunks."""
        words = text.split()
        chunk_words = chunk_size * 4 // 5  # Approx words per chunk
        overlap_words = overlap * 4 // 5
        step = max(1, chunk_words - overlap_words)

        chunks = []
        for i in range(0, len(words), step):
            chunk_text = ' '.join(words[i:i + chunk_words])
            if self._estimate_tokens(chunk_text) >= self.min_size:
                chunks.append(ChunkResult(
                    text=chunk_text,
                    token_count=self._estimate_tokens(chunk_text),
                    page_number=page_number,
                    source_index=source_index,
                ))

        return chunks

    def _sentence_chunk(
        self,
        text: str,
        chunk_size: int,
        page_number: int | None,
        source_index: int,
    ) -> list[ChunkResult]:
        """One sentence per chunk (for short docs)."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 20:
                chunks.append(ChunkResult(
                    text=sentence,
                    token_count=self._estimate_tokens(sentence),
                    page_number=page_number,
                    source_index=source_index,
                ))

        return chunks


def get_chunker() -> TextChunker:
    """Get chunker instance."""
    return TextChunker()
