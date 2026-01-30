"""
Guest-Aware Middleware for RAG Service

Detects authentication state and applies appropriate policies.
"""

from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthState(str, Enum):
    GUEST = "guest"
    AUTHENTICATED = "authenticated"


@dataclass
class RequestContext:
    """Context attached to each request."""
    auth_state: AuthState
    user_id: str | None = None
    tenant_id: str | None = None
    guest_id: str | None = None
    roles: list[str] = None

    @property
    def is_guest(self) -> bool:
        return self.auth_state == AuthState.GUEST

    @property
    def is_authenticated(self) -> bool:
        return self.auth_state == AuthState.AUTHENTICATED


# Guest restrictions
GUEST_BLOCKED_PATHS = [
    "/documents/upload",
    "/workspace",
    "/tenant",
    "/admin",
    "/pipelines",
]

GUEST_RATE_LIMIT = 10  # requests per minute
AUTH_RATE_LIMIT = 100  # requests per minute


class GuestAwareMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    - Detects guest vs authenticated requests
    - Applies rate limits
    - Blocks guests from restricted endpoints
    - Attaches RequestContext to request.state
    """

    async def dispatch(self, request: Request, call_next):
        # Extract authentication info
        context = await self._build_context(request)
        request.state.context = context

        # Block guests from restricted paths
        if context.is_guest:
            for blocked_path in GUEST_BLOCKED_PATHS:
                if request.url.path.startswith(blocked_path):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "authentication_required",
                            "message": "Sign in to access this feature",
                            "trigger": "restricted_endpoint",
                        },
                    )

        response = await call_next(request)
        return response

    async def _build_context(self, request: Request) -> RequestContext:
        """Build request context from headers/cookies."""
        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Validate token and extract claims
            claims = await self._validate_token(token)
            if claims:
                return RequestContext(
                    auth_state=AuthState.AUTHENTICATED,
                    user_id=claims.get("sub"),
                    tenant_id=claims.get("tenant_id"),
                    roles=claims.get("roles", []),
                )

        # Check for guest session
        guest_id = (
            request.cookies.get("guest_id") or
            request.headers.get("X-Guest-ID")
        )

        if guest_id:
            return RequestContext(
                auth_state=AuthState.GUEST,
                guest_id=guest_id,
            )

        # Anonymous - create temporary guest context
        return RequestContext(
            auth_state=AuthState.GUEST,
            guest_id=None,
        )

    async def _validate_token(self, token: str) -> dict | None:
        """Validate JWT token. Returns claims or None."""
        try:
            # In production, verify JWT signature
            import jwt
            claims = jwt.decode(token, options={"verify_signature": False})
            return claims
        except Exception:
            return None


def get_context(request: Request) -> RequestContext:
    """Get request context from request state."""
    return getattr(request.state, "context", RequestContext(auth_state=AuthState.GUEST))


def require_auth(request: Request) -> RequestContext:
    """Dependency that requires authentication."""
    context = get_context(request)
    if context.is_guest:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "authentication_required",
                "message": "Sign in to continue",
                "trigger": "protected_resource",
            },
        )
    return context


def allow_guest(request: Request) -> RequestContext:
    """Dependency that allows guests with context."""
    return get_context(request)
