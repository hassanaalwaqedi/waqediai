"""
Authentication API routes.

Handles login, token refresh, and logout operations.
"""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth_service.api.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshResponse,
    ProblemDetail,
)
from auth_service.adapters import (
    get_session,
    UserRepository,
    TenantRepository,
    RefreshTokenRepository,
)
from auth_service.core import (
    verify_password,
    hash_password,
    needs_rehash,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    generate_token_family_id,
    decode_access_token,
    TokenExpiredError,
    TokenInvalidError,
)
from auth_service.domain import UserStatus
from auth_service.config import get_settings
from auth_service.services.audit import log_auth_event

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


def _create_problem(status: int, title: str, detail: str, instance: str = "") -> dict:
    """Create RFC 7807 problem details response."""
    return {
        "type": f"urn:waqedi:error:{title.lower().replace(' ', '-')}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ProblemDetail, "description": "Invalid credentials"},
        403: {"model": ProblemDetail, "description": "Account suspended"},
        429: {"model": ProblemDetail, "description": "Rate limit exceeded"},
    },
)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
) -> TokenResponse:
    """
    Authenticate user and issue tokens.
    
    Returns access token in response body and refresh token
    in HttpOnly cookie.
    """
    settings = get_settings()

    async with get_session() as session:
        # Get tenant
        tenant_repo = TenantRepository(session)
        tenant = await tenant_repo.get_by_slug(body.tenant_slug)

        if not tenant:
            # Log failed attempt
            await log_auth_event(
                event_type="auth.login.failure",
                tenant_id=None,
                user_id=None,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                data={"reason": "tenant_not_found", "email": body.email},
            )
            raise HTTPException(
                status_code=401,
                detail=_create_problem(
                    401, "Authentication Failed", "Invalid email or password"
                ),
            )

        if not tenant.is_active:
            raise HTTPException(
                status_code=403,
                detail=_create_problem(
                    403, "Tenant Suspended", "This organization has been suspended"
                ),
            )

        # Get user
        user_repo = UserRepository(session, tenant.id)
        user, password_hash = await user_repo.get_by_email(body.email, tenant.id)

        if not user or not password_hash:
            await log_auth_event(
                event_type="auth.login.failure",
                tenant_id=tenant.id,
                user_id=None,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                data={"reason": "user_not_found", "email": body.email},
            )
            raise HTTPException(
                status_code=401,
                detail=_create_problem(
                    401, "Authentication Failed", "Invalid email or password"
                ),
            )

        # Verify password
        if not verify_password(body.password, password_hash):
            await log_auth_event(
                event_type="auth.login.failure",
                tenant_id=tenant.id,
                user_id=user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                data={"reason": "invalid_password"},
            )
            raise HTTPException(
                status_code=401,
                detail=_create_problem(
                    401, "Authentication Failed", "Invalid email or password"
                ),
            )

        # Check user status
        if user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=403,
                detail=_create_problem(
                    403, "Account Suspended", "Your account has been suspended"
                ),
            )

        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail=_create_problem(
                    403, "Account Not Active", "Your account is not active"
                ),
            )

        # Generate tokens
        roles = [r.name for r in user.roles]
        permissions = list(user.permissions)

        access_token, jti = create_access_token(
            user_id=str(user.id),
            tenant_id=str(tenant.id),
            roles=roles,
            permissions=permissions,
            dept_id=str(user.department_id) if user.department_id else None,
        )

        refresh_token = create_refresh_token()
        family_id = generate_token_family_id()

        # Store refresh token
        token_repo = RefreshTokenRepository(session)
        await token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            family_id=UUID(family_id),
        )

        # Update last login
        await user_repo.update_last_login(user.id)

        # Log success
        await log_auth_event(
            event_type="auth.login.success",
            tenant_id=tenant.id,
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            data={"jti": jti},
        )

        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.environment != "development",
            samesite="strict",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
            path="/api/v1/auth",
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        401: {"model": ProblemDetail, "description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> RefreshResponse:
    """
    Refresh access token using refresh token from cookie.
    
    Implements token rotation - old refresh token is invalidated.
    """
    settings = get_settings()

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail=_create_problem(
                401, "Token Required", "Refresh token is required"
            ),
        )

    async with get_session() as session:
        token_repo = RefreshTokenRepository(session)
        token_hash = hash_refresh_token(refresh_token)
        stored_token = await token_repo.get_by_hash(token_hash)

        if not stored_token:
            # Potential token reuse - revoke entire family
            # In production, we'd look up the family_id from the token
            await log_auth_event(
                event_type="auth.token.reuse_attempt",
                tenant_id=None,
                user_id=None,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                data={"reason": "token_not_found"},
            )
            raise HTTPException(
                status_code=401,
                detail=_create_problem(
                    401, "Invalid Token", "Refresh token is invalid or expired"
                ),
            )

        # Get user
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(stored_token.user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=401,
                detail=_create_problem(
                    401, "Invalid Token", "User not found or inactive"
                ),
            )

        # Revoke old token
        await token_repo.revoke(stored_token.id)

        # Generate new tokens
        roles = [r.name for r in user.roles]
        permissions = list(user.permissions)

        access_token, jti = create_access_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=roles,
            permissions=permissions,
            dept_id=str(user.department_id) if user.department_id else None,
        )

        new_refresh_token = create_refresh_token()

        # Store new refresh token in same family
        await token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            family_id=stored_token.family_id,
        )

        # Log refresh
        await log_auth_event(
            event_type="auth.token.refresh",
            tenant_id=user.tenant_id,
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            data={"family_id": str(stored_token.family_id)},
        )

        # Set new refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=settings.environment != "development",
            samesite="strict",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
            path="/api/v1/auth",
        )

        return RefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )


@router.post(
    "/logout",
    status_code=204,
)
async def logout(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> None:
    """
    Logout user by revoking all refresh tokens.
    
    Clears refresh token cookie.
    """
    user_id = None

    # Try to get user from access token
    if credentials:
        try:
            claims = decode_access_token(credentials.credentials)
            user_id = UUID(claims.sub)
        except (TokenExpiredError, TokenInvalidError):
            pass

    # Revoke refresh token if present
    if refresh_token:
        async with get_session() as session:
            token_repo = RefreshTokenRepository(session)
            token_hash = hash_refresh_token(refresh_token)
            stored_token = await token_repo.get_by_hash(token_hash)

            if stored_token:
                # Revoke entire token family
                await token_repo.revoke_family(stored_token.family_id)
                user_id = stored_token.user_id

                await log_auth_event(
                    event_type="auth.logout",
                    tenant_id=None,
                    user_id=user_id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    data={"family_id": str(stored_token.family_id)},
                )

    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )
