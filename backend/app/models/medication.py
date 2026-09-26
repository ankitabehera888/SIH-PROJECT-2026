import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Medication(Base):
    """Reusable drug and pharmaceutical medication catalog item."""

    __tablename__ = "medications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    generic_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    strength: Mapped[str] = mapped_column(String(50), nullable=False)
    dosage_form: Mapped[str] = mapped_column(String(50), nullable=False, default="TABLET")
    route: Mapped[str] = mapped_column(String(50), nullable=False, default="ORAL")
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="mg")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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
