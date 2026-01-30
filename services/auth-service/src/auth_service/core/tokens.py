"""
JWT token generation and validation.

Implements RS256-signed JWTs with proper claim handling
and token lifecycle management.
"""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel

from auth_service.config import get_settings


class TokenClaims(BaseModel):
    """JWT token claims."""

    sub: str  # Subject (user_id)
    tenant_id: str
    dept_id: str | None = None
    roles: list[str]
    permissions: list[str]
    jti: str  # JWT ID (unique identifier)
    exp: datetime
    iat: datetime
    iss: str
    aud: str


class TokenPair(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenError(Exception):
    """Base exception for token errors."""

    pass


class TokenExpiredError(TokenError):
    """Token has expired."""

    pass


class TokenInvalidError(TokenError):
    """Token is invalid or malformed."""

    pass


def create_access_token(
    user_id: str,
    tenant_id: str,
    roles: list[str],
    permissions: list[str],
    dept_id: str | None = None,
) -> tuple[str, str]:
    """
    Create a signed JWT access token.

    Args:
        user_id: Unique user identifier.
        tenant_id: User's tenant identifier.
        roles: List of role names.
        permissions: List of permission strings.
        dept_id: Optional department identifier.

    Returns:
        Tuple of (token_string, jti).
    """
    settings = get_settings()
    now = datetime.now(UTC)
    jti = str(uuid4())

    claims = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "dept_id": dept_id,
        "roles": roles,
        "permissions": permissions,
        "jti": jti,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        "iat": now,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    # For development, use HS256 with a simple secret
    # In production, use RS256 with proper key pair
    if settings.environment == "development":
        token = jwt.encode(
            claims,
            settings.jwt_private_key.get_secret_value(),
            algorithm="HS256",
        )
    else:
        token = jwt.encode(
            claims,
            settings.jwt_private_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

    return token, jti


def decode_access_token(token: str) -> TokenClaims:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string.

    Returns:
        Validated token claims.

    Raises:
        TokenExpiredError: If token has expired.
        TokenInvalidError: If token is invalid.
    """
    settings = get_settings()

    try:
        # For development, use HS256
        if settings.environment == "development":
            payload = jwt.decode(
                token,
                settings.jwt_private_key.get_secret_value(),
                algorithms=["HS256"],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
            )
        else:
            payload = jwt.decode(
                token,
                settings.jwt_public_key.get_secret_value(),
                algorithms=[settings.jwt_algorithm],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
            )

        return TokenClaims(
            sub=payload["sub"],
            tenant_id=payload["tenant_id"],
            dept_id=payload.get("dept_id"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            jti=payload["jti"],
            exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
            iat=datetime.fromtimestamp(payload["iat"], tz=UTC),
            iss=payload["iss"],
            aud=payload["aud"],
        )

    except ExpiredSignatureError as e:
        raise TokenExpiredError("Access token has expired") from e
    except JWTError as e:
        raise TokenInvalidError(f"Invalid access token: {e}") from e


def create_refresh_token() -> str:
    """
    Create an opaque refresh token.

    Uses cryptographically secure random bytes.
    The token should be stored hashed in the database.

    Returns:
        256-bit random token as hex string.
    """
    return secrets.token_hex(32)  # 256 bits


def hash_refresh_token(token: str) -> str:
    """
    Hash a refresh token for storage.

    Uses SHA-256 for fast comparison.
    (Argon2 is overkill for high-entropy tokens)

    Args:
        token: Raw refresh token.

    Returns:
        SHA-256 hash of the token.
    """
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token_family_id() -> str:
    """
    Generate a unique token family ID.

    Used to track token rotation and detect reuse.
    """
    return str(uuid4())
