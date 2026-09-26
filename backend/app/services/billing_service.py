import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.billing import Invoice
from app.models.patient import Patient
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    PaymentRecordRequest,
)


class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def create_invoice(self, data: InvoiceCreate) -> InvoiceResponse:
        patient = self.db.get(Patient, data.patient_id)
        if not patient:
            raise AppException(status_code=404, detail="Patient not found")

        count = self.db.query(Invoice).count() + 1
        inv_num = f"INV-{datetime.now().year}-{count:05d}"

        invoice = Invoice(
            invoice_number=inv_num,
            patient_id=data.patient_id,
            encounter_id=data.encounter_id,
            total_amount=data.total_amount,
            paid_amount=0.0,
            status="UNPAID",
            due_date=data.due_date,
            notes=data.notes,
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return self._to_response(invoice)

    def get_invoice(self, invoice_id: uuid.UUID) -> InvoiceResponse:
        invoice = self.db.get(Invoice, invoice_id)
        if not invoice:
            raise AppException(status_code=404, detail="Invoice not found")
        return self._to_response(invoice)

    def list_invoices(
        self, patient_id: Optional[uuid.UUID] = None, status_filter: Optional[str] = None
    ) -> InvoiceListResponse:
        stmt = select(Invoice).order_by(desc(Invoice.created_at))
        if patient_id:
            stmt = stmt.where(Invoice.patient_id == patient_id)
        if status_filter:
            stmt = stmt.where(Invoice.status == status_filter)

        invoices = self.db.scalars(stmt).all()
        resp_items = [self._to_response(inv) for inv in invoices]
        return InvoiceListResponse(items=resp_items, total=len(resp_items))

    def record_payment(self, invoice_id: uuid.UUID, data: PaymentRecordRequest) -> InvoiceResponse:
        invoice = self.db.get(Invoice, invoice_id)
        if not invoice:
            raise AppException(status_code=404, detail="Invoice not found")

        invoice.paid_amount += data.amount
        invoice.payment_method = data.payment_method

        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = "PAID"
        elif invoice.paid_amount > 0:
            invoice.status = "PARTIAL"

        self.db.commit()
        self.db.refresh(invoice)
        return self._to_response(invoice)

    def _to_response(self, inv: Invoice) -> InvoiceResponse:
        patient_name = f"{inv.patient.first_name} {inv.patient.last_name}" if inv.patient else "Patient"
        balance = max(0.0, inv.total_amount - inv.paid_amount)
        return InvoiceResponse(
            id=inv.id,
            invoice_number=inv.invoice_number,
            patient_id=inv.patient_id,
            patient_name=patient_name,
            encounter_id=inv.encounter_id,
            total_amount=inv.total_amount,
            paid_amount=inv.paid_amount,
            balance_due=balance,
            status=inv.status,
            due_date=inv.due_date,
            payment_method=inv.payment_method,
            notes=inv.notes,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
        )
