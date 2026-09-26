import math
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.appointment import AppointmentResponse
from app.schemas.diagnostic import DiagnosticOrderResponse
from app.schemas.encounter import EncounterResponse
from app.schemas.patient import PatientResponse
from app.schemas.prescription import PrescriptionResponse
from app.schemas.referral import ReferralResponse


class TimelineEventType(str, Enum):
    APPOINTMENT = "APPOINTMENT"
    ENCOUNTER = "ENCOUNTER"
    VITAL = "VITAL"
    PRESCRIPTION = "PRESCRIPTION"
    DIAGNOSTIC_ORDER = "DIAGNOSTIC_ORDER"
    DIAGNOSTIC_RESULT = "DIAGNOSTIC_RESULT"
    REFERRAL = "REFERRAL"


class PatientTimelineEvent(BaseModel):
    event_id: str
    event_type: TimelineEventType
    event_date: datetime
    title: str
    summary_text: str
    source_id: uuid.UUID
    facility_id: Optional[uuid.UUID] = None
    provider_id: Optional[int] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PatientRecordSummary(BaseModel):
    total_encounters: int = 0
    total_vitals_recorded: int = 0
    total_prescriptions: int = 0
    total_diagnostic_orders: int = 0
    total_referrals: int = 0
    total_appointments: int = 0
    last_encounter_at: Optional[datetime] = None
    last_facility_id: Optional[uuid.UUID] = None


class PatientTimelineResponse(BaseModel):
    items: List[PatientTimelineEvent]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[PatientTimelineEvent], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class PatientRecordResponse(BaseModel):
    patient: PatientResponse
    summary: PatientRecordSummary
    timeline: List[PatientTimelineEvent] = []
    encounters: List[EncounterResponse] = []
    prescriptions: List[PrescriptionResponse] = []
    diagnostic_orders: List[DiagnosticOrderResponse] = []
    referrals: List[ReferralResponse] = []
    appointments: List[AppointmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
