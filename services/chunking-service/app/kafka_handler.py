"""
Kafka event handler for chunking pipeline.

Consumes document.extracted events and publishes document.chunked events.
"""

import asyncio
import json
import logging
from uuid import UUID, uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.config import get_settings
from app.chunker import get_chunker
from app.schemas import ChunkingStrategy

logger = logging.getLogger(__name__)


class ChunkingKafkaHandler:
    """
    Handles Kafka events for the chunking pipeline.
    
    Subscribes to document.extracted events and publishes document.chunked events.
    """

    def __init__(self):
        self.settings = get_settings()
        self._consumer: AIOKafkaConsumer | None = None
        self._producer: AIOKafkaProducer | None = None
        self._running = False
        self._chunker = None

    async def start(self) -> None:
        """Start the Kafka consumer and producer."""
        logger.info("Starting chunking Kafka handler...")
        
        self._consumer = AIOKafkaConsumer(
            self.settings.kafka_topic_documents,
            bootstrap_servers=self.settings.kafka_bootstrap_servers,
            group_id=self.settings.kafka_consumer_group,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        
        await self._consumer.start()
        await self._producer.start()
        
        self._chunker = get_chunker()
        self._running = True
        
        logger.info(f"Chunking consumer started, subscribed to: {self.settings.kafka_topic_documents}")

    async def stop(self) -> None:
        """Stop the Kafka consumer and producer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        logger.info("Chunking Kafka handler stopped")

    async def run(self) -> None:
        """Main consumer loop."""
        if not self._consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        logger.info("Chunking consumer running, waiting for events...")
        
        async for message in self._consumer:
            if not self._running:
                break
                
            try:
                await self._handle_message(message.value)
            except Exception as e:
                logger.exception(f"Error processing message: {e}")

    async def _handle_message(self, event: dict) -> None:
        """Process a single event message."""
        event_type = event.get("event_type")
        
        if event_type != "document.extracted":
            return  # Only process extracted documents
        
        payload = event.get("payload", {})
        tenant_id = event.get("tenant_id")
        correlation_id = event.get("correlation_id")
        document_id = payload.get("document_id")
        text = payload.get("text", "")
        
        if not text:
            logger.warning(f"No text to chunk for document {document_id}")
            return
        
        logger.info(
            f"Processing document.extracted event: "
            f"document_id={document_id}, text_length={len(text)}"
        )
        
        try:
            # Get chunking strategy from config
            strategy_name = self.settings.default_strategy.upper()
            strategy = ChunkingStrategy(strategy_name)
            
            # Perform chunking
            chunk_results = self._chunker.chunk(
                text=text,
                strategy=strategy,
                chunk_size=self.settings.default_chunk_size,
                overlap=self.settings.overlap_tokens,
            )
            
            # Convert to output format
            chunks = []
            for i, result in enumerate(chunk_results):
                chunk_id = f"chunk_{document_id}_{i:04d}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "index": i,
                    "text": result.text,
                    "token_count": result.token_count,
                    "page_number": result.page_number,
                    "language": payload.get("language", "en"),
                })
            
            # Publish chunked event
            chunked_event = {
                "event_type": "document.chunked",
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "payload": {
                    "document_id": document_id,
                    "chunk_count": len(chunks),
                    "strategy": strategy.value,
                    "chunks": chunks,
                    "language": payload.get("language", "en"),
                },
            }
            
            await self._producer.send_and_wait(
                self.settings.kafka_topic_documents,
                value=chunked_event,
            )
            
            logger.info(
                f"Published document.chunked: document_id={document_id}, "
                f"chunk_count={len(chunks)}"
            )
            
        except Exception as e:
            logger.exception(f"Chunking failed for document {document_id}: {e}")
            
            # Publish failure event
            failure_event = {
                "event_type": "document.chunking_failed",
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "payload": {
                    "document_id": document_id,
                    "error": str(e),
                },
            }
            await self._producer.send_and_wait(
                self.settings.kafka_topic_documents,
                value=failure_event,
            )


# Singleton
_kafka_handler: ChunkingKafkaHandler | None = None


def get_kafka_handler() -> ChunkingKafkaHandler:
    """Get or create Kafka handler instance."""
    global _kafka_handler
    if _kafka_handler is None:
        _kafka_handler = ChunkingKafkaHandler()
    return _kafka_handler
