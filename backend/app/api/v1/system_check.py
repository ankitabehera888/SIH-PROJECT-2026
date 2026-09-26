from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.system_check import SystemCheckCreate, SystemCheckResponse
from app.services.system_check_service import SystemCheckService

router = APIRouter(prefix="/system-checks", tags=["System Checks"])


@router.post("", response_model=SystemCheckResponse, status_code=status.HTTP_201_CREATED)
def create_system_check(
    payload: SystemCheckCreate,
    db: Session = Depends(get_db),
):
    """Record an infrastructure verification event through the Service/Repository layer."""
    service = SystemCheckService(db)
    return service.record_check(payload)


@router.get("", response_model=List[SystemCheckResponse])
def list_system_checks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve recorded verification checks."""
    service = SystemCheckService(db)
    return service.list_checks(skip=skip, limit=limit)


@router.get("/{check_id}", response_model=SystemCheckResponse)
def get_system_check_by_id(
    check_id: int,
    db: Session = Depends(get_db),
):
    """Fetch a specific verification event by ID."""
    service = SystemCheckService(db)
    return service.get_check(check_id)
