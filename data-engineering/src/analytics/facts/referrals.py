from typing import Dict
import pandas as pd

def build_fact_referral(
    df_staged_referrals: pd.DataFrame,
    patient_map: Dict[str, int],
    facility_map: Dict[str, int],
    date_map: Dict[str, int]
) -> pd.DataFrame:
    """
    Builds fact_referral table.
    Grain: One row represents one referral episode.
    """
    if df_staged_referrals.empty:
        return pd.DataFrame()
        
    records = []
    for _, row in df_staged_referrals.iterrows():
        ref_id = str(row["id"])
        pid = str(row["patient_id"])
        ref_fac_id = str(row.get("referring_facility_id", ""))
        rec_fac_id = str(row.get("receiving_facility_id", ""))
        
        created_at = row.get("created_at")
        completed_at = row.get("completed_at")
        
        created_date_str = str(created_at)[:10] if pd.notna(created_at) else "2026-09-01"
        c_date_key = date_map.get(created_date_str, int(created_date_str.replace("-", "")))
        
        comp_date_key = None
        comp_days = None
        if pd.notna(completed_at):
            comp_date_str = str(completed_at)[:10]
            comp_date_key = date_map.get(comp_date_str, int(comp_date_str.replace("-", "")))
            try:
                t0 = pd.to_datetime(created_at)
                t1 = pd.to_datetime(completed_at)
                comp_days = round((t1 - t0).total_seconds() / 86400.0, 2)
                if comp_days < 0:
                    comp_days = None
            except Exception:
                comp_days = None
                
        p_key = patient_map.get(pid)
        ref_fac_key = facility_map.get(ref_fac_id)
        rec_fac_key = facility_map.get(rec_fac_id)
        
        status = str(row.get("status", "pending")).lower()
        is_completed = (status == "completed")
        is_cancelled = (status in ("cancelled", "rejected"))
        
        records.append({
            "referral_id": ref_id,
            "created_date_key": c_date_key,
            "completed_date_key": comp_date_key,
            "patient_key": p_key,
            "referring_facility_key": ref_fac_key,
            "receiving_facility_key": rec_fac_key,
            "referral_status": status,
            "priority": str(row.get("priority", "routine")).lower(),
            "completion_days": comp_days,
            "is_completed": is_completed,
            "is_cancelled": is_cancelled,
        })
        
    return pd.DataFrame(records)
