import enum
import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class FollowupStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    MISSED = "missed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FollowupPriority(str, enum.Enum):
    ROUTINE = "routine"
    HIGH = "high"
    URGENT = "urgent"


class Followup(Base):
    """Clinical follow-up tracking model linking patients, providers, and encounters."""

    __tablename__ = "followups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    encounter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="SET NULL"),
        nullable=True,
    )
    condition: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(50),
        default=FollowupPriority.ROUTINE.value,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=FollowupStatus.UPCOMING.value,
        nullable=False,
        index=True,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_rate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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

    patient = relationship("Patient")
    provider = relationship("User")
    encounter = relationship("Encounter")
