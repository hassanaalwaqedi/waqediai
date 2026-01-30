"""
Advanced RAG Engine Configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """RAG engine configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="rag-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8009)
    debug: bool = Field(default=False)

    # Qdrant
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection: str = Field(default="waqedi_knowledge")

    # Embedding
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)

    # LLM (Ollama with Qwen - fully offline, no external API)
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen3:8b")
    ollama_timeout: int = Field(default=120)
    ollama_temperature: float = Field(default=0.1)
    ollama_max_tokens: int = Field(default=2048)

    # Retrieval
    default_top_k: int = Field(default=5)
    max_top_k: int = Field(default=20)
    min_relevance_score: float = Field(default=0.3)
    rerank_enabled: bool = Field(default=True)

    # Context
    max_context_tokens: int = Field(default=3000)
    max_chunks_per_query: int = Field(default=10)
    deduplication_threshold: float = Field(default=0.95)

    # Conversation
    max_conversation_history: int = Field(default=5)

    # Logging
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
