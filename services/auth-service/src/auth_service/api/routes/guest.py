"""
Guest Routes

Handles guest session creation and management.
"""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from auth_service.adapters.redis import get_redis
from auth_service.core.guest_session import AuthState, GuestSessionStore

router = APIRouter(prefix="/guest", tags=["guest"])


class GuestSessionResponse(BaseModel):
    """Guest session info."""
    guest_id: str
    auth_state: str
    messages_remaining: int
    session_valid: bool


class GuestUpgradeRequest(BaseModel):
    """Request to upgrade guest to user."""
    guest_id: str


class GuestUpgradeResponse(BaseModel):
    """Response after guest upgrade."""
    success: bool
    user_id: str
    messages_migrated: int


@router.post("/session", response_model=GuestSessionResponse)
async def create_guest_session(
    response: Response,
    request: Request,
):
    """
    Create a new guest session.

    Returns guest_id which must be sent with subsequent requests.
    Sets guest_id in HTTP-only cookie.
    """
    redis_client = await get_redis()
    store = GuestSessionStore(redis_client)

    # Check for existing session in cookie
    existing_guest_id = request.cookies.get("guest_id")
    if existing_guest_id:
        session = await store.get_session(existing_guest_id)
        if session and not session.is_expired:
            return GuestSessionResponse(
                guest_id=session.guest_id,
                auth_state=AuthState.GUEST,
                messages_remaining=session.messages_remaining,
                session_valid=True,
            )

    # Create new session
    session = await store.create_session()

    # Set HTTP-only cookie
    response.set_cookie(
        key="guest_id",
        value=session.guest_id,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="lax",
        max_age=24 * 60 * 60,  # 24 hours
    )

    return GuestSessionResponse(
        guest_id=session.guest_id,
        auth_state=AuthState.GUEST,
        messages_remaining=session.messages_remaining,
        session_valid=True,
    )


@router.get("/session", response_model=GuestSessionResponse)
async def get_guest_session(request: Request):
    """Get current guest session status."""
    guest_id = request.cookies.get("guest_id") or request.headers.get("X-Guest-ID")

    if not guest_id:
        raise HTTPException(status_code=404, detail="No guest session found")

    redis_client = await get_redis()
    store = GuestSessionStore(redis_client)
    session = await store.get_session(guest_id)

    if not session:
        raise HTTPException(status_code=404, detail="Guest session expired")

    return GuestSessionResponse(
        guest_id=session.guest_id,
        auth_state=AuthState.GUEST,
        messages_remaining=session.messages_remaining,
        session_valid=not session.is_expired,
    )


@router.delete("/session")
async def delete_guest_session(request: Request, response: Response):
    """Delete current guest session."""
    guest_id = request.cookies.get("guest_id")

    if guest_id:
        redis_client = await get_redis()
        store = GuestSessionStore(redis_client)
        await store.delete_session(guest_id)

    response.delete_cookie("guest_id")
    return {"success": True}


@router.post("/upgrade", response_model=GuestUpgradeResponse)
async def upgrade_guest_to_user(
    request: GuestUpgradeRequest,
    # user_id comes from authenticated request
):
    """
    Upgrade guest session to authenticated user.

    Called after successful authentication to:
    - Link guest_id to user_id
    - Migrate chat history
    - Delete guest session

    This endpoint requires authentication.
    """
    # TODO: Implement after auth middleware check
    # 1. Get user_id from JWT
    # 2. Migrate guest chat history to user
    # 3. Delete guest session

    raise HTTPException(
        status_code=501,
        detail="Guest upgrade requires authentication. Use OAuth first.",
    )
