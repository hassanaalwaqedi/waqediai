"""
Prompt engineering module.

Constructs structured prompts for LLM with citation enforcement.
"""

import logging

from app.models import ContextWindow, EnrichedQuery, QueryIntent, RankedChunk

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    LLM prompt construction.

    Builds citation-enforced prompts for Arabic and English.
    """

    SYSTEM_PROMPT_EN = """You are a precise enterprise AI assistant for WaqediAI.

CRITICAL RULES:
1. ONLY use information from the PROVIDED CONTEXT below
2. NEVER invent, assume, or infer information not in the context
3. For EVERY claim, include a citation like [chunk_id]
4. If the context doesn't contain the answer, say: "I cannot find this information in the available documents."
5. Be concise and professional

Your response MUST include citations. Without citations, your answer is invalid."""

    SYSTEM_PROMPT_AR = """أنت مساعد ذكاء اصطناعي دقيق لمنصة WaqediAI.

قواعد صارمة:
1. استخدم فقط المعلومات من السياق المقدم أدناه
2. لا تخترع أو تفترض معلومات غير موجودة في السياق
3. لكل ادعاء، أضف مرجعاً مثل [chunk_id]
4. إذا لم يحتوي السياق على الإجابة، قل: "لا أجد هذه المعلومات في الوثائق المتاحة"
5. كن موجزاً ومحترفاً

يجب أن تتضمن إجابتك مراجع. بدون مراجع، إجابتك غير صالحة."""

    INTENT_INSTRUCTIONS = {
        QueryIntent.FACTUAL: "Provide a direct factual answer.",
        QueryIntent.SUMMARY: "Provide a concise summary of the relevant information.",
        QueryIntent.COMPARISON: "Compare the relevant items point by point.",
        QueryIntent.PROCEDURAL: "List the steps or process clearly.",
        QueryIntent.CLARIFICATION: "Explain the concept clearly and simply.",
    }

    def build_prompt(
        self,
        query: EnrichedQuery,
        context: ContextWindow,
    ) -> dict:
        """
        Build complete prompt for LLM.

        Returns dict with 'system' and 'user' messages.
        """
        # Select language-appropriate system prompt
        system_prompt = (
            self.SYSTEM_PROMPT_AR if query.language == "ar" else self.SYSTEM_PROMPT_EN
        )

        # Build context block
        context_block = self._build_context_block(context.chunks)

        # Build user prompt
        user_prompt = self._build_user_prompt(query, context_block)

        logger.info(
            f"Built prompt: lang={query.language}, intent={query.intent.value}, "
            f"context_chunks={len(context.chunks)}"
        )

        return {
            "system": system_prompt,
            "user": user_prompt,
        }

    def _build_context_block(self, chunks: list[RankedChunk]) -> str:
        """Build formatted context from chunks."""
        if not chunks:
            return "No relevant context available."

        blocks = []
        for chunk in chunks:
            block = f"""--- CHUNK [{chunk.chunk_id}] ---
Document: {chunk.document_id}
Language: {chunk.language}

{chunk.text}
--- END CHUNK ---"""
            blocks.append(block)

        return "\n\n".join(blocks)

    def _build_user_prompt(self, query: EnrichedQuery, context_block: str) -> str:
        """Build the user message with context and question."""
        intent_instruction = self.INTENT_INSTRUCTIONS.get(
            query.intent, self.INTENT_INSTRUCTIONS[QueryIntent.FACTUAL]
        )

        # Include conversation context if present
        conversation_section = ""
        if query.conversation_context:
            prev_turns = "\n".join(f"- {turn}" for turn in query.conversation_context[-3:])
            conversation_section = f"""
## Previous Questions
{prev_turns}

"""

        prompt = f"""## CONTEXT (Use ONLY this information)

{context_block}

{conversation_section}## INSTRUCTIONS
{intent_instruction}
Cite every claim using [chunk_id] format.

## USER QUESTION
{query.normalized_query}

## YOUR RESPONSE (with citations)"""

        return prompt


def get_prompt_builder() -> PromptBuilder:
    """Get prompt builder instance."""
    return PromptBuilder()
