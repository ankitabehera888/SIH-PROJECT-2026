from typing import Dict
from sqlalchemy import text
from src.database import engine as default_engine
from src.metrics.definitions import METRIC_CATALOG

def sync_metric_registry(engine_instance=None) -> Dict[str, int]:
    """
    Synchronizes the authoritative KPI catalog in analytics.metric_registry.
    Returns a dictionary mapping metric_code -> metric_key.
    """
    engine = engine_instance or default_engine
    metric_keys = {}
    
    with engine.begin() as conn:
        for m_def in METRIC_CATALOG:
            stmt = text("""
                INSERT INTO analytics.metric_registry (
                    metric_code, metric_name, description, metric_type,
                    numerator_definition, denominator_definition,
                    population_definition, exclusion_definition,
                    time_basis, grain, source_tables, calculation_version, is_active
                ) VALUES (
                    :code, :name, :desc, :m_type,
                    :num_def, :den_def,
                    :pop_def, :excl_def,
                    :time_b, :grain, :sources, :version, TRUE
                )
                ON CONFLICT (metric_code)
                DO UPDATE SET
                    metric_name = EXCLUDED.metric_name,
                    description = EXCLUDED.description,
                    metric_type = EXCLUDED.metric_type,
                    numerator_definition = EXCLUDED.numerator_definition,
                    denominator_definition = EXCLUDED.denominator_definition,
                    population_definition = EXCLUDED.population_definition,
                    exclusion_definition = EXCLUDED.exclusion_definition,
                    time_basis = EXCLUDED.time_basis,
                    grain = EXCLUDED.grain,
                    source_tables = EXCLUDED.source_tables,
                    calculation_version = EXCLUDED.calculation_version,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING metric_key;
            """)
            key = conn.execute(stmt, {
                "code": m_def.metric_code,
                "name": m_def.metric_name,
                "desc": m_def.description,
                "m_type": m_def.metric_type,
                "num_def": m_def.numerator_definition,
                "den_def": m_def.denominator_definition,
                "pop_def": m_def.population_definition,
                "excl_def": m_def.exclusion_definition,
                "time_b": m_def.time_basis,
                "grain": m_def.grain,
                "sources": m_def.source_tables,
                "version": m_def.calculation_version,
            }).scalar()
            
            metric_keys[m_def.metric_code] = key
            
    return metric_keys
