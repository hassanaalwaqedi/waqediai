"""
User Management API routes.

Handles user CRUD operations with tenant-scoped access.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from auth_service.adapters import UserRepository, get_session
from auth_service.api.schemas import (
    ProblemDetail,
    RoleAssignRequest,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from auth_service.core import hash_password
from auth_service.core.tokens import TokenClaims
from auth_service.domain import UserStatus
from auth_service.middleware.auth import get_current_user, require_permission

router = APIRouter(prefix="/users", tags=["Users"])


def _user_to_response(user) -> UserResponse:
    """Convert domain user to response schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        status=user.status.value,
        profile=user.profile,
        department_id=user.department_id,
        roles=[r.name for r in user.roles],
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.get(
    "",
    response_model=UserListResponse,
    dependencies=[Depends(require_permission("users", "read", "tenant"))],
)
async def list_users(
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, pattern="^(pending|active|suspended)$"),
    department_id: UUID | None = None,
) -> UserListResponse:
    """
    List users in the current tenant.

    Requires 'users:read:tenant' permission.
    """
    async with get_session() as session:
        user_repo = UserRepository(session, UUID(current_user.tenant_id))

        user_status = UserStatus(status) if status else None
        offset = (page - 1) * limit

        users, total = await user_repo.list_users(
            limit=limit,
            offset=offset,
            status=user_status,
            department_id=department_id,
        )

        return UserListResponse(
            items=[_user_to_response(u) for u in users],
            total=total,
            page=page,
            limit=limit,
        )


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    dependencies=[Depends(require_permission("users", "create", "tenant"))],
)
async def create_user(
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
    body: UserCreateRequest,
) -> UserResponse:
    """
    Create a new user in the current tenant.

    Requires 'users:create:tenant' permission.
    """
    async with get_session() as session:
        tenant_id = UUID(current_user.tenant_id)
        user_repo = UserRepository(session, tenant_id)

        # Check if email already exists
        existing_user, _ = await user_repo.get_by_email(body.email, tenant_id)
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail={
                    "type": "urn:waqedi:error:user-exists",
                    "title": "User Exists",
                    "status": 409,
                    "detail": f"User with email {body.email} already exists",
                },
            )

        # Create user
        password_hash = hash_password(body.password)
        user = await user_repo.create(
            email=body.email,
            password_hash=password_hash,
            tenant_id=tenant_id,
            department_id=body.department_id,
            profile={
                "first_name": body.profile.first_name,
                "last_name": body.profile.last_name,
                "display_name": body.profile.display_name,
                "avatar_url": body.profile.avatar_url,
                "timezone": body.profile.timezone,
                "locale": body.profile.locale,
            },
            status=UserStatus.PENDING,
        )

        # TODO: Assign roles
        # TODO: Send activation email

        return _user_to_response(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ProblemDetail}},
)
async def get_user(
    user_id: UUID,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
) -> UserResponse:
    """
    Get user by ID.

    Users can view their own profile.
    Tenant admins can view any user in the tenant.
    """
    async with get_session() as session:
        user_repo = UserRepository(session, UUID(current_user.tenant_id))
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "type": "urn:waqedi:error:user-not-found",
                    "title": "User Not Found",
                    "status": 404,
                    "detail": f"User {user_id} not found",
                },
            )

        # Check access: own user or has permission
        if str(user_id) != current_user.sub:
            # TODO: Check for users:read:tenant permission
            pass

        return _user_to_response(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ProblemDetail}},
)
async def update_user(
    user_id: UUID,
    body: UserUpdateRequest,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
) -> UserResponse:
    """
    Update user.

    Users can update their own profile.
    Admins can update status and department.
    """
    async with get_session() as session:
        user_repo = UserRepository(session, UUID(current_user.tenant_id))
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "type": "urn:waqedi:error:user-not-found",
                    "title": "User Not Found",
                    "status": 404,
                    "detail": f"User {user_id} not found",
                },
            )

        # Update status if provided (admin only)
        if body.status:
            # TODO: Check admin permission
            await user_repo.update_status(user_id, UserStatus(body.status))

        # Re-fetch updated user
        user = await user_repo.get_by_id(user_id)
        return _user_to_response(user)


@router.put(
    "/{user_id}/roles",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users", "manage", "tenant"))],
    responses={404: {"model": ProblemDetail}},
)
async def assign_roles(
    user_id: UUID,
    body: RoleAssignRequest,
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
) -> UserResponse:
    """
    Assign roles to a user.

    Requires 'users:manage:tenant' permission.
    """
    async with get_session() as session:
        user_repo = UserRepository(session, UUID(current_user.tenant_id))
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "type": "urn:waqedi:error:user-not-found",
                    "title": "User Not Found",
                    "status": 404,
                    "detail": f"User {user_id} not found",
                },
            )

        # TODO: Implement role assignment
        # 1. Validate all roles exist
        # 2. Clear existing role assignments
        # 3. Assign new roles

        return _user_to_response(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[TokenClaims, Depends(get_current_user)],
) -> UserResponse:
    """Get the current authenticated user's profile."""
    async with get_session() as session:
        user_repo = UserRepository(session, UUID(current_user.tenant_id))
        user = await user_repo.get_by_id(UUID(current_user.sub))

        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "type": "urn:waqedi:error:user-not-found",
                    "title": "User Not Found",
                    "status": 404,
                    "detail": "Current user not found",
                },
            )

        return _user_to_response(user)
