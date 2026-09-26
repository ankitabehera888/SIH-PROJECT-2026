import math
import uuid
from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppointmentStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    WAITING = "WAITING"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class AppointmentTypeEnum(str, Enum):
    GENERAL_CONSULTATION = "GENERAL_CONSULTATION"
    FOLLOW_UP = "FOLLOW_UP"
    SPECIALIST_REFERRAL = "SPECIALIST_REFERRAL"
    EMERGENCY_TRIAGE = "EMERGENCY_TRIAGE"
    MATERNAL_CHILD_CARE = "MATERNAL_CHILD_CARE"


class AppointmentBase(BaseModel):
    patient_id: uuid.UUID
    provider_id: int
    facility_id: uuid.UUID
    appointment_date: date
    start_time: time
    end_time: time
    appointment_type: AppointmentTypeEnum = AppointmentTypeEnum.GENERAL_CONSULTATION
    reason: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

    @field_validator("appointment_date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentRescheduleRequest(BaseModel):
    appointment_date: date
    start_time: time
    end_time: time

    @field_validator("appointment_date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Rescheduled date cannot be in the past")
        return v


class AppointmentCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=255)


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    provider_id: int
    facility_id: uuid.UUID
    appointment_date: date
    start_time: time
    end_time: time
    appointment_type: AppointmentTypeEnum
    status: AppointmentStatusEnum
    reason: Optional[str] = None
    notes: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentListResponse(BaseModel):
    items: List[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[AppointmentResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
