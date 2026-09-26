import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.followup import FollowupPriority, FollowupStatus


class FollowupCreate(BaseModel):
    patient_id: uuid.UUID = Field(..., description="Target patient UUID")
    provider_id: Optional[int] = Field(None, description="Assigned clinician user ID")
    encounter_id: Optional[uuid.UUID] = Field(None, description="Linked clinical encounter UUID")
    condition: str = Field(..., min_length=1, description="Medical condition or reason for follow-up")
    priority: FollowupPriority = Field(FollowupPriority.ROUTINE, description="Priority level")
    scheduled_date: date = Field(..., description="Scheduled follow-up date")
    completion_rate: int = Field(0, ge=0, le=100, description="Completion progress (0-100%)")
    notes: Optional[str] = Field(None, description="Clinical notes or instructions")


class FollowupRescheduleRequest(BaseModel):
    new_date: date = Field(..., description="New scheduled follow-up date")
    reason: Optional[str] = Field(None, description="Reason for rescheduling")


class FollowupCompleteRequest(BaseModel):
    completion_rate: int = Field(100, ge=0, le=100, description="Final completion rate percentage")
    notes: Optional[str] = Field(None, description="Completion clinical notes")


class FollowupResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: Optional[str] = None
    provider_id: Optional[int] = None
    assigned_doctor: Optional[str] = None
    encounter_id: Optional[uuid.UUID] = None
    condition: str
    priority: str
    status: str
    scheduled_date: date
    completed_at: Optional[datetime] = None
    completion_rate: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FollowupSummary(BaseModel):
    upcoming: int = 0
    missed: int = 0
    completed: int = 0
    total: int = 0


class FollowupListResponse(BaseModel):
    summary: FollowupSummary
    items: List[FollowupResponse]
    total: int
