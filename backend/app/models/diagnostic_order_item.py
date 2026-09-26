import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class DiagnosticItemStatus(str, Enum):
    PENDING = "PENDING"
    SAMPLE_COLLECTED = "SAMPLE_COLLECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DiagnosticOrderItem(Base):
    """Specific diagnostic investigation requested within a DiagnosticOrder."""

    __tablename__ = "diagnostic_order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    diagnostic_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    diagnostic_test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DiagnosticItemStatus.PENDING.value,
        index=True,
    )
    specimen_collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    performed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    order: Mapped["DiagnosticOrder"] = relationship("DiagnosticOrder", back_populates="items")
    test: Mapped["DiagnosticTest"] = relationship("DiagnosticTest", lazy="joined")
    result: Mapped[Optional["DiagnosticResult"]] = relationship(
        "DiagnosticResult",
        back_populates="order_item",
        uselist=False,
        lazy="joined",
    )
