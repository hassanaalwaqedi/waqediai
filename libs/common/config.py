"""
Configuration management for WaqediAI services.

Provides a base settings class with common configuration patterns
for all services, ensuring consistency across the platform.
"""

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings, SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    """
    Base settings class for all WaqediAI services.

    Subclass this in each service to add service-specific settings:

        class QueryOrchestratorSettings(BaseSettings):
            rag_engine_url: str = Field(default="http://rag-engine:8000")

    Settings are loaded from environment variables with the prefix
    defined in env_prefix.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="unknown-service")
    service_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")

    # Server Configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)
    debug: bool = Field(default=False)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Observability
    otlp_endpoint: str | None = Field(default=None)
    metrics_enabled: bool = Field(default=True)
    tracing_enabled: bool = Field(default=True)

    # Security
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    api_key_header: str = Field(default="X-API-Key")

    # Health Check
    health_check_path: str = Field(default="/health")
    ready_check_path: str = Field(default="/ready")

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache
def get_settings(**kwargs: Any) -> BaseSettings:
    """
    Get cached settings instance.

    Override with specific settings class in service:

        from libs.common import get_settings
        settings = get_settings(_settings_class=MyServiceSettings)
    """
    settings_class = kwargs.pop("_settings_class", BaseSettings)
    return settings_class(**kwargs)
