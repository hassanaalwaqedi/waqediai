"""
Domain models for the Identity system.

These are the core business entities, independent of
database representation or API schemas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class UserStatus(str, Enum):
    """User account status."""

    PENDING = "pending"  # Awaiting email verification
    ACTIVE = "active"  # Normal active user
    SUSPENDED = "suspended"  # Temporarily disabled
    DELETED = "deleted"  # Soft-deleted


class TenantTier(str, Enum):
    """Tenant subscription tier."""

    FREE = "free"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"


class RoleScope(str, Enum):
    """Scope at which a role operates."""

    SYSTEM = "system"  # Platform-wide (super admin)
    TENANT = "tenant"  # Tenant-wide
    DEPARTMENT = "department"  # Department-specific


class PermissionScope(str, Enum):
    """Scope of a permission."""

    OWN = "own"  # User's own resources
    DEPARTMENT = "department"  # Department resources
    TENANT = "tenant"  # All tenant resources
    SYSTEM = "system"  # Cross-tenant (admin only)


@dataclass(frozen=True)
class Permission:
    """
    A single permission grant.
    
    Format: resource:action:scope
    Example: documents:read:department
    """

    id: UUID
    resource: str
    action: str
    scope: PermissionScope

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}:{self.scope.value}"

    @classmethod
    def from_string(cls, perm_str: str, id: UUID) -> "Permission":
        """Parse permission from string format."""
        parts = perm_str.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid permission format: {perm_str}")
        return cls(
            id=id,
            resource=parts[0],
            action=parts[1],
            scope=PermissionScope(parts[2]),
        )


@dataclass
class Role:
    """
    A role that can be assigned to users.
    
    System roles cannot be modified.
    Tenant-specific roles can be customized.
    """

    id: UUID
    name: str
    scope: RoleScope
    is_system: bool
    tenant_id: UUID | None  # None for system roles
    permissions: list[Permission] = field(default_factory=list)
    description: str | None = None
    created_at: datetime | None = None


@dataclass
class Department:
    """
    An organizational unit within a tenant.
    
    Departments can be nested (parent_id).
    """

    id: UUID
    tenant_id: UUID
    name: str
    parent_id: UUID | None = None
    created_at: datetime | None = None


@dataclass
class Tenant:
    """
    A tenant (organization) in the system.
    
    All users and data belong to exactly one tenant.
    """

    id: UUID
    slug: str
    name: str
    tier: TenantTier
    is_active: bool = True
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class UserProfile:
    """User profile information."""

    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    timezone: str = "UTC"
    locale: str = "en"


@dataclass
class User:
    """
    A user in the system.
    
    Users belong to exactly one tenant.
    They may optionally belong to a department.
    """

    id: UUID
    tenant_id: UUID
    email: str
    status: UserStatus
    profile: UserProfile
    department_id: UUID | None = None
    roles: list[Role] = field(default_factory=list)
    last_login: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        """Check if user can authenticate."""
        return self.status == UserStatus.ACTIVE

    @property
    def permissions(self) -> set[str]:
        """Get all permissions from assigned roles."""
        perms = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(str(perm))
        return perms

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, resource: str, action: str, scope: str) -> bool:
        """Check if user has a specific permission."""
        perm_str = f"{resource}:{action}:{scope}"
        return perm_str in self.permissions


@dataclass
class RefreshToken:
    """
    A refresh token for obtaining new access tokens.
    
    Tokens are tracked by family to detect reuse attacks.
    """

    id: UUID
    user_id: UUID
    token_hash: str
    family_id: UUID
    expires_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime | None = None

    @property
    def is_valid(self) -> bool:
        """Check if token is not expired and not revoked."""
        if self.revoked_at is not None:
            return False
        return datetime.utcnow() < self.expires_at
