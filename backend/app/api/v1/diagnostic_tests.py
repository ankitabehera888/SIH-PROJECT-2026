from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.diagnostic import (
    DiagnosticTestCreate,
    DiagnosticTestListResponse,
    DiagnosticTestResponse,
)
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(prefix="/diagnostic-tests", tags=["Diagnostic Tests"])


@router.post(
    "",
    response_model=DiagnosticTestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add diagnostic test to catalog",
)
def create_test(
    payload: DiagnosticTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """Add a new laboratory, imaging, or pathology test to the system diagnostic catalog."""
    service = DiagnosticService(db)
    return service.create_test(data=payload)


@router.get(
    "",
    response_model=DiagnosticTestListResponse,
    summary="List diagnostic tests catalog",
)
def list_tests(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all available diagnostic investigations in the test catalog."""
    service = DiagnosticService(db)
    return service.list_tests(active_only=active_only)
