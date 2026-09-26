import uuid
from typing import Optional
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PrescriptionItem(Base):
    """Specific line-item instruction for a prescribed medication."""

    __tablename__ = "prescription_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    prescription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False, default="ONCE_DAILY")
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    duration_unit: Mapped[str] = mapped_column(String(50), nullable=False, default="DAYS")
    route: Mapped[str] = mapped_column(String(50), nullable=False, default="ORAL")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    prescription: Mapped["Prescription"] = relationship("Prescription", back_populates="items")
    medication: Mapped["Medication"] = relationship("Medication", lazy="joined")
