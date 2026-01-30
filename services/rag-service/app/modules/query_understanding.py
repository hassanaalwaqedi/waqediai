"""
Query understanding module.

Normalizes, enriches, and classifies incoming queries.
"""

import logging
import re

from app.config import get_settings
from app.models import EnrichedQuery, QueryIntent, RAGQuery

logger = logging.getLogger(__name__)


class QueryUnderstanding:
    """
    Query analysis and enrichment.

    Handles language detection, normalization, intent classification,
    and conversation context integration.
    """

    # Arabic stopwords for keyword extraction
    ARABIC_STOPWORDS = {'من', 'إلى', 'في', 'على', 'هذا', 'التي', 'الذي', 'ما', 'كيف', 'لماذا', 'أين', 'متى'}
    ENGLISH_STOPWORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}

    # Intent detection patterns
    INTENT_PATTERNS = {
        QueryIntent.SUMMARY: [r'summarize', r'summary', r'overview', r'ملخص', r'لخص'],
        QueryIntent.COMPARISON: [r'compare', r'difference', r'versus', r'vs', r'قارن', r'الفرق'],
        QueryIntent.PROCEDURAL: [r'how to', r'steps', r'process', r'كيف', r'خطوات'],
        QueryIntent.CLARIFICATION: [r'what is', r'define', r'explain', r'ما هو', r'اشرح', r'عرف'],
    }

    def __init__(self):
        self._conversation_cache: dict[str, list[str]] = {}
        settings = get_settings()
        self.max_history = settings.max_conversation_history

    def process(self, query: RAGQuery) -> EnrichedQuery:
        """
        Process and enrich the incoming query.
        """
        # Normalize query text
        normalized = self._normalize_query(query.query)

        # Detect language
        language = query.language or self._detect_language(normalized)

        # Classify intent
        intent = self._classify_intent(normalized, language)

        # Extract keywords
        keywords = self._extract_keywords(normalized, language)

        # Get conversation context
        context = self._get_conversation_context(query.conversation_id)

        # Update conversation history
        if query.conversation_id:
            self._update_conversation(query.conversation_id, normalized)

        logger.info(
            f"Query processed: lang={language}, intent={intent.value}, "
            f"keywords={len(keywords)}, context_turns={len(context)}"
        )

        return EnrichedQuery(
            original_query=query.query,
            normalized_query=normalized,
            language=language,
            intent=intent,
            keywords=keywords,
            conversation_context=context,
        )

    def _normalize_query(self, query: str) -> str:
        """Normalize query text."""
        # Strip and collapse whitespace
        text = ' '.join(query.split())
        # Remove excessive punctuation
        text = re.sub(r'[?!.]{2,}', '?', text)
        return text.strip()

    def _detect_language(self, text: str) -> str:
        """Detect query language."""
        if not text:
            return "en"

        # Check for Arabic characters
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        if arabic_chars > len(text) * 0.3:
            return "ar"

        try:
            from langdetect import detect
            detected = detect(text)
            return detected if detected in ["ar", "en"] else "en"
        except Exception:
            return "en"

    def _classify_intent(self, query: str, language: str) -> QueryIntent:
        """Classify query intent."""
        query_lower = query.lower()

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent

        return QueryIntent.FACTUAL

    def _extract_keywords(self, query: str, language: str) -> list[str]:
        """Extract significant keywords from query."""
        stopwords = self.ARABIC_STOPWORDS if language == "ar" else self.ENGLISH_STOPWORDS

        # Split into words
        words = re.findall(r'\b\w+\b', query.lower())

        # Filter stopwords and short words
        keywords = [
            w for w in words
            if w not in stopwords and len(w) > 2
        ]

        return keywords[:10]

    def _get_conversation_context(self, conversation_id: str | None) -> list[str]:
        """Get previous conversation turns."""
        if not conversation_id:
            return []

        return self._conversation_cache.get(conversation_id, [])

    def _update_conversation(self, conversation_id: str, query: str) -> None:
        """Update conversation history."""
        if conversation_id not in self._conversation_cache:
            self._conversation_cache[conversation_id] = []

        history = self._conversation_cache[conversation_id]
        history.append(query)

        # Trim to max history
        if len(history) > self.max_history:
            self._conversation_cache[conversation_id] = history[-self.max_history:]


def get_query_understanding() -> QueryUnderstanding:
    """Get query understanding instance."""
    return QueryUnderstanding()
