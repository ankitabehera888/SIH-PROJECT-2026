from pathlib import Path
from typing import Dict, List
import pandas as pd
from sqlalchemy import text
from src.database import engine as default_engine

SQL_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "monitoring"

def run_freshness_checks(max_hours: float = 48.0, engine_instance=None) -> List[Dict]:
    """Calculates table data freshness and verifies staleness thresholds."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "freshness.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    results = []
    for _, row in df.iterrows():
        hours = float(row["freshness_hours"]) if pd.notna(row["freshness_hours"]) else 999.0
        is_fresh = hours <= max_hours
        results.append({
            "check_code": f"{row['table_name']}_freshness_check",
            "check_type": "FRESHNESS",
            "observed_value": hours,
            "expected_value": 0.0,
            "threshold_value": max_hours,
            "status": "PASS" if is_fresh else "WARNING",
            "severity": "WARNING",
            "message": f"Freshness for '{row['table_name']}' is {hours:.1f} hours (threshold: {max_hours}h)",
            "details": {"latest_record_date": str(row["latest_record_date"]), "freshness_hours": hours},
        })
    return results
