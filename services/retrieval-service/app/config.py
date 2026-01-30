"""
Retrieval Service Configuration.

Environment-based configuration for Qdrant and embedding settings.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Retrieval service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="retrieval-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8005)
    debug: bool = Field(default=False)

    # Qdrant Configuration
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection_prefix: str = Field(default="waqedi")
    qdrant_use_shared_collection: bool = Field(default=True)

    # Embedding Configuration
    embedding_provider: str = Field(default="sentence-transformers")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)
    embedding_batch_size: int = Field(default=32)

    # Search Configuration
    default_top_k: int = Field(default=5)
    max_top_k: int = Field(default=20)
    min_score_threshold: float = Field(default=0.3)

    # Chunk Validation
    max_chunk_length: int = Field(default=8192)
    max_chunks_per_request: int = Field(default=100)

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_documents: str = Field(default="documents")
    kafka_consumer_group: str = Field(default="retrieval-service")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
