from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CohortDefinition:
    name: str
    version: str
    description: str
    inclusion_criteria: str
    exclusion_criteria: str
    index_date_rule: str
    observation_window_days: int
    sql_file: str

COHORT_DEFINITIONS: List[CohortDefinition] = [
    CohortDefinition(
        name="diabetes",
        version="v1.0",
        description="Patients with confirmed or suspected Diabetes Mellitus",
        inclusion_criteria="Documented diabetes diagnosis/complaint OR anti-diabetic prescription",
        exclusion_criteria="Invalid/unverified patient identifiers",
        index_date_rule="Earliest qualifying diabetes encounter or medication date",
        observation_window_days=365,
        sql_file="diabetes.sql"
    ),
    CohortDefinition(
        name="hypertension",
        version="v1.0",
        description="Patients with Essential Hypertension or elevated blood pressure",
        inclusion_criteria="Documented hypertension diagnosis OR elevated BP (SBP >= 140 or DBP >= 90)",
        exclusion_criteria="Invalid clinical vitals records",
        index_date_rule="Earliest qualifying hypertension encounter or elevated reading date",
        observation_window_days=365,
        sql_file="hypertension.sql"
    ),
    CohortDefinition(
        name="high_risk",
        version="v1.0",
        description="High-risk patients identified by multi-factor clinical risk score",
        inclusion_criteria="Weighted composite clinical risk score >= 30.0",
        exclusion_criteria="Deceased or inactive patient accounts",
        index_date_rule="Assessment evaluation date",
        observation_window_days=180,
        sql_file="high_risk.sql"
    ),
    CohortDefinition(
        name="missed_appointments",
        version="v1.0",
        description="Patients with cancelled appointments or missed visits (no-show)",
        inclusion_criteria="Appointment status in ('cancelled', 'no_show') or is_cancelled = TRUE",
        exclusion_criteria="Future scheduled appointments",
        index_date_rule="Latest missed appointment scheduled date",
        observation_window_days=90,
        sql_file="missed_appointments.sql"
    ),
    CohortDefinition(
        name="pending_referrals",
        version="v1.0",
        description="Patients with unresolved care transfers and pending specialist referrals",
        inclusion_criteria="Referral records with is_completed = FALSE",
        exclusion_criteria="Completed or rejected referrals",
        index_date_rule="Referral request creation date",
        observation_window_days=60,
        sql_file="pending_referrals.sql"
    ),
    CohortDefinition(
        name="chronic_followup",
        version="v1.0",
        description="Patients with chronic conditions overdue for follow-up (>= 180 days)",
        inclusion_criteria="Documented chronic condition and time since last visit >= 180 days",
        exclusion_criteria="Patients with encounter within last 180 days",
        index_date_rule="Most recent clinical encounter date",
        observation_window_days=180,
        sql_file="chronic_followup.sql"
    ),
]
