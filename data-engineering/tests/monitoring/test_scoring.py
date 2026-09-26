from src.monitoring.scoring import calculate_quality_score
from src.monitoring.alerts import sync_quality_alerts
from src.database import engine
from sqlalchemy import text

def test_scoring_healthy():
    checks = [{"status": "PASS", "severity": "CRITICAL"} for _ in range(10)]
    score, status, warns, crits = calculate_quality_score(checks)
    assert score == 100.0
    assert status == "HEALTHY"
    assert crits == 0

def test_critical_failure_override():
    # 9 passed, 1 critical failure
    checks = [{"status": "PASS", "severity": "CRITICAL"} for _ in range(9)]
    checks.append({"status": "FAIL", "severity": "CRITICAL"})
    score, status, warns, crits = calculate_quality_score(checks)
    assert score == 90.0
    # Overrides to CRITICAL
    assert status == "CRITICAL"
    assert crits == 1

def test_alert_deduplication_and_resolution():
    """Verify alert deduplication and auto-resolution lifecycle."""
    # 1. Setup a test check in registry
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO analytics.quality_check_registry (
                check_code, check_name, check_type, description, severity, is_active
            ) VALUES (
                'test_alert_lifecycle', 'Test Alert Lifecycle', 'INTEGRITY', 'Test Alert', 'CRITICAL', TRUE
            ) ON CONFLICT (check_code) DO NOTHING;
        """))
        check_key = conn.execute(
            text("SELECT check_key FROM analytics.quality_check_registry WHERE check_code = 'test_alert_lifecycle';")
        ).scalar()

    check_keys = {"test_alert_lifecycle": check_key}

    # 2. Run 1: Failure generates 1 OPEN alert
    res_fail = [{
        "check_code": "test_alert_lifecycle",
        "status": "FAIL",
        "severity": "CRITICAL",
        "message": "Simulated initial failure",
    }]
    stats1 = sync_quality_alerts(res_fail, "test_run_1", check_keys, engine)
    assert stats1["new_alerts_opened"] == 1

    # 3. Run 2: Duplicate failure updates existing alert, does NOT create a second alert
    res_fail_repeat = [{
        "check_code": "test_alert_lifecycle",
        "status": "FAIL",
        "severity": "CRITICAL",
        "message": "Simulated repeated failure",
    }]
    stats2 = sync_quality_alerts(res_fail_repeat, "test_run_2", check_keys, engine)
    assert stats2["new_alerts_opened"] == 0

    with engine.connect() as conn:
        open_count = conn.execute(text(
            "SELECT COUNT(*) FROM analytics.quality_alerts WHERE check_key = :ckey AND status = 'OPEN';"
        ), {"ckey": check_key}).scalar()
        assert open_count == 1

    # 4. Run 3: Check passes -> transitions alert to RESOLVED
    res_pass = [{
        "check_code": "test_alert_lifecycle",
        "status": "PASS",
        "severity": "CRITICAL",
        "message": "Simulated resolution",
    }]
    stats3 = sync_quality_alerts(res_pass, "test_run_3", check_keys, engine)
    assert stats3["alerts_resolved"] == 1

    with engine.connect() as conn:
        resolved_row = conn.execute(text(
            "SELECT status, resolved_at FROM analytics.quality_alerts WHERE check_key = :ckey ORDER BY created_at DESC LIMIT 1;"
        ), {"ckey": check_key}).fetchone()
        assert resolved_row[0] == "RESOLVED"
        assert resolved_row[1] is not None
