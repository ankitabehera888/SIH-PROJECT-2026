from datetime import datetime, timezone
from typing import Dict, List
from sqlalchemy import text
from src.database import engine as default_engine

def sync_quality_alerts(
    check_results: List[Dict],
    run_id: str,
    check_keys: Dict[str, int],
    engine_instance=None
) -> Dict[str, int]:
    """
    Manages quality alert lifecycle:
    - Generates new alerts for FAIL/WARNING results.
    - Deduplicates existing OPEN alerts for the same check.
    - Resolves OPEN alerts when failing checks transition back to PASS.
    """
    engine = engine_instance or default_engine
    opened_count = 0
    resolved_count = 0

    with engine.begin() as conn:
        for res in check_results:
            code = res["check_code"]
            status = res["status"]
            sev = res["severity"]
            msg = res["message"]
            c_key = check_keys.get(code)
            if not c_key:
                continue

            # Query existing OPEN alert for this check
            existing = conn.execute(
                text("SELECT alert_key FROM analytics.quality_alerts WHERE check_key = :ckey AND status = 'OPEN';"),
                {"ckey": c_key}
            ).fetchone()

            if status in ("FAIL", "WARNING"):
                if existing:
                    # Deduplicate: update existing open alert message
                    conn.execute(
                        text("""
                            UPDATE analytics.quality_alerts
                            SET message = :msg, pipeline_run_id = :run_id
                            WHERE alert_key = :akey;
                        """),
                        {"msg": msg, "run_id": run_id, "akey": existing[0]}
                    )
                else:
                    # Create new alert
                    conn.execute(
                        text("""
                            INSERT INTO analytics.quality_alerts (
                                check_key, pipeline_run_id, severity, alert_code, message, status
                            ) VALUES (
                                :ckey, :run_id, :sev, :code, :msg, 'OPEN'
                            );
                        """),
                        {"ckey": c_key, "run_id": run_id, "sev": sev, "code": code.upper(), "msg": msg}
                    )
                    opened_count += 1

            elif status == "PASS" and existing:
                # Resolve previously failing check
                conn.execute(
                    text("""
                        UPDATE analytics.quality_alerts
                        SET status = 'RESOLVED', resolved_at = CURRENT_TIMESTAMP
                        WHERE alert_key = :akey;
                    """),
                    {"akey": existing[0]}
                )
                resolved_count += 1

    return {
        "new_alerts_opened": opened_count,
        "alerts_resolved": resolved_count,
    }
