from src.database import engine
from src.monitoring.freshness import run_freshness_checks

def test_freshness_monitoring():
    """Verify freshness evaluation across core operational fact tables."""
    results = run_freshness_checks(max_hours=48.0, engine_instance=engine)
    assert len(results) == 3
    for r in results:
        assert r["check_type"] == "FRESHNESS"
        assert r["observed_value"] >= 0.0
        assert r["status"] == "PASS"
