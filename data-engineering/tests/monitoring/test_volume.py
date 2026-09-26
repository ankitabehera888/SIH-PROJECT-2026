from src.database import engine
from src.monitoring.anomaly import run_volume_checks

def test_volume_monitoring():
    """Verify table volume checks detect non-empty active tables."""
    results = run_volume_checks(engine)
    assert len(results) == 5
    for r in results:
        assert r["check_type"] == "VOLUME"
        assert r["observed_value"] > 0
        assert r["status"] == "PASS"
