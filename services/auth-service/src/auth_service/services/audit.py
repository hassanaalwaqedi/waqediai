"""
Audit Service

Logs authentication events for compliance.
"""

import logging
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def log_auth_event(
    session: AsyncSession,
    event_type: str,
    user_id: UUID | None,
    email: str | None,
    request: Request,
    success: bool,
    failure_reason: str | None = None,
    metadata: dict | None = None,
) -> None:
    """
    Log authentication event to audit table.

    Event types:
    - signup
    - signup_failed
    - verify_email
    - verify_email_failed
    - login
    - login_failed
    - oauth_login
    - oauth_failed
    - logout
    - refresh
    """
    try:
        # Extract request info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:500]

        # Get tenant from metadata if available
        tenant_id = metadata.get("tenant_id") if metadata else None

        await session.execute(
            """
            INSERT INTO audit.auth_events
            (event_type, user_id, email, tenant_id, ip_address, user_agent, success, failure_reason, metadata)
            VALUES (:event_type, :user_id, :email, :tenant_id, :ip_address, :user_agent, :success, :failure_reason, :metadata)
            """,
            {
                "event_type": event_type,
                "user_id": str(user_id) if user_id else None,
                "email": email,
                "tenant_id": tenant_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
                "failure_reason": failure_reason,
                "metadata": metadata,
            },
        )
        await session.commit()

        logger.info(
            f"Auth event: {event_type} | user={user_id} | success={success}"
        )

    except Exception as e:
        logger.error(f"Failed to log auth event: {e}")
        # Don't fail the request if audit logging fails


async def log_authorization_decision(
    user_id: UUID | None,
    resource: str,
    action: str,
    allowed: bool,
    reason: str | None = None,
) -> None:
    """
    Log authorization decision for audit trail.

    Args:
        user_id: The user making the request
        resource: Resource being accessed
        action: Action being performed
        allowed: Whether access was granted
        reason: Reason for decision
    """
    try:
        logger.info(
            f"Authorization: user={user_id} | resource={resource} | "
            f"action={action} | allowed={allowed} | reason={reason}"
        )
    except Exception as e:
        logger.error(f"Failed to log authorization decision: {e}")
