"""
Core domain models used across WaqediAI services.

These models represent cross-cutting concerns like tenant context,
request tracing, and user identity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TenantContext:
    """
    Represents the tenant context for multi-tenant isolation.

    Extracted from authenticated requests and propagated through
    all service calls to ensure data isolation.
    """

    tenant_id: str
    tenant_name: str | None = None
    tier: str = "standard"
    features: frozenset[str] = field(default_factory=frozenset)

    def has_feature(self, feature: str) -> bool:
        """Check if tenant has a specific feature enabled."""
        return feature in self.features


@dataclass(frozen=True)
class UserIdentity:
    """
    Represents an authenticated user.

    Extracted from JWT claims after authentication.
    """

    user_id: str
    email: str
    roles: frozenset[str] = field(default_factory=frozenset)
    permissions: frozenset[str] = field(default_factory=frozenset)

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions


@dataclass
class RequestContext:
    """
    Request context propagated through the system.

    Contains all cross-cutting concerns for a single request,
    including tracing, tenant isolation, and user identity.
    """

    # Tracing
    request_id: str
    trace_id: str
    span_id: str

    # Tenant and User
    tenant: TenantContext
    user: UserIdentity | None = None

    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_headers(self) -> dict[str, str]:
        """Convert context to HTTP headers for propagation."""
        return {
            "X-Request-ID": self.request_id,
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": self.span_id,
            "X-Tenant-ID": self.tenant.tenant_id,
        }


@dataclass
class PaginationParams:
    """Standard pagination parameters."""

    cursor: str | None = None
    limit: int = 20
    order: str = "desc"

    def __post_init__(self) -> None:
        if self.limit < 1:
            self.limit = 1
        elif self.limit > 100:
            self.limit = 100


@dataclass
class PaginatedResult:
    """Standard paginated result wrapper."""

    items: list[Any]
    next_cursor: str | None = None
    has_more: bool = False
    total_count: int | None = None
