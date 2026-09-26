import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.followup import (
    FollowupCompleteRequest,
    FollowupCreate,
    FollowupListResponse,
    FollowupRescheduleRequest,
    FollowupResponse,
)
from app.services.followup_service import FollowupService

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


@router.post(
    "",
    response_model=FollowupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a clinical follow-up",
)
def create_followup(
    payload: FollowupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a clinical follow-up task for a patient."""
    service = FollowupService(db)
    return service.create_followup(payload, current_user)


@router.get(
    "",
    response_model=FollowupListResponse,
    summary="List follow-ups with status filter and summary cards",
)
def list_followups(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (upcoming, missed, completed, all)"),
    patient_id: Optional[uuid.UUID] = Query(None, description="Filter by patient UUID"),
    provider_id: Optional[int] = Query(None, description="Filter by doctor/provider user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve list of clinical follow-ups with summary counters for upcoming, missed, and completed."""
    service = FollowupService(db)
    return service.list_followups(
        current_user=current_user,
        status_filter=status_filter,
        patient_id=patient_id,
        provider_id=provider_id,
    )


@router.get(
    "/{followup_id}",
    response_model=FollowupResponse,
    summary="Get follow-up details",
)
def get_followup(
    followup_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details for a specific clinical follow-up."""
    service = FollowupService(db)
    return service.get_followup(followup_id)


@router.post(
    "/{followup_id}/reschedule",
    response_model=FollowupResponse,
    summary="Reschedule a missed or upcoming follow-up",
)
def reschedule_followup(
    followup_id: uuid.UUID,
    payload: FollowupRescheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reschedule a follow-up to a new date."""
    service = FollowupService(db)
    return service.reschedule_followup(followup_id, payload, current_user)


@router.post(
    "/{followup_id}/complete",
    response_model=FollowupResponse,
    summary="Mark a follow-up as completed",
)
def complete_followup(
    followup_id: uuid.UUID,
    payload: FollowupCompleteRequest = FollowupCompleteRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark follow-up as completed and update progress percentage."""
    service = FollowupService(db)
    return service.complete_followup(followup_id, payload, current_user)


@router.post(
    "/{followup_id}/remind",
    summary="Send a reminder notification for an upcoming follow-up",
)
def send_reminder(
    followup_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger an in-app/SMS reminder notification to the patient."""
    service = FollowupService(db)
    return service.send_reminder(followup_id, current_user)
