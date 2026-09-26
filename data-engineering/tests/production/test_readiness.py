from src.database import engine
from sqlalchemy import text

def test_production_tables_exist():
    """Verify all core analytical and orchestration tables exist in PostgreSQL."""
    expected_tables = {
        "dim_patient",
        "fact_encounter",
        "fact_appointment",
        "fact_referral",
        "fact_vital",
        "cohort_membership",
        "metric_results",
        "quality_check_results",
        "quality_alerts",
        "pipeline_runs",
        "pipeline_task_runs",
    }
    with engine.connect() as conn:
        actual_tables = set(conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'analytics';"
        )).scalars().all())

        missing = expected_tables - actual_tables
        assert len(missing) == 0, f"Missing required analytical tables: {missing}"
