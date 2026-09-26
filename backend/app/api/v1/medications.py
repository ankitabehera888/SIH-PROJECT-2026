import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.medication import (
    MedicationCreate,
    MedicationListResponse,
    MedicationResponse,
)
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.post(
    "",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add medication to catalog",
)
def create_medication(
    payload: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """Add a new pharmaceutical drug or formulation to the system medication catalog."""
    service = MedicationService(db)
    return service.create_medication(data=payload)


@router.get(
    "",
    response_model=MedicationListResponse,
    summary="List medications catalog",
)
def list_medications(
    active_only: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated medications from the formulary catalog."""
    service = MedicationService(db)
    return service.list_medications(active_only=active_only, page=page, page_size=page_size)


@router.get(
    "/{medication_id}",
    response_model=MedicationResponse,
    summary="Get medication details",
)
def get_medication(
    medication_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details for a specific medication by ID."""
    service = MedicationService(db)
    return service.get_medication(medication_id=medication_id)
