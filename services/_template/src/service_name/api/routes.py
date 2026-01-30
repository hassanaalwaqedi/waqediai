"""API routes for the service."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/example", tags=["Example"])
async def example_endpoint() -> dict:
    """
    Example endpoint.

    Replace this with your actual API endpoints.
    """
    return {"message": "Hello from the service template!"}
