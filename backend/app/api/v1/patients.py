import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])

# Role guards
CLINICAL_STAFF = [UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN, UserRole.WORKER]
ELEVATED_STAFF = [UserRole.DOCTOR, UserRole.ADMIN]



@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Register a new patient identity in the healthcare system."""
    service = PatientService(db)
    return service.create_patient(data=payload, created_by_id=current_user.id)


@router.get(
    "/search",
    response_model=PatientListResponse,
    summary="Search patients",
)
def search_patients(
    q: str = Query(..., min_length=1, description="Search query across names, patient number, or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Search patients by substring match."""
    service = PatientService(db)
    return service.search_patients(
        query=q,
        page=page,
        page_size=page_size,
        is_active_only=is_active_only,
    )


@router.get(
    "",
    response_model=PatientListResponse,
    summary="List patients with pagination",
)
def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Retrieve paginated patient directory."""
    service = PatientService(db)
    return service.list_patients(
        page=page,
        page_size=page_size,
        is_active_only=is_active_only,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by UUID",
)
def get_patient_by_id(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Retrieve demographic details for a single patient."""
    service = PatientService(db)
    return service.get_patient(patient_id)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient demographic details",
)
def update_patient(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*CLINICAL_STAFF)),
):
    """Update contact, demographic, or emergency contact details for a patient."""
    service = PatientService(db)
    return service.update_patient(
        patient_id=patient_id,
        data=payload,
        updated_by_id=current_user.id,
    )


@router.delete(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Soft-deactivate patient record",
)
def deactivate_patient(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ELEVATED_STAFF)),
):
    """Soft deactivation for patient records. Does not physically delete historical healthcare data."""
    service = PatientService(db)
    return service.deactivate_patient(
        patient_id=patient_id,
        updated_by_id=current_user.id,
    )
