from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResearchCreate(BaseModel):
    """Request body for creating a research session."""

    question: str = Field(
        min_length=1,
        max_length=5000,
        description="Research question to investigate.",
    )


class ResearchResponse(BaseModel):
    """API response representing a research session."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    status: str
    confidence: float | None
    final_report: str | None
    created_at: datetime
    updated_at: datetime