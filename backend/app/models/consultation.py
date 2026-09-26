import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ConsultationType(str, Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    ASSISTED_VIDEO = "ASSISTED_VIDEO"


class ConsultationStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    EXPIRED = "EXPIRED"


VALID_CONSULTATION_TRANSITIONS = {
    ConsultationStatus.SCHEDULED: {
        ConsultationStatus.READY,
        ConsultationStatus.IN_PROGRESS,
        ConsultationStatus.CANCELLED,
        ConsultationStatus.NO_SHOW,
        ConsultationStatus.EXPIRED,
    },
    ConsultationStatus.READY: {
        ConsultationStatus.IN_PROGRESS,
        ConsultationStatus.CANCELLED,
        ConsultationStatus.NO_SHOW,
        ConsultationStatus.EXPIRED,
    },
    ConsultationStatus.IN_PROGRESS: {
        ConsultationStatus.COMPLETED,
        ConsultationStatus.CANCELLED,
    },
    ConsultationStatus.COMPLETED: set(),
    ConsultationStatus.CANCELLED: set(),
    ConsultationStatus.NO_SHOW: set(),
    ConsultationStatus.EXPIRED: set(),
}


class Consultation(Base):
    """Teleconsultation session controlling real-time WebRTC room state and attendance tracking."""

    __tablename__ = "consultations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # 1-to-1 linkage with scheduled Appointment
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

    consultation_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ConsultationType.VIDEO.value,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ConsultationStatus.SCHEDULED.value,
        index=True,
    )

    # Daily.co WebRTC Private Room Metadata
    room_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    room_url: Mapped[str] = mapped_column(String(512), nullable=False)

    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Clinical encounter linkage
    encounter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    participants: Mapped[List["ConsultationParticipant"]] = relationship(
        "ConsultationParticipant",
        back_populates="consultation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
