"""
Kafka event consumer for extraction pipeline.

Consumes document.uploaded events and triggers extraction processing.
"""

import asyncio
import json
import logging
from uuid import UUID
from dataclasses import dataclass
from typing import Callable, Awaitable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import aioboto3

from extraction_service.config import get_settings
from extraction_service.services.worker import get_extraction_worker

logger = logging.getLogger(__name__)


@dataclass
class DocumentUploadedEvent:
    """Document uploaded event payload."""
    document_id: str
    tenant_id: str
    correlation_id: str
    file_category: str
    content_type: str
    size_bytes: int
    storage_bucket: str
    storage_key: str


class ExtractionKafkaHandler:
    """
    Handles Kafka events for the extraction pipeline.
    
    Subscribes to document.uploaded events and publishes document.extracted events.
    """

    def __init__(self):
        self.settings = get_settings()
        self._consumer: AIOKafkaConsumer | None = None
        self._producer: AIOKafkaProducer | None = None
        self._running = False
        self._worker = None

    async def start(self) -> None:
        """Start the Kafka consumer and producer."""
        logger.info("Starting extraction Kafka handler...")
        
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
        
        self._worker = get_extraction_worker()
        self._running = True
        
        logger.info(f"Subscribed to topic: {self.settings.kafka_topic_documents}")

    async def stop(self) -> None:
        """Stop the Kafka consumer and producer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        logger.info("Extraction Kafka handler stopped")

    async def run(self) -> None:
        """Main consumer loop."""
        if not self._consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        logger.info("Extraction consumer running, waiting for events...")
        
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
        
        if event_type != "document.uploaded":
            return  # Ignore other event types
        
        payload = event.get("payload", {})
        tenant_id = event.get("tenant_id")
        correlation_id = event.get("correlation_id")
        
        logger.info(
            f"Processing document.uploaded event: "
            f"document_id={payload.get('document_id')}, "
            f"tenant_id={tenant_id}"
        )
        
        try:
            # Fetch file from MinIO
            file_bytes = await self._fetch_from_storage(
                payload.get("storage_bucket", self.settings.storage_bucket),
                payload.get("storage_key")
            )
            
            # Process extraction
            result = await self._worker.process(
                document_id=payload["document_id"],
                tenant_id=UUID(tenant_id),
                file_category=payload["file_category"],
                content_type=payload["content_type"],
                file_bytes=file_bytes,
            )
            
            # Publish extracted event
            extracted_event = {
                "event_type": "document.extracted",
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "timestamp": result.created_at.isoformat(),
                "payload": {
                    "document_id": payload["document_id"],
                    "extraction_id": result.id,
                    "extraction_type": result.extraction_type.value,
                    "text": result.result_data.get("full_text", ""),
                    "page_count": result.result_data.get("total_pages", 1),
                    "language": result.detected_language,
                    "confidence": result.mean_confidence,
                    "processing_time_ms": result.processing_time_ms,
                },
            }
            
            await self._producer.send_and_wait(
                self.settings.kafka_topic_documents,
                value=extracted_event,
            )
            
            logger.info(
                f"Published document.extracted: document_id={payload['document_id']}, "
                f"text_length={len(result.result_data.get('full_text', ''))}"
            )
            
        except Exception as e:
            logger.exception(f"Extraction failed for document {payload.get('document_id')}: {e}")
            
            # Publish failure event
            failure_event = {
                "event_type": "document.extraction_failed",
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "payload": {
                    "document_id": payload.get("document_id"),
                    "error": str(e),
                },
            }
            await self._producer.send_and_wait(
                self.settings.kafka_topic_documents,
                value=failure_event,
            )

    async def _fetch_from_storage(self, bucket: str, key: str) -> bytes:
        """Fetch file from MinIO/S3."""
        settings = self.settings
        session = aioboto3.Session()
        
        async with session.client(
            "s3",
            endpoint_url=settings.storage_endpoint,
            aws_access_key_id=settings.storage_access_key.get_secret_value(),
            aws_secret_access_key=settings.storage_secret_key.get_secret_value(),
        ) as client:
            response = await client.get_object(Bucket=bucket, Key=key)
            body = await response["Body"].read()
            return body


# Singleton
_kafka_handler: ExtractionKafkaHandler | None = None


def get_kafka_handler() -> ExtractionKafkaHandler:
    """Get or create Kafka handler instance."""
    global _kafka_handler
    if _kafka_handler is None:
        _kafka_handler = ExtractionKafkaHandler()
    return _kafka_handler
