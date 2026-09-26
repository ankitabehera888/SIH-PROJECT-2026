from typing import Dict, List, Set
from sqlalchemy import text
from src.database import engine as default_engine

EXPECTED_SCHEMA = {
    "dim_patient": {"patient_key", "patient_id", "gender", "date_of_birth", "is_current"},
    "fact_encounter": {"encounter_key", "encounter_id", "date_key", "patient_key", "provider_key", "facility_key", "duration_minutes"},
    "fact_appointment": {"appointment_key", "appointment_id", "date_key", "patient_key", "wait_minutes", "is_completed", "is_cancelled", "is_no_show"},
    "fact_referral": {"referral_key", "referral_id", "created_date_key", "patient_key", "completion_days", "is_completed"},
}

def run_schema_drift_checks(engine_instance=None) -> List[Dict]:
    """Inspects PostgreSQL information_schema to detect schema drift against expected columns."""
    engine = engine_instance or default_engine
    results = []

    with engine.connect() as conn:
        for table, expected_cols in EXPECTED_SCHEMA.items():
            query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'analytics' AND table_name = :tbl;
            """)
            actual_cols = set(conn.execute(query, {"tbl": table}).scalars().all())

            missing_cols = expected_cols - actual_cols
            is_pass = len(missing_cols) == 0

            results.append({
                "check_code": f"{table}_schema_drift_check",
                "check_type": "SCHEMA",
                "observed_value": float(len(missing_cols)),
                "expected_value": 0.0,
                "threshold_value": 0.0,
                "status": "PASS" if is_pass else "FAIL",
                "severity": "CRITICAL",
                "message": f"Table '{table}' has {len(missing_cols)} missing required columns: {list(missing_cols)}" if not is_pass else f"Table '{table}' matches expected column schema",
                "details": {
                    "expected_count": len(expected_cols),
                    "actual_count": len(actual_cols),
                    "missing_columns": list(missing_cols)
                },
            })
    return results
