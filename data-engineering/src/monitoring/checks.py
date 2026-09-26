from pathlib import Path
from typing import Dict, List
import pandas as pd
from sqlalchemy import text
from src.database import engine as default_engine

SQL_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "monitoring"

def run_completeness_checks(engine_instance=None) -> List[Dict]:
    """Executes completeness SQL and returns evaluated results."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "completeness.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    results = []
    for _, row in df.iterrows():
        null_rate = float(row["null_rate"])
        is_pass = null_rate == 0.0
        results.append({
            "check_code": f"{row['check_target']}_completeness",
            "check_type": "COMPLETENESS",
            "observed_value": null_rate,
            "expected_value": 0.0,
            "threshold_value": 0.0,
            "status": "PASS" if is_pass else "FAIL",
            "severity": "CRITICAL",
            "message": f"Null rate for {row['check_target']} is {null_rate:.4f} ({row['null_rows']} nulls / {row['total_rows']} rows)",
            "details": {"null_rows": int(row["null_rows"]), "total_rows": int(row["total_rows"])},
        })
    return results

def run_integrity_checks(engine_instance=None) -> List[Dict]:
    """Executes referential integrity checks across dimensional relationships."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "integrity.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    results = []
    for _, row in df.iterrows():
        orphans = int(row["orphan_count"])
        is_pass = orphans == 0
        results.append({
            "check_code": f"{row['check_target']}_check",
            "check_type": "INTEGRITY",
            "observed_value": float(orphans),
            "expected_value": 0.0,
            "threshold_value": 0.0,
            "status": "PASS" if is_pass else "FAIL",
            "severity": "CRITICAL",
            "message": f"Found {orphans} orphan records for relationship '{row['check_target']}'",
            "details": {"orphan_count": orphans},
        })
    return results

def run_duplicate_checks(engine_instance=None) -> List[Dict]:
    """Executes natural key duplicate checks across dimensional model."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "duplicates.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    results = []
    for _, row in df.iterrows():
        dups = int(row["duplicate_count"])
        is_pass = dups == 0
        results.append({
            "check_code": f"{row['check_target']}_check",
            "check_type": "DUPLICATE",
            "observed_value": float(dups),
            "expected_value": 0.0,
            "threshold_value": 0.0,
            "status": "PASS" if is_pass else "FAIL",
            "severity": "CRITICAL",
            "message": f"Found {dups} duplicate natural keys for '{row['check_target']}'",
            "details": {"duplicate_count": dups},
        })
    return results

def run_clinical_validity_checks(engine_instance=None) -> List[Dict]:
    """Validates biometric physiological ranges."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "clinical_validation.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    results = []
    for _, row in df.iterrows():
        invalid = int(row["invalid_count"])
        is_pass = invalid == 0
        results.append({
            "check_code": f"biometric_{row['check_target']}_check",
            "check_type": "VALIDITY",
            "observed_value": float(invalid),
            "expected_value": 0.0,
            "threshold_value": 0.0,
            "status": "PASS" if is_pass else "WARNING",
            "severity": "WARNING",
            "message": f"Found {invalid} records exceeding clinical biometric boundaries for '{row['check_target']}'",
            "details": {"invalid_count": invalid},
        })
    return results
