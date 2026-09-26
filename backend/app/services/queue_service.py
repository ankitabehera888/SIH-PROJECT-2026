import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ConflictException, NotFoundException
from app.models.appointment import Appointment, AppointmentStatus
from app.models.queue import (
    VALID_QUEUE_TRANSITIONS,
    QueueEntry,
    QueuePriority,
    QueueStatus,
)
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.queue import (
    QueueEntryResponse,
    QueueListResponse,
    QueuePriorityEnum,
)


class QueueService:
    """Service layer managing facility-level operational queues, check-ins, and triage."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = QueueRepository(db)
        self.appointment_repo = AppointmentRepository(db)
        self.facility_repo = FacilityRepository(db)

    def check_in(
        self,
        appointment_id: uuid.UUID,
        priority: QueuePriorityEnum = QueuePriorityEnum.NORMAL,
        current_user: Optional[User] = None,
    ) -> QueueEntryResponse:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        # Verify appointment status allows check-in
        if appointment.status not in [AppointmentStatus.SCHEDULED.value, AppointmentStatus.CONFIRMED.value]:
            raise AppException(
                message=f"Cannot check in appointment currently in '{appointment.status}' status",
                code="INVALID_CHECKIN_STATE",
                status_code=400,
            )

        # Check if already checked in
        existing_entry = self.repository.get_by_appointment_id(appointment_id)
        if existing_entry:
            raise ConflictException(
                message=f"Patient is already checked in with queue number '{existing_entry.queue_number}'",
                details={"queue_number": existing_entry.queue_number},
            )

        today = date.today()
        queue_number = self.repository.generate_next_queue_number(appointment.facility_id, today)

        # Create queue entry
        entry = self.repository.create(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            facility_id=appointment.facility_id,
            queue_date=today,
            queue_number=queue_number,
            priority=priority.value,
        )

        # Advance appointment status to WAITING
        appointment.status = AppointmentStatus.WAITING.value
        appointment.updated_by = current_user.id if current_user else None
        self.db.commit()

        return QueueEntryResponse.model_validate(entry)

    def get_facility_queue(
        self,
        facility_id: uuid.UUID,
        queue_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> QueueListResponse:
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise NotFoundException(message=f"Facility with id '{facility_id}' not found")

        target_date = queue_date or date.today()
        items = self.repository.list_for_facility(
            facility_id=facility_id,
            queue_date=target_date,
            status=status,
        )
        response_items = [QueueEntryResponse.model_validate(e) for e in items]
        return QueueListResponse(
            items=response_items,
            facility_id=facility_id,
            queue_date=target_date,
            total=len(response_items),
        )

    def call_next(
        self,
        facility_id: uuid.UUID,
        current_user: User,
    ) -> QueueEntryResponse:
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise NotFoundException(message=f"Facility with id '{facility_id}' not found")

        today = date.today()
        entry = self.repository.get_next_waiting(facility_id=facility_id, queue_date=today)
        if not entry:
            raise NotFoundException(message="No patients currently waiting in queue for this facility")

        called_entry = self.repository.mark_called(entry)
        return QueueEntryResponse.model_validate(called_entry)

    def start_consultation(
        self,
        queue_entry_id: uuid.UUID,
        current_user: User,
    ) -> QueueEntryResponse:
        entry = self.repository.get_by_id(queue_entry_id)
        if not entry:
            raise NotFoundException(message=f"Queue entry with id '{queue_entry_id}' not found")

        if entry.status not in [QueueStatus.WAITING.value, QueueStatus.CALLED.value]:
            raise AppException(
                message=f"Cannot start consultation for patient in '{entry.status}' status",
                code="INVALID_QUEUE_TRANSITION",
                status_code=400,
            )

        updated_entry = self.repository.mark_in_consultation(entry)

        # Sync appointment status
        appointment = self.appointment_repo.get_by_id(entry.appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.IN_CONSULTATION.value
            appointment.updated_by = current_user.id
            self.db.commit()

        return QueueEntryResponse.model_validate(updated_entry)

    def complete_consultation(
        self,
        queue_entry_id: uuid.UUID,
        current_user: User,
    ) -> QueueEntryResponse:
        entry = self.repository.get_by_id(queue_entry_id)
        if not entry:
            raise NotFoundException(message=f"Queue entry with id '{queue_entry_id}' not found")

        if entry.status != QueueStatus.IN_CONSULTATION.value:
            raise AppException(
                message=f"Cannot complete consultation for patient not in 'IN_CONSULTATION' status (current: {entry.status})",
                code="INVALID_QUEUE_TRANSITION",
                status_code=400,
            )

        updated_entry = self.repository.mark_completed(entry)

        # Sync appointment status
        appointment = self.appointment_repo.get_by_id(entry.appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.COMPLETED.value
            appointment.updated_by = current_user.id
            self.db.commit()

        return QueueEntryResponse.model_validate(updated_entry)

    def skip_queue_entry(
        self,
        queue_entry_id: uuid.UUID,
        current_user: User,
    ) -> QueueEntryResponse:
        entry = self.repository.get_by_id(queue_entry_id)
        if not entry:
            raise NotFoundException(message=f"Queue entry with id '{queue_entry_id}' not found")

        if entry.status not in [QueueStatus.WAITING.value, QueueStatus.CALLED.value]:
            raise AppException(
                message=f"Cannot skip patient currently in '{entry.status}' status",
                code="INVALID_QUEUE_TRANSITION",
                status_code=400,
            )

        updated_entry = self.repository.mark_skipped(entry)
        return QueueEntryResponse.model_validate(updated_entry)
