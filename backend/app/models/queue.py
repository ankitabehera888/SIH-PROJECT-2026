import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class QueuePriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class QueueStatus(str, Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


VALID_QUEUE_TRANSITIONS = {
    QueueStatus.WAITING: {QueueStatus.CALLED, QueueStatus.SKIPPED, QueueStatus.CANCELLED},
    QueueStatus.CALLED: {QueueStatus.IN_CONSULTATION, QueueStatus.SKIPPED, QueueStatus.WAITING},
    QueueStatus.IN_CONSULTATION: {QueueStatus.COMPLETED, QueueStatus.CANCELLED},
    QueueStatus.SKIPPED: {QueueStatus.WAITING, QueueStatus.CANCELLED},
    QueueStatus.COMPLETED: set(),
    QueueStatus.CANCELLED: set(),
}


class QueueEntry(Base):
    """Operational facility arrival queue record for daily clinical queueing."""

    __tablename__ = "queue_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    appointment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    queue_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    queue_number: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=QueuePriority.NORMAL.value,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=QueueStatus.WAITING.value,
        index=True,
    )

    # Operational Analytics Timestamps
    checked_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    called_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
