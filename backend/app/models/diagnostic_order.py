import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class DiagnosticOrderStatus(str, Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DiagnosticOrderPriority(str, Enum):
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    STAT = "STAT"


VALID_DIAGNOSTIC_ORDER_TRANSITIONS = {
    DiagnosticOrderStatus.DRAFT: {DiagnosticOrderStatus.ORDERED, DiagnosticOrderStatus.CANCELLED},
    DiagnosticOrderStatus.ORDERED: {DiagnosticOrderStatus.IN_PROGRESS, DiagnosticOrderStatus.CANCELLED},
    DiagnosticOrderStatus.IN_PROGRESS: {DiagnosticOrderStatus.COMPLETED, DiagnosticOrderStatus.CANCELLED},
    DiagnosticOrderStatus.COMPLETED: set(),
    DiagnosticOrderStatus.CANCELLED: set(),
}


class DiagnosticOrder(Base):
    """Clinical request ordering diagnostic laboratory, imaging, or pathology investigations."""

    __tablename__ = "diagnostic_orders"

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
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordering_provider_id: Mapped[int] = mapped_column(
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

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DiagnosticOrderStatus.ORDERED.value,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DiagnosticOrderPriority.ROUTINE.value,
        index=True,
    )
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
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

    # Cancellation Audit
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["DiagnosticOrderItem"]] = relationship(
        "DiagnosticOrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
