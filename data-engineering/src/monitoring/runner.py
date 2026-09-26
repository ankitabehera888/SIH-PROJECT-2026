from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
from sqlalchemy import text

from src.database import engine as default_engine
from src.staging.pipeline import REPORTS_DIR
from src.monitoring.registry import sync_quality_registry
from src.monitoring.checks import (
    run_completeness_checks,
    run_integrity_checks,
    run_duplicate_checks,
    run_clinical_validity_checks,
)
from src.monitoring.freshness import run_freshness_checks
from src.monitoring.schema import run_schema_drift_checks
from src.monitoring.anomaly import run_volume_checks, run_kpi_anomaly_checks
from src.monitoring.alerts import sync_quality_alerts
from src.monitoring.scoring import calculate_quality_score

def run_quality_monitoring_pipeline(run_id: str = None, engine_instance=None) -> Dict:
    """
    Executes the automated continuous quality monitoring suite across all data domains.
    Records results, generates/resolves alerts, and calculates system health scores.
    """
    engine = engine_instance or default_engine
    current_run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # 1. Sync quality check catalog
    check_keys = sync_quality_registry(engine)

    # 2. Run all diagnostic checks
    all_results: List[Dict] = []
    all_results.extend(run_completeness_checks(engine))
    all_results.extend(run_integrity_checks(engine))
    all_results.extend(run_duplicate_checks(engine))
    all_results.extend(run_clinical_validity_checks(engine))
    all_results.extend(run_freshness_checks(engine_instance=engine))
    all_results.extend(run_volume_checks(engine))
    all_results.extend(run_schema_drift_checks(engine))
    all_results.extend(run_kpi_anomaly_checks(engine))

    # 3. Calculate health score and evaluate critical failures
    quality_score, status, warning_count, critical_count = calculate_quality_score(all_results)
    quality_gate_passed = critical_count == 0

    # 4. Record execution results in analytics.quality_check_results
    with engine.begin() as conn:
        for r in all_results:
            c_key = check_keys.get(r["check_code"])
            details_json = json.dumps(r.get("details", {}))
            stmt = text("""
                INSERT INTO analytics.quality_check_results (
                    check_key, check_code, pipeline_run_id, execution_time,
                    observed_value, expected_value, threshold_value,
                    status, severity, message, details
                ) VALUES (
                    :ckey, :code, :run_id, CURRENT_TIMESTAMP,
                    :obs, :exp, :thresh,
                    :status, :sev, :msg, :details
                );
            """)
            conn.execute(stmt, {
                "ckey": c_key,
                "code": r["check_code"],
                "run_id": current_run_id,
                "obs": r.get("observed_value"),
                "exp": r.get("expected_value"),
                "thresh": r.get("threshold_value"),
                "status": r["status"],
                "sev": r["severity"],
                "msg": r["message"],
                "details": details_json,
            })

    # 5. Synchronize alerts (deduplication + auto-resolution)
    alert_stats = sync_quality_alerts(all_results, current_run_id, check_keys, engine)

    # 6. Generate summary CSV report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "quality_monitoring_summary.csv"
    report_rows = []
    for r in all_results:
        report_rows.append({
            "check_code": r["check_code"],
            "check_type": r["check_type"],
            "execution_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "observed_value": r["observed_value"],
            "expected_value": r["expected_value"],
            "threshold_value": r["threshold_value"],
            "status": r["status"],
            "severity": r["severity"],
            "message": r["message"],
            "pipeline_run_id": str(current_run_id),
        })
    df_report = pd.DataFrame(report_rows)
    df_report.to_csv(report_path, index=False)

    return {
        "run_id": current_run_id,
        "total_checks": len(all_results),
        "passed_checks": sum(1 for c in all_results if c["status"] == "PASS"),
        "warnings": warning_count,
        "critical_failures": critical_count,
        "quality_score": quality_score,
        "status": status,
        "quality_gate": "PASSED" if quality_gate_passed else "BLOCKED",
        "quality_gate_passed": quality_gate_passed,
        "alerts": alert_stats,
        "report_path": str(report_path),
        "results": all_results,
    }
