import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionCancelRequest,
    PrescriptionCreate,
    PrescriptionListResponse,
    PrescriptionResponse,
)
from app.services.prescription_service import PrescriptionService

router = APIRouter(tags=["Prescriptions"])

PRESCRIBER_ROLES = [UserRole.DOCTOR, UserRole.ADMIN]


@router.post(
    "/encounters/{encounter_id}/prescriptions",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and issue prescription for an encounter",
)
def create_prescription(
    encounter_id: uuid.UUID,
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*PRESCRIBER_ROLES)),
):
    """Licensed prescriber generates a prescription with validated medication line items."""
    service = PrescriptionService(db)
    return service.create_from_encounter(
        encounter_id=encounter_id,
        data=payload,
        current_user=current_user,
    )


@router.get(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionResponse,
    summary="Get prescription details",
)
def get_prescription(
    prescription_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full details and items of a specific prescription."""
    service = PrescriptionService(db)
    return service.get_prescription(prescription_id=prescription_id, current_user=current_user)


@router.get(
    "/patients/{patient_id}/prescriptions",
    response_model=PrescriptionListResponse,
    summary="Get longitudinal prescription history for patient",
)
def get_patient_prescriptions(
    patient_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated prescription history for a patient."""
    service = PrescriptionService(db)
    return service.list_patient_prescriptions(
        patient_id=patient_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/encounters/{encounter_id}/prescriptions",
    response_model=List[PrescriptionResponse],
    summary="Get prescriptions created during encounter",
)
def get_encounter_prescriptions(
    encounter_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all prescriptions written during a clinical encounter."""
    service = PrescriptionService(db)
    return service.list_encounter_prescriptions(encounter_id=encounter_id, current_user=current_user)


@router.post(
    "/prescriptions/{prescription_id}/issue",
    response_model=PrescriptionResponse,
    summary="Issue prescription",
)
def issue_prescription(
    prescription_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*PRESCRIBER_ROLES)),
):
    """Formally issue a draft prescription."""
    service = PrescriptionService(db)
    return service.issue_prescription(prescription_id=prescription_id, current_user=current_user)


@router.post(
    "/prescriptions/{prescription_id}/cancel",
    response_model=PrescriptionResponse,
    summary="Cancel prescription with audit reason",
)
def cancel_prescription(
    prescription_id: uuid.UUID,
    payload: PrescriptionCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*PRESCRIBER_ROLES)),
):
    """Cancel a prescription and record reason and clinician provenance."""
    service = PrescriptionService(db)
    return service.cancel_prescription(prescription_id=prescription_id, data=payload, current_user=current_user)
