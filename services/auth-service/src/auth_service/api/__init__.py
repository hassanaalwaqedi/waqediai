"""API package."""

from auth_service.api.routes import auth_router, users_router

__all__ = [
    "auth_router",
    "users_router",
]
