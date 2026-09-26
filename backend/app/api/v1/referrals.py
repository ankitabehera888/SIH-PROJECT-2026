import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.referral import (
    ReferralCancelRequest,
    ReferralCompleteRequest,
    ReferralCreate,
    ReferralListResponse,
    ReferralRejectRequest,
    ReferralResponse,
    ReferralScheduleRequest,
)
from app.services.referral_service import ReferralService

router = APIRouter(tags=["Referrals"])

CLINICAL_STAFF = [UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]
CLINICAL_PRACTITIONERS = [UserRole.DOCTOR, UserRole.ADMIN]


@router.post(
    "/encounters/{encounter_id}/referral",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create clinical referral from encounter",
)
def create_referral_from_encounter(
    encounter_id: uuid.UUID,
    payload: ReferralCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_PRACTITIONERS)),
):
    """Create a care transfer referral from an active or completed encounter to another facility."""
    service = ReferralService(db)
    return service.create_from_encounter(
        encounter_id=encounter_id,
        data=payload,
        current_user=current_user,
    )


@router.get(
    "/referrals/{referral_id}",
    response_model=ReferralResponse,
    summary="Get referral details",
)
def get_referral(
    referral_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full details of a clinical referral."""
    service = ReferralService(db)
    return service.get_referral(referral_id=referral_id, current_user=current_user)


@router.get(
    "/patients/{patient_id}/referrals",
    response_model=ReferralListResponse,
    summary="Get patient referral history",
)
def get_patient_referrals(
    patient_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve longitudinal referral history for a patient."""
    service = ReferralService(db)
    return service.list_patient_referrals(
        patient_id=patient_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/facilities/{facility_id}/referrals/incoming",
    response_model=ReferralListResponse,
    summary="Get incoming referrals for receiving facility",
)
def get_incoming_referrals(
    facility_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """List referrals sent to this receiving facility inbox."""
    service = ReferralService(db)
    return service.list_incoming_referrals(
        facility_id=facility_id,
        status=status_filter,
        priority=priority_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/facilities/{facility_id}/referrals/outgoing",
    response_model=ReferralListResponse,
    summary="Get outgoing referrals for referring facility",
)
def get_outgoing_referrals(
    facility_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """List referrals originating from this referring facility outbox."""
    service = ReferralService(db)
    return service.list_outgoing_referrals(
        facility_id=facility_id,
        status=status_filter,
        priority=priority_filter,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/referrals/{referral_id}/accept",
    response_model=ReferralResponse,
    summary="Accept referral at receiving facility",
)
def accept_referral(
    referral_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Receiving facility accepts patient care transfer."""
    service = ReferralService(db)
    return service.accept_referral(referral_id=referral_id, current_user=current_user)


@router.post(
    "/referrals/{referral_id}/reject",
    response_model=ReferralResponse,
    summary="Reject referral at receiving facility",
)
def reject_referral(
    referral_id: uuid.UUID,
    payload: ReferralRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Receiving facility rejects referral with a documented reason."""
    service = ReferralService(db)
    return service.reject_referral(referral_id=referral_id, data=payload, current_user=current_user)


@router.post(
    "/referrals/{referral_id}/schedule",
    response_model=ReferralResponse,
    summary="Schedule patient visit for accepted referral",
)
def schedule_referral(
    referral_id: uuid.UUID,
    payload: ReferralScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Schedule date and time for patient care at the destination facility."""
    service = ReferralService(db)
    return service.schedule_referral(referral_id=referral_id, data=payload, current_user=current_user)


@router.post(
    "/referrals/{referral_id}/complete",
    response_model=ReferralResponse,
    summary="Complete referral with clinical outcome",
)
def complete_referral(
    referral_id: uuid.UUID,
    payload: ReferralCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_PRACTITIONERS)),
):
    """Complete referral and record clinical outcome and follow-up directives."""
    service = ReferralService(db)
    return service.complete_referral(referral_id=referral_id, data=payload, current_user=current_user)


@router.post(
    "/referrals/{referral_id}/cancel",
    response_model=ReferralResponse,
    summary="Cancel referral",
)
def cancel_referral(
    referral_id: uuid.UUID,
    payload: ReferralCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Cancel a pending, accepted, or scheduled referral."""
    service = ReferralService(db)
    return service.cancel_referral(referral_id=referral_id, data=payload, current_user=current_user)
