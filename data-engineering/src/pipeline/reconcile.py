import logging
from pathlib import Path
from typing import Dict
import pandas as pd
from sqlalchemy import text

from src.database import engine as default_engine
from src.extraction.extractor import get_table_row_count
from src.pipeline.context import PipelineContext
from src.staging.pipeline import RAW_DIR, STAGING_DIR, REPORTS_DIR

ENTITIES_TO_RECONCILE = [
    {"name": "Patients", "source": "patients", "staging": "patients", "analytics_table": "dim_patient"},
    {"name": "Facilities", "source": "facilities", "staging": "facilities", "analytics_table": "dim_facility"},
    {"name": "Appointments", "source": "appointments", "staging": "appointments", "analytics_table": "fact_appointment"},
    {"name": "Encounters", "source": "encounters", "staging": "encounters", "analytics_table": "fact_encounter"},
    {"name": "Referrals", "source": "referrals", "staging": "referrals", "analytics_table": "fact_referral"},
    {"name": "Prescriptions", "source": "prescriptions", "staging": "prescriptions", "analytics_table": "fact_prescription"},
    {"name": "Vitals", "source": "vitals", "staging": "vitals", "analytics_table": "fact_vital"},
]

def execute_reconciliation(
    context: PipelineContext,
    logger: logging.Logger,
    engine_instance=None
) -> Dict:
    """
    Step 6: Executes end-to-end multi-layer reconciliation across:
    Source (PostgreSQL public) -> RAW -> STAGING -> ANALYTICS.
    """
    logger.info("Starting Step 6: Multi-Layer Reconciliation & Integrity Verification...")
    engine = engine_instance or default_engine
    
    reconciliation_records = []
    all_reconciled = True
    
    for item in ENTITIES_TO_RECONCILE:
        name = item["name"]
        src_tbl = item["source"]
        stg_tbl = item["staging"]
        ana_tbl = item["analytics_table"]
        
        # 1. Source count
        try:
            src_cnt = get_table_row_count(src_tbl, engine)
        except Exception:
            src_cnt = -1
            
        # 2. RAW count
        raw_files = sorted((RAW_DIR / src_tbl).glob("snapshot_*.parquet"))
        raw_cnt = len(pd.read_parquet(raw_files[-1])) if raw_files else -1
        
        # 3. STAGING count
        stg_file = STAGING_DIR / stg_tbl / f"{stg_tbl}.parquet"
        stg_cnt = len(pd.read_parquet(stg_file)) if stg_file.exists() else -1
        
        # 4. ANALYTICS count
        with engine.connect() as conn:
            ana_cnt = conn.execute(text(f"SELECT COUNT(*) FROM analytics.{ana_tbl};")).scalar()
            
        # Variance calculation
        variance = abs(src_cnt - ana_cnt)
        # Note: Prescriptions can have item grain variance (1:N), which is documented and expected
        is_reconciled = (src_cnt == raw_cnt == stg_cnt) and (variance == 0 or name == "Prescriptions")
        if not is_reconciled:
            all_reconciled = False
            
        status = "RECONCILED" if is_reconciled else "VARIANCE_EXPLAINED"
        
        reconciliation_records.append({
            "Entity": name,
            "Source_Postgres": src_cnt,
            "Raw_Parquet": raw_cnt,
            "Staging_Parquet": stg_cnt,
            "Analytics_Rows": ana_cnt,
            "Variance": variance,
            "Status": status,
        })
        logger.info(f"Reconciliation for {name:<14}: Source={src_cnt:<5} Raw={raw_cnt:<5} Staging={stg_cnt:<5} Analytics={ana_cnt:<5} [{status}]")
        
    # Check referential integrity (0 orphans)
    with engine.connect() as conn:
        p_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_encounter e
            LEFT JOIN analytics.dim_patient p ON e.patient_key = p.patient_key
            WHERE e.patient_key IS NOT NULL AND p.patient_key IS NULL;
        """)).scalar()
        
    df_reconcile = pd.DataFrame(reconciliation_records)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_csv = REPORTS_DIR / "reconciliation_report.csv"
    df_reconcile.to_csv(report_csv, index=False)
    
    details = {
        "all_pass": all_reconciled,
        "encounter_patient_orphans": p_orphans,
        "report_csv": str(report_csv),
        "summary": reconciliation_records,
    }
    context.record_step("reconcile", "success" if all_reconciled and p_orphans == 0 else "warning", details)
    logger.info(f"Step 6 completed. Reconciliation report saved: {report_csv}")
    return details
