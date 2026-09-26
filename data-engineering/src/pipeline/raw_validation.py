import logging
from pathlib import Path
from typing import Dict, List
import pandas as pd
from src.pipeline.context import PipelineContext
from src.staging.pipeline import RAW_DIR

CORE_RAW_TABLES = [
    "patients",
    "appointments",
    "encounters",
    "vitals",
    "prescriptions",
    "referrals",
    "facilities",
]

EXPECTED_COLUMNS = {
    "patients": ["id", "gender", "created_at"],
    "appointments": ["id", "patient_id", "status", "created_at"],
    "encounters": ["id", "patient_id", "status", "started_at"],
    "vitals": ["id", "encounter_id", "patient_id"],
    "prescriptions": ["id", "patient_id", "encounter_id"],
    "referrals": ["id", "patient_id", "status"],
    "facilities": ["id", "name", "facility_code"],
}

def execute_raw_validation(context: PipelineContext, logger: logging.Logger) -> Dict:
    """Step 2: Validates raw Parquet files integrity, non-emptiness, and schema requirements."""
    logger.info("Starting Step 2: RAW Data Layer Validation...")
    
    validation_results = {}
    
    for tbl in CORE_RAW_TABLES:
        t_dir = RAW_DIR / tbl
        if not t_dir.exists():
            err_msg = f"Missing raw directory for required table '{tbl}' at {t_dir}"
            logger.error(err_msg)
            context.record_error("raw_validation", err_msg)
            raise FileNotFoundError(err_msg)
            
        snapshots = sorted(t_dir.glob("snapshot_*.parquet"))
        if not snapshots:
            err_msg = f"No raw snapshot Parquet files found for table '{tbl}' in {t_dir}"
            logger.error(err_msg)
            context.record_error("raw_validation", err_msg)
            raise FileNotFoundError(err_msg)
            
        latest_file = snapshots[-1]
        try:
            df = pd.read_parquet(latest_file)
        except Exception as e:
            err_msg = f"Failed to read raw snapshot file {latest_file}: {e}"
            logger.error(err_msg)
            context.record_error("raw_validation", err_msg)
            raise
            
        row_count = len(df)
        if row_count == 0:
            err_msg = f"Table '{tbl}' raw snapshot has 0 rows: {latest_file}"
            logger.error(err_msg)
            context.record_error("raw_validation", err_msg)
            raise ValueError(err_msg)
            
        # Check expected columns
        exp_cols = EXPECTED_COLUMNS.get(tbl, [])
        missing_cols = [c for c in exp_cols if c not in df.columns]
        if missing_cols:
            err_msg = f"Table '{tbl}' is missing expected columns {missing_cols}"
            logger.error(err_msg)
            context.record_error("raw_validation", err_msg)
            raise ValueError(err_msg)
            
        validation_results[tbl] = {
            "snapshot_file": latest_file.name,
            "row_count": row_count,
            "columns_verified": len(exp_cols),
            "status": "PASSED",
        }
        logger.info(f"Validated raw table '{tbl}': {row_count:,} rows, columns OK.")
        
    context.record_step("raw_validation", "success", validation_results)
    logger.info("Step 2 completed successfully. All core raw tables validated.")
    return validation_results
