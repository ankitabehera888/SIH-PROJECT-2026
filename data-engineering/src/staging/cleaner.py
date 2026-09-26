from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import pandas as pd

from src.staging.normalizer import (
    normalize_string_series,
    standardize_code_series,
    normalize_phone_series,
    normalize_email_series,
    standardize_timestamps_utc,
    normalize_uuid_series,
)
from src.staging.validators import (
    validate_vitals_non_destructive,
    check_orphans,
    flag_patient_duplicates,
)

def attach_lineage(
    df: pd.DataFrame,
    source_table: str,
    source_file: str,
    run_id: str,
    quality_status: Optional[pd.Series] = None
) -> pd.DataFrame:
    """Appends standardized audit lineage tracking and data quality status columns."""
    df_out = df.copy()
    staged_timestamp = datetime.now(timezone.utc).isoformat()
    
    df_out["_source_table"] = source_table
    df_out["_source_file"] = source_file
    df_out["_extraction_run_id"] = run_id
    df_out["_staged_at"] = staged_timestamp
    
    if quality_status is not None:
        df_out["_data_quality_status"] = quality_status
    elif "_data_quality_status" not in df_out.columns:
        df_out["_data_quality_status"] = "valid"
        
    return df_out

def clean_patients(
    df_raw: pd.DataFrame,
    df_identifiers: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "patients.parquet"
) -> pd.DataFrame:
    """Standardizes demographic patient records and separates external national identifiers."""
    df = df_raw.copy()
    
    # 1. String trimming
    for col in ["first_name", "middle_name", "last_name", "address", "patient_number"]:
        if col in df.columns:
            df[col] = normalize_string_series(df[col], lowercase=False)
            
    # 2. Gender code standardization
    if "gender" in df.columns:
        gender_map = config.get("code_mappings", {}).get("gender", {"male": "male", "female": "female"})
        df["gender"] = standardize_code_series(df["gender"], gender_map)
        
    # 3. Phone number normalization (preserves raw & adds normalized)
    if "phone" in df.columns:
        phone_raw, phone_norm = normalize_phone_series(df["phone"])
        df["phone_raw"] = phone_raw
        df["phone_normalized"] = phone_norm
        
    # 4. Email normalization
    if "email" in df.columns:
        email_norm, email_valid = normalize_email_series(df["email"])
        df["email"] = email_norm
        df["email_is_valid"] = email_valid
        
    # 5. Distinct identifier separation & UUID normalization
    df["id"] = normalize_uuid_series(df["id"])
    df["patient_id"] = df["id"]
    df["source_patient_id"] = df.get("patient_number", df["id"])
    df["abha_id"] = None
    df["fhir_patient_id"] = None
    
    # Link ABHA ID from patient_identifiers if available
    if df_identifiers is not None and not df_identifiers.empty and "patient_id" in df_identifiers.columns:
        # Match ABHA value
        abha_rows = df_identifiers[df_identifiers["system"].str.contains("abha|abdm", case=False, na=False)]
        if not abha_rows.empty:
            pid_norm = normalize_uuid_series(abha_rows["patient_id"])
            abha_map = dict(zip(pid_norm, abha_rows["value"]))
            df["abha_id"] = df["patient_id"].map(abha_map)
            
    # 6. Flag potential duplicates
    df["possible_duplicate"] = flag_patient_duplicates(df)
    
    # 7. Timestamps
    df = standardize_timestamps_utc(df, ["created_at", "updated_at"])
    
    # Quality status assignment
    quality_status = pd.Series("valid", index=df.index)
    if "email_is_valid" in df.columns:
        quality_status = np.where(~df["email_is_valid"], "review_required", quality_status)
    quality_status = np.where(df["possible_duplicate"], "duplicate_flagged", quality_status)
    
    return attach_lineage(df, "patients", source_file, run_id, quality_status=pd.Series(quality_status, index=df.index))

def clean_appointments(
    df_raw: pd.DataFrame,
    df_patients: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "appointments.parquet"
) -> pd.DataFrame:
    """Cleans appointment records and maps status codes."""
    df = df_raw.copy()
    
    # Normalize UUIDs
    for col in ["id", "patient_id", "facility_id"]:
        if col in df.columns:
            df[col] = normalize_uuid_series(df[col])
            
    # Trim reasons/notes
    for col in ["reason", "notes", "cancellation_reason"]:
        if col in df.columns:
            df[col] = normalize_string_series(df[col], lowercase=False)
            
    # Status standardization
    if "status" in df.columns:
        status_map = config.get("code_mappings", {}).get("appointment_status", {})
        df["status"] = standardize_code_series(df["status"], status_map)
        
    # Timestamps
    df = standardize_timestamps_utc(df, ["created_at", "updated_at", "cancelled_at"])
    
    # Orphan check against patients
    quality_status = pd.Series("valid", index=df.index)
    if df_patients is not None and "patient_id" in df.columns:
        orphans = check_orphans(df, df_patients, foreign_key="patient_id", parent_key="patient_id")
        quality_status = np.where(orphans, "orphan", quality_status)
        
    return attach_lineage(df, "appointments", source_file, run_id, quality_status=pd.Series(quality_status, index=df.index))

def clean_encounters(
    df_raw: pd.DataFrame,
    df_patients: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "encounters.parquet"
) -> pd.DataFrame:
    """Cleans clinical encounters preserving doctor progress narratives."""
    df = df_raw.copy()
    
    # Normalize UUIDs
    for col in ["id", "patient_id", "facility_id", "appointment_id"]:
        if col in df.columns:
            df[col] = normalize_uuid_series(df[col])
            
    # Preserve narratives (only trim whitespace)
    for col in ["chief_complaint", "clinical_notes"]:
        if col in df.columns:
            df[col] = normalize_string_series(df[col], lowercase=False)
            
    # Status mapping
    if "status" in df.columns:
        status_map = config.get("code_mappings", {}).get("encounter_status", {})
        df["status"] = standardize_code_series(df["status"], status_map)
        
    # Timestamps
    df = standardize_timestamps_utc(df, ["started_at", "ended_at", "created_at", "updated_at"])
    
    # Orphan check
    quality_status = pd.Series("valid", index=df.index)
    if df_patients is not None and "patient_id" in df.columns:
        orphans = check_orphans(df, df_patients, foreign_key="patient_id", parent_key="patient_id")
        quality_status = np.where(orphans, "orphan", quality_status)
        
    return attach_lineage(df, "encounters", source_file, run_id, quality_status=pd.Series(quality_status, index=df.index))

def clean_vitals(
    df_raw: pd.DataFrame,
    df_encounters: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "vitals.parquet"
) -> pd.DataFrame:
    """Performs non-destructive vital sign validation and bounds checks."""
    df_copy = df_raw.copy()
    for col in ["id", "encounter_id", "patient_id"]:
        if col in df_copy.columns:
            df_copy[col] = normalize_uuid_series(df_copy[col])
            
    bounds = config.get("vital_bounds", {}) if config else None
    df = validate_vitals_non_destructive(df_copy, bounds=bounds)
    
    # Orphan check against encounters
    quality_status = df["_vital_quality_status"]
    if df_encounters is not None and "encounter_id" in df.columns:
        orphans = check_orphans(df, df_encounters, foreign_key="encounter_id", parent_key="id")
        quality_status = np.where(orphans, "orphan", quality_status)
        
    return attach_lineage(df, "vitals", source_file, run_id, quality_status=pd.Series(quality_status, index=df.index))

def clean_prescriptions(
    df_raw: pd.DataFrame,
    df_encounters: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "prescriptions.parquet"
) -> pd.DataFrame:
    """Standardizes prescription records and validates parent encounter linkages."""
    df = df_raw.copy()
    for col in ["id", "encounter_id", "patient_id", "facility_id"]:
        if col in df.columns:
            df[col] = normalize_uuid_series(df[col])
            
    if "status" in df.columns:
        status_map = config.get("code_mappings", {}).get("prescription_status", {})
        df["status"] = standardize_code_series(df["status"], status_map)
        
    df = standardize_timestamps_utc(df, ["prescribed_at", "created_at", "updated_at", "cancelled_at"])
    
    quality_status = pd.Series("valid", index=df.index)
    if df_encounters is not None and "encounter_id" in df.columns:
        orphans = check_orphans(df, df_encounters, foreign_key="encounter_id", parent_key="id")
        quality_status = np.where(orphans, "orphan", quality_status)
        
    return attach_lineage(df, "prescriptions", source_file, run_id, quality_status=pd.Series(quality_status, index=df.index))

def clean_referrals(
    df_raw: pd.DataFrame,
    df_encounters: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "referrals.parquet"
) -> pd.DataFrame:
    """Standardizes referral care transfers and referral status transitions."""
    df = df_raw.copy()
    for col in ["id", "encounter_id", "patient_id", "referring_facility_id", "receiving_facility_id"]:
        if col in df.columns:
            df[col] = normalize_uuid_series(df[col])
            
    for col in ["reason", "clinical_summary", "rejection_reason", "cancellation_reason"]:
        if col in df.columns:
            df[col] = normalize_string_series(df[col], lowercase=False)
            
    if "status" in df.columns:
        status_map = config.get("code_mappings", {}).get("referral_status", {})
        df["status"] = standardize_code_series(df["status"], status_map)
        
    df = standardize_timestamps_utc(df, ["created_at", "updated_at", "completed_at"])
    
    quality_status = pd.Series("valid", index=df.index)
    if df_encounters is not None and "encounter_id" in df.columns:
        orphans = check_orphans(df, df_encounters, foreign_key="encounter_id", parent_key="id")
        quality_status = np.where(orphans, "orphan", quality_status)
        
    return attach_lineage(df, "referrals", source_file, run_id, quality_status=pd.Series(quality_status, index=df.index))

def clean_facilities(
    df_raw: pd.DataFrame,
    config: Optional[Dict] = None,
    run_id: str = "staging_run",
    source_file: str = "facilities.parquet"
) -> pd.DataFrame:
    """Cleans facility records and standardizes UUIDs and names."""
    df = df_raw.copy()
    if "id" in df.columns:
        df["id"] = normalize_uuid_series(df["id"])
    for col in ["name", "facility_code", "address", "phone", "email"]:
        if col in df.columns:
            df[col] = normalize_string_series(df[col], lowercase=False)
    df = standardize_timestamps_utc(df, ["created_at", "updated_at"])
    return attach_lineage(df, "facilities", source_file, run_id, quality_status=pd.Series("valid", index=df.index))
