import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InvoiceCreate(BaseModel):
    patient_id: uuid.UUID = Field(..., description="Target patient UUID")
    encounter_id: Optional[uuid.UUID] = Field(None, description="Linked encounter UUID")
    total_amount: float = Field(..., ge=0, description="Total billed amount")
    due_date: date = Field(..., description="Payment due date")
    notes: Optional[str] = Field(None, description="Invoice description or notes")


class PaymentRecordRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount received")
    payment_method: str = Field("UPI", description="Payment method: CASH, CARD, UPI, INSURANCE")


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    invoice_number: str
    patient_id: uuid.UUID
    patient_name: Optional[str] = None
    encounter_id: Optional[uuid.UUID] = None
    total_amount: float
    paid_amount: float
    balance_due: float = 0.0
    status: str
    due_date: date
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
