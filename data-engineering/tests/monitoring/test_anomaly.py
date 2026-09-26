from src.database import engine
from src.monitoring.anomaly import run_kpi_anomaly_checks

def test_kpi_anomaly_monitoring():
    """Verify KPI anomaly monitor confirms all calculated metrics conform to expected bounds."""
    results = run_kpi_anomaly_checks(engine)
    assert len(results) == 1
    r = results[0]
    assert r["check_type"] == "ANOMALY"
    assert r["status"] == "PASS"
    assert r["observed_value"] == 0.0
