"""
Email Verification Service

Handles email verification token generation and validation.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Verification token settings
TOKEN_LENGTH = 64
TOKEN_EXPIRY_HOURS = 24


async def create_verification_token(
    session: AsyncSession,
    user_id: UUID,
) -> str:
    """
    Create email verification token.
    
    Returns the token (to send via email).
    """
    token = secrets.token_urlsafe(TOKEN_LENGTH)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)

    await session.execute(
        """
        INSERT INTO auth.email_verifications (user_id, token, expires_at)
        VALUES (:user_id, :token, :expires_at)
        """,
        {"user_id": str(user_id), "token": token, "expires_at": expires_at},
    )
    await session.commit()

    logger.info(f"Created verification token for user {user_id}")
    return token


async def verify_email_token(
    session: AsyncSession,
    token: str,
) -> Optional[UUID]:
    """
    Verify email token and mark as verified.
    
    Returns user_id if valid, None if invalid/expired.
    """
    result = await session.execute(
        """
        SELECT user_id, expires_at, verified_at
        FROM auth.email_verifications
        WHERE token = :token
        """,
        {"token": token},
    )
    row = result.fetchone()

    if not row:
        logger.warning("Invalid verification token")
        return None

    user_id, expires_at, verified_at = row

    # Already verified
    if verified_at is not None:
        logger.info(f"Token already verified for user {user_id}")
        return UUID(user_id)

    # Expired
    if expires_at < datetime.now(timezone.utc):
        logger.warning(f"Expired verification token for user {user_id}")
        return None

    # Mark as verified
    await session.execute(
        """
        UPDATE auth.email_verifications
        SET verified_at = :now
        WHERE token = :token
        """,
        {"token": token, "now": datetime.now(timezone.utc)},
    )

    # Update user email_verified status
    await session.execute(
        """
        UPDATE auth.users
        SET email_verified = TRUE, status = 'active'
        WHERE id = :user_id
        """,
        {"user_id": user_id},
    )

    await session.commit()
    logger.info(f"Email verified for user {user_id}")

    return UUID(user_id)


async def invalidate_existing_tokens(
    session: AsyncSession,
    user_id: UUID,
) -> None:
    """Invalidate any existing verification tokens for user."""
    await session.execute(
        """
        DELETE FROM auth.email_verifications
        WHERE user_id = :user_id AND verified_at IS NULL
        """,
        {"user_id": str(user_id)},
    )
    await session.commit()
