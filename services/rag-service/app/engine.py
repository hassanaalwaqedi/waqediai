"""
Advanced RAG Engine orchestrator.

Coordinates the full RAG pipeline from query to answer.
"""

import logging
import time
from uuid import UUID

from app.models import RAGQuery, RAGResponse
from app.modules import (
    get_query_understanding,
    get_retriever,
    get_context_assembler,
    get_prompt_builder,
    get_generator,
    get_audit_logger,
)

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Advanced RAG Engine.
    
    Orchestrates: Query → Retrieve → Rank → Prompt → Generate → Cite
    """

    def __init__(self):
        self.query_understanding = get_query_understanding()
        self.retriever = get_retriever()
        self.context_assembler = get_context_assembler()
        self.prompt_builder = get_prompt_builder()
        self.generator = get_generator()
        self.audit = get_audit_logger()

    async def query(self, query: RAGQuery) -> RAGResponse:
        """
        Process a RAG query through the full pipeline.
        """
        start_time = time.time()

        # Step 1: Query Understanding
        enriched = self.query_understanding.process(query)
        trace_id = self.audit.log_query(query, enriched)

        logger.info(f"[{trace_id}] Processing: lang={enriched.language}, intent={enriched.intent.value}")

        # Step 2: Retrieval
        chunks = self.retriever.retrieve(query, enriched)

        if not chunks:
            return RAGResponse(
                answer=self._get_no_results_message(enriched.language),
                citations=[],
                confidence=0.9,
                answer_type="direct",
                language=enriched.language,
                metadata={"trace_id": trace_id, "reason": "no_chunks_found"},
            )

        # Step 3: Context Assembly
        context = self.context_assembler.assemble(chunks, query.top_k)
        self.audit.log_retrieval(trace_id, query.tenant_id, context)

        logger.info(f"[{trace_id}] Context: {len(context.chunks)} chunks, {context.total_tokens} tokens")

        # Step 4: Prompt Engineering
        prompt = self.prompt_builder.build_prompt(enriched, context)

        # Step 5: Generation
        response = await self.generator.generate(
            prompt, context, enriched.intent, enriched.language
        )

        # Finalize
        latency_ms = int((time.time() - start_time) * 1000)
        self.audit.log_generation(trace_id, query.tenant_id, response, latency_ms)
        self.audit.create_trace(
            trace_id, query.tenant_id, query.query, context, response, latency_ms
        )

        # Add trace_id to metadata
        response.metadata["trace_id"] = trace_id
        response.metadata["latency_ms"] = latency_ms

        logger.info(
            f"[{trace_id}] Complete: {len(response.citations)} citations, "
            f"confidence={response.confidence:.2f}, {latency_ms}ms"
        )

        return response

    def _get_no_results_message(self, language: str) -> str:
        """Get appropriate no-results message."""
        if language == "ar":
            return "لم أتمكن من العثور على معلومات ذات صلة في الوثائق المتاحة."
        return "I could not find relevant information in the available documents."


def get_rag_engine() -> RAGEngine:
    """Get RAG engine instance."""
    return RAGEngine()
