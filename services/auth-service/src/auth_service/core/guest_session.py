"""
Guest Session Model

Handles anonymous guest access with progressive authentication.
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

import redis.asyncio as redis


class AuthState(str, Enum):
    GUEST = "guest"
    AUTHENTICATED = "authenticated"


@dataclass
class GuestSession:
    """Represents an anonymous guest session."""
    guest_id: str
    created_at: datetime
    last_active: datetime
    message_count: int = 0
    rate_limit_remaining: int = 10
    
    # Configurable limits
    MAX_MESSAGES_PER_SESSION: int = 20
    MAX_SESSION_DURATION_HOURS: int = 24
    RATE_LIMIT_WINDOW_MINUTES: int = 1
    RATE_LIMIT_MAX_REQUESTS: int = 10

    @classmethod
    def create(cls) -> "GuestSession":
        """Create a new guest session."""
        now = datetime.now(timezone.utc)
        return cls(
            guest_id=f"guest_{uuid4().hex[:12]}",
            created_at=now,
            last_active=now,
        )

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        expiry = self.created_at + timedelta(hours=self.MAX_SESSION_DURATION_HOURS)
        return datetime.now(timezone.utc) > expiry

    @property
    def can_send_message(self) -> bool:
        """Check if guest can send more messages."""
        return self.message_count < self.MAX_MESSAGES_PER_SESSION

    @property
    def messages_remaining(self) -> int:
        """Get remaining messages."""
        return max(0, self.MAX_MESSAGES_PER_SESSION - self.message_count)

    def increment_message_count(self) -> None:
        """Increment message count."""
        self.message_count += 1
        self.last_active = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "guest_id": self.guest_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "message_count": self.message_count,
            "messages_remaining": self.messages_remaining,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GuestSession":
        """Deserialize from dict."""
        return cls(
            guest_id=data["guest_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"]),
            message_count=data.get("message_count", 0),
        )


class GuestSessionStore:
    """
    Redis-backed guest session storage.
    
    Guest sessions are stored in Redis with TTL.
    They are NOT stored in the database.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "guest:"
        self.ttl_seconds = GuestSession.MAX_SESSION_DURATION_HOURS * 3600

    async def create_session(self) -> GuestSession:
        """Create and store a new guest session."""
        session = GuestSession.create()
        await self._save(session)
        return session

    async def get_session(self, guest_id: str) -> Optional[GuestSession]:
        """Get existing guest session."""
        key = f"{self.prefix}{guest_id}"
        data = await self.redis.hgetall(key)
        
        if not data:
            return None

        session = GuestSession(
            guest_id=guest_id,
            created_at=datetime.fromisoformat(data[b"created_at"].decode()),
            last_active=datetime.fromisoformat(data[b"last_active"].decode()),
            message_count=int(data.get(b"message_count", 0)),
        )

        if session.is_expired:
            await self.delete_session(guest_id)
            return None

        return session

    async def update_session(self, session: GuestSession) -> None:
        """Update existing session."""
        await self._save(session)

    async def delete_session(self, guest_id: str) -> None:
        """Delete guest session."""
        key = f"{self.prefix}{guest_id}"
        await self.redis.delete(key)

    async def _save(self, session: GuestSession) -> None:
        """Save session to Redis."""
        key = f"{self.prefix}{session.guest_id}"
        await self.redis.hset(key, mapping={
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
            "message_count": str(session.message_count),
        })
        await self.redis.expire(key, self.ttl_seconds)

    async def check_rate_limit(self, guest_id: str) -> tuple[bool, int]:
        """
        Check and update rate limit for guest.
        
        Returns (allowed, remaining).
        """
        key = f"{self.prefix}rate:{guest_id}"
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, 60)  # 1 minute window
        
        limit = GuestSession.RATE_LIMIT_MAX_REQUESTS
        allowed = current <= limit
        remaining = max(0, limit - current)
        
        return allowed, remaining
