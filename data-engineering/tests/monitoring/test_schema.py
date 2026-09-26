from src.database import engine
from src.monitoring.schema import run_schema_drift_checks

def test_schema_drift_monitoring():
    """Verify schema drift monitor confirms all tables match required column sets."""
    results = run_schema_drift_checks(engine)
    assert len(results) == 4
    for r in results:
        assert r["check_type"] == "SCHEMA"
        assert r["status"] == "PASS"
        assert r["observed_value"] == 0.0
