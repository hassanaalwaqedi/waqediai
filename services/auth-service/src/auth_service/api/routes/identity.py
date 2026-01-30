"""
Auth Routes - Signup, Login, OAuth, Verification

All identity data stored in PostgreSQL.
No external auth providers.
"""

import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.adapters.database import get_session
from auth_service.api.auth_schemas import (
    GoogleOAuthRequest,
    GoogleOAuthResponse,
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserStatus,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from auth_service.config import get_settings
from auth_service.core.google_oauth import get_google_verifier
from auth_service.core.password import hash_password, verify_password
from auth_service.core.tokens import create_access_token, create_refresh_token
from auth_service.services.audit import log_auth_event
from auth_service.services.email_verification import (
    create_verification_token,
    verify_email_token,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


# ============================================================
# SIGNUP (Email)
# ============================================================

@router.post("/signup", response_model=SignupResponse)
async def signup(
    request: SignupRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Register new user with email and password.

    User is created in PENDING status until email verified.
    """
    get_settings()

    # Check if email already exists (prevent enumeration with generic message)
    result = await session.execute(
        "SELECT id FROM auth.users WHERE email = :email",
        {"email": request.email.lower()},
    )
    if result.fetchone():
        # Log but return generic error
        await log_auth_event(
            session, "signup_failed", None, request.email,
            http_request, False, "email_exists"
        )
        raise HTTPException(status_code=400, detail="Unable to create account")

    # Create user
    user_id = uuid4()
    password_hash = hash_password(request.password)

    # Determine tenant (invite or default)
    tenant_id = await _get_or_create_tenant(session, request.invite_token)

    await session.execute(
        """
        INSERT INTO auth.users (id, email, password_hash, display_name, tenant_id, status, email_verified)
        VALUES (:id, :email, :password_hash, :display_name, :tenant_id, 'pending', FALSE)
        """,
        {
            "id": str(user_id),
            "email": request.email.lower(),
            "password_hash": password_hash,
            "display_name": request.display_name,
            "tenant_id": str(tenant_id),
        },
    )

    # Assign default role
    await _assign_default_role(session, user_id, tenant_id)

    # Create verification token
    await create_verification_token(session, user_id)

    # TODO: Send verification email
    # await send_verification_email(request.email, token)

    await log_auth_event(
        session, "signup", user_id, request.email,
        http_request, True, None, {"tenant_id": str(tenant_id)}
    )

    logger.info(f"User {user_id} created, verification required")

    return SignupResponse(
        user_id=user_id,
        email=request.email,
        status=UserStatus.PENDING,
        verification_required=True,
        message="Account created. Please verify your email.",
    )


# ============================================================
# EMAIL VERIFICATION
# ============================================================

@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Verify email with token."""
    user_id = await verify_email_token(session, request.token)

    if not user_id:
        await log_auth_event(
            session, "verify_email_failed", None, None,
            http_request, False, "invalid_token"
        )
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    await log_auth_event(
        session, "verify_email", user_id, None,
        http_request, True, None
    )

    return VerifyEmailResponse(
        verified=True,
        message="Email verified successfully. You can now log in.",
    )


# ============================================================
# LOGIN (Email)
# ============================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Login with email and password.

    Blocked if email not verified.
    """
    settings = get_settings()

    # Find user
    result = await session.execute(
        """
        SELECT id, password_hash, email_verified, status, tenant_id
        FROM auth.users WHERE email = :email
        """,
        {"email": request.email.lower()},
    )
    row = result.fetchone()

    # Generic error for security
    auth_error = HTTPException(status_code=401, detail="Invalid credentials")

    if not row:
        await log_auth_event(
            session, "login_failed", None, request.email,
            http_request, False, "user_not_found"
        )
        raise auth_error

    user_id, password_hash, email_verified, status, tenant_id = row

    # Verify password
    if not verify_password(request.password, password_hash):
        await log_auth_event(
            session, "login_failed", UUID(user_id), request.email,
            http_request, False, "wrong_password"
        )
        raise auth_error

    # Check email verified
    if not email_verified:
        await log_auth_event(
            session, "login_failed", UUID(user_id), request.email,
            http_request, False, "email_not_verified"
        )
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in",
        )

    # Check status
    if status == "suspended":
        await log_auth_event(
            session, "login_failed", UUID(user_id), request.email,
            http_request, False, "account_suspended"
        )
        raise HTTPException(status_code=403, detail="Account suspended")

    # Get roles
    roles = await _get_user_roles(session, UUID(user_id))

    # Create tokens
    access_token = create_access_token(
        user_id=user_id,
        email=request.email,
        tenant_id=tenant_id,
        roles=roles,
    )

    refresh_token = create_refresh_token(user_id=user_id)

    # Set refresh token as http-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.environment != "development",
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
    )

    await log_auth_event(
        session, "login", UUID(user_id), request.email,
        http_request, True, None, {"tenant_id": tenant_id}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


# ============================================================
# GOOGLE OAUTH
# ============================================================

@router.post("/oauth/google", response_model=GoogleOAuthResponse)
async def google_oauth(
    request: GoogleOAuthRequest,
    response: Response,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Login/signup with Google.

    - Validates Google ID token
    - Creates user if new
    - Email auto-verified (trusted by Google)
    - OAuth tokens NOT stored
    """
    settings = get_settings()

    # Verify Google ID token
    verifier = get_google_verifier(settings.google_client_id)
    google_user = await verifier.verify_id_token(request.id_token)

    if not google_user:
        await log_auth_event(
            session, "oauth_failed", None, None,
            http_request, False, "invalid_google_token"
        )
        raise HTTPException(status_code=401, detail="Invalid Google credentials")

    if not google_user.email_verified:
        raise HTTPException(status_code=400, detail="Google email not verified")

    # Check if OAuth account exists
    result = await session.execute(
        """
        SELECT user_id FROM auth.oauth_accounts
        WHERE provider = 'google' AND provider_user_id = :provider_id
        """,
        {"provider_id": google_user.provider_user_id},
    )
    oauth_row = result.fetchone()

    is_new_user = False

    if oauth_row:
        # Existing OAuth account
        user_id = UUID(oauth_row[0])
    else:
        # Check if email exists
        result = await session.execute(
            "SELECT id FROM auth.users WHERE email = :email",
            {"email": google_user.email.lower()},
        )
        user_row = result.fetchone()

        if user_row:
            # Link OAuth to existing user
            user_id = UUID(user_row[0])
        else:
            # Create new user
            is_new_user = True
            user_id = uuid4()
            tenant_id = await _get_or_create_tenant(session, request.invite_token)

            await session.execute(
                """
                INSERT INTO auth.users (id, email, display_name, tenant_id, status, email_verified)
                VALUES (:id, :email, :display_name, :tenant_id, 'active', TRUE)
                """,
                {
                    "id": str(user_id),
                    "email": google_user.email.lower(),
                    "display_name": google_user.name or google_user.email.split("@")[0],
                    "tenant_id": str(tenant_id),
                },
            )

            await _assign_default_role(session, user_id, tenant_id)

        # Create OAuth account link
        await session.execute(
            """
            INSERT INTO auth.oauth_accounts (user_id, provider, provider_user_id, provider_email)
            VALUES (:user_id, 'google', :provider_id, :email)
            """,
            {
                "user_id": str(user_id),
                "provider_id": google_user.provider_user_id,
                "email": google_user.email,
            },
        )

    await session.commit()

    # Get user info
    result = await session.execute(
        "SELECT email, tenant_id FROM auth.users WHERE id = :id",
        {"id": str(user_id)},
    )
    user_row = result.fetchone()
    email, tenant_id = user_row

    # Get roles
    roles = await _get_user_roles(session, user_id)

    # Create tokens
    access_token = create_access_token(
        user_id=str(user_id),
        email=email,
        tenant_id=tenant_id,
        roles=roles,
    )

    refresh_token = create_refresh_token(user_id=str(user_id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.environment != "development",
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )

    await log_auth_event(
        session, "oauth_login", user_id, email,
        http_request, True, None, {"provider": "google", "is_new": is_new_user}
    )

    return GoogleOAuthResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        is_new_user=is_new_user,
        user_id=user_id,
        email=email,
    )


# ============================================================
# HELPERS
# ============================================================

async def _get_or_create_tenant(
    session: AsyncSession,
    invite_token: str | None,
) -> UUID:
    """Get tenant from invite or create default."""
    # TODO: Implement invite token logic
    # For now, use or create default tenant

    result = await session.execute(
        "SELECT id FROM auth.tenants WHERE slug = 'default' LIMIT 1"
    )
    row = result.fetchone()

    if row:
        return UUID(row[0])

    # Create default tenant
    tenant_id = uuid4()
    await session.execute(
        """
        INSERT INTO auth.tenants (id, name, slug)
        VALUES (:id, 'Default', 'default')
        """,
        {"id": str(tenant_id)},
    )
    return tenant_id


async def _assign_default_role(
    session: AsyncSession,
    user_id: UUID,
    tenant_id: UUID,
) -> None:
    """Assign default 'user' role."""
    # Get or create user role
    result = await session.execute(
        "SELECT id FROM auth.roles WHERE name = 'user' LIMIT 1"
    )
    row = result.fetchone()

    if row:
        role_id = row[0]
    else:
        role_id = str(uuid4())
        await session.execute(
            "INSERT INTO auth.roles (id, name) VALUES (:id, 'user')",
            {"id": role_id},
        )

    # Assign role
    await session.execute(
        """
        INSERT INTO auth.user_roles (user_id, role_id)
        VALUES (:user_id, :role_id)
        ON CONFLICT DO NOTHING
        """,
        {"user_id": str(user_id), "role_id": role_id},
    )


async def _get_user_roles(session: AsyncSession, user_id: UUID) -> list[str]:
    """Get user's roles."""
    result = await session.execute(
        """
        SELECT r.name FROM auth.roles r
        JOIN auth.user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = :user_id
        """,
        {"user_id": str(user_id)},
    )
    return [row[0] for row in result.fetchall()]
