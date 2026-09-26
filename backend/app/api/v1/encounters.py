import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.encounter import (
    EncounterCompleteRequest,
    EncounterCreate,
    EncounterListResponse,
    EncounterResponse,
    EncounterUpdate,
)
from app.schemas.vital import (
    VitalCreate,
    VitalListResponse,
    VitalResponse,
)
from app.services.encounter_service import EncounterService
from app.services.vital_service import VitalService

router = APIRouter(tags=["Encounters"])

CLINICAL_PRACTITIONERS = [UserRole.DOCTOR, UserRole.ADMIN]
ALL_CLINICAL_STAFF = [UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]


@router.post(
    "/encounters",
    response_model=EncounterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a clinical encounter",
)
def create_encounter(
    payload: EncounterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_PRACTITIONERS)),
):
    """Create a new clinical encounter directly."""
    service = EncounterService(db)
    return service.create_direct_encounter(data=payload, current_user=current_user)


@router.get(
    "/encounters/{encounter_id}",
    response_model=EncounterResponse,
    summary="Get encounter details",
)
def get_encounter(
    encounter_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details of a clinical encounter by UUID."""
    service = EncounterService(db)
    return service.get_encounter(encounter_id=encounter_id, current_user=current_user)


@router.get(
    "/patients/{patient_id}/encounters",
    response_model=EncounterListResponse,
    summary="Get longitudinal encounter history for a patient",
)
def get_patient_encounters(
    patient_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated historical clinical encounters for a patient."""
    service = EncounterService(db)
    return service.list_patient_encounters(
        patient_id=patient_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/encounters/{encounter_id}",
    response_model=EncounterResponse,
    summary="Update clinical notes or chief complaint for an in-progress encounter",
)
def update_encounter(
    encounter_id: uuid.UUID,
    payload: EncounterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_PRACTITIONERS)),
):
    """Update active encounter notes. Completed encounters are locked against direct edits."""
    service = EncounterService(db)
    return service.update_encounter(
        encounter_id=encounter_id,
        data=payload,
        current_user=current_user,
    )


@router.post(
    "/encounters/{encounter_id}/complete",
    response_model=EncounterResponse,
    summary="Complete a clinical encounter",
)
def complete_encounter(
    encounter_id: uuid.UUID,
    payload: Optional[EncounterCompleteRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_PRACTITIONERS)),
):
    """Finalize clinical encounter, set completion timestamp, and lock the record."""
    service = EncounterService(db)
    req = payload or EncounterCompleteRequest()
    return service.complete_encounter(
        encounter_id=encounter_id,
        data=req,
        current_user=current_user,
    )


@router.post(
    "/encounters/{encounter_id}/vitals",
    response_model=VitalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record observation vitals for an encounter",
)
def record_vitals(
    encounter_id: uuid.UUID,
    payload: VitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_CLINICAL_STAFF)),
):
    """Record a vitals snapshot (BP, HR, SpO2, Temp, RR) for an active clinical encounter."""
    service = VitalService(db)
    return service.record_vitals(
        encounter_id=encounter_id,
        data=payload,
        current_user=current_user,
    )


@router.get(
    "/encounters/{encounter_id}/vitals",
    response_model=VitalListResponse,
    summary="Get all recorded vitals observations for an encounter",
)
def get_encounter_vitals(
    encounter_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve time-series vitals observations recorded during an encounter."""
    service = VitalService(db)
    return service.get_encounter_vitals(encounter_id=encounter_id, current_user=current_user)
