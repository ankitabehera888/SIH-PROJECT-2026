import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.diagnostic import (
    DiagnosticOrderCancelRequest,
    DiagnosticOrderCreate,
    DiagnosticOrderListResponse,
    DiagnosticOrderResponse,
    DiagnosticResultCreate,
    DiagnosticResultResponse,
)
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(tags=["Diagnostics"])

ORDERING_ROLES = [UserRole.DOCTOR, UserRole.ADMIN]
LAB_ROLES = [UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]


@router.post(
    "/encounters/{encounter_id}/diagnostic-orders",
    response_model=DiagnosticOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create diagnostic investigation order",
)
def create_diagnostic_order(
    encounter_id: uuid.UUID,
    payload: DiagnosticOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ORDERING_ROLES)),
):
    """Clinical practitioner orders diagnostic laboratory or imaging tests for an encounter."""
    service = DiagnosticService(db)
    return service.create_order_from_encounter(
        encounter_id=encounter_id,
        data=payload,
        current_user=current_user,
    )


@router.get(
    "/diagnostic-orders/{order_id}",
    response_model=DiagnosticOrderResponse,
    summary="Get diagnostic order details",
)
def get_diagnostic_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details and line items for a diagnostic order."""
    service = DiagnosticService(db)
    return service.get_order(order_id=order_id, current_user=current_user)


@router.get(
    "/patients/{patient_id}/diagnostic-orders",
    response_model=DiagnosticOrderListResponse,
    summary="Get longitudinal diagnostic order history for patient",
)
def get_patient_diagnostic_orders(
    patient_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve historical diagnostic investigation orders for a patient."""
    service = DiagnosticService(db)
    return service.list_patient_orders(
        patient_id=patient_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/encounters/{encounter_id}/diagnostic-orders",
    response_model=List[DiagnosticOrderResponse],
    summary="Get diagnostic orders placed during encounter",
)
def get_encounter_diagnostic_orders(
    encounter_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all diagnostic orders placed during an encounter."""
    service = DiagnosticService(db)
    return service.list_encounter_orders(encounter_id=encounter_id, current_user=current_user)


@router.post(
    "/diagnostic-orders/{order_id}/cancel",
    response_model=DiagnosticOrderResponse,
    summary="Cancel diagnostic order",
)
def cancel_diagnostic_order(
    order_id: uuid.UUID,
    payload: DiagnosticOrderCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ORDERING_ROLES)),
):
    """Cancel a diagnostic order and record reason and clinician provenance."""
    service = DiagnosticService(db)
    return service.cancel_order(order_id=order_id, data=payload, current_user=current_user)


@router.post(
    "/diagnostic-order-items/{item_id}/result",
    response_model=DiagnosticResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record verified diagnostic result",
)
def record_diagnostic_result(
    item_id: uuid.UUID,
    payload: DiagnosticResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*LAB_ROLES)),
):
    """Authorized laboratory or diagnostic staff records and verifies an investigation result."""
    service = DiagnosticService(db)
    return service.record_result(item_id=item_id, data=payload, current_user=current_user)


@router.get(
    "/diagnostic-order-items/{item_id}/result",
    response_model=DiagnosticResultResponse,
    summary="Get diagnostic result for order item",
)
def get_diagnostic_result(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the verified result finding for a specific diagnostic order item."""
    service = DiagnosticService(db)
    return service.get_item_result(item_id=item_id, current_user=current_user)
