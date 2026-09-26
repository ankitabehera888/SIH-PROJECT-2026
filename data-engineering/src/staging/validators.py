from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

DEFAULT_VITAL_BOUNDS = {
    "systolic_bp": {"min": 60, "max": 260},
    "diastolic_bp": {"min": 30, "max": 180},
    "heart_rate": {"min": 25, "max": 240},
    "temperature": {"min": 30.0, "max": 45.0},
    "spo2": {"min": 50.0, "max": 100.0},
    "respiratory_rate": {"min": 6, "max": 60},
}

def validate_vitals_non_destructive(
    df: pd.DataFrame,
    bounds: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Validates vital signs non-destructively:
    - Retains exact raw value in <vital>_raw
    - Sets <vital>_validated = NULL when out of physiological bounds
    - Assigns per-record _vital_quality_status ('valid', 'invalid', 'incomplete')
    """
    df_out = df.copy()
    b = bounds or DEFAULT_VITAL_BOUNDS
    
    vital_fields = ["systolic_bp", "diastolic_bp", "heart_rate", "temperature", "spo2", "respiratory_rate"]
    invalid_rows = pd.Series(False, index=df_out.index)
    has_any_vital = pd.Series(False, index=df_out.index)
    
    for field in vital_fields:
        if field in df_out.columns:
            # Preserve raw
            raw_col = f"{field}_raw"
            val_col = f"{field}_validated"
            df_out[raw_col] = df_out[field]
            
            # Numeric conversion
            numeric_s = pd.to_numeric(df_out[field], errors="coerce")
            f_bounds = b.get(field, {})
            min_val = f_bounds.get("min", -np.inf)
            max_val = f_bounds.get("max", np.inf)
            
            # Mask valid values
            is_valid = (numeric_s >= min_val) & (numeric_s <= max_val)
            is_present = numeric_s.notna()
            has_any_vital = has_any_vital | is_present
            
            # Invalid values flagged
            is_invalid = is_present & (~is_valid)
            invalid_rows = invalid_rows | is_invalid
            
            # Set validated column: keep valid, set invalid to None
            df_out[val_col] = np.where(is_valid, numeric_s, np.nan)
            
    # Check systolic > diastolic ratio
    if "systolic_bp_validated" in df_out.columns and "diastolic_bp_validated" in df_out.columns:
        both_present = df_out["systolic_bp_validated"].notna() & df_out["diastolic_bp_validated"].notna()
        inverted = both_present & (df_out["systolic_bp_validated"] <= df_out["diastolic_bp_validated"])
        invalid_rows = invalid_rows | inverted
        df_out.loc[inverted, "systolic_bp_validated"] = np.nan
        df_out.loc[inverted, "diastolic_bp_validated"] = np.nan
        
    # Assign quality status
    status_list = []
    for is_inv, is_pres in zip(invalid_rows, has_any_vital):
        if is_inv:
            status_list.append("invalid")
        elif is_pres:
            status_list.append("valid")
        else:
            status_list.append("incomplete")
            
    df_out["_vital_quality_status"] = status_list
    return df_out

def check_orphans(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    foreign_key: str,
    parent_key: str = "id"
) -> pd.Series:
    """
    Flags records referencing non-existent parents as orphans.
    
    Returns boolean series where True indicates an orphan record.
    """
    if foreign_key not in child_df.columns or parent_key not in parent_df.columns:
        return pd.Series(False, index=child_df.index)
        
    parent_keys_set = set(parent_df[parent_key].dropna().astype(str))
    
    def is_orphan(fk_val):
        if pd.isna(fk_val) or fk_val is None:
            return False  # Optional foreign key is not an orphan
        return str(fk_val) not in parent_keys_set
        
    return child_df[foreign_key].apply(is_orphan)

def flag_patient_duplicates(df_patients: pd.DataFrame) -> pd.Series:
    """
    Flags potential duplicate patient records (possible_duplicate = True)
    based on shared normalized phone or email.
    """
    if df_patients.empty:
        return pd.Series([], dtype=bool)
        
    is_dup = pd.Series(False, index=df_patients.index)
    
    # Shared phone
    if "phone_normalized" in df_patients.columns:
        phone_s = df_patients["phone_normalized"].dropna()
        dup_phones = set(phone_s[phone_s.duplicated()].unique())
        if dup_phones:
            is_dup = is_dup | df_patients["phone_normalized"].isin(dup_phones)
            
    # Shared email
    if "email" in df_patients.columns:
        email_s = df_patients["email"].dropna().str.lower().str.strip()
        dup_emails = set(email_s[email_s.duplicated()].unique())
        if dup_emails:
            is_dup = is_dup | df_patients["email"].str.lower().str.strip().isin(dup_emails)
            
    return is_dup
