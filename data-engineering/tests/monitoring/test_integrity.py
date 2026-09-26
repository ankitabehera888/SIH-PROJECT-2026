from src.database import engine
from src.monitoring.checks import run_integrity_checks

def test_referential_integrity_monitoring():
    """Verify zero orphan records across all dimensional relationships."""
    results = run_integrity_checks(engine)
    assert len(results) == 5
    for r in results:
        assert r["status"] == "PASS"
        assert r["observed_value"] == 0.0
        assert r["severity"] == "CRITICAL"
