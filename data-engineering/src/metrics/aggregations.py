from typing import List, Dict
import pandas as pd
from sqlalchemy import text
from src.database import engine as default_engine

def compute_facility_aggregations(engine_instance=None) -> List[Dict]:
    """Computes clinical encounter volumes aggregated by healthcare facility."""
    engine = engine_instance or default_engine
    query = text("""
        SELECT
            f.facility_key,
            f.facility_name,
            COUNT(e.encounter_key) AS encounter_volume,
            COUNT(DISTINCT e.patient_key) AS patients_served
        FROM analytics.dim_facility f
        LEFT JOIN analytics.fact_encounter e ON f.facility_key = e.facility_key
        GROUP BY f.facility_key, f.facility_name
        HAVING COUNT(e.encounter_key) > 0
        ORDER BY encounter_volume DESC;
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_dict(orient="records")

def compute_geography_aggregations(engine_instance=None) -> List[Dict]:
    """Computes clinical encounter volumes aggregated by geography / district."""
    engine = engine_instance or default_engine
    query = text("""
        SELECT
            g.geography_key,
            g.district AS district_name,
            COUNT(e.encounter_key) AS encounter_volume
        FROM analytics.dim_geography g
        LEFT JOIN analytics.fact_encounter e ON 1=1 -- Regional reference link
        GROUP BY g.geography_key, g.district
        ORDER BY g.district ASC;
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_dict(orient="records")
