"""
Repository layer for identity data access.

Provides tenant-scoped data access with proper isolation.
"""

from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_service.adapters.database import (
    UserModel,
    TenantModel,
    RoleModel,
    PermissionModel,
    RefreshTokenModel,
    DepartmentModel,
    user_roles_table,
)
from auth_service.domain.models import (
    User,
    Tenant,
    Role,
    RefreshToken,
    UserStatus,
)
from auth_service.config import get_settings


class UserRepository:
    """Repository for user data access."""

    def __init__(self, session: AsyncSession, tenant_id: UUID | None = None):
        self.session = session
        self.tenant_id = tenant_id

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID within tenant scope."""
        query = (
            select(UserModel)
            .options(selectinload(UserModel.roles).selectinload(RoleModel.permissions))
            .where(UserModel.id == user_id)
        )
        if self.tenant_id:
            query = query.where(UserModel.tenant_id == self.tenant_id)

        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain(include_roles=True) if user_model else None

    async def get_by_email(self, email: str, tenant_id: UUID | None = None) -> tuple[User | None, str | None]:
        """
        Get user by email within tenant scope.
        
        Returns tuple of (User, password_hash) for authentication.
        Password hash is only returned for this specific use case.
        """
        t_id = tenant_id or self.tenant_id
        if not t_id:
            return None, None

        query = (
            select(UserModel)
            .options(selectinload(UserModel.roles).selectinload(RoleModel.permissions))
            .where(
                and_(
                    UserModel.tenant_id == t_id,
                    UserModel.email == email,
                    UserModel.status != UserStatus.DELETED.value,
                )
            )
        )

        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()
        if user_model:
            return user_model.to_domain(include_roles=True), user_model.password_hash
        return None, None

    async def create(
        self,
        email: str,
        password_hash: str,
        tenant_id: UUID,
        profile: dict | None = None,
        department_id: UUID | None = None,
        status: UserStatus = UserStatus.PENDING,
    ) -> User:
        """Create a new user."""
        user_model = UserModel(
            id=uuid4(),
            tenant_id=tenant_id,
            department_id=department_id,
            email=email,
            password_hash=password_hash,
            status=status.value,
            profile=profile or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(user_model)
        await self.session.flush()
        return user_model.to_domain()

    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp."""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )

    async def update_status(self, user_id: UUID, status: UserStatus) -> None:
        """Update user status."""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(status=status.value, updated_at=datetime.now(timezone.utc))
        )

    async def list_users(
        self,
        limit: int = 20,
        offset: int = 0,
        status: UserStatus | None = None,
        department_id: UUID | None = None,
    ) -> tuple[Sequence[User], int]:
        """List users with pagination."""
        if not self.tenant_id:
            return [], 0

        conditions = [
            UserModel.tenant_id == self.tenant_id,
            UserModel.status != UserStatus.DELETED.value,
        ]
        if status:
            conditions.append(UserModel.status == status.value)
        if department_id:
            conditions.append(UserModel.department_id == department_id)

        # Count
        count_query = select(UserModel.id).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = len(count_result.all())

        # Fetch
        query = (
            select(UserModel)
            .where(and_(*conditions))
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        users = [u.to_domain() for u in result.scalars()]

        return users, total


class TenantRepository:
    """Repository for tenant data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        """Get tenant by ID."""
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.id == tenant_id)
        )
        tenant_model = result.scalar_one_or_none()
        return tenant_model.to_domain() if tenant_model else None

    async def get_by_slug(self, slug: str) -> Tenant | None:
        """Get tenant by slug."""
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.slug == slug)
        )
        tenant_model = result.scalar_one_or_none()
        return tenant_model.to_domain() if tenant_model else None

    async def create(
        self,
        slug: str,
        name: str,
        tier: str = "standard",
    ) -> Tenant:
        """Create a new tenant."""
        tenant_model = TenantModel(
            id=uuid4(),
            slug=slug,
            name=name,
            tier=tier,
            is_active=True,
            settings={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(tenant_model)
        await self.session.flush()
        return tenant_model.to_domain()


class RefreshTokenRepository:
    """Repository for refresh token management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        token_hash: str,
        family_id: UUID,
    ) -> RefreshToken:
        """Store a new refresh token."""
        settings = get_settings()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

        token_model = RefreshTokenModel(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(token_model)
        await self.session.flush()
        return token_model.to_domain()

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Get refresh token by hash."""
        result = await self.session.execute(
            select(RefreshTokenModel).where(
                and_(
                    RefreshTokenModel.token_hash == token_hash,
                    RefreshTokenModel.revoked_at.is_(None),
                    RefreshTokenModel.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        token_model = result.scalar_one_or_none()
        return token_model.to_domain() if token_model else None

    async def revoke(self, token_id: UUID) -> None:
        """Revoke a specific token."""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_family(self, family_id: UUID) -> None:
        """Revoke all tokens in a family (security breach response)."""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(
                and_(
                    RefreshTokenModel.family_id == family_id,
                    RefreshTokenModel.revoked_at.is_(None),
                )
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_user_tokens(self, user_id: UUID) -> None:
        """Revoke all tokens for a user (logout all sessions)."""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.revoked_at.is_(None),
                )
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )


class RoleRepository:
    """Repository for role data access."""

    def __init__(self, session: AsyncSession, tenant_id: UUID | None = None):
        self.session = session
        self.tenant_id = tenant_id

    async def get_by_name(self, name: str) -> Role | None:
        """Get role by name (tenant-specific or system role)."""
        conditions = [RoleModel.name == name]

        if self.tenant_id:
            # Match tenant-specific OR system roles
            conditions.append(
                or_(
                    RoleModel.tenant_id == self.tenant_id,
                    RoleModel.is_system == True,
                )
            )
        else:
            # Only system roles
            conditions.append(RoleModel.is_system == True)

        query = (
            select(RoleModel)
            .options(selectinload(RoleModel.permissions))
            .where(and_(*conditions))
        )
        result = await self.session.execute(query)
        role_model = result.scalar_one_or_none()
        return role_model.to_domain() if role_model else None

    async def list_roles(self) -> Sequence[Role]:
        """List all available roles for the tenant."""
        conditions = []
        if self.tenant_id:
            conditions.append(
                or_(
                    RoleModel.tenant_id == self.tenant_id,
                    RoleModel.is_system == True,
                )
            )
        else:
            conditions.append(RoleModel.is_system == True)

        query = (
            select(RoleModel)
            .options(selectinload(RoleModel.permissions))
            .where(and_(*conditions) if conditions else True)
        )
        result = await self.session.execute(query)
        return [r.to_domain() for r in result.scalars()]
