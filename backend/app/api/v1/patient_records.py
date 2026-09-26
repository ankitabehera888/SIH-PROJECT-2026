import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.patient_record import (
    PatientRecordResponse,
    PatientTimelineResponse,
)
from app.services.patient_record_service import PatientRecordService

router = APIRouter(prefix="/patients", tags=["Patient Records"])


@router.get(
    "/{patient_id}/record",
    response_model=PatientRecordResponse,
    summary="Get longitudinal patient health record",
)
def get_patient_record(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full assembled longitudinal health record including demographics, summary, timeline, encounters, vitals, prescriptions, diagnostics, referrals, and appointments."""
    service = PatientRecordService(db)
    return service.get_patient_record(patient_id=patient_id, current_user=current_user)


@router.get(
    "/{patient_id}/timeline",
    response_model=PatientTimelineResponse,
    summary="Get chronological clinical timeline stream",
)
def get_patient_timeline(
    patient_id: uuid.UUID,
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. ENCOUNTER, PRESCRIPTION, DIAGNOSTIC_RESULT)"),
    from_date: Optional[str] = Query(None, description="Filter events on or after ISO datetime"),
    to_date: Optional[str] = Query(None, description="Filter events on or before ISO datetime"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve filtered, paginated chronological clinical events stream for a patient."""
    service = PatientRecordService(db)
    return service.get_patient_timeline(
        patient_id=patient_id,
        current_user=current_user,
        event_type=event_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
    )
