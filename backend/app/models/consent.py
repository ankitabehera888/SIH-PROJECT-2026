import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ConsentStatus(str, Enum):
    REQUESTED = "REQUESTED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class ConsentPurpose(str, Enum):
    CARE_MANAGEMENT = "CARE_MANAGEMENT"
    EMERGENCY = "EMERGENCY"
    DIAGNOSTIC_CONSULTATION = "DIAGNOSTIC_CONSULTATION"
    RESEARCH = "RESEARCH"


class ConsentScope(str, Enum):
    ALL = "ALL"
    VITALS = "VITALS"
    PRESCRIPTIONS = "PRESCRIPTIONS"
    DIAGNOSTICS = "DIAGNOSTICS"
    ENCOUNTERS = "ENCOUNTERS"


class Consent(Base):
    """ABDM-aligned patient consent artefact and authorization policy model.
    
    Controls whether external health information exchanges (HIE-CM) or providers
    can access parts or all of a patient's longitudinal record.
    """

    __tablename__ = "consents"

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

    consent_artefact_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="ABDM Consent Artefact identifier if issued by external Gateway",
    )

    purpose: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=ConsentPurpose.CARE_MANAGEMENT.value,
    )

    scope: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=ConsentScope.ALL.value,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ConsentStatus.GRANTED.value,
        index=True,
    )

    granted_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
