import sys
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import text

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import engine
from src.metrics.calculator import calculate_all_metrics

SQL_METRICS_DIR = Path(__file__).resolve().parent.parent / "sql" / "metrics"

def apply_metric_ddl():
    """Applies metric registry and results DDL migrations to PostgreSQL analytics schema."""
    ddl_files = ["metric_registry.sql", "metric_results.sql"]
    with engine.begin() as conn:
        for fname in ddl_files:
            fpath = SQL_METRICS_DIR / fname
            if fpath.exists():
                sql_text = fpath.read_text(encoding="utf-8")
                conn.execute(text(sql_text))

def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print(f"HEALTHCARE METRICS & KPIS PIPELINE -- RUN ID: {run_id}")
    print("=" * 70)
    
    apply_metric_ddl()
    print("[1/3] Applied metric DDL migrations (metric_registry, metric_results).")
    
    results = calculate_all_metrics(run_id=run_id)
    print(f"[2/3] Calculated {results['metrics_calculated']} standardized healthcare indicators:")
    for row in results["summary"]:
        val_str = f"{row['metric_value']:,.4f}" if row['metric_value'] is not None else "NULL"
        print(f"    - {row['metric_code']:<32} [{row['metric_type']:<7}]: {val_str}")
        
    print(f"[3/3] Materialized metrics and generated summary report.")
    print(f"Report: {results['report_path']}")
    print("=" * 70)
    print("HEALTHCARE METRICS PIPELINE COMPLETED SUCCESSFULLY.")
    print("=" * 70)

if __name__ == "__main__":
    main()
