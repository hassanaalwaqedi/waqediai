"""
Pydantic schemas for Auth API requests and responses.

These schemas define the API contract and handle validation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# =============================================================================
# Authentication Schemas
# =============================================================================


class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    tenant_slug: str = Field(..., min_length=1, max_length=63, description="Tenant identifier")


class TokenResponse(BaseModel):
    """Access token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshResponse(BaseModel):
    """Token refresh response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


# =============================================================================
# User Schemas
# =============================================================================


class UserProfile(BaseModel):
    """User profile data."""

    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    timezone: str = "UTC"
    locale: str = "en"


class UserCreateRequest(BaseModel):
    """Create user request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=12, description="Password (min 12 chars)")
    department_id: UUID | None = Field(None, description="Department ID")
    profile: UserProfile = Field(default_factory=UserProfile)
    roles: list[str] = Field(default_factory=list, description="Role names to assign")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Basic password validation (NIST 800-63B compliant)."""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        # Note: We avoid complexity rules per NIST guidance
        # Instead, we check against breach databases in production
        return v


class UserUpdateRequest(BaseModel):
    """Update user request."""

    department_id: UUID | None = None
    profile: UserProfile | None = None
    status: str | None = Field(None, pattern="^(active|suspended)$")


class UserResponse(BaseModel):
    """User response (public view)."""

    id: UUID
    email: str
    status: str
    profile: UserProfile
    department_id: UUID | None
    roles: list[str] = []
    created_at: datetime
    last_login: datetime | None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UserResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# Role Schemas
# =============================================================================


class RoleResponse(BaseModel):
    """Role response."""

    id: UUID
    name: str
    scope: str
    is_system: bool
    permissions: list[str]
    description: str | None

    class Config:
        from_attributes = True


class RoleAssignRequest(BaseModel):
    """Assign roles to user."""

    roles: list[str] = Field(..., min_length=1, description="Role names to assign")


# =============================================================================
# Error Schemas (RFC 7807)
# =============================================================================


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details response."""

    type: str = Field(..., description="Error type URI")
    title: str = Field(..., description="Short error title")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Detailed error message")
    instance: str | None = Field(None, description="Request path")


# =============================================================================
# Tenant Schemas
# =============================================================================


class TenantResponse(BaseModel):
    """Tenant response (public view)."""

    id: UUID
    slug: str
    name: str
    tier: str
    is_active: bool

    class Config:
        from_attributes = True
