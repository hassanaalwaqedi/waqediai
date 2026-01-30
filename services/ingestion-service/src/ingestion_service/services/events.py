"""
Event publisher service.

Publishes document lifecycle events to Kafka.
"""

import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from ingestion_service.config import get_settings
from ingestion_service.domain.events import DocumentEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes document events to Kafka.
    
    Uses document ID as partition key for ordering guarantees.
    """

    def __init__(self, producer: AIOKafkaProducer, topic: str):
        self.producer = producer
        self.topic = topic

    async def publish(self, event: DocumentEvent) -> None:
        """
        Publish a document event.
        
        Args:
            event: Document event to publish.
        """
        document_id = event.payload.get("document_id", event.event_id)

        try:
            value = json.dumps(event.to_dict()).encode("utf-8")
            key = document_id.encode("utf-8")

            await self.producer.send_and_wait(
                topic=self.topic,
                value=value,
                key=key,
            )

            logger.info(
                f"Published event {event.event_type}",
                extra={
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "document_id": document_id,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to publish event: {e}",
                extra={
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "error": str(e),
                },
            )
            raise


# Global producer instance
_producer: AIOKafkaProducer | None = None
_publisher: EventPublisher | None = None


async def get_producer() -> AIOKafkaProducer:
    """Get or create Kafka producer."""
    global _producer
    if _producer is None:
        settings = get_settings()
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            acks="all",
            enable_idempotence=True,
        )
        await _producer.start()
    return _producer


async def get_event_publisher() -> EventPublisher:
    """Get or create event publisher."""
    global _publisher
    if _publisher is None:
        settings = get_settings()
        producer = await get_producer()
        _publisher = EventPublisher(producer, settings.kafka_topic_documents)
    return _publisher


async def close_producer() -> None:
    """Close Kafka producer."""
    global _producer, _publisher
    if _producer:
        await _producer.stop()
        _producer = None
        _publisher = None
