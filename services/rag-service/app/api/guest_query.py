"""
Guest Query Handler for RAG Service

Handles AI queries from guest users with restrictions.
"""


from app.middleware.guest_aware import (
    RequestContext,
    allow_guest,
)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class GuestQueryRequest(BaseModel):
    """Query request that works for both guests and authenticated users."""
    query: str
    top_k: int = 3  # Limited for guests
    guest_id: str | None = None


class GuestQueryResponse(BaseModel):
    """Response with auth state awareness."""
    answer: str
    citations: list[dict]
    confidence: float
    auth_state: str
    messages_remaining: int | None = None
    upgrade_prompt: str | None = None


# Guest limits
GUEST_TOP_K_LIMIT = 3
GUEST_DEMO_KNOWLEDGE_ONLY = True


@router.post("/query/public", response_model=GuestQueryResponse)
async def public_query(
    request: GuestQueryRequest,
    context: RequestContext = Depends(allow_guest),
):
    """
    Public query endpoint that supports both guests and authenticated users.

    Guests:
    - Limited to demo/public knowledge
    - Restricted top_k
    - Shows upgrade prompts after limit

    Authenticated:
    - Full access to tenant knowledge
    - Higher limits
    """
    # Apply guest restrictions
    if context.is_guest:
        min(request.top_k, GUEST_TOP_K_LIMIT)

        # TODO: Query only public/demo knowledge base
        # tenant_filter = "demo"

        # Check message limit (from Redis)
        messages_remaining = await _check_guest_limit(request.guest_id)

        if messages_remaining <= 0:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "guest_limit_exceeded",
                    "message": "Sign in to continue chatting",
                    "trigger": "message_limit",
                },
            )
    else:
        messages_remaining = None

    # TODO: Execute RAG query
    # This is a placeholder - integrate with actual RAG pipeline
    answer = f"[Demo Response] Processing: {request.query[:50]}..."
    citations = []
    confidence = 0.0

    # Build response
    response = GuestQueryResponse(
        answer=answer,
        citations=citations,
        confidence=confidence,
        auth_state=context.auth_state.value,
        messages_remaining=messages_remaining,
    )

    # Add upgrade prompt if guest is running low
    if context.is_guest and messages_remaining and messages_remaining <= 3:
        response.upgrade_prompt = (
            "Sign in to save your conversation and access more features"
        )

    return response


async def _check_guest_limit(guest_id: str | None) -> int:
    """Check remaining messages for guest."""
    if not guest_id:
        return 5  # Anonymous gets fewer

    # TODO: Check Redis for actual count
    # For now return default
    return 15


# Progressive auth triggers
AUTH_TRIGGERS = {
    "save_conversation": "Sign in to save this conversation",
    "upload_document": "Sign in to upload documents",
    "access_knowledge": "Sign in to access your organization's knowledge",
    "create_workspace": "Sign in to create a workspace",
    "message_limit": "Sign in to continue chatting",
}


def get_auth_trigger_message(trigger: str) -> str:
    """Get user-friendly message for auth trigger."""
    return AUTH_TRIGGERS.get(trigger, "Sign in to continue")
