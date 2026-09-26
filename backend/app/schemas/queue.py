import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class QueuePriorityEnum(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class QueueStatusEnum(str, Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class CheckInRequest(BaseModel):
    priority: QueuePriorityEnum = QueuePriorityEnum.NORMAL


class QueueEntryResponse(BaseModel):
    id: uuid.UUID
    appointment_id: uuid.UUID
    patient_id: uuid.UUID
    facility_id: uuid.UUID
    queue_date: date
    queue_number: str
    priority: QueuePriorityEnum
    status: QueueStatusEnum
    checked_in_at: datetime
    called_at: Optional[datetime] = None
    consultation_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueueListResponse(BaseModel):
    items: List[QueueEntryResponse]
    facility_id: uuid.UUID
    queue_date: date
    total: int
