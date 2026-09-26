import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dispensing import (
    DispensingListResponse,
    MedicationDispenseCreate,
    MedicationDispenseResponse,
)
from app.services.dispensing_service import DispensingService

router = APIRouter(prefix="/dispensing", tags=["Medication Dispensing"])


@router.post(
    "",
    response_model=MedicationDispenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record medication dispense / active medication",
)
def record_dispense(
    payload: MedicationDispenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record pharmacy dispensing or register an active medication for a patient."""
    service = DispensingService(db)
    return service.record_dispense(payload)


@router.get(
    "/patients/{patient_id}",
    response_model=DispensingListResponse,
    summary="List active medications for a patient",
)
def list_patient_medications(
    patient_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter status e.g. Active, Completed, Discontinued"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve active and historical medication dispense records for a patient."""
    service = DispensingService(db)
    return service.list_active_medications(patient_id, status_filter=status_filter)


@router.patch(
    "/{dispense_id}/status",
    response_model=MedicationDispenseResponse,
    summary="Update medication dispense status",
)
def update_dispense_status(
    dispense_id: uuid.UUID,
    status_val: str = Query(..., alias="status", description="New status e.g. Active, Completed, Discontinued"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update active medication status (e.g. mark completed or discontinued)."""
    service = DispensingService(db)
    return service.update_status(dispense_id, status_val)
