import uuid
from datetime import date, datetime, time
from typing import List, Optional, Tuple
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate


class AppointmentRepository:
    """Data access repository for clinical Appointments."""

    def __init__(self, db: Session):
        self.db = db

    def has_provider_conflict(
        self,
        provider_id: int,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Checks if a provider has an overlapping active appointment on the given date.
        
        Overlap condition: start_time < existing.end_time AND end_time > existing.start_time
        Excludes CANCELLED appointments.
        """
        conditions = [
            Appointment.provider_id == provider_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status != AppointmentStatus.CANCELLED.value,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
        ]
        if exclude_id:
            conditions.append(Appointment.id != exclude_id)

        stmt = select(func.count(Appointment.id)).where(and_(*conditions))
        count = self.db.scalar(stmt) or 0
        return count > 0

    def create(self, data: AppointmentCreate, created_by_id: Optional[int] = None) -> Appointment:
        appointment = Appointment(
            patient_id=data.patient_id,
            provider_id=data.provider_id,
            facility_id=data.facility_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
            end_time=data.end_time,
            appointment_type=data.appointment_type.value,
            status=AppointmentStatus.SCHEDULED.value,
            reason=data.reason,
            notes=data.notes,
            created_by=created_by_id,
            updated_by=created_by_id,
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_by_id(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        return self.db.scalars(stmt).first()

    def list(
        self,
        patient_id: Optional[uuid.UUID] = None,
        provider_id: Optional[int] = None,
        facility_id: Optional[uuid.UUID] = None,
        appointment_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Appointment], int]:
        base_query = select(Appointment)
        filters = []
        if patient_id:
            filters.append(Appointment.patient_id == patient_id)
        if provider_id:
            filters.append(Appointment.provider_id == provider_id)
        if facility_id:
            filters.append(Appointment.facility_id == facility_id)
        if appointment_date:
            filters.append(Appointment.appointment_date == appointment_date)
        if status:
            filters.append(Appointment.status == status)

        if filters:
            base_query = base_query.where(and_(*filters))

        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        stmt = (
            base_query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.asc())
            .offset(skip)
            .limit(limit)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update_status(
        self,
        appointment: Appointment,
        new_status: str,
        updated_by_id: Optional[int] = None,
    ) -> Appointment:
        appointment.status = new_status
        appointment.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def reschedule(
        self,
        appointment: Appointment,
        new_date: date,
        new_start: time,
        new_end: time,
        updated_by_id: Optional[int] = None,
    ) -> Appointment:
        appointment.appointment_date = new_date
        appointment.start_time = new_start
        appointment.end_time = new_end
        appointment.status = AppointmentStatus.SCHEDULED.value
        appointment.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def cancel(
        self,
        appointment: Appointment,
        reason: str,
        cancelled_by_id: Optional[int] = None,
    ) -> Appointment:
        appointment.status = AppointmentStatus.CANCELLED.value
        appointment.cancelled_at = func.now()
        appointment.cancelled_by = cancelled_by_id
        appointment.cancellation_reason = reason
        appointment.updated_by = cancelled_by_id
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
