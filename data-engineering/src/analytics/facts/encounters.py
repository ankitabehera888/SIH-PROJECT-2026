from typing import Dict, Optional
import pandas as pd

def build_fact_encounter(
    df_staged_encounters: pd.DataFrame,
    patient_map: Dict[str, int],
    facility_map: Dict[str, int],
    provider_map: Dict[int, int],
    date_map: Dict[str, int],
    df_vitals: Optional[pd.DataFrame] = None,
    df_prescriptions: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Builds fact_encounter table.
    Grain: One row represents one recorded patient visit/encounter.
    """
    if df_staged_encounters.empty:
        return pd.DataFrame()
        
    # Pre-calculate counts per encounter
    vitals_encounter_set = set()
    if df_vitals is not None and not df_vitals.empty and "encounter_id" in df_vitals.columns:
        vitals_encounter_set = set(df_vitals["encounter_id"].dropna().astype(str))
        
    rx_counts = {}
    if df_prescriptions is not None and not df_prescriptions.empty and "encounter_id" in df_prescriptions.columns:
        s_cnt = df_prescriptions["encounter_id"].dropna().astype(str).value_counts()
        rx_counts = s_cnt.to_dict()
        
    records = []
    for _, row in df_staged_encounters.iterrows():
        enc_id = str(row["id"])
        pid = str(row["patient_id"])
        fac_id = str(row.get("facility_id", ""))
        prov_id = int(row.get("provider_id", 1)) if pd.notna(row.get("provider_id")) else 1
        
        started_at = row.get("started_at")
        date_str = str(started_at)[:10] if pd.notna(started_at) else "2026-09-01"
        d_key = date_map.get(date_str, int(date_str.replace("-", "")))
        
        p_key = patient_map.get(pid)
        f_key = facility_map.get(fac_id)
        pr_key = provider_map.get(prov_id)
        
        status = str(row.get("status", "completed")).lower()
        enc_type = str(row.get("encounter_type", "outpatient")).lower()
        
        # Duration calculation
        ended_at = row.get("ended_at")
        duration = None
        if pd.notna(started_at) and pd.notna(ended_at):
            try:
                t0 = pd.to_datetime(started_at)
                t1 = pd.to_datetime(ended_at)
                duration = round((t1 - t0).total_seconds() / 60.0, 2)
                if duration < 0:
                    duration = None
            except Exception:
                duration = None
        if duration is None and status == "completed":
            duration = 15.0  # standard OPD consultation duration
            
        has_v = enc_id in vitals_encounter_set
        p_count = rx_counts.get(enc_id, 0)
        
        records.append({
            "encounter_id": enc_id,
            "date_key": d_key,
            "patient_key": p_key,
            "provider_key": pr_key,
            "facility_key": f_key,
            "encounter_type": enc_type,
            "encounter_status": status,
            "duration_minutes": duration,
            "diagnosis_count": 1,
            "prescription_count": p_count,
            "has_vitals": has_v,
        })
        
    return pd.DataFrame(records)
