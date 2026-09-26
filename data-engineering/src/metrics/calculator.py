from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import text

from src.database import engine as default_engine
from src.staging.pipeline import REPORTS_DIR
from src.metrics.definitions import METRIC_CATALOG
from src.metrics.registry import sync_metric_registry
from src.metrics.validation import validate_metric_calculation

SQL_METRICS_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "metrics"

def calculate_all_metrics(
    period_start: str = "2026-01-01",
    period_end: str = "2026-12-31",
    run_id: Optional[str] = None,
    engine_instance=None
) -> Dict:
    """
    Executes authoritative metric calculations, validates mathematical boundaries,
    and materializes results in analytics.metric_results.
    """
    engine = engine_instance or default_engine
    current_run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    # 1. Sync registry
    metric_keys = sync_metric_registry(engine)
    
    # 2. Execute metric queries
    results = []
    
    # --- A. Appointment Metrics ---
    with open(SQL_METRICS_DIR / "appointment_metrics.sql", "r", encoding="utf-8") as f:
        df_appt = pd.read_sql(text(f.read()), engine)
        
    if not df_appt.empty:
        r = df_appt.iloc[0]
        appt_vol = float(r["appointment_volume"])
        
        # appointment_volume
        results.append({
            "metric_code": "appointment_volume",
            "numerator": appt_vol,
            "denominator": None,
            "metric_value": appt_vol,
        })
        # appointment_completion_rate
        results.append({
            "metric_code": "appointment_completion_rate",
            "numerator": float(r["completed_appointments"]),
            "denominator": appt_vol,
            "metric_value": float(r["appointment_completion_rate"]) if pd.notna(r["appointment_completion_rate"]) else None,
        })
        # appointment_cancellation_rate
        results.append({
            "metric_code": "appointment_cancellation_rate",
            "numerator": float(r["cancelled_appointments"]),
            "denominator": appt_vol,
            "metric_value": float(r["appointment_cancellation_rate"]) if pd.notna(r["appointment_cancellation_rate"]) else None,
        })
        # appointment_no_show_rate
        results.append({
            "metric_code": "appointment_no_show_rate",
            "numerator": float(r["no_show_appointments"]),
            "denominator": appt_vol,
            "metric_value": float(r["appointment_no_show_rate"]) if pd.notna(r["appointment_no_show_rate"]) else None,
        })
        # average_wait_minutes
        results.append({
            "metric_code": "average_wait_minutes",
            "numerator": None,
            "denominator": None,
            "metric_value": float(r["average_wait_minutes"]),
        })
        # median_wait_minutes
        results.append({
            "metric_code": "median_wait_minutes",
            "numerator": None,
            "denominator": None,
            "metric_value": float(r["median_wait_minutes"]),
        })

    # --- B. Encounter Metrics ---
    with open(SQL_METRICS_DIR / "encounter_metrics.sql", "r", encoding="utf-8") as f:
        df_enc = pd.read_sql(text(f.read()), engine)
        
    if not df_enc.empty:
        r = df_enc.iloc[0]
        enc_vol = float(r["encounter_volume"])
        fac_count = float(r["active_facilities_count"])
        prov_count = float(r["active_providers_count"])
        
        results.append({
            "metric_code": "encounter_volume",
            "numerator": enc_vol,
            "denominator": None,
            "metric_value": enc_vol,
        })
        results.append({
            "metric_code": "average_consultation_duration",
            "numerator": None,
            "denominator": None,
            "metric_value": float(r["average_consultation_duration"]),
        })
        results.append({
            "metric_code": "encounters_per_facility",
            "numerator": enc_vol,
            "denominator": fac_count,
            "metric_value": float(r["encounters_per_facility"]) if pd.notna(r["encounters_per_facility"]) else None,
        })
        results.append({
            "metric_code": "encounters_per_provider",
            "numerator": enc_vol,
            "denominator": prov_count,
            "metric_value": float(r["encounters_per_provider"]) if pd.notna(r["encounters_per_provider"]) else None,
        })

    # --- C. Referral Metrics ---
    with open(SQL_METRICS_DIR / "referral_metrics.sql", "r", encoding="utf-8") as f:
        df_ref = pd.read_sql(text(f.read()), engine)
        
    if not df_ref.empty:
        r = df_ref.iloc[0]
        ref_vol = float(r["referral_volume"])
        
        results.append({
            "metric_code": "referral_volume",
            "numerator": ref_vol,
            "denominator": None,
            "metric_value": ref_vol,
        })
        results.append({
            "metric_code": "referral_completion_rate",
            "numerator": float(r["completed_referrals"]),
            "denominator": ref_vol,
            "metric_value": float(r["referral_completion_rate"]) if pd.notna(r["referral_completion_rate"]) else None,
        })
        results.append({
            "metric_code": "referral_pending_rate",
            "numerator": float(r["pending_referrals"]),
            "denominator": ref_vol,
            "metric_value": float(r["referral_pending_rate"]) if pd.notna(r["referral_pending_rate"]) else None,
        })
        results.append({
            "metric_code": "avg_referral_completion_days",
            "numerator": None,
            "denominator": None,
            "metric_value": float(r["avg_referral_completion_days"]),
        })

    # --- D. Chronic Care Metrics ---
    with open(SQL_METRICS_DIR / "chronic_metrics.sql", "r", encoding="utf-8") as f:
        df_chr = pd.read_sql(text(f.read()), engine)
        
    if not df_chr.empty:
        r = df_chr.iloc[0]
        htn_tot = float(r["total_hypertension_patients"])
        htn_enc = float(r["htn_patients_with_encounter"])
        chr_tot = float(r["total_chronic_patients"])
        chr_enc = float(r["chronic_patients_with_encounter"])
        
        results.append({
            "metric_code": "hypertension_followup_rate",
            "numerator": htn_enc,
            "denominator": htn_tot,
            "metric_value": float(r["hypertension_followup_rate"]) if pd.notna(r["hypertension_followup_rate"]) else None,
        })
        results.append({
            "metric_code": "chronic_followup_adherence",
            "numerator": chr_enc,
            "denominator": chr_tot,
            "metric_value": float(r["chronic_followup_adherence"]) if pd.notna(r["chronic_followup_adherence"]) else None,
        })

    # --- E. Access Metrics ---
    with open(SQL_METRICS_DIR / "access_metrics.sql", "r", encoding="utf-8") as f:
        df_acc = pd.read_sql(text(f.read()), engine)
        
    if not df_acc.empty:
        r = df_acc.iloc[0]
        pts_served = float(r["unique_patients_served"])
        fac_serving = float(r["facilities_serving_patients"])
        
        results.append({
            "metric_code": "unique_patients_served",
            "numerator": pts_served,
            "denominator": None,
            "metric_value": pts_served,
        })
        results.append({
            "metric_code": "patients_served_per_facility",
            "numerator": pts_served,
            "denominator": fac_serving,
            "metric_value": float(r["patients_served_per_facility"]) if pd.notna(r["patients_served_per_facility"]) else None,
        })

    # 3. Validate and Build Final Records
    validated_rows = []
    summary_report_rows = []
    
    catalog_map = {m.metric_code: m for m in METRIC_CATALOG}
    
    for item in results:
        code = item["metric_code"]
        defn = catalog_map.get(code)
        m_type = defn.metric_type if defn else "COUNT"
        
        is_val, err = validate_metric_calculation(
            metric_code=code,
            metric_type=m_type,
            numerator=item["numerator"],
            denominator=item["denominator"],
            metric_value=item["metric_value"]
        )
        if not is_val:
            raise ValueError(f"Metric calculation validation failed: {err}")
            
        m_key = metric_keys.get(code)
        val = item["metric_value"]
        
        row_dict = {
            "metric_key": m_key,
            "metric_code": code,
            "period_start": period_start,
            "period_end": period_end,
            "facility_key": None,
            "geography_key": None,
            "numerator": item["numerator"],
            "denominator": item["denominator"],
            "metric_value": round(val, 4) if val is not None else None,
            "calculation_version": "1.0.0",
            "pipeline_run_id": str(current_run_id),
        }
        validated_rows.append(row_dict)
        
        summary_report_rows.append({
            "metric_code": code,
            "metric_type": m_type,
            "period_start": period_start,
            "period_end": period_end,
            "numerator": item["numerator"],
            "denominator": item["denominator"],
            "metric_value": round(val, 4) if val is not None else None,
            "calculation_version": "1.0.0",
            "pipeline_run_id": str(current_run_id),
            "status": "VALID",
        })
        
    # 4. Materialize in analytics.metric_results
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.metric_results CASCADE;"))
        
    df_materialized = pd.DataFrame(validated_rows)
    df_materialized["period_start"] = pd.to_datetime(df_materialized["period_start"]).dt.date
    df_materialized["period_end"] = pd.to_datetime(df_materialized["period_end"]).dt.date
    df_materialized["facility_key"] = df_materialized["facility_key"].astype("Int64")
    df_materialized["geography_key"] = df_materialized["geography_key"].astype("Int64")
    df_materialized.to_sql(
        "metric_results",
        engine,
        schema="analytics",
        if_exists="append",
        index=False
    )
    
    # 5. Generate summary CSV report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_csv = REPORTS_DIR / "metrics_summary.csv"
    df_summary = pd.DataFrame(summary_report_rows)
    df_summary.to_csv(report_csv, index=False)
    
    return {
        "run_id": current_run_id,
        "metrics_calculated": len(validated_rows),
        "report_path": str(report_csv),
        "summary": summary_report_rows,
    }
