"""
Authentication and authorization middleware.

Provides FastAPI dependencies for extracting and validating
JWT tokens, and enforcing permissions.
"""

from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth_service.core.tokens import (
    decode_access_token,
    TokenClaims,
    TokenExpiredError,
    TokenInvalidError,
)
from auth_service.services.audit import log_authorization_decision

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenClaims:
    """
    Extract and validate JWT from Authorization header.
    
    Returns the token claims if valid.
    
    Raises:
        HTTPException 401: If token is missing, expired, or invalid.
    """
    try:
        claims = decode_access_token(credentials.credentials)
        return claims
    except TokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "urn:waqedi:error:token-expired",
                "title": "Token Expired",
                "status": 401,
                "detail": "Access token has expired",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "urn:waqedi:error:invalid-token",
                "title": "Invalid Token",
                "status": 401,
                "detail": str(e),
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(resource: str, action: str, scope: str) -> Callable:
    """
    Create a dependency that checks for a specific permission.
    
    Usage:
        @router.get("/", dependencies=[Depends(require_permission("users", "read", "tenant"))])
        async def list_users(): ...
    
    Args:
        resource: Resource type (e.g., "users", "documents")
        action: Action type (e.g., "read", "create", "delete")
        scope: Permission scope (e.g., "own", "department", "tenant")
    
    Returns:
        FastAPI dependency that checks the permission.
    """
    required_permission = f"{resource}:{action}:{scope}"

    async def check_permission(
        request: Request,
        current_user: Annotated[TokenClaims, Depends(get_current_user)],
    ) -> None:
        # Super admin bypasses all checks
        if "super_admin" in current_user.roles:
            return

        # Tenant admin has all tenant-level permissions
        if "tenant_admin" in current_user.roles and scope in ("tenant", "department", "own"):
            return

        # Check explicit permission
        if required_permission in current_user.permissions:
            return

        # Check for higher-scope permission (tenant covers department and own)
        if scope == "own":
            if f"{resource}:{action}:department" in current_user.permissions:
                return
            if f"{resource}:{action}:tenant" in current_user.permissions:
                return
        elif scope == "department":
            if f"{resource}:{action}:tenant" in current_user.permissions:
                return

        # Log denial
        await log_authorization_decision(
            user_id=UUID(current_user.sub),
            tenant_id=UUID(current_user.tenant_id),
            resource=resource,
            action=action,
            decision=False,
            reason=f"Missing permission: {required_permission}",
        )

        raise HTTPException(
            status_code=403,
            detail={
                "type": "urn:waqedi:error:forbidden",
                "title": "Forbidden",
                "status": 403,
                "detail": f"Missing required permission: {required_permission}",
            },
        )

    return check_permission


class TenantContext:
    """Tenant context extracted from JWT claims."""

    def __init__(self, tenant_id: str, tenant_slug: str = ""):
        self.tenant_id = tenant_id
        self.tenant_slug = tenant_slug


async def get_tenant_context(
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
) -> TenantContext:
    """
    Extract tenant context from JWT.
    
    This dependency can be used to get the tenant context
    without requiring the full user claims.
    """
    return TenantContext(
        tenant_id=current_user.tenant_id,
        tenant_slug="",  # Would be populated from claims if included
    )
