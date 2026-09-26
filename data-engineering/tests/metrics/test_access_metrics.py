import pandas as pd
from sqlalchemy import text
from src.database import engine
from src.metrics.aggregations import compute_facility_aggregations

def test_access_metrics_calculation():
    """Verify unique patients served and facility metrics."""
    with open("sql/metrics/access_metrics.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert not df.empty
    r = df.iloc[0]
    
    assert r["unique_patients_served"] > 0
    assert r["facilities_serving_patients"] > 0
    assert r["patients_served_per_facility"] >= 1.0

def test_facility_aggregations():
    """Verify compute_facility_aggregations returns non-empty list of facilities with encounter counts."""
    fac_records = compute_facility_aggregations()
    assert len(fac_records) > 0
    for fac in fac_records:
        assert fac["encounter_volume"] > 0
        assert fac["patients_served"] > 0
