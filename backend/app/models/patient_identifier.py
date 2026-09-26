import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class IdentifierType(str, Enum):
    ABHA_NUMBER = "ABHA_NUMBER"
    ABHA_ADDRESS = "ABHA_ADDRESS"
    NATIONAL_ID = "NATIONAL_ID"
    PASSPORT = "PASSPORT"
    DRIVING_LICENSE = "DRIVING_LICENSE"


class IdentifierStatus(str, Enum):
    ACTIVE = "ACTIVE"
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"


class PatientIdentifier(Base):
    """External identity mapping for ABDM ABHA numbers, PHR addresses, and national identifiers.
    
    Decouples external identities from internal database primary keys.
    Prevents duplicate linkage of the same external identifier across multiple patient records.
    """

    __tablename__ = "patient_identifiers"

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

    system: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="https://healthid.abdm.gov.in",
        comment="URI identifying the authority or namespace (e.g. ABDM HealthID)",
    )

    value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="External identifier value (e.g. 14-digit ABHA number or phr@abdm)",
    )

    identifier_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=IdentifierType.ABHA_NUMBER.value,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=IdentifierStatus.ACTIVE.value,
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

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

    # Unique constraint: No duplicate external identity mapping across patients within the same system
    __table_args__ = (
        UniqueConstraint("system", "value", name="uq_patient_identifier_system_value"),
    )
