import math
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EncounterStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class EncounterTypeEnum(str, Enum):
    OUTPATIENT = "OUTPATIENT"
    EMERGENCY = "EMERGENCY"
    INPATIENT = "INPATIENT"
    FOLLOW_UP = "FOLLOW_UP"
    HOME_VISIT = "HOME_VISIT"


class EncounterCreate(BaseModel):
    patient_id: uuid.UUID
    provider_id: int
    facility_id: uuid.UUID
    appointment_id: Optional[uuid.UUID] = None
    encounter_type: EncounterTypeEnum = EncounterTypeEnum.OUTPATIENT
    chief_complaint: Optional[str] = Field(None, max_length=255)
    clinical_notes: Optional[str] = None


class EncounterUpdate(BaseModel):
    chief_complaint: Optional[str] = Field(None, max_length=255)
    clinical_notes: Optional[str] = None


class EncounterCompleteRequest(BaseModel):
    clinical_notes: Optional[str] = None


class EncounterResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    appointment_id: Optional[uuid.UUID] = None
    provider_id: int
    facility_id: uuid.UUID
    encounter_type: EncounterTypeEnum
    status: EncounterStatusEnum
    started_at: datetime
    ended_at: Optional[datetime] = None
    chief_complaint: Optional[str] = None
    clinical_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class EncounterListResponse(BaseModel):
    items: List[EncounterResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[EncounterResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
