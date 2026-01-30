"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field


class ExampleRequest(BaseModel):
    """Example request schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Name")
    value: int = Field(..., ge=0, description="Numeric value")


class ExampleResponse(BaseModel):
    """Example response schema."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")
    value: int = Field(..., description="Numeric value")
    created_at: str = Field(..., description="Creation timestamp")
