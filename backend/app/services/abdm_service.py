import uuid
from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.interoperability.abdm.identity import ABDMIdentityService
from app.models.consent import Consent, ConsentStatus
from app.models.interoperability_audit import InteropAction
from app.models.patient import Patient
from app.models.patient_identifier import IdentifierStatus, IdentifierType, PatientIdentifier
from app.models.user import User
from app.repositories.interoperability_repository import InteroperabilityRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas.interoperability import (
    ConsentCreateRequest,
    ConsentResponse,
    PatientIdentifierCreate,
    PatientIdentifierResponse,
)


class ABDMService:
    """Business logic for ABDM identity management, ABHA linkage, and patient consent policies."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = InteroperabilityRepository

    def _verify_patient_access(self, patient: Patient, current_user: User):
        """Ensures user is the patient themselves or authorized clinical/admin staff."""
        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException("Access denied: Cannot access another patient's identity records")
        elif current_user.role not in (
            UserRole.DOCTOR.value,
            UserRole.ADMIN.value,
            UserRole.NURSE.value,
        ):
            raise ForbiddenException("Access denied: Insufficient privileges")

    def link_patient_identifier(
        self,
        patient_id: uuid.UUID,
        data: PatientIdentifierCreate,
        current_user: User,
    ) -> PatientIdentifierResponse:
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id '{patient_id}' not found")

        self._verify_patient_access(patient, current_user)

        # 1. Format and validation
        if data.identifier_type == IdentifierType.ABHA_NUMBER:
            if not ABDMIdentityService.validate_abha_number(data.value):
                raise ConflictException("Invalid ABHA Number format. Must be 14 numeric digits.")
        elif data.identifier_type == IdentifierType.ABHA_ADDRESS:
            if not ABDMIdentityService.validate_abha_address(data.value):
                raise ConflictException("Invalid ABHA Address format. Must follow pattern name@abdm or name@sbx.")

        # 2. Duplicate Detection: Check if system + value is already registered
        existing = self.repo.get_identifier_by_system_and_value(self.db, data.system, data.value)
        if existing:
            if existing.patient_id == patient_id:
                return PatientIdentifierResponse.model_validate(existing)
            raise ConflictException(
                f"External identifier '{data.value}' in system '{data.system}' is already linked to another patient"
            )

        identifier = PatientIdentifier(
            id=uuid.uuid4(),
            patient_id=patient_id,
            system=data.system,
            value=data.value,
            identifier_type=data.identifier_type.value,
            status=IdentifierStatus.ACTIVE.value,
        )
        saved = self.repo.create_identifier(self.db, identifier)

        # Record Audit
        self.repo.record_audit(
            self.db,
            action=InteropAction.ABHA_LINK.value,
            resource_type="PatientIdentifier",
            resource_id=str(saved.id),
            patient_id=patient_id,
            user_id=current_user.id,
            purpose="IDENTITY_LINKAGE",
            status="SUCCESS",
            details=f"Linked {data.identifier_type.value}: {data.value}",
        )

        return PatientIdentifierResponse.model_validate(saved)

    def list_patient_identifiers(
        self,
        patient_id: uuid.UUID,
        current_user: User,
    ) -> List[PatientIdentifierResponse]:
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id '{patient_id}' not found")

        self._verify_patient_access(patient, current_user)

        identifiers = self.repo.list_identifiers_by_patient(self.db, patient_id)
        return [PatientIdentifierResponse.model_validate(i) for i in identifiers]

    def create_consent(
        self,
        data: ConsentCreateRequest,
        current_user: User,
    ) -> ConsentResponse:
        patient = self.db.get(Patient, data.patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id '{data.patient_id}' not found")

        self._verify_patient_access(patient, current_user)

        consent = Consent(
            id=uuid.uuid4(),
            patient_id=data.patient_id,
            consent_artefact_id=f"ARTEFACT-{uuid.uuid4().hex[:10]}",
            purpose=data.purpose.value,
            scope=data.scope.value,
            status=ConsentStatus.GRANTED.value,
            granted_by=current_user.id,
            expires_at=data.expires_at,
            notes=data.notes,
        )
        saved = self.repo.create_consent(self.db, consent)

        self.repo.record_audit(
            self.db,
            action=InteropAction.CONSENT_GRANTED.value,
            resource_type="Consent",
            resource_id=str(saved.id),
            patient_id=data.patient_id,
            user_id=current_user.id,
            purpose=data.purpose.value,
            status="SUCCESS",
        )

        return ConsentResponse.model_validate(saved)

    def revoke_consent(
        self,
        consent_id: uuid.UUID,
        current_user: User,
    ) -> ConsentResponse:
        consent = self.repo.get_consent_by_id(self.db, consent_id)
        if not consent:
            raise NotFoundException(f"Consent with id '{consent_id}' not found")

        patient = self.db.get(Patient, consent.patient_id)
        self._verify_patient_access(patient, current_user)

        revoked = self.repo.revoke_consent(self.db, consent_id)

        self.repo.record_audit(
            self.db,
            action=InteropAction.CONSENT_REVOKED.value,
            resource_type="Consent",
            resource_id=str(consent_id),
            patient_id=consent.patient_id,
            user_id=current_user.id,
            status="SUCCESS",
        )

        return ConsentResponse.model_validate(revoked)
