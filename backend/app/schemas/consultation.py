import math
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ConsultationTypeEnum(str, Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    ASSISTED_VIDEO = "ASSISTED_VIDEO"


class ConsultationStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    EXPIRED = "EXPIRED"


class ParticipantRoleEnum(str, Enum):
    PATIENT = "PATIENT"
    PROVIDER = "PROVIDER"
    HEALTH_WORKER = "HEALTH_WORKER"


class ConnectionStatusEnum(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"


class ConsultationCreate(BaseModel):
    consultation_type: ConsultationTypeEnum = ConsultationTypeEnum.VIDEO


class ConsultationParticipantResponse(BaseModel):
    id: uuid.UUID
    consultation_id: uuid.UUID
    user_id: int
    role: str
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    duration_seconds: int = 0
    connection_status: str
    reconnect_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ConsultationResponse(BaseModel):
    id: uuid.UUID
    appointment_id: uuid.UUID
    patient_id: uuid.UUID
    provider_id: int
    facility_id: uuid.UUID
    consultation_type: str
    status: str
    room_name: str
    room_url: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    encounter_id: Optional[uuid.UUID] = None
    participants: List[ConsultationParticipantResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsultationListResponse(BaseModel):
    items: List[ConsultationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[ConsultationResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class ConsultationJoinResponse(BaseModel):
    consultation_id: uuid.UUID
    room_name: str
    room_url: str
    token: str
    role: str
    expires_at: datetime


class ConsultationCancelRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=255)


class DailyWebhookPayload(BaseModel):
    version: Optional[str] = None
    event: str
    room: Optional[str] = None
    payload: Dict[str, Any] = {}
