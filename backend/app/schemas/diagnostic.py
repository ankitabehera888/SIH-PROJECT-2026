import math
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DiagnosticOrderStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DiagnosticOrderPriorityEnum(str, Enum):
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    STAT = "STAT"


class DiagnosticItemStatusEnum(str, Enum):
    PENDING = "PENDING"
    SAMPLE_COLLECTED = "SAMPLE_COLLECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DiagnosticResultStatusEnum(str, Enum):
    PRELIMINARY = "PRELIMINARY"
    FINAL = "FINAL"
    CORRECTED = "CORRECTED"


# Diagnostic Test Catalog Schemas
class DiagnosticTestCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field("HEMATOLOGY", max_length=100)
    specimen_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class DiagnosticTestResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    category: str
    specimen_type: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiagnosticTestListResponse(BaseModel):
    items: List[DiagnosticTestResponse]
    total: int


# Diagnostic Result Schemas
class DiagnosticResultCreate(BaseModel):
    result_value: str = Field(..., min_length=1, max_length=255)
    unit: Optional[str] = Field(None, max_length=50)
    reference_range: Optional[str] = Field(None, max_length=100)
    abnormal_flag: bool = False
    notes: Optional[str] = None


class DiagnosticResultResponse(BaseModel):
    id: uuid.UUID
    diagnostic_order_item_id: uuid.UUID
    patient_id: uuid.UUID
    result_value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: bool
    result_status: DiagnosticResultStatusEnum
    notes: Optional[str] = None
    performed_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[int] = None
    created_at: datetime
    created_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Diagnostic Order Item Schemas
class DiagnosticOrderItemCreate(BaseModel):
    diagnostic_test_id: uuid.UUID
    notes: Optional[str] = None


class DiagnosticOrderItemResponse(BaseModel):
    id: uuid.UUID
    diagnostic_order_id: uuid.UUID
    diagnostic_test_id: uuid.UUID
    status: DiagnosticItemStatusEnum
    specimen_collected_at: Optional[datetime] = None
    performed_at: Optional[datetime] = None
    notes: Optional[str] = None
    test: Optional[DiagnosticTestResponse] = None
    result: Optional[DiagnosticResultResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Diagnostic Order Schemas
class DiagnosticOrderCreate(BaseModel):
    items: List[DiagnosticOrderItemCreate] = Field(..., min_length=1)
    priority: DiagnosticOrderPriorityEnum = DiagnosticOrderPriorityEnum.ROUTINE
    notes: Optional[str] = None


class DiagnosticOrderCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class DiagnosticOrderResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    encounter_id: uuid.UUID
    ordering_provider_id: int
    facility_id: uuid.UUID
    status: DiagnosticOrderStatusEnum
    priority: DiagnosticOrderPriorityEnum
    ordered_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancellation_reason: Optional[str] = None
    items: List[DiagnosticOrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DiagnosticOrderListResponse(BaseModel):
    items: List[DiagnosticOrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[DiagnosticOrderResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
