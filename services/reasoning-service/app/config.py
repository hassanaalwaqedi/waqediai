"""
Reasoning Service Configuration.

Environment-based configuration for LLM integration and service settings.
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Reasoning service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="reasoning-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8007)
    debug: bool = Field(default=False)

    # LLM Configuration (Ollama)
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="deepseek-r1:8b")
    ollama_timeout: int = Field(default=120)
    ollama_max_tokens: int = Field(default=2048)
    ollama_temperature: float = Field(default=0.1)

    # Reasoning
    max_context_chunks: int = Field(default=10)
    min_confidence_threshold: float = Field(default=0.3)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
