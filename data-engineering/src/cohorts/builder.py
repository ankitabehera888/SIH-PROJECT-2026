from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import pandas as pd
from sqlalchemy import text

from src.database import engine as default_engine
from src.staging.pipeline import REPORTS_DIR
from src.cohorts.definitions import COHORT_DEFINITIONS
from src.cohorts.registry import sync_cohort_registry

SQL_COHORTS_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "cohorts"

def build_all_cohorts(run_id: str = None, engine_instance=None) -> Dict:
    """
    Executes all cohort definition SQLs and populates analytics.cohort_membership.
    Ensures zero duplicate patient membership and full audit lineage.
    """
    engine = engine_instance or default_engine
    current_run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    # 1. Synchronize registry
    cohort_keys = sync_cohort_registry(engine)
    
    # Truncate membership for fresh idempotent run
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.cohort_membership CASCADE;"))
        
    summary_results = []
    
    for c_def in COHORT_DEFINITIONS:
        c_key = cohort_keys.get(f"{c_def.name}_{c_def.version}")
        sql_path = SQL_COHORTS_DIR / c_def.sql_file
        
        if not sql_path.exists():
            continue
            
        sql_text = sql_path.read_text(encoding="utf-8")
        
        with engine.connect() as conn:
            df_cohort = pd.read_sql(text(sql_text), conn)
            
        if not df_cohort.empty:
            df_cohort["cohort_key"] = c_key
            df_cohort["pipeline_run_id"] = str(current_run_id)
            
            # Deduplicate strictly on (cohort_key, patient_key, index_date)
            df_cohort = df_cohort.drop_duplicates(subset=["cohort_key", "patient_key", "index_date"])
            
            # Write to PostgreSQL
            df_cohort.to_sql(
                "cohort_membership",
                engine,
                schema="analytics",
                if_exists="append",
                index=False
            )
            patient_count = int(df_cohort["patient_key"].nunique())
        else:
            patient_count = 0
            
        summary_results.append({
            "Cohort": c_def.name.replace("_", " ").title(),
            "Version": c_def.version,
            "Patients": patient_count,
            "Active_Criteria": c_def.inclusion_criteria,
            "Generated_At": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        })
        
    # Generate report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "cohort_summary.csv"
    df_summary = pd.DataFrame(summary_results)
    df_summary.to_csv(report_path, index=False)
    
    return {
        "run_id": current_run_id,
        "cohorts_built": len(summary_results),
        "summary": summary_results,
        "report_path": str(report_path),
    }
