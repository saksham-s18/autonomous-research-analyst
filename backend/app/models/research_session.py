import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchSession(Base):
    """Persistent record of a research request and its result."""

    __tablename__ = "research_sessions"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
    )

    workflow_state: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    research_plan: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    sources: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    evidence: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    findings: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    citations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    finding_citations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    conflicts: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    sufficiency_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    sufficiency_reasons: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    final_report: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )