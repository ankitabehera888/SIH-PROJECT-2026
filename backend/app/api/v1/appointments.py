import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentRescheduleRequest,
    AppointmentResponse,
)
from app.schemas.encounter import EncounterResponse
from app.schemas.queue import CheckInRequest, QueueEntryResponse
from app.services.appointment_service import AppointmentService
from app.services.encounter_service import EncounterService
from app.services.queue_service import QueueService

router = APIRouter(prefix="/appointments", tags=["Appointments"])

CLINICAL_STAFF = [UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a new appointment",
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Book an appointment with conflict detection and resource authorization."""
    service = AppointmentService(db)
    return service.create_appointment(data=payload, current_user=current_user)


@router.get(
    "",
    response_model=AppointmentListResponse,
    summary="List appointments with filters and pagination",
)
def list_appointments(
    patient_id: Optional[uuid.UUID] = Query(None),
    provider_id: Optional[int] = Query(None),
    facility_id: Optional[uuid.UUID] = Query(None),
    appointment_date: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List appointments. Patients are restricted strictly to their own appointments."""
    service = AppointmentService(db)
    return service.list_appointments(
        current_user=current_user,
        patient_id=patient_id,
        provider_id=provider_id,
        facility_id=facility_id,
        appointment_date=appointment_date,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment details",
)
def get_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details for an appointment by UUID (resource-authorized)."""
    service = AppointmentService(db)
    return service.get_appointment(appointment_id=appointment_id, current_user=current_user)


@router.post(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
    summary="Reschedule an appointment",
)
def reschedule_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentRescheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reschedule an existing scheduled appointment with conflict checks."""
    service = AppointmentService(db)
    return service.reschedule_appointment(
        appointment_id=appointment_id,
        data=payload,
        current_user=current_user,
    )


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    summary="Cancel an appointment",
)
def cancel_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an appointment and record cancellation audit."""
    service = AppointmentService(db)
    return service.cancel_appointment(
        appointment_id=appointment_id,
        data=payload,
        current_user=current_user,
    )


@router.post(
    "/{appointment_id}/check-in",
    response_model=QueueEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Check in patient for today's facility queue",
)
def check_in_patient(
    appointment_id: uuid.UUID,
    payload: Optional[CheckInRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Clinical staff checks in patient, advances appointment, and creates facility QueueEntry."""
    queue_service = QueueService(db)
    req = payload or CheckInRequest()
    return queue_service.check_in(
        appointment_id=appointment_id,
        priority=req.priority,
        current_user=current_user,
    )


@router.post(
    "/{appointment_id}/encounter",
    response_model=EncounterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create clinical encounter from appointment",
)
def create_encounter_from_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """Doctor converts an appointment/queue interaction into an active clinical encounter."""
    service = EncounterService(db)
    return service.create_from_appointment(
        appointment_id=appointment_id,
        current_user=current_user,
    )
