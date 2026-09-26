"""Healthcare Platform — Staging, Cleaning & Standardization Module."""

from .normalizer import (
    normalize_string_series,
    standardize_code_series,
    normalize_phone_series,
    normalize_email_series,
    standardize_timestamps_utc,
)
from .validators import (
    validate_vitals_non_destructive,
    check_orphans,
    flag_patient_duplicates,
)
from .cleaner import (
    attach_lineage,
    clean_patients,
    clean_appointments,
    clean_encounters,
    clean_vitals,
    clean_prescriptions,
    clean_referrals,
)
from .pipeline import run_staging_pipeline, load_cleaning_config

__all__ = [
    "normalize_string_series",
    "standardize_code_series",
    "normalize_phone_series",
    "normalize_email_series",
    "standardize_timestamps_utc",
    "validate_vitals_non_destructive",
    "check_orphans",
    "flag_patient_duplicates",
    "attach_lineage",
    "clean_patients",
    "clean_appointments",
    "clean_encounters",
    "clean_vitals",
    "clean_prescriptions",
    "clean_referrals",
    "run_staging_pipeline",
    "load_cleaning_config",
]
