"""
WaqediAI Common Library

Shared utilities for all services.
"""

__version__ = "0.1.0"

from libs.common.config import BaseSettings, get_settings
from libs.common.errors import (
    WaqediError,
    ValidationError,
    NotFoundError,
    AuthorizationError,
    ServiceUnavailableError,
)
from libs.common.models import TenantContext, RequestContext
from libs.common.utils import generate_id, utc_now

__all__ = [
    "BaseSettings",
    "get_settings",
    "WaqediError",
    "ValidationError",
    "NotFoundError",
    "AuthorizationError",
    "ServiceUnavailableError",
    "TenantContext",
    "RequestContext",
    "generate_id",
    "utc_now",
]
