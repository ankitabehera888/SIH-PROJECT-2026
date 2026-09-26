from src.database import engine
from src.monitoring.checks import run_completeness_checks

def test_completeness_monitoring_success():
    """Verify that all core surrogate and business keys have zero null rate."""
    results = run_completeness_checks(engine)
    assert len(results) == 4
    for r in results:
        assert r["status"] == "PASS"
        assert r["observed_value"] == 0.0
        assert r["severity"] == "CRITICAL"
