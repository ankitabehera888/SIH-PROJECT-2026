from src.database import engine
from src.monitoring.checks import run_duplicate_checks

def test_duplicate_monitoring():
    """Verify zero duplicate natural keys across dimensions and facts."""
    results = run_duplicate_checks(engine)
    assert len(results) == 4
    for r in results:
        assert r["status"] == "PASS"
        assert r["observed_value"] == 0.0
        assert r["severity"] == "CRITICAL"
