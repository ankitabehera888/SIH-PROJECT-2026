import json
from typing import Dict
from sqlalchemy import text
from src.database import engine as default_engine
from src.monitoring.thresholds import load_monitoring_rules

def sync_quality_registry(engine_instance=None) -> Dict[str, int]:
    """
    Synchronizes quality check catalog in analytics.quality_check_registry.
    Returns mapping check_code -> check_key.
    """
    engine = engine_instance or default_engine
    rules = load_monitoring_rules()
    check_keys = {}

    with engine.begin() as conn:
        for r in rules:
            config_json = json.dumps(r)
            stmt = text("""
                INSERT INTO analytics.quality_check_registry (
                    check_code, check_name, check_type, description,
                    severity, threshold_config, source_table, is_active
                ) VALUES (
                    :code, :name, :ctype, :desc,
                    :sev, :cfg, :tbl, TRUE
                )
                ON CONFLICT (check_code)
                DO UPDATE SET
                    check_name = EXCLUDED.check_name,
                    check_type = EXCLUDED.check_type,
                    description = EXCLUDED.description,
                    severity = EXCLUDED.severity,
                    threshold_config = EXCLUDED.threshold_config,
                    source_table = EXCLUDED.source_table,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING check_key;
            """)
            key = conn.execute(stmt, {
                "code": r["code"],
                "name": r.get("name", r["code"]),
                "ctype": r.get("type", "COMPLETENESS"),
                "desc": r.get("name", r["code"]),
                "sev": r.get("severity", "WARNING"),
                "cfg": config_json,
                "tbl": r.get("table", ""),
            }).scalar()
            check_keys[r["code"]] = key

    return check_keys
