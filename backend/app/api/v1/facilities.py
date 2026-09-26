import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.facility import (
    FacilityCreate,
    FacilityListResponse,
    FacilityResponse,
)
from app.services.facility_service import FacilityService

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.post(
    "",
    response_model=FacilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new healthcare facility",
)
def create_facility(
    payload: FacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Register a new Sub-centre, PHC, Rural Hospital, or District Hospital (Admin only)."""
    service = FacilityService(db)
    return service.create_facility(payload)


@router.get(
    "",
    response_model=FacilityListResponse,
    summary="List healthcare facilities",
)
def list_facilities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve directory of active healthcare facilities."""
    service = FacilityService(db)
    skip = (page - 1) * page_size
    return service.list_facilities(skip=skip, limit=page_size)


@router.get(
    "/{facility_id}",
    response_model=FacilityResponse,
    summary="Get healthcare facility details",
)
def get_facility(
    facility_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details for a single facility by UUID."""
    service = FacilityService(db)
    return service.get_facility(facility_id)
