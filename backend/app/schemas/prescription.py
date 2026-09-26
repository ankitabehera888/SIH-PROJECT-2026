import math
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.medication import MedicationResponse


class PrescriptionStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PrescriptionItemCreate(BaseModel):
    medication_id: uuid.UUID
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field("ONCE_DAILY", max_length=100)
    duration: int = Field(1, ge=1)
    duration_unit: str = Field("DAYS", max_length=50)
    route: str = Field("ORAL", max_length=50)
    quantity: int = Field(1, ge=1)
    instructions: Optional[str] = None
    notes: Optional[str] = None


class PrescriptionItemResponse(BaseModel):
    id: uuid.UUID
    prescription_id: uuid.UUID
    medication_id: uuid.UUID
    dosage: str
    frequency: str
    duration: int
    duration_unit: str
    route: str
    quantity: int
    instructions: Optional[str] = None
    notes: Optional[str] = None
    medication: Optional[MedicationResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PrescriptionCreate(BaseModel):
    items: List[PrescriptionItemCreate] = Field(..., min_length=1)
    notes: Optional[str] = None


class PrescriptionCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class PrescriptionResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    encounter_id: uuid.UUID
    prescriber_id: int
    facility_id: uuid.UUID
    status: PrescriptionStatusEnum
    prescribed_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    created_by: Optional[int] = None
    issued_at: Optional[datetime] = None
    issued_by: Optional[int] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancellation_reason: Optional[str] = None
    items: List[PrescriptionItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PrescriptionListResponse(BaseModel):
    items: List[PrescriptionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[PrescriptionResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
