"""API routes package."""

from auth_service.api.routes.auth import router as auth_router
from auth_service.api.routes.users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
]
