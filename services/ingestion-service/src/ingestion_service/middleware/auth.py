"""
Authentication middleware for Ingestion Service.

Validates JWT tokens and extracts tenant context.
"""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from ingestion_service.config import get_settings

# Make auto_error=False to allow bypassing auth in dev mode
security = HTTPBearer(auto_error=False)

# Default development tenant/user IDs
DEV_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@dataclass
class TenantContext:
    """Extracted tenant and user context from JWT."""

    tenant_id: UUID
    user_id: UUID
    department_id: UUID | None = None
    roles: list[str] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = []


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TenantContext:
    """
    Extract and validate JWT from Authorization header.

    In development mode, allows unauthenticated requests with default context.
    Returns tenant context for use in route handlers.
    """
    settings = get_settings()

    # Development mode bypass - allow unauthenticated requests
    if settings.environment == "development" and credentials is None:
        return TenantContext(
            tenant_id=DEV_TENANT_ID,
            user_id=DEV_USER_ID,
            department_id=None,
            roles=["admin"],
        )

    # Require credentials in production
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "urn:waqedi:error:missing-token",
                "title": "Missing Token",
                "status": 401,
                "detail": "Authorization header required",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # For development, use HS256
        if settings.environment == "development":
            payload = jwt.decode(
                credentials.credentials,
                settings.jwt_public_key.get_secret_value(),
                algorithms=["HS256"],
                audience="waqedi-api",
            )
        else:
            payload = jwt.decode(
                credentials.credentials,
                settings.jwt_public_key.get_secret_value(),
                algorithms=["RS256"],
                audience="waqedi-api",
            )

        return TenantContext(
            tenant_id=UUID(payload["tenant_id"]),
            user_id=UUID(payload["sub"]),
            department_id=UUID(payload["dept_id"]) if payload.get("dept_id") else None,
            roles=payload.get("roles", []),
        )

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "urn:waqedi:error:token-expired",
                "title": "Token Expired",
                "status": 401,
                "detail": "Access token has expired",
            },
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "urn:waqedi:error:invalid-token",
                "title": "Invalid Token",
                "status": 401,
                "detail": str(e),
            },
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

