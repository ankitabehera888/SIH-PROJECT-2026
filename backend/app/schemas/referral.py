import math
import uuid
from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ReferralStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class ReferralTypeEnum(str, Enum):
    SPECIALIST = "SPECIALIST"
    DIAGNOSTIC = "DIAGNOSTIC"
    EMERGENCY = "EMERGENCY"
    HIGHER_CARE = "HIGHER_CARE"
    FOLLOW_UP = "FOLLOW_UP"


class ReferralPriorityEnum(str, Enum):
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    EMERGENCY = "EMERGENCY"


class ReferralCreate(BaseModel):
    receiving_facility_id: uuid.UUID
    referral_type: ReferralTypeEnum = ReferralTypeEnum.SPECIALIST
    priority: ReferralPriorityEnum = ReferralPriorityEnum.ROUTINE
    requested_specialty: Optional[str] = Field(None, max_length=100)
    reason: str = Field(..., min_length=3, max_length=255)
    clinical_summary: Optional[str] = None
    requested_date: Optional[date] = None


class ReferralRejectRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class ReferralScheduleRequest(BaseModel):
    scheduled_date: date
    scheduled_time: time
    notes: Optional[str] = None


class ReferralCompleteRequest(BaseModel):
    outcome_status: str = Field(..., min_length=2, max_length=100)
    outcome_notes: str = Field(..., min_length=3)
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None


class ReferralCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class ReferralResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    encounter_id: uuid.UUID
    referring_facility_id: uuid.UUID
    referring_provider_id: int
    receiving_facility_id: uuid.UUID
    receiving_provider_id: Optional[int] = None
    referral_type: ReferralTypeEnum
    priority: ReferralPriorityEnum
    status: ReferralStatusEnum
    reason: str
    clinical_summary: Optional[str] = None
    requested_specialty: Optional[str] = None
    requested_date: Optional[date] = None

    # Lifecycle & Audit Metadata
    created_at: datetime
    created_by: Optional[int] = None
    accepted_at: Optional[datetime] = None
    accepted_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    scheduled_by: Optional[int] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None
    outcome_status: Optional[str] = None
    outcome_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancellation_reason: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ReferralListResponse(BaseModel):
    items: List[ReferralResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[ReferralResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
