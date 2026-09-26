import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class FacilityType(str, Enum):
    SUB_CENTER = "SUB_CENTER"
    PHC = "PHC"
    RURAL_HOSPITAL = "RURAL_HOSPITAL"
    DISTRICT_HOSPITAL = "DISTRICT_HOSPITAL"


class Facility(Base):
    """Healthcare facility / centre delivering operational care."""

    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    facility_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False, default=FacilityType.PHC.value)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
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
