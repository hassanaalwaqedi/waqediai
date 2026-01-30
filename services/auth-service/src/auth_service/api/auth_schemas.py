"""
Auth Schemas for Signup, Login, OAuth
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class OAuthProvider(str, Enum):
    GOOGLE = "google"


# Signup
class SignupRequest(BaseModel):
    """Email signup request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=2, max_length=100)
    invite_token: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v


class SignupResponse(BaseModel):
    """Signup response."""
    user_id: UUID
    email: str
    status: UserStatus
    verification_required: bool
    message: str


# Email Verification
class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str


class VerifyEmailResponse(BaseModel):
    """Email verification response."""
    verified: bool
    message: str


# Login
class LoginRequest(BaseModel):
    """Email login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


# Google OAuth
class GoogleOAuthRequest(BaseModel):
    """Google OAuth request with ID token."""
    id_token: str
    invite_token: Optional[str] = None


class GoogleOAuthResponse(BaseModel):
    """Google OAuth response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    is_new_user: bool
    user_id: UUID
    email: str


# User Info
class UserResponse(BaseModel):
    """User info response."""
    id: UUID
    email: str
    display_name: str
    tenant_id: UUID
    roles: list[str]
    email_verified: bool
    status: UserStatus
    created_at: datetime


# Error
class AuthError(BaseModel):
    """Auth error response (non-leaky)."""
    type: str
    title: str
    status: int
    detail: str
