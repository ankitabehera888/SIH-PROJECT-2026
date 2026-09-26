from datetime import date, datetime
from typing import Optional
import numpy as np
import pandas as pd

def calculate_age_band(dob_series: pd.Series) -> pd.Series:
    """Calculates age band (0-5, 6-17, 18-35, 36-60, 60+, Unknown) from Date of Birth."""
    today = date.today()
    bands = []
    
    for val in dob_series:
        if pd.isna(val) or val is None:
            bands.append("Unknown")
            continue
        try:
            if isinstance(val, str):
                d = datetime.strptime(val[:10], "%Y-%m-%d").date()
            elif isinstance(val, (datetime, pd.Timestamp)):
                d = val.date()
            elif isinstance(val, date):
                d = val
            else:
                bands.append("Unknown")
                continue
                
            age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
            if age < 0:
                bands.append("Unknown")
            elif age <= 5:
                bands.append("0-5")
            elif age <= 17:
                bands.append("6-17")
            elif age <= 35:
                bands.append("18-35")
            elif age <= 60:
                bands.append("36-60")
            else:
                bands.append("60+")
        except Exception:
            bands.append("Unknown")
            
    return pd.Series(bands, index=dob_series.index)

def build_dim_patient(df_staged_patients: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms staged patient data into dim_patient applying data minimization:
    - Direct identifiers (name, phone, email, address) are strictly EXCLUDED
    - Age band calculated
    - SCD Type 2 tracking attributes assigned
    """
    df = pd.DataFrame()
    df["patient_id"] = df_staged_patients["patient_id"].astype(str)
    df["source_patient_id"] = df_staged_patients.get("source_patient_id", df_staged_patients["patient_id"]).astype(str)
    df["abha_id"] = df_staged_patients.get("abha_id", None)
    df["gender"] = df_staged_patients.get("gender", "unknown").fillna("unknown").str.lower()
    
    # Date of Birth & Age Band
    dob_col = df_staged_patients.get("date_of_birth", None)
    df["date_of_birth"] = pd.to_datetime(dob_col, errors="coerce").dt.date if dob_col is not None else None
    df["age_band"] = calculate_age_band(df["date_of_birth"])
    
    # Clinical categorization
    df["blood_group"] = df_staged_patients.get("blood_group", None)
    df["district"] = "Kendrapada"
    df["state"] = "Odisha"
    df["source_system"] = "healthcare_dev"
    
    # SCD Type 2 tracking
    created_at = df_staged_patients.get("created_at", None)
    df["effective_from"] = pd.to_datetime(created_at, utc=True) if created_at is not None else pd.Timestamp.now(tz="UTC")
    df["effective_to"] = pd.Series([pd.NaT] * len(df), dtype="datetime64[ns, UTC]")
    df["is_current"] = True
    
    return df
