import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class InteropAction(str, Enum):
    FHIR_READ = "FHIR_READ"
    FHIR_BUNDLE_EXPORT = "FHIR_BUNDLE_EXPORT"
    ABHA_LINK = "ABHA_LINK"
    ABHA_UNLINK = "ABHA_UNLINK"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    CONSENT_VERIFIED = "CONSENT_VERIFIED"
    GATEWAY_EXCHANGE = "GATEWAY_EXCHANGE"


class InteroperabilityAudit(Base):
    """Immutable audit trail for FHIR queries, ABHA linkage, and external ABDM data transfers."""

    __tablename__ = "interoperability_audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    patient_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="FHIR resourceType or ABDM entity (e.g. Patient, Bundle, Consent)",
    )

    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    purpose: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="SUCCESS",
    )

    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON or contextual event metadata",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
