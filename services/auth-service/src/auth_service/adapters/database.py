"""
Database adapter for the Auth Service.

Uses SQLAlchemy async with PostgreSQL for all identity data.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from auth_service.config import get_settings
from auth_service.domain.models import (
    Department,
    Permission,
    PermissionScope,
    RefreshToken,
    Role,
    RoleScope,
    Tenant,
    TenantTier,
    User,
    UserProfile,
    UserStatus,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


# Association tables
user_roles_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("scope_type", String(20)),
    Column("scope_id", PGUUID(as_uuid=True)),
    Column("granted_at", DateTime(timezone=True), default=datetime.utcnow),
    Column("granted_by", PGUUID(as_uuid=True), ForeignKey("users.id")),
    schema="auth",
)

role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", PGUUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    schema="auth",
)


class TenantModel(Base):
    """Tenant database model."""

    __tablename__ = "tenants"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="standard")
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("UserModel", back_populates="tenant")
    departments = relationship("DepartmentModel", back_populates="tenant")

    def to_domain(self) -> Tenant:
        return Tenant(
            id=self.id,
            slug=self.slug,
            name=self.name,
            tier=TenantTier(self.tier),
            is_active=self.is_active,
            settings=self.settings or {},
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class DepartmentModel(Base):
    """Department database model."""

    __tablename__ = "departments"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("auth.tenants.id"), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("auth.departments.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="departments")

    def to_domain(self) -> Department:
        return Department(
            id=self.id,
            tenant_id=self.tenant_id,
            name=self.name,
            parent_id=self.parent_id,
            created_at=self.created_at,
        )


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("auth.tenants.id"), nullable=False)
    department_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("auth.departments.id"))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    profile: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="users")
    roles = relationship("RoleModel", secondary=user_roles_table, back_populates="users")

    def to_domain(self, include_roles: bool = False) -> User:
        profile_data = self.profile or {}
        user = User(
            id=self.id,
            tenant_id=self.tenant_id,
            department_id=self.department_id,
            email=self.email,
            status=UserStatus(self.status),
            profile=UserProfile(
                first_name=profile_data.get("first_name"),
                last_name=profile_data.get("last_name"),
                display_name=profile_data.get("display_name"),
                avatar_url=profile_data.get("avatar_url"),
                timezone=profile_data.get("timezone", "UTC"),
                locale=profile_data.get("locale", "en"),
            ),
            last_login=self.last_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
        if include_roles and self.roles:
            user.roles = [r.to_domain() for r in self.roles]
        return user


class RoleModel(Base):
    """Role database model."""

    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("auth.tenants.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="tenant")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    users = relationship("UserModel", secondary=user_roles_table, back_populates="roles")
    permissions = relationship("PermissionModel", secondary=role_permissions_table, back_populates="roles")

    def to_domain(self) -> Role:
        role = Role(
            id=self.id,
            name=self.name,
            scope=RoleScope(self.scope),
            is_system=self.is_system,
            tenant_id=self.tenant_id,
            description=self.description,
            created_at=self.created_at,
        )
        if self.permissions:
            role.permissions = [p.to_domain() for p in self.permissions]
        return role


class PermissionModel(Base):
    """Permission database model."""

    __tablename__ = "permissions"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    roles = relationship("RoleModel", secondary=role_permissions_table, back_populates="permissions")

    def to_domain(self) -> Permission:
        return Permission(
            id=self.id,
            resource=self.resource,
            action=self.action,
            scope=PermissionScope(self.scope),
        )


class RefreshTokenModel(Base):
    """Refresh token database model."""

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    family_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def to_domain(self) -> RefreshToken:
        return RefreshToken(
            id=self.id,
            user_id=self.user_id,
            token_hash=self.token_hash,
            family_id=self.family_id,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
        )


# Database connection
_engine = None
_session_factory = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url.get_secret_value(),
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
