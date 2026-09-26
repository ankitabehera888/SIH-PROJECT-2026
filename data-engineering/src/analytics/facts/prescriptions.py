from typing import Dict, Optional
import pandas as pd
from src.staging.normalizer import normalize_uuid_series

def build_fact_prescription(
    df_staged_prescriptions: pd.DataFrame,
    df_raw_items: Optional[pd.DataFrame],
    patient_map: Dict[str, int],
    encounter_map: Dict[str, int],
    date_map: Dict[str, int]
) -> pd.DataFrame:
    """
    Builds fact_prescription table.
    Grain: One row represents one prescribed medication line item.
    """
    if df_staged_prescriptions.empty:
        return pd.DataFrame()
        
    # Map prescriptions metadata
    rx_meta = {}
    for _, row in df_staged_prescriptions.iterrows():
        rx_id = str(row["id"])
        rx_meta[rx_id] = {
            "patient_id": str(row["patient_id"]),
            "encounter_id": str(row.get("encounter_id", "")),
            "created_at": row.get("created_at"),
            "status": str(row.get("status", "active")),
        }
        
    records = []
    
    if df_raw_items is not None and not df_raw_items.empty:
        # Item-level grain
        df_items = df_raw_items.copy()
        if "id" in df_items.columns:
            df_items["id"] = normalize_uuid_series(df_items["id"])
        if "prescription_id" in df_items.columns:
            df_items["prescription_id"] = normalize_uuid_series(df_items["prescription_id"])
            
        for _, item in df_items.iterrows():
            item_id = str(item["id"])
            rx_id = str(item["prescription_id"])
            parent = rx_meta.get(rx_id, {})
            
            pid = parent.get("patient_id", "")
            enc_id = parent.get("encounter_id", "")
            created_at = parent.get("created_at")
            
            date_str = str(created_at)[:10] if pd.notna(created_at) else "2026-09-01"
            d_key = date_map.get(date_str, int(date_str.replace("-", "")))
            
            p_key = patient_map.get(pid)
            e_key = encounter_map.get(enc_id)
            
            med_id = str(item.get("medication_id", ""))
            qty = float(item.get("quantity", 1.0)) if pd.notna(item.get("quantity")) else 1.0
            dur = int(item.get("duration_days", 5)) if pd.notna(item.get("duration_days")) else 5
            
            records.append({
                "prescription_item_id": item_id,
                "prescription_id": rx_id,
                "date_key": d_key,
                "patient_key": p_key,
                "encounter_key": e_key,
                "medication_id": med_id,
                "quantity": qty,
                "duration_days": dur,
                "prescription_status": parent.get("status", "active"),
            })
    else:
        # Fallback to prescription grain if item table not present
        for rx_id, parent in rx_meta.items():
            pid = parent["patient_id"]
            enc_id = parent["encounter_id"]
            created_at = parent["created_at"]
            
            date_str = str(created_at)[:10] if pd.notna(created_at) else "2026-09-01"
            d_key = date_map.get(date_str, int(date_str.replace("-", "")))
            
            records.append({
                "prescription_item_id": f"item-{rx_id}",
                "prescription_id": rx_id,
                "date_key": d_key,
                "patient_key": patient_map.get(pid),
                "encounter_key": encounter_map.get(enc_id),
                "medication_id": "MED-001",
                "quantity": 1.0,
                "duration_days": 5,
                "prescription_status": parent["status"],
            })
            
    return pd.DataFrame(records)
