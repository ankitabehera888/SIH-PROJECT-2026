import json
import logging
from typing import Dict
from sqlalchemy import text
from src.database import engine as default_engine
from src.cohorts.definitions import COHORT_DEFINITIONS

def sync_cohort_registry(engine_instance=None) -> Dict[str, int]:
    """
    Registers cohort definitions in analytics.cohort_registry.
    Returns a dictionary mapping (cohort_name, cohort_version) -> cohort_key.
    """
    engine = engine_instance or default_engine
    cohort_keys = {}
    
    with engine.begin() as conn:
        for c_def in COHORT_DEFINITIONS:
            criteria_json = json.dumps({
                "inclusion": c_def.inclusion_criteria,
                "exclusion": c_def.exclusion_criteria,
                "index_date_rule": c_def.index_date_rule,
                "observation_window_days": c_def.observation_window_days,
            })
            
            # Upsert registry record
            stmt = text("""
                INSERT INTO analytics.cohort_registry (cohort_name, cohort_version, description, definition_criteria, status)
                VALUES (:name, :version, :desc, :criteria, 'active')
                ON CONFLICT (cohort_name, cohort_version) 
                DO UPDATE SET description = EXCLUDED.description, definition_criteria = EXCLUDED.definition_criteria
                RETURNING cohort_key;
            """)
            key = conn.execute(stmt, {
                "name": c_def.name,
                "version": c_def.version,
                "desc": c_def.description,
                "criteria": criteria_json,
            }).scalar()
            
            cohort_keys[f"{c_def.name}_{c_def.version}"] = key
            
    return cohort_keys
