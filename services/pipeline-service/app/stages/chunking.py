"""
Intelligent chunking stage.

Splits text into semantic chunks optimized for retrieval.
"""

import logging
import re
from uuid import uuid4

from app.config import get_settings
from app.models import NormalizedText, TextChunk

logger = logging.getLogger(__name__)


class Chunker:
    """
    Semantic text chunker.

    Creates chunks that respect sentence and paragraph boundaries.
    """

    def __init__(self):
        settings = get_settings()
        self.default_size = settings.default_chunk_size
        self.overlap = settings.chunk_overlap
        self.min_size = settings.min_chunk_size

    def chunk(self, normalized: NormalizedText) -> list[TextChunk]:
        """
        Split normalized text into semantic chunks.
        """
        text = normalized.text

        if len(text) < self.min_size:
            # Document too small to chunk
            return [self._create_chunk(
                text=text,
                document_id=normalized.document_id,
                tenant_id=normalized.tenant_id,
                language=normalized.language,
                page_number=1,
                chunk_index=0,
            )]

        # Try paragraph-based chunking first
        paragraphs = self._split_paragraphs(text)

        if len(paragraphs) > 1:
            chunks = self._chunk_paragraphs(
                paragraphs, normalized.document_id, normalized.tenant_id, normalized.language
            )
        else:
            # Fall back to sentence-based chunking
            chunks = self._chunk_sentences(
                text, normalized.document_id, normalized.tenant_id, normalized.language
            )

        logger.info(
            f"Created {len(chunks)} chunks from {len(text)} chars "
            f"(avg {len(text) // max(len(chunks), 1)} chars/chunk)"
        )

        return chunks

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle Arabic and English sentence endings
        sentences = re.split(r'(?<=[.!?؟。])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approx 4 chars per token)."""
        return max(1, len(text) // 4)

    def _chunk_paragraphs(
        self,
        paragraphs: list[str],
        document_id: str,
        tenant_id,
        language: str,
    ) -> list[TextChunk]:
        """Create chunks from paragraphs, merging small ones."""
        chunks = []
        current_text = ""
        current_tokens = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)

            # If paragraph alone exceeds chunk size, split it
            if para_tokens > self.default_size:
                # Flush current buffer
                if current_text:
                    chunks.append(self._create_chunk(
                        text=current_text.strip(),
                        document_id=document_id,
                        tenant_id=tenant_id,
                        language=language,
                        page_number=None,
                        chunk_index=chunk_index,
                    ))
                    chunk_index += 1
                    current_text = ""
                    current_tokens = 0

                # Split large paragraph by sentences
                sub_chunks = self._chunk_sentences(
                    para, document_id, tenant_id, language, start_index=chunk_index
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
                continue

            # Check if adding this paragraph exceeds size
            if current_tokens + para_tokens > self.default_size:
                if current_text:
                    chunks.append(self._create_chunk(
                        text=current_text.strip(),
                        document_id=document_id,
                        tenant_id=tenant_id,
                        language=language,
                        page_number=None,
                        chunk_index=chunk_index,
                    ))
                    chunk_index += 1

                current_text = para
                current_tokens = para_tokens
            else:
                current_text += "\n\n" + para if current_text else para
                current_tokens += para_tokens

        # Flush remaining
        if current_text and self._estimate_tokens(current_text) >= self.min_size:
            chunks.append(self._create_chunk(
                text=current_text.strip(),
                document_id=document_id,
                tenant_id=tenant_id,
                language=language,
                page_number=None,
                chunk_index=chunk_index,
            ))

        return chunks

    def _chunk_sentences(
        self,
        text: str,
        document_id: str,
        tenant_id,
        language: str,
        start_index: int = 0,
    ) -> list[TextChunk]:
        """Create chunks from sentences with overlap."""
        sentences = self._split_sentences(text)
        chunks = []
        current_sentences = []
        current_tokens = 0
        chunk_index = start_index

        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)

            if current_tokens + sentence_tokens > self.default_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append(self._create_chunk(
                    text=chunk_text,
                    document_id=document_id,
                    tenant_id=tenant_id,
                    language=language,
                    page_number=None,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1

                # Keep overlap sentences
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_sentences):
                    s_tokens = self._estimate_tokens(s)
                    if overlap_tokens + s_tokens <= self.overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break

                current_sentences = overlap_sentences
                current_tokens = overlap_tokens

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        # Final chunk
        if current_sentences:
            chunk_text = " ".join(current_sentences)
            if self._estimate_tokens(chunk_text) >= self.min_size:
                chunks.append(self._create_chunk(
                    text=chunk_text,
                    document_id=document_id,
                    tenant_id=tenant_id,
                    language=language,
                    page_number=None,
                    chunk_index=chunk_index,
                ))

        return chunks

    def _create_chunk(
        self,
        text: str,
        document_id: str,
        tenant_id,
        language: str,
        page_number: int | None,
        chunk_index: int,
    ) -> TextChunk:
        """Create a TextChunk instance."""
        return TextChunk(
            chunk_id=f"chunk_{uuid4().hex[:12]}",
            document_id=document_id,
            tenant_id=tenant_id,
            text=text,
            language=language,
            page_number=page_number,
            chunk_index=chunk_index,
            token_count=self._estimate_tokens(text),
        )


def get_chunker() -> Chunker:
    """Get chunker instance."""
    return Chunker()
