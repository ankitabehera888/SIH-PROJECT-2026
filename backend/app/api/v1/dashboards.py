from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard_views import (
    DoctorDashboardResponse,
    PatientDashboardResponse,
    WorkerDashboardResponse,
)
from app.services.dashboard_view_service import DashboardViewService

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get(
    "/doctor",
    response_model=DoctorDashboardResponse,
    summary="Get Doctor Dashboard operational summary and queues",
)
def get_doctor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve consolidated operational metrics, split in-person/video queues, and alerts for doctors."""
    service = DashboardViewService(db)
    return service.get_doctor_dashboard(current_user)


@router.get(
    "/patient",
    response_model=PatientDashboardResponse,
    summary="Get Patient Dashboard personal summary and care journey",
)
def get_patient_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve next appointment, care journey progress, urgent alerts, and recommended facilities for patients."""
    service = DashboardViewService(db)
    return service.get_patient_dashboard(current_user)


@router.get(
    "/worker",
    response_model=WorkerDashboardResponse,
    summary="Get Worker/CHW Dashboard operational metrics",
)
def get_worker_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve community health worker stats, assigned facility name, and recent patients."""
    service = DashboardViewService(db)
    return service.get_worker_dashboard(current_user)

