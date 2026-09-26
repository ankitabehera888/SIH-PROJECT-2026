from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import yaml

from src.staging.cleaner import (
    clean_patients,
    clean_appointments,
    clean_encounters,
    clean_vitals,
    clean_prescriptions,
    clean_referrals,
    clean_facilities,
    attach_lineage,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
STAGING_DIR = BASE_DIR / "data" / "staging"
CONFIG_PATH = BASE_DIR / "configs" / "cleaning_rules.yaml"
REPORTS_DIR = BASE_DIR / "reports"

def load_cleaning_config(config_path: Optional[Path] = None) -> Dict:
    """Loads declarative cleaning configuration rules from YAML."""
    path = config_path or CONFIG_PATH
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_latest_raw_file(table_name: str, raw_dir: Optional[Path] = None) -> Optional[Path]:
    """Finds the latest snapshot Parquet file for a table in the raw data layer."""
    t_dir = (raw_dir or RAW_DIR) / table_name
    if not t_dir.exists():
        return None
    parquets = sorted(t_dir.glob("snapshot_*.parquet"))
    return parquets[-1] if parquets else None

def run_staging_pipeline(
    raw_dir: Optional[Path] = None,
    staging_dir: Optional[Path] = None,
    config_path: Optional[Path] = None,
    run_id: Optional[str] = None
) -> Dict:
    """
    Executes the complete Staging, Cleaning & Standardization pipeline.
    
    Guarantees:
    - Never modifies RAW input Parquet snapshots.
    - Idempotent execution (overwrites staging targets safely).
    - Preserves lineage metadata on all staged records.
    - Compiles reports/staging_quality_report.csv.
    """
    r_dir = raw_dir or RAW_DIR
    s_dir = staging_dir or STAGING_DIR
    cfg = load_cleaning_config(config_path)
    current_run_id = run_id or f"stage_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    
    s_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Raw Datasets
    raw_dfs = {}
    raw_files = {}
    core_tables = [
        "patients", "patient_identifiers", "appointments",
        "encounters", "vitals", "prescriptions", "prescription_items",
        "referrals", "facilities", "diagnostic_orders", "diagnostic_results"
    ]
    
    for tbl in core_tables:
        raw_file = get_latest_raw_file(tbl, r_dir)
        if raw_file and raw_file.exists():
            raw_dfs[tbl] = pd.read_parquet(raw_file)
            raw_files[tbl] = raw_file.name
        else:
            raw_dfs[tbl] = pd.DataFrame()
            raw_files[tbl] = "N/A"
            
    # 2. Stage & Clean Sequentially
    staged_dfs = {}
    
    # Patients
    df_p = raw_dfs.get("patients", pd.DataFrame())
    df_p_ids = raw_dfs.get("patient_identifiers", pd.DataFrame())
    if not df_p.empty:
        staged_dfs["patients"] = clean_patients(
            df_p, df_identifiers=df_p_ids, config=cfg,
            run_id=current_run_id, source_file=raw_files.get("patients", "patients.parquet")
        )
        
    # Appointments
    df_a = raw_dfs.get("appointments", pd.DataFrame())
    if not df_a.empty:
        staged_dfs["appointments"] = clean_appointments(
            df_a, df_patients=staged_dfs.get("patients"), config=cfg,
            run_id=current_run_id, source_file=raw_files.get("appointments", "appointments.parquet")
        )
        
    # Encounters
    df_e = raw_dfs.get("encounters", pd.DataFrame())
    if not df_e.empty:
        staged_dfs["encounters"] = clean_encounters(
            df_e, df_patients=staged_dfs.get("patients"), config=cfg,
            run_id=current_run_id, source_file=raw_files.get("encounters", "encounters.parquet")
        )
        
    # Vitals
    df_v = raw_dfs.get("vitals", pd.DataFrame())
    if not df_v.empty:
        staged_dfs["vitals"] = clean_vitals(
            df_v, df_encounters=staged_dfs.get("encounters"), config=cfg,
            run_id=current_run_id, source_file=raw_files.get("vitals", "vitals.parquet")
        )
        
    # Prescriptions
    df_rx = raw_dfs.get("prescriptions", pd.DataFrame())
    if not df_rx.empty:
        staged_dfs["prescriptions"] = clean_prescriptions(
            df_rx, df_encounters=staged_dfs.get("encounters"), config=cfg,
            run_id=current_run_id, source_file=raw_files.get("prescriptions", "prescriptions.parquet")
        )
        
    # Referrals
    df_ref = raw_dfs.get("referrals", pd.DataFrame())
    if not df_ref.empty:
        staged_dfs["referrals"] = clean_referrals(
            df_ref, df_encounters=staged_dfs.get("encounters"), config=cfg,
            run_id=current_run_id, source_file=raw_files.get("referrals", "referrals.parquet")
        )
        
    # Facilities
    df_fac = raw_dfs.get("facilities", pd.DataFrame())
    if not df_fac.empty:
        staged_dfs["facilities"] = clean_facilities(
            df_fac, config=cfg, run_id=current_run_id, source_file=raw_files.get("facilities", "facilities.parquet")
        )
        
    # 3. Write Staging Parquet Outputs (Idempotent Overwrite)
    report_rows = []
    
    for tbl, df_staged in staged_dfs.items():
        tbl_staging_dir = s_dir / tbl
        tbl_staging_dir.mkdir(parents=True, exist_ok=True)
        staging_file = tbl_staging_dir / f"{tbl}.parquet"
        
        # Idempotent write
        df_staged.to_parquet(staging_file, engine="pyarrow", compression="snappy", index=False)
        
        # Quality Metrics Calculation
        in_rows = len(raw_dfs.get(tbl, []))
        out_rows = len(df_staged)
        status_col = df_staged.get("_data_quality_status", pd.Series(["valid"] * out_rows))
        
        valid_cnt = int((status_col == "valid").sum())
        invalid_cnt = int((status_col == "invalid").sum())
        orphan_cnt = int((status_col == "orphan").sum())
        missing_cnt = int((status_col == "incomplete").sum())
        
        # Duplicates check
        if "possible_duplicate" in df_staged.columns:
            dup_cnt = int(df_staged["possible_duplicate"].sum())
        else:
            dup_cnt = int((status_col == "duplicate_flagged").sum())
            
        report_rows.append({
            "Table": tbl,
            "Input_Rows": in_rows,
            "Output_Rows": out_rows,
            "Valid_Rows": valid_cnt,
            "Invalid_Rows": invalid_cnt,
            "Missing_Values": missing_cnt,
            "Duplicates_Flagged": dup_cnt,
            "Orphans_Flagged": orphan_cnt,
            "Status": "STAGED",
        })
        
    # 4. Generate Staging Quality Report
    df_report = pd.DataFrame(report_rows)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_csv = REPORTS_DIR / "staging_quality_report.csv"
    df_report.to_csv(report_csv, index=False)
    
    return {
        "run_id": current_run_id,
        "tables_staged": list(staged_dfs.keys()),
        "report_path": str(report_csv),
        "report_df": df_report,
    }
