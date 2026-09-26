import uuid
from datetime import date, datetime, time
from enum import Enum
from typing import Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ReferralStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class ReferralType(str, Enum):
    SPECIALIST = "SPECIALIST"
    DIAGNOSTIC = "DIAGNOSTIC"
    EMERGENCY = "EMERGENCY"
    HIGHER_CARE = "HIGHER_CARE"
    FOLLOW_UP = "FOLLOW_UP"


class ReferralPriority(str, Enum):
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    EMERGENCY = "EMERGENCY"


# Strict Referral Lifecycle State Machine
VALID_REFERRAL_TRANSITIONS = {
    ReferralStatus.DRAFT: {ReferralStatus.SENT, ReferralStatus.CANCELLED},
    ReferralStatus.SENT: {
        ReferralStatus.ACCEPTED,
        ReferralStatus.REJECTED,
        ReferralStatus.CANCELLED,
        ReferralStatus.EXPIRED,
    },
    ReferralStatus.ACCEPTED: {ReferralStatus.SCHEDULED, ReferralStatus.CANCELLED},
    ReferralStatus.SCHEDULED: {ReferralStatus.COMPLETED, ReferralStatus.CANCELLED},
    ReferralStatus.COMPLETED: set(),
    ReferralStatus.REJECTED: set(),
    ReferralStatus.CANCELLED: set(),
    ReferralStatus.EXPIRED: set(),
}


class Referral(Base):
    """Clinical referral requesting transfer of patient care between healthcare facilities."""

    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Core Healthcare Domain Links
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Facility & Provider Provenance
    referring_facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    referring_provider_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiving_facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiving_provider_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Classification & Triage
    referral_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ReferralType.SPECIALIST.value,
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ReferralPriority.ROUTINE.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ReferralStatus.SENT.value,
        index=True,
    )

    # Clinical Context
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    clinical_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    requested_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Creation Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Acceptance Audit
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Rejection Audit
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Scheduling Audit
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Completion Audit & Structured Outcome
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    outcome_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Cancellation Audit
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # General Record Audit
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
