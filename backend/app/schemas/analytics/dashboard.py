from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel

class AppointmentSummaryResponse(BaseModel):
    appointment_volume: int
    completed_appointments: int
    completion_rate: Optional[Decimal] = None
    cancelled_appointments: int
    cancellation_rate: Optional[Decimal] = None
    no_show_appointments: int
    no_show_rate: Optional[Decimal] = None
    average_wait_minutes: Decimal
    median_wait_minutes: Decimal

class AppointmentTrendPoint(BaseModel):
    period: str
    appointments: int
    completed: int
    cancelled: int
    no_show: int

class AppointmentTrendsResponse(BaseModel):
    data: List[AppointmentTrendPoint]

class ReferralSummaryResponse(BaseModel):
    referral_volume: int
    completed_referrals: int
    completion_rate: Optional[Decimal] = None
    pending_referrals: int
    pending_rate: Optional[Decimal] = None
    average_completion_days: Decimal

class ReferralAgingBucket(BaseModel):
    bucket: str
    count: int

class ReferralAgingResponse(BaseModel):
    buckets: List[ReferralAgingBucket]

class CohortSummaryItem(BaseModel):
    cohort_name: str
    cohort_version: str
    eligible_patients: int
    risk_score_avg: Optional[Decimal] = None
    active_criteria: str

class CohortSummaryResponse(BaseModel):
    data: List[CohortSummaryItem]

class DashboardOverviewResponse(BaseModel):
    period: Dict[str, date]
    appointments: Dict[str, Optional[Decimal]]
    encounters: Dict[str, Optional[Decimal]]
    referrals: Dict[str, Optional[Decimal]]
    chronic_care: Dict[str, Optional[Decimal]]
    access: Dict[str, Optional[Decimal]]
