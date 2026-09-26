import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_encounter_metrics_calculation():
    """Verify clinical encounter metrics calculation and positive counts."""
    with open("sql/metrics/encounter_metrics.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert not df.empty
    r = df.iloc[0]
    
    assert r["encounter_volume"] > 0
    assert r["average_consultation_duration"] >= 0.0
    assert r["active_facilities_count"] > 0
    assert r["encounters_per_facility"] >= 1.0
    assert r["active_providers_count"] > 0
    assert r["encounters_per_provider"] >= 1.0
