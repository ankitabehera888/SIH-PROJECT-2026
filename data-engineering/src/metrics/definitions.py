from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricDefinition:
    metric_code: str
    metric_name: str
    description: str
    metric_type: str  # 'COUNT', 'RATE', 'AVERAGE', 'MEDIAN', 'DURATION', 'AGING'
    numerator_definition: Optional[str]
    denominator_definition: Optional[str]
    population_definition: str
    exclusion_definition: str
    time_basis: str
    grain: str
    source_tables: str
    calculation_version: str = "1.0.0"

METRIC_CATALOG: List[MetricDefinition] = [
    # Appointment Metrics
    MetricDefinition(
        metric_code="appointment_volume",
        metric_name="Appointment Volume",
        description="Total scheduled and registered patient appointments",
        metric_type="COUNT",
        numerator_definition="Count of appointments in reporting period",
        denominator_definition="N/A",
        population_definition="All patient appointment records",
        exclusion_definition="None",
        time_basis="Appointment date",
        grain="Reporting period",
        source_tables="analytics.fact_appointment"
    ),
    MetricDefinition(
        metric_code="appointment_completion_rate",
        metric_name="Appointment Completion Rate",
        description="Percentage of eligible appointments successfully completed",
        metric_type="RATE",
        numerator_definition="Count of appointments with is_completed = TRUE",
        denominator_definition="Total eligible appointments",
        population_definition="Eligible appointment records",
        exclusion_definition="None",
        time_basis="Appointment date",
        grain="Reporting period",
        source_tables="analytics.fact_appointment"
    ),
    MetricDefinition(
        metric_code="appointment_cancellation_rate",
        metric_name="Appointment Cancellation Rate",
        description="Percentage of scheduled appointments cancelled prior to visit",
        metric_type="RATE",
        numerator_definition="Count of appointments with is_cancelled = TRUE",
        denominator_definition="Total scheduled appointments",
        population_definition="All scheduled appointments",
        exclusion_definition="None",
        time_basis="Appointment date",
        grain="Reporting period",
        source_tables="analytics.fact_appointment"
    ),
    MetricDefinition(
        metric_code="appointment_no_show_rate",
        metric_name="Appointment No-Show Rate",
        description="Percentage of booked appointments where patient failed to appear",
        metric_type="RATE",
        numerator_definition="Count of appointments with is_no_show = TRUE",
        denominator_definition="Total scheduled appointments",
        population_definition="All scheduled appointments",
        exclusion_definition="Cancelled appointments",
        time_basis="Appointment date",
        grain="Reporting period",
        source_tables="analytics.fact_appointment"
    ),
    MetricDefinition(
        metric_code="average_wait_minutes",
        metric_name="Average Waiting Time",
        description="Mean clinic waiting time from check-in to consultation in minutes",
        metric_type="AVERAGE",
        numerator_definition="Sum of waiting minutes",
        denominator_definition="Count of eligible waiting encounters",
        population_definition="Completed clinic visits with valid check-in timestamps",
        exclusion_definition="Negative or invalid wait durations",
        time_basis="Appointment date",
        grain="Reporting period",
        source_tables="analytics.fact_appointment"
    ),
    MetricDefinition(
        metric_code="median_wait_minutes",
        metric_name="Median Waiting Time",
        description="50th percentile clinic waiting time in minutes",
        metric_type="MEDIAN",
        numerator_definition="50th percentile of wait_minutes",
        denominator_definition="N/A",
        population_definition="Completed clinic visits with valid check-in timestamps",
        exclusion_definition="Negative or invalid wait durations",
        time_basis="Appointment date",
        grain="Reporting period",
        source_tables="analytics.fact_appointment"
    ),
    
    # Encounter Metrics
    MetricDefinition(
        metric_code="encounter_volume",
        metric_name="Clinical Encounter Volume",
        description="Total completed outpatient and clinical consultation encounters",
        metric_type="COUNT",
        numerator_definition="Count of clinical encounters",
        denominator_definition="N/A",
        population_definition="All recorded patient encounters",
        exclusion_definition="None",
        time_basis="Encounter date",
        grain="Reporting period",
        source_tables="analytics.fact_encounter"
    ),
    MetricDefinition(
        metric_code="average_consultation_duration",
        metric_name="Average Consultation Duration",
        description="Mean consultation duration in minutes",
        metric_type="AVERAGE",
        numerator_definition="Sum of duration_minutes",
        denominator_definition="Count of encounters with valid duration",
        population_definition="Completed encounters with duration",
        exclusion_definition="Invalid or negative durations",
        time_basis="Encounter date",
        grain="Reporting period",
        source_tables="analytics.fact_encounter"
    ),
    MetricDefinition(
        metric_code="encounters_per_facility",
        metric_name="Encounters per Facility",
        description="Average clinical encounter volume per active healthcare facility",
        metric_type="AVERAGE",
        numerator_definition="Total encounter volume",
        denominator_definition="Count of distinct active facilities",
        population_definition="Active facilities with clinical encounters",
        exclusion_definition="Inactive facilities",
        time_basis="Encounter date",
        grain="Facility",
        source_tables="analytics.fact_encounter"
    ),
    MetricDefinition(
        metric_code="encounters_per_provider",
        metric_name="Encounters per Provider",
        description="Average clinical encounter volume per clinical provider",
        metric_type="AVERAGE",
        numerator_definition="Total encounter volume",
        denominator_definition="Count of distinct clinical providers",
        population_definition="Clinical providers with consultations",
        exclusion_definition="Providers with zero encounters",
        time_basis="Encounter date",
        grain="Provider",
        source_tables="analytics.fact_encounter"
    ),
    
    # Referral Metrics
    MetricDefinition(
        metric_code="referral_volume",
        metric_name="Referral Transfer Volume",
        description="Total care transfers and specialist referral requests",
        metric_type="COUNT",
        numerator_definition="Count of referrals",
        denominator_definition="N/A",
        population_definition="All recorded referral requests",
        exclusion_definition="None",
        time_basis="Referral creation date",
        grain="Reporting period",
        source_tables="analytics.fact_referral"
    ),
    MetricDefinition(
        metric_code="referral_completion_rate",
        metric_name="Referral Completion Rate",
        description="Percentage of initiated referrals completed at receiving facility",
        metric_type="RATE",
        numerator_definition="Count of referrals with is_completed = TRUE",
        denominator_definition="Total initiated referrals",
        population_definition="All initiated care transfers",
        exclusion_definition="Cancelled referrals",
        time_basis="Referral creation date",
        grain="Reporting period",
        source_tables="analytics.fact_referral"
    ),
    MetricDefinition(
        metric_code="referral_pending_rate",
        metric_name="Referral Pending Rate",
        description="Percentage of care transfers currently pending resolution",
        metric_type="RATE",
        numerator_definition="Count of referrals with is_completed = FALSE",
        denominator_definition="Total initiated referrals",
        population_definition="All initiated care transfers",
        exclusion_definition="Cancelled referrals",
        time_basis="Referral creation date",
        grain="Reporting period",
        source_tables="analytics.fact_referral"
    ),
    MetricDefinition(
        metric_code="avg_referral_completion_days",
        metric_name="Average Referral Turnaround Days",
        description="Mean turnaround time in days from referral request to completion",
        metric_type="DURATION",
        numerator_definition="Sum of completion_days for completed referrals",
        denominator_definition="Count of completed referrals",
        population_definition="Completed referrals with valid completion dates",
        exclusion_definition="Pending or cancelled referrals",
        time_basis="Referral creation date",
        grain="Reporting period",
        source_tables="analytics.fact_referral"
    ),
    
    # Chronic Care & Cohort Metrics
    MetricDefinition(
        metric_code="hypertension_followup_rate",
        metric_name="Hypertension Care Continuity Rate",
        description="Proportion of hypertension cohort patients with qualifying follow-up",
        metric_type="RATE",
        numerator_definition="Hypertension cohort patients with follow-up encounter",
        denominator_definition="Total eligible hypertension cohort patients",
        population_definition="analytics.cohort_membership (Hypertension v1.0)",
        exclusion_definition="Inactive patients",
        time_basis="Cohort index date",
        grain="Cohort",
        source_tables="analytics.cohort_membership, analytics.fact_encounter"
    ),
    MetricDefinition(
        metric_code="chronic_followup_adherence",
        metric_name="Chronic Disease Follow-up Adherence",
        description="Adherence rate of chronic condition patients to recommended follow-up",
        metric_type="RATE",
        numerator_definition="Chronic disease cohort patients with clinical review",
        denominator_definition="Total eligible chronic follow-up cohort patients",
        population_definition="analytics.cohort_membership (Chronic Followup v1.0)",
        exclusion_definition="Inactive patients",
        time_basis="Cohort index date",
        grain="Cohort",
        source_tables="analytics.cohort_membership, analytics.fact_encounter"
    ),
    
    # Access Metrics
    MetricDefinition(
        metric_code="unique_patients_served",
        metric_name="Unique Patients Served",
        description="Distinct count of unique patients receiving clinical care",
        metric_type="COUNT",
        numerator_definition="Count of distinct patient_key with encounters",
        denominator_definition="N/A",
        population_definition="All active patients with clinical encounters",
        exclusion_definition="None",
        time_basis="Encounter date",
        grain="Reporting period",
        source_tables="analytics.fact_encounter"
    ),
    MetricDefinition(
        metric_code="patients_served_per_facility",
        metric_name="Patients Served per Facility",
        description="Average number of distinct patients served per active facility",
        metric_type="AVERAGE",
        numerator_definition="Count of distinct patient_key",
        denominator_definition="Count of distinct facility_key",
        population_definition="Active facilities serving patients",
        exclusion_definition="None",
        time_basis="Encounter date",
        grain="Facility",
        source_tables="analytics.fact_encounter"
    ),
]
