from pathlib import Path
from typing import Dict, List
import pandas as pd
from sqlalchemy import text
from src.database import engine as default_engine

SQL_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "monitoring"

def run_volume_checks(engine_instance=None) -> List[Dict]:
    """Inspects table volume counts to ensure non-empty tables and catch volume drops."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "volume.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    results = []
    for _, row in df.iterrows():
        cnt = int(row["current_row_count"])
        is_pass = cnt > 0
        results.append({
            "check_code": f"{row['table_name']}_volume_check",
            "check_type": "VOLUME",
            "observed_value": float(cnt),
            "expected_value": 1.0,
            "threshold_value": 0.0,
            "status": "PASS" if is_pass else "FAIL",
            "severity": "CRITICAL" if cnt == 0 else "WARNING",
            "message": f"Table '{row['table_name']}' volume is {cnt} rows",
            "details": {"current_row_count": cnt},
        })
    return results

def run_kpi_anomaly_checks(engine_instance=None) -> List[Dict]:
    """Detects KPI values outside expected clinical ranges (e.g. rate < 0 or > 1)."""
    engine = engine_instance or default_engine
    with open(SQL_DIR / "metric_anomalies.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    anomalies = df[df["anomaly_status"] != "NORMAL"]
    is_pass = len(anomalies) == 0

    return [{
        "check_code": "kpi_boundary_anomaly_check",
        "check_type": "ANOMALY",
        "observed_value": float(len(anomalies)),
        "expected_value": 0.0,
        "threshold_value": 0.0,
        "status": "PASS" if is_pass else "WARNING",
        "severity": "WARNING",
        "message": f"Detected {len(anomalies)} KPI anomalies out of bounds" if not is_pass else "All calculated KPIs conform to normal bounds",
        "details": {"anomalous_metrics": anomalies.to_dict(orient="records")},
    }]
