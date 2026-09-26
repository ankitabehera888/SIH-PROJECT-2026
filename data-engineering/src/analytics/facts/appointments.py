from datetime import datetime
from typing import Dict
import pandas as pd

def build_fact_appointment(
    df_staged_appointments: pd.DataFrame,
    patient_map: Dict[str, int],
    facility_map: Dict[str, int],
    provider_map: Dict[int, int],
    date_map: Dict[str, int]
) -> pd.DataFrame:
    """
    Builds fact_appointment table.
    Grain: One row represents one appointment occurrence.
    """
    if df_staged_appointments.empty:
        return pd.DataFrame()
        
    records = []
    for _, row in df_staged_appointments.iterrows():
        appt_id = str(row["id"])
        pid = str(row["patient_id"])
        fac_id = str(row.get("facility_id", ""))
        prov_id = int(row.get("provider_id", 1)) if pd.notna(row.get("provider_id")) else 1
        
        # Determine date key
        created_at = row.get("created_at")
        date_str = str(created_at)[:10] if pd.notna(created_at) else "2026-09-01"
        d_key = date_map.get(date_str, int(date_str.replace("-", "")))
        
        p_key = patient_map.get(pid)
        f_key = facility_map.get(fac_id)
        pr_key = provider_map.get(prov_id)
        
        status = str(row.get("status", "booked")).lower()
        is_completed = (status == "completed")
        is_cancelled = (status in ("cancelled", "no_show"))
        is_no_show = (status == "no_show")
        
        wait_min = 15.0 if is_completed else None
        
        records.append({
            "appointment_id": appt_id,
            "date_key": d_key,
            "patient_key": p_key,
            "provider_key": pr_key,
            "facility_key": f_key,
            "appointment_status": status,
            "wait_minutes": wait_min,
            "is_completed": is_completed,
            "is_cancelled": is_cancelled,
            "is_no_show": is_no_show,
        })
        
    return pd.DataFrame(records)
