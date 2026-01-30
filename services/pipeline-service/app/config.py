"""
Pipeline Service Configuration.

Central configuration for the ingestion-to-embedding pipeline.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pipeline service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="pipeline-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8008)
    debug: bool = Field(default=False)

    # Qdrant
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection_prefix: str = Field(default="waqedi")

    # Embedding
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)
    embedding_version: str = Field(default="v1.0")

    # Chunking
    default_chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=50)
    min_chunk_size: int = Field(default=100)

    # OCR
    ocr_languages: list[str] = Field(default_factory=lambda: ["en", "ar"])
    ocr_confidence_threshold: float = Field(default=0.5)

    # Processing
    max_document_size_mb: int = Field(default=50)
    supported_extensions: list[str] = Field(
        default_factory=lambda: [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx"]
    )

    # Temp storage
    temp_dir: str = Field(default="/tmp/pipeline")

    # Logging
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
