import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    PaymentRecordRequest,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing & Invoicing"])


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create healthcare service invoice",
)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a billing invoice for clinical services, consultations, or lab tests."""
    service = BillingService(db)
    return service.create_invoice(payload)


@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    summary="List billing invoices",
)
def list_invoices(
    patient_id: Optional[uuid.UUID] = Query(None, description="Filter by patient UUID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: UNPAID, PARTIAL, PAID, CANCELLED"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve list of invoices with optional patient and status filters."""
    service = BillingService(db)
    return service.list_invoices(patient_id=patient_id, status_filter=status_filter)


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get invoice details by UUID",
)
def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details for a specific billing invoice."""
    service = BillingService(db)
    return service.get_invoice(invoice_id)


@router.post(
    "/invoices/{invoice_id}/pay",
    response_model=InvoiceResponse,
    summary="Record payment against invoice",
)
def record_payment(
    invoice_id: uuid.UUID,
    payload: PaymentRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process a payment (Cash, Card, UPI, Insurance) against an active invoice."""
    service = BillingService(db)
    return service.record_payment(invoice_id, payload)
