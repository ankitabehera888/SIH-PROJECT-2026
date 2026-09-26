from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.database import engine

def detect_outliers(engine_instance=None) -> pd.DataFrame:
    """Detects statistical outliers across operational duration and count metrics using IQR and Z-score."""
    eng = engine_instance or engine
    outlier_metrics = []
    
    with eng.connect() as conn:
        # 1. OPD Waiting Time (Minutes)
        q_wait = text("""
            SELECT id, EXTRACT(EPOCH FROM (consultation_started_at - checked_in_at)) / 60.0 as wait_minutes
            FROM queue_entries
            WHERE consultation_started_at IS NOT NULL AND checked_in_at IS NOT NULL AND consultation_started_at >= checked_in_at
        """)
        df_wait = pd.read_sql(q_wait, con=conn)
        outlier_metrics.append(_analyze_metric(df_wait, "wait_minutes", "OPD Waiting Duration", "Minutes"))
        
        # 2. Teleconsultation Attendance Duration (Minutes)
        q_tele = text("""
            SELECT id, duration_seconds / 60.0 as duration_minutes
            FROM consultation_participants
            WHERE duration_seconds IS NOT NULL AND duration_seconds > 0
        """)
        df_tele = pd.read_sql(q_tele, con=conn)
        outlier_metrics.append(_analyze_metric(df_tele, "duration_minutes", "Teleconsultation Duration", "Minutes"))
        
        # 3. Appointment Lead Time (Days from booking to appointment)
        q_lead = text("""
            SELECT id, (appointment_date - created_at::date) as lead_days
            FROM appointments
            WHERE appointment_date IS NOT NULL
        """)
        df_lead = pd.read_sql(q_lead, con=conn)
        outlier_metrics.append(_analyze_metric(df_lead, "lead_days", "Appointment Booking Lead Time", "Days"))
        
        # 4. Prescription Item Density (Number of items per prescription)
        q_items = text("""
            SELECT prescription_id as id, COUNT(*) as item_count
            FROM prescription_items
            GROUP BY prescription_id
        """)
        df_items = pd.read_sql(q_items, con=conn)
        outlier_metrics.append(_analyze_metric(df_items, "item_count", "Prescription Items Density", "Items"))

    df_outliers = pd.DataFrame(outlier_metrics)
    return df_outliers

def _analyze_metric(df: pd.DataFrame, col: str, label: str, unit: str) -> Dict:
    """Calculates IQR and Z-Score outlier metrics for a single distribution."""
    if df.empty or len(df[col].dropna()) < 4:
        return {
            "Metric": label,
            "Unit": unit,
            "Total_Evaluated": len(df),
            "Median": 0.0,
            "Mean": 0.0,
            "Std_Dev": 0.0,
            "IQR": 0.0,
            "IQR_Lower_Bound": 0.0,
            "IQR_Upper_Bound": 0.0,
            "Outliers_IQR_Count": 0,
            "Outliers_ZScore_Count": 0,
            "Max_Observed": 0.0,
            "Outlier_Status": "INSUFFICIENT_DATA"
        }
        
    s = df[col].dropna().astype(float)
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    iqr_lower = round(q1 - 1.5 * iqr, 2)
    iqr_upper = round(q3 + 1.5 * iqr, 2)
    
    # IQR outliers
    iqr_outliers = s[(s < iqr_lower) | (s > iqr_upper)]
    
    # Z-Score outliers (|z| > 3.0)
    mean = float(s.mean())
    std = float(s.std(ddof=1))
    if std > 0:
        z_scores = (s - mean) / std
        z_outliers = s[np.abs(z_scores) > 3.0]
    else:
        z_outliers = pd.Series([], dtype=float)
        
    return {
        "Metric": label,
        "Unit": unit,
        "Total_Evaluated": len(s),
        "Median": round(float(s.median()), 2),
        "Mean": round(mean, 2),
        "Std_Dev": round(std, 2),
        "IQR": round(iqr, 2),
        "IQR_Lower_Bound": iqr_lower,
        "IQR_Upper_Bound": iqr_upper,
        "Outliers_IQR_Count": len(iqr_outliers),
        "Outliers_ZScore_Count": len(z_outliers),
        "Max_Observed": round(float(s.max()), 2),
        "Outlier_Status": "REVIEW_NEEDED" if len(iqr_outliers) > 0 else "NORMAL"
    }
