from datetime import datetime, timezone
from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.consent import Consent, ConsentStatus
from app.models.interoperability_audit import InteroperabilityAudit
from app.models.patient_identifier import IdentifierStatus, PatientIdentifier


class InteroperabilityRepository:
    """Data Access Layer for ABDM Identifiers, Consent artefacts, and Interoperability Audit trails."""

    # --- Patient Identifiers (ABHA) ---
    @staticmethod
    def create_identifier(db: Session, identifier: PatientIdentifier) -> PatientIdentifier:
        db.add(identifier)
        db.commit()
        db.refresh(identifier)
        return identifier

    @staticmethod
    def list_identifiers_by_patient(db: Session, patient_id: uuid.UUID) -> List[PatientIdentifier]:
        stmt = select(PatientIdentifier).where(PatientIdentifier.patient_id == patient_id)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_identifier_by_system_and_value(
        db: Session,
        system: str,
        value: str,
    ) -> Optional[PatientIdentifier]:
        stmt = select(PatientIdentifier).where(
            PatientIdentifier.system == system,
            PatientIdentifier.value == value,
        )
        return db.scalars(stmt).first()

    @staticmethod
    def get_identifier_by_id(db: Session, identifier_id: uuid.UUID) -> Optional[PatientIdentifier]:
        return db.get(PatientIdentifier, identifier_id)

    @staticmethod
    def revoke_identifier(db: Session, identifier_id: uuid.UUID) -> Optional[PatientIdentifier]:
        ident = db.get(PatientIdentifier, identifier_id)
        if ident:
            ident.status = IdentifierStatus.REVOKED.value
            db.commit()
            db.refresh(ident)
        return ident

    # --- Consent Artefacts ---
    @staticmethod
    def create_consent(db: Session, consent: Consent) -> Consent:
        db.add(consent)
        db.commit()
        db.refresh(consent)
        return consent

    @staticmethod
    def get_consent_by_id(db: Session, consent_id: uuid.UUID) -> Optional[Consent]:
        return db.get(Consent, consent_id)

    @staticmethod
    def list_consents_by_patient(db: Session, patient_id: uuid.UUID) -> List[Consent]:
        stmt = select(Consent).where(Consent.patient_id == patient_id).order_by(Consent.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def revoke_consent(db: Session, consent_id: uuid.UUID) -> Optional[Consent]:
        consent = db.get(Consent, consent_id)
        if consent:
            consent.status = ConsentStatus.REVOKED.value
            consent.revoked_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(consent)
        return consent

    # --- Interoperability Audit ---
    @staticmethod
    def record_audit(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        patient_id: Optional[uuid.UUID] = None,
        user_id: Optional[int] = None,
        purpose: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None,
    ) -> InteroperabilityAudit:
        audit = InteroperabilityAudit(
            id=uuid.uuid4(),
            patient_id=patient_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose=purpose,
            status=status,
            details=details,
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
