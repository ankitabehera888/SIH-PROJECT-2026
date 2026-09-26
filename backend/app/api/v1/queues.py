import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.queue import (
    QueueEntryResponse,
    QueueListResponse,
)
from app.services.queue_service import QueueService

router = APIRouter(prefix="/queues", tags=["Queues"])

CLINICAL_STAFF = [UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]
CONSULTATION_STAFF = [UserRole.DOCTOR, UserRole.ADMIN]


@router.get(
    "/{facility_id}",
    response_model=QueueListResponse,
    summary="Get operational queue for a facility",
)
def get_facility_queue(
    facility_id: uuid.UUID,
    queue_date: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Retrieve the daily priority queue for a specific healthcare facility."""
    service = QueueService(db)
    return service.get_facility_queue(
        facility_id=facility_id,
        queue_date=queue_date,
        status=status_filter,
    )


@router.post(
    "/{facility_id}/call-next",
    response_model=QueueEntryResponse,
    summary="Call the next eligible patient in queue",
)
def call_next_patient(
    facility_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Picks the highest priority, longest-waiting patient and updates status to CALLED."""
    service = QueueService(db)
    return service.call_next(facility_id=facility_id, current_user=current_user)


@router.post(
    "/{queue_entry_id}/start",
    response_model=QueueEntryResponse,
    summary="Start consultation for a called queue entry",
)
def start_consultation(
    queue_entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CONSULTATION_STAFF)),
):
    """Doctor marks patient as in consultation and starts duration timer."""
    service = QueueService(db)
    return service.start_consultation(queue_entry_id=queue_entry_id, current_user=current_user)


@router.post(
    "/{queue_entry_id}/complete",
    response_model=QueueEntryResponse,
    summary="Complete consultation for a queue entry",
)
def complete_consultation(
    queue_entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CONSULTATION_STAFF)),
):
    """Doctor marks consultation as completed and closes the queue entry and appointment."""
    service = QueueService(db)
    return service.complete_consultation(queue_entry_id=queue_entry_id, current_user=current_user)


@router.post(
    "/{queue_entry_id}/skip",
    response_model=QueueEntryResponse,
    summary="Mark patient as skipped in queue",
)
def skip_patient(
    queue_entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Marks patient as skipped if unavailable when called."""
    service = QueueService(db)
    return service.skip_queue_entry(queue_entry_id=queue_entry_id, current_user=current_user)
