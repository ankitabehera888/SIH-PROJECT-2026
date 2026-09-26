from typing import Dict
import pandas as pd

def build_fact_vital(
    df_staged_vitals: pd.DataFrame,
    patient_map: Dict[str, int],
    encounter_map: Dict[str, int],
    date_map: Dict[str, int]
) -> pd.DataFrame:
    """
    Builds fact_vital table.
    Grain: One row represents one clinical vital measurement panel recorded for an encounter.
    """
    if df_staged_vitals.empty:
        return pd.DataFrame()
        
    records = []
    for _, row in df_staged_vitals.iterrows():
        vital_id = str(row["id"])
        pid = str(row["patient_id"])
        enc_id = str(row.get("encounter_id", ""))
        
        recorded_at = row.get("recorded_at")
        date_str = str(recorded_at)[:10] if pd.notna(recorded_at) else "2026-09-01"
        d_key = date_map.get(date_str, int(date_str.replace("-", "")))
        
        p_key = patient_map.get(pid)
        e_key = encounter_map.get(enc_id)
        
        systolic = row.get("systolic_bp_validated")
        diastolic = row.get("diastolic_bp_validated")
        hr = row.get("heart_rate_validated")
        temp = row.get("temperature_validated")
        spo2 = row.get("spo2_validated")
        rr = row.get("respiratory_rate_validated")
        
        q_status = str(row.get("_vital_quality_status", "valid"))
        
        records.append({
            "vital_id": vital_id,
            "date_key": d_key,
            "patient_key": p_key,
            "encounter_key": e_key,
            "systolic_bp": float(systolic) if pd.notna(systolic) else None,
            "diastolic_bp": float(diastolic) if pd.notna(diastolic) else None,
            "heart_rate": float(hr) if pd.notna(hr) else None,
            "temperature": float(temp) if pd.notna(temp) else None,
            "spo2": float(spo2) if pd.notna(spo2) else None,
            "respiratory_rate": float(rr) if pd.notna(rr) else None,
            "quality_status": q_status,
        })
        
    return pd.DataFrame(records)
