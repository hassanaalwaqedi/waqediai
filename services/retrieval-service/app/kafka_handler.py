"""
Kafka event handler for retrieval/indexing pipeline.

Consumes document.chunked events and indexes vectors in Qdrant.
"""

import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.config import get_settings
from app.qdrant_client import get_qdrant_service

logger = logging.getLogger(__name__)


class RetrievalKafkaHandler:
    """
    Handles Kafka events for the retrieval/indexing pipeline.
    
    Subscribes to document.chunked events and indexes in Qdrant.
    """

    def __init__(self):
        self.settings = get_settings()
        self._consumer: AIOKafkaConsumer | None = None
        self._producer: AIOKafkaProducer | None = None
        self._running = False
        self._qdrant = None

    async def start(self) -> None:
        """Start the Kafka consumer and producer."""
        logger.info("Starting retrieval Kafka handler...")
        
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
        
        self._qdrant = get_qdrant_service()
        self._running = True
        
        logger.info(f"Retrieval consumer started, subscribed to: {self.settings.kafka_topic_documents}")

    async def stop(self) -> None:
        """Stop the Kafka consumer and producer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        logger.info("Retrieval Kafka handler stopped")

    async def run(self) -> None:
        """Main consumer loop."""
        if not self._consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        logger.info("Retrieval consumer running, waiting for events...")
        
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
        
        if event_type != "document.chunked":
            return  # Only process chunked documents
        
        payload = event.get("payload", {})
        tenant_id = event.get("tenant_id")
        correlation_id = event.get("correlation_id")
        document_id = payload.get("document_id")
        chunks = payload.get("chunks", [])
        
        if not chunks:
            logger.warning(f"No chunks to index for document {document_id}")
            return
        
        logger.info(
            f"Processing document.chunked event: "
            f"document_id={document_id}, chunk_count={len(chunks)}"
        )
        
        try:
            # Index chunks in Qdrant
            indexed_count = self._qdrant.index_chunks(
                tenant_id=UUID(tenant_id),
                document_id=document_id,
                chunks=chunks,
            )
            
            # Publish indexed event
            indexed_event = {
                "event_type": "document.indexed",
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "payload": {
                    "document_id": document_id,
                    "vectors_indexed": indexed_count,
                    "collection": f"{self.settings.qdrant_collection_prefix}_vectors",
                },
            }
            
            await self._producer.send_and_wait(
                self.settings.kafka_topic_documents,
                value=indexed_event,
            )
            
            logger.info(
                f"Published document.indexed: document_id={document_id}, "
                f"vectors={indexed_count}"
            )
            
        except Exception as e:
            logger.exception(f"Indexing failed for document {document_id}: {e}")
            
            # Publish failure event
            failure_event = {
                "event_type": "document.indexing_failed",
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
_kafka_handler: RetrievalKafkaHandler | None = None


def get_kafka_handler() -> RetrievalKafkaHandler:
    """Get or create Kafka handler instance."""
    global _kafka_handler
    if _kafka_handler is None:
        _kafka_handler = RetrievalKafkaHandler()
    return _kafka_handler
