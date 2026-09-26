import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.prescription import Prescription, PrescriptionStatus, VALID_PRESCRIPTION_TRANSITIONS
from app.models.user import User
from app.repositories.encounter_repository import EncounterRepository
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.prescription_repository import PrescriptionRepository
from app.schemas.prescription import (
    PrescriptionCancelRequest,
    PrescriptionCreate,
    PrescriptionListResponse,
    PrescriptionResponse,
)


class PrescriptionService:
    """Service governing clinical prescriptions, medication line-item validations, and issuance."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = PrescriptionRepository(db)
        self.encounter_repo = EncounterRepository(db)
        self.patient_repo = PatientRepository(db)
        self.medication_repo = MedicationRepository(db)

    def create_from_encounter(
        self,
        encounter_id: uuid.UUID,
        data: PrescriptionCreate,
        current_user: User,
    ) -> PrescriptionResponse:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        patient = self.patient_repo.get_by_id(encounter.patient_id)
        if not patient or not patient.is_active:
            raise NotFoundException(message=f"Patient with id '{encounter.patient_id}' not found or inactive")

        # Validate each medication exists and is active
        for item in data.items:
            med = self.medication_repo.get_by_id(item.medication_id)
            if not med:
                raise NotFoundException(message=f"Medication with id '{item.medication_id}' not found")
            if not med.is_active:
                raise AppException(
                    message=f"Medication '{med.name}' is inactive and cannot be prescribed",
                    code="MEDICATION_INACTIVE",
                    status_code=400,
                )

        prescription = self.repository.create(
            patient_id=encounter.patient_id,
            encounter_id=encounter.id,
            prescriber_id=current_user.id,
            facility_id=encounter.facility_id,
            data=data,
            created_by_id=current_user.id,
        )
        return PrescriptionResponse.model_validate(prescription)

    def get_prescription(
        self,
        prescription_id: uuid.UUID,
        current_user: User,
    ) -> PrescriptionResponse:
        prescription = self.repository.get_by_id(prescription_id)
        if not prescription:
            raise NotFoundException(message=f"Prescription with id '{prescription_id}' not found")

        # Resource authorization check
        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(prescription.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own prescriptions")

        return PrescriptionResponse.model_validate(prescription)

    def list_patient_prescriptions(
        self,
        patient_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> PrescriptionListResponse:
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(message=f"Patient with id '{patient_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own prescriptions")

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.get_patient_prescriptions(
            patient_id=patient_id,
            skip=skip,
            limit=page_size,
        )
        response_items = [PrescriptionResponse.model_validate(p) for p in items]
        return PrescriptionListResponse.create(response_items, total, page, page_size)

    def list_encounter_prescriptions(
        self,
        encounter_id: uuid.UUID,
        current_user: User,
    ) -> List[PrescriptionResponse]:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(encounter.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own prescriptions")

        items = self.repository.get_encounter_prescriptions(encounter_id)
        return [PrescriptionResponse.model_validate(p) for p in items]

    def issue_prescription(
        self,
        prescription_id: uuid.UUID,
        current_user: User,
    ) -> PrescriptionResponse:
        prescription = self.repository.get_by_id(prescription_id)
        if not prescription:
            raise NotFoundException(message=f"Prescription with id '{prescription_id}' not found")

        if prescription.status not in [PrescriptionStatus.DRAFT.value, PrescriptionStatus.ISSUED.value]:
            raise AppException(
                message=f"Cannot issue prescription in status '{prescription.status}'",
                code="INVALID_PRESCRIPTION_TRANSITION",
                status_code=400,
            )

        updated = self.repository.issue(prescription=prescription, issued_by_id=current_user.id)
        return PrescriptionResponse.model_validate(updated)

    def cancel_prescription(
        self,
        prescription_id: uuid.UUID,
        data: PrescriptionCancelRequest,
        current_user: User,
    ) -> PrescriptionResponse:
        prescription = self.repository.get_by_id(prescription_id)
        if not prescription:
            raise NotFoundException(message=f"Prescription with id '{prescription_id}' not found")

        if prescription.status in [PrescriptionStatus.COMPLETED.value, PrescriptionStatus.CANCELLED.value]:
            raise AppException(
                message=f"Cannot cancel prescription in terminal status '{prescription.status}'",
                code="INVALID_PRESCRIPTION_TRANSITION",
                status_code=400,
            )

        updated = self.repository.cancel(
            prescription=prescription,
            cancelled_by_id=current_user.id,
            reason=data.reason,
        )
        return PrescriptionResponse.model_validate(updated)
