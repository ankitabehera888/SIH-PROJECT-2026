import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class EncounterStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class EncounterType(str, Enum):
    OUTPATIENT = "OUTPATIENT"
    EMERGENCY = "EMERGENCY"
    INPATIENT = "INPATIENT"
    FOLLOW_UP = "FOLLOW_UP"
    HOME_VISIT = "HOME_VISIT"


# Strict Encounter Lifecycle Transitions
VALID_ENCOUNTER_TRANSITIONS = {
    EncounterStatus.SCHEDULED: {EncounterStatus.IN_PROGRESS, EncounterStatus.CANCELLED},
    EncounterStatus.IN_PROGRESS: {EncounterStatus.COMPLETED, EncounterStatus.CANCELLED},
    EncounterStatus.COMPLETED: set(),
    EncounterStatus.CANCELLED: set(),
}


class Encounter(Base):
    """Actual clinical care delivery interaction between a Patient and a Healthcare Provider."""

    __tablename__ = "encounters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # One appointment creates at most one clinical encounter
    appointment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )
    provider_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    encounter_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=EncounterType.OUTPATIENT.value,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=EncounterStatus.IN_PROGRESS.value,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    chief_complaint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    clinical_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Provenance Audit
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
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
