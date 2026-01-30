"""
Chunking Service Configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Chunking service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="chunking-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8004)
    debug: bool = Field(default=False)

    # Chunking Configuration
    default_strategy: str = Field(default="semantic")
    default_chunk_size: int = Field(default=512)
    max_chunk_size: int = Field(default=1024)
    overlap_tokens: int = Field(default=50)
    min_chunk_size: int = Field(default=100)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://waqedi:waqedi_dev@localhost:5432/waqedi"
    )

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_documents: str = Field(default="documents")
    kafka_consumer_group: str = Field(default="chunking-service")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
