"""Healthcare Platform — Dimensional & Analytical Data Model Module."""

from .builder import build_analytics_model, run_ddl_scripts
from .dimensions.date import build_dim_date
from .dimensions.patient import build_dim_patient
from .dimensions.provider import build_dim_provider
from .dimensions.facility import build_dim_facility
from .dimensions.geography import build_dim_geography
from .facts.appointments import build_fact_appointment
from .facts.encounters import build_fact_encounter
from .facts.referrals import build_fact_referral
from .facts.prescriptions import build_fact_prescription
from .facts.vitals import build_fact_vital

__all__ = [
    "build_analytics_model",
    "run_ddl_scripts",
    "build_dim_date",
    "build_dim_patient",
    "build_dim_provider",
    "build_dim_facility",
    "build_dim_geography",
    "build_fact_appointment",
    "build_fact_encounter",
    "build_fact_referral",
    "build_fact_prescription",
    "build_fact_vital",
]
