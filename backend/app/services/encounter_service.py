import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ConflictException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.models.encounter import Encounter, EncounterStatus, EncounterType
from app.models.patient import Patient
from app.models.queue import QueueEntry, QueueStatus
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.encounter_repository import EncounterRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.encounter import (
    EncounterCompleteRequest,
    EncounterCreate,
    EncounterListResponse,
    EncounterResponse,
    EncounterTypeEnum,
    EncounterUpdate,
)


class EncounterService:
    """Service orchestrating clinical encounters, appointment linkages, and encounter life cycle."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = EncounterRepository(db)
        self.appointment_repo = AppointmentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.facility_repo = FacilityRepository(db)
        self.queue_repo = QueueRepository(db)

    def create_from_appointment(
        self,
        appointment_id: uuid.UUID,
        current_user: User,
        chief_complaint: Optional[str] = None,
        clinical_notes: Optional[str] = None,
    ) -> EncounterResponse:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        if appointment.status == AppointmentStatus.CANCELLED.value:
            raise AppException(
                message="Cannot create a clinical encounter for a cancelled appointment",
                code="APPOINTMENT_CANCELLED",
                status_code=400,
            )

        # Check for existing encounter for this appointment
        existing = self.repository.get_by_appointment_id(appointment_id)
        if existing:
            raise ConflictException(
                message="An encounter already exists for this appointment",
                details={"code": "ENCOUNTER_ALREADY_EXISTS", "encounter_id": str(existing.id)},
            )

        # Build EncounterCreate
        data = EncounterCreate(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            provider_id=appointment.provider_id,
            facility_id=appointment.facility_id,
            encounter_type=EncounterTypeEnum.OUTPATIENT,
            chief_complaint=chief_complaint or appointment.reason,
            clinical_notes=clinical_notes or appointment.notes,
        )

        encounter = self.repository.create(data, created_by_id=current_user.id)

        # Advance appointment status to IN_CONSULTATION
        appointment.status = AppointmentStatus.IN_CONSULTATION.value
        appointment.updated_by = current_user.id

        # If there's an associated queue entry, advance it to IN_CONSULTATION
        queue_entry = self.queue_repo.get_by_appointment_id(appointment_id)
        if queue_entry and queue_entry.status in [QueueStatus.WAITING.value, QueueStatus.CALLED.value]:
            self.queue_repo.mark_in_consultation(queue_entry)

        self.db.commit()
        return EncounterResponse.model_validate(encounter)

    def create_direct_encounter(
        self,
        data: EncounterCreate,
        current_user: User,
    ) -> EncounterResponse:
        patient = self.patient_repo.get_by_id(data.patient_id)
        if not patient or not patient.is_active:
            raise NotFoundException(message=f"Patient with id '{data.patient_id}' not found or inactive")

        facility = self.facility_repo.get_by_id(data.facility_id)
        if not facility or not facility.is_active:
            raise NotFoundException(message=f"Facility with id '{data.facility_id}' not found or inactive")

        encounter = self.repository.create(data, created_by_id=current_user.id)
        return EncounterResponse.model_validate(encounter)

    def get_encounter(
        self,
        encounter_id: uuid.UUID,
        current_user: User,
    ) -> EncounterResponse:
        encounter = self.repository.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        # Resource-level authorization
        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(encounter.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own clinical encounters")

        return EncounterResponse.model_validate(encounter)

    def list_patient_encounters(
        self,
        patient_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> EncounterListResponse:
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(message=f"Patient with id '{patient_id}' not found")

        # Resource-level authorization
        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own clinical records")

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.get_patient_encounters(
            patient_id=patient_id,
            skip=skip,
            limit=page_size,
        )
        response_items = [EncounterResponse.model_validate(e) for e in items]
        return EncounterListResponse.create(response_items, total, page, page_size)

    def update_encounter(
        self,
        encounter_id: uuid.UUID,
        data: EncounterUpdate,
        current_user: User,
    ) -> EncounterResponse:
        encounter = self.repository.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        if encounter.status == EncounterStatus.COMPLETED.value:
            raise AppException(
                message="Completed clinical encounters are immutable and cannot be modified directly",
                code="ENCOUNTER_LOCKED",
                status_code=400,
            )

        updated = self.repository.update(
            encounter=encounter,
            chief_complaint=data.chief_complaint,
            clinical_notes=data.clinical_notes,
            updated_by_id=current_user.id,
        )
        return EncounterResponse.model_validate(updated)

    def complete_encounter(
        self,
        encounter_id: uuid.UUID,
        data: EncounterCompleteRequest,
        current_user: User,
    ) -> EncounterResponse:
        encounter = self.repository.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        if encounter.status == EncounterStatus.COMPLETED.value:
            raise AppException(
                message="Encounter is already completed",
                code="ENCOUNTER_ALREADY_COMPLETED",
                status_code=400,
            )

        completed = self.repository.complete(
            encounter=encounter,
            clinical_notes=data.clinical_notes,
            updated_by_id=current_user.id,
        )

        # Sync associated appointment
        if completed.appointment_id:
            appointment = self.appointment_repo.get_by_id(completed.appointment_id)
            if appointment and appointment.status != AppointmentStatus.COMPLETED.value:
                appointment.status = AppointmentStatus.COMPLETED.value
                appointment.updated_by = current_user.id

            # Sync queue entry
            queue_entry = self.queue_repo.get_by_appointment_id(completed.appointment_id)
            if queue_entry and queue_entry.status != QueueStatus.COMPLETED.value:
                self.queue_repo.mark_completed(queue_entry)

        self.db.commit()
        return EncounterResponse.model_validate(completed)
