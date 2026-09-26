import sys
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import text

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import engine
from src.monitoring.runner import run_quality_monitoring_pipeline

SQL_MONITORING_DIR = Path(__file__).resolve().parent.parent / "sql" / "monitoring"

def apply_monitoring_ddl():
    """Applies quality monitoring schema DDL migrations to PostgreSQL."""
    ddl_files = ["quality_registry.sql", "quality_results.sql", "quality_alerts.sql"]
    with engine.begin() as conn:
        for fname in ddl_files:
            fpath = SQL_MONITORING_DIR / fname
            if fpath.exists():
                conn.execute(text(fpath.read_text(encoding="utf-8")))

def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print(f"CONTINUOUS DATA QUALITY MONITORING -- RUN ID: {run_id}")
    print("=" * 70)

    apply_monitoring_ddl()
    print("[1/3] Applied monitoring DDL migrations (registry, results, alerts).")

    res = run_quality_monitoring_pipeline(run_id=run_id)
    print(f"[2/3] Evaluated {res['total_checks']} quality checks across all dimensions:")
    print(f"    - Passed:            {res['passed_checks']}")
    print(f"    - Warnings:          {res['warnings']}")
    print(f"    - Critical Failures: {res['critical_failures']}")
    print(f"    - Quality Score:     {res['quality_score']}%")
    print(f"    - Platform Status:   {res['status']}")
    print(f"    - Quality Gate:      {'PASSED' if res['quality_gate_passed'] else 'BLOCKED'}")

    print(f"[3/3] Exported summary scorecard:")
    print(f"    Report: {res['report_path']}")
    print("=" * 70)
    print("QUALITY MONITORING COMPLETED SUCCESSFULLY.")
    print("=" * 70)

if __name__ == "__main__":
    main()
