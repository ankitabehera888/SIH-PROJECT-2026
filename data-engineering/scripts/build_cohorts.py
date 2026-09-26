import sys
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import text

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import engine
from src.cohorts.builder import build_all_cohorts

SQL_COHORTS_DIR = Path(__file__).resolve().parent.parent / "sql" / "cohorts"

def apply_cohort_ddl():
    """Applies cohort schema DDL migrations to PostgreSQL analytics schema."""
    ddl_files = ["cohort_registry.sql", "cohort_membership.sql"]
    with engine.begin() as conn:
        for fname in ddl_files:
            fpath = SQL_COHORTS_DIR / fname
            if fpath.exists():
                sql_text = fpath.read_text(encoding="utf-8")
                conn.execute(text(sql_text))

def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print(f"CLINICAL COHORT GENERATION -- RUN ID: {run_id}")
    print("=" * 70)
    
    apply_cohort_ddl()
    print("[1/2] Applied cohort DDL migrations (cohort_registry, cohort_membership).")
    
    results = build_all_cohorts(run_id=run_id)
    print(f"[2/2] Generated {results['cohorts_built']} clinical cohorts:")
    for s in results["summary"]:
        print(f"    - {s['Cohort']:<22} [{s['Version']}]: {s['Patients']:,} eligible patients")
        
    print("=" * 70)
    print(f"COHORT GENERATION COMPLETED SUCCESSFULLY.")
    print(f"Summary Report: {results['report_path']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
