import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class QueueItemSchema(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str
    patient_age: Optional[int] = None
    patient_avatar: Optional[str] = None
    patient_location: Optional[str] = None
    time: str
    reason: str
    mode: str  # 'Video' or 'In-Person'
    priority: str

    model_config = ConfigDict(from_attributes=True)


class ReferralAlertSchema(BaseModel):
    id: uuid.UUID
    patient_name: str
    from_facility: str
    reason: str
    created_at: datetime


class FollowupAlertSchema(BaseModel):
    id: uuid.UUID
    patient_name: str
    condition: str
    due_date: str
    is_overdue: bool


class DoctorDashboardResponse(BaseModel):
    todays_patients_count: int = 0
    pending_consultations_count: int = 0
    pending_referrals_count: int = 0
    followups_due_count: int = 0
    in_person_queue: List[QueueItemSchema] = []
    video_queue: List[QueueItemSchema] = []
    pending_referrals: List[ReferralAlertSchema] = []
    followup_alerts: List[FollowupAlertSchema] = []


class JourneyStepSchema(BaseModel):
    label: str
    status: str  # 'completed', 'current', 'upcoming'
    date: Optional[str] = None


class PatientDashboardResponse(BaseModel):
    next_appointment: Optional[Dict[str, Any]] = None
    referral_status: Optional[Dict[str, Any]] = None
    followup_due: Optional[Dict[str, Any]] = None
    care_journey: List[JourneyStepSchema] = []
    journey_percent: int = 0
    urgent_alerts: List[Dict[str, Any]] = []
    recommended_facilities: List[Dict[str, Any]] = []


class WorkerDashboardResponse(BaseModel):
    todays_patients_count: int = 0
    pending_referrals_count: int = 0
    followups_count: int = 0
    high_priority_count: int = 0
    assigned_facility_name: Optional[str] = None
    recent_patients: List[Dict[str, Any]] = []

