import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.consultation import (
    ConsultationCancelRequest,
    ConsultationCreate,
    ConsultationJoinResponse,
    ConsultationListResponse,
    ConsultationParticipantResponse,
    ConsultationResponse,
)
from app.services.consultation_service import ConsultationService

router = APIRouter(tags=["Teleconsultation"])


@router.post(
    "/appointments/{appointment_id}/consultation",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a teleconsultation session for a scheduled appointment",
)
def create_consultation(
    appointment_id: uuid.UUID,
    data: ConsultationCreate = ConsultationCreate(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.create_consultation(appointment_id, data, current_user)


@router.get(
    "/consultations/{consultation_id}",
    response_model=ConsultationResponse,
    summary="Retrieve teleconsultation session details and participant attendance",
)
def get_consultation(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.get_consultation(consultation_id, current_user)


@router.get(
    "/consultations",
    response_model=ConsultationListResponse,
    summary="List teleconsultation sessions for the authenticated user",
)
def list_consultations(
    status: Optional[str] = Query(None, description="Filter by status (SCHEDULED, READY, IN_PROGRESS, COMPLETED, CANCELLED)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.list_consultations(current_user, status=status, page=page, page_size=page_size)


@router.post(
    "/consultations/{consultation_id}/join",
    response_model=ConsultationJoinResponse,
    summary="Authenticate and generate Daily.co WebRTC room meeting token",
)
def join_consultation(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.generate_join_credentials(consultation_id, current_user)


@router.post(
    "/consultations/{consultation_id}/end",
    response_model=ConsultationResponse,
    summary="Conclude teleconsultation and link to clinical encounter",
)
def end_consultation(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.end_consultation(consultation_id, current_user)


@router.post(
    "/consultations/{consultation_id}/cancel",
    response_model=ConsultationResponse,
    summary="Cancel a scheduled or pending teleconsultation session",
)
def cancel_consultation(
    consultation_id: uuid.UUID,
    data: ConsultationCancelRequest = ConsultationCancelRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.cancel_consultation(consultation_id, data, current_user)


@router.get(
    "/consultations/{consultation_id}/participants",
    response_model=List[ConsultationParticipantResponse],
    summary="Get participant attendance and connection log for a consultation",
)
def list_participants(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    return service.list_participants(consultation_id, current_user)
