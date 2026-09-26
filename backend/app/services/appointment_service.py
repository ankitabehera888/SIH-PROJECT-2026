import uuid
from datetime import date, datetime, time
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ConflictException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.appointment import (
    VALID_APPOINTMENT_TRANSITIONS,
    Appointment,
    AppointmentStatus,
)
from app.models.facility import Facility
from app.models.patient import Patient
from app.models.queue import QueueStatus
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentRescheduleRequest,
    AppointmentResponse,
)


class AppointmentService:
    """Business logic and validation for Clinical Appointments."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = AppointmentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.facility_repo = FacilityRepository(db)
        self.queue_repo = QueueRepository(db)

    def _get_patient_for_user(self, user_id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.user_id == user_id).first()

    def create_appointment(
        self,
        data: AppointmentCreate,
        current_user: User,
    ) -> AppointmentResponse:
        # 1. Validate time bounds
        if data.start_time >= data.end_time:
            raise AppException(
                message="Appointment start time must be earlier than end time",
                code="INVALID_TIME_RANGE",
                status_code=400,
            )

        # 2. Check patient exists and is active
        patient = self.patient_repo.get_by_id(data.patient_id)
        if not patient:
            raise NotFoundException(message=f"Patient with id '{data.patient_id}' not found")
        if not patient.is_active:
            raise AppException(
                message="Cannot book appointment for a deactivated patient",
                code="PATIENT_INACTIVE",
                status_code=400,
            )

        # Resource authorization: if PATIENT role, verify ownership
        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id is not None and patient.user_id != current_user.id:
                raise ForbiddenException(message="You can only book appointments for yourself")
            elif patient.user_id is None:
                # Link patient to this user
                patient.user_id = current_user.id
                self.db.commit()

        # 3. Check facility exists and is active
        facility = self.facility_repo.get_by_id(data.facility_id)
        if not facility or not facility.is_active:
            raise NotFoundException(message=f"Facility with id '{data.facility_id}' not found or inactive")

        # 4. Check provider exists and is active clinical staff
        provider = self.db.query(User).filter(User.id == data.provider_id).first()
        if not provider or not provider.is_active:
            raise NotFoundException(message=f"Provider with id '{data.provider_id}' not found")
        if provider.role not in [UserRole.DOCTOR.value, UserRole.NURSE.value, UserRole.ADMIN.value]:
            raise AppException(
                message="Selected provider is not authorized for clinical appointments",
                code="INVALID_PROVIDER",
                status_code=400,
            )

        # 5. Check provider / facility association if assigned
        if provider.facility_id and provider.facility_id != data.facility_id:
            raise AppException(
                message=f"Provider is assigned to a different facility",
                code="FACILITY_MISMATCH",
                status_code=400,
            )

        # 6. Check time overlap conflict
        has_conflict = self.repository.has_provider_conflict(
            provider_id=data.provider_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        if has_conflict:
            raise ConflictException(
                message=(
                    f"Provider {provider.email} is already booked for an overlapping time slot "
                    f"on {data.appointment_date}"
                ),
                details={"code": "APPOINTMENT_CONFLICT"},
            )

        appointment = self.repository.create(data, created_by_id=current_user.id)
        return AppointmentResponse.model_validate(appointment)

    def get_appointment(
        self,
        appointment_id: uuid.UUID,
        current_user: User,
    ) -> AppointmentResponse:
        appointment = self.repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        # Resource authorization check
        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(appointment.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own appointments")

        return AppointmentResponse.model_validate(appointment)

    def list_appointments(
        self,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
        provider_id: Optional[int] = None,
        facility_id: Optional[uuid.UUID] = None,
        appointment_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AppointmentListResponse:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        # If user is a patient, strictly restrict to their own records
        if current_user.role == UserRole.PATIENT.value:
            user_patient = self._get_patient_for_user(current_user.id)
            if not user_patient:
                return AppointmentListResponse.create([], 0, page, page_size)
            patient_id = user_patient.id

        skip = (page - 1) * page_size
        items, total = self.repository.list(
            patient_id=patient_id,
            provider_id=provider_id,
            facility_id=facility_id,
            appointment_date=appointment_date,
            status=status,
            skip=skip,
            limit=page_size,
        )
        response_items = [AppointmentResponse.model_validate(a) for a in items]
        return AppointmentListResponse.create(response_items, total, page, page_size)

    def reschedule_appointment(
        self,
        appointment_id: uuid.UUID,
        data: AppointmentRescheduleRequest,
        current_user: User,
    ) -> AppointmentResponse:
        appointment = self.repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(appointment.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only reschedule your own appointment")

        if appointment.status in [AppointmentStatus.COMPLETED.value, AppointmentStatus.CANCELLED.value]:
            raise AppException(
                message=f"Cannot reschedule appointment in status '{appointment.status}'",
                code="INVALID_STATE_TRANSITION",
                status_code=400,
            )

        if data.start_time >= data.end_time:
            raise AppException(
                message="Appointment start time must be earlier than end time",
                code="INVALID_TIME_RANGE",
                status_code=400,
            )

        # Overlap check
        has_conflict = self.repository.has_provider_conflict(
            provider_id=appointment.provider_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
            end_time=data.end_time,
            exclude_id=appointment.id,
        )
        if has_conflict:
            raise ConflictException(
                message="Provider is already booked for this requested rescheduled time slot",
                details={"code": "APPOINTMENT_CONFLICT"},
            )

        rescheduled = self.repository.reschedule(
            appointment=appointment,
            new_date=data.appointment_date,
            new_start=data.start_time,
            new_end=data.end_time,
            updated_by_id=current_user.id,
        )
        return AppointmentResponse.model_validate(rescheduled)

    def cancel_appointment(
        self,
        appointment_id: uuid.UUID,
        data: AppointmentCancelRequest,
        current_user: User,
    ) -> AppointmentResponse:
        appointment = self.repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(appointment.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only cancel your own appointment")

        current_status = AppointmentStatus(appointment.status)
        if AppointmentStatus.CANCELLED not in VALID_APPOINTMENT_TRANSITIONS[current_status]:
            raise AppException(
                message=f"Cannot cancel appointment currently in '{appointment.status}' status",
                code="INVALID_STATE_TRANSITION",
                status_code=400,
            )

        cancelled = self.repository.cancel(
            appointment=appointment,
            reason=data.reason,
            cancelled_by_id=current_user.id,
        )

        # Also cancel queue entry if present
        queue_entry = self.queue_repo.get_by_appointment_id(appointment_id)
        if queue_entry and queue_entry.status not in [QueueStatus.COMPLETED.value, QueueStatus.CANCELLED.value]:
            queue_entry.status = QueueStatus.CANCELLED.value
            self.db.commit()

        return AppointmentResponse.model_validate(cancelled)

    def update_status(
        self,
        appointment_id: uuid.UUID,
        new_status: AppointmentStatus,
        current_user: User,
    ) -> AppointmentResponse:
        appointment = self.repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        current_status = AppointmentStatus(appointment.status)
        if new_status not in VALID_APPOINTMENT_TRANSITIONS[current_status]:
            raise AppException(
                message=f"Invalid state transition from '{appointment.status}' to '{new_status.value}'",
                code="INVALID_STATE_TRANSITION",
                status_code=400,
            )

        updated = self.repository.update_status(
            appointment=appointment,
            new_status=new_status.value,
            updated_by_id=current_user.id,
        )
        return AppointmentResponse.model_validate(updated)
