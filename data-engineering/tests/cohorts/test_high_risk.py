import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_high_risk_cohort_threshold():
    """Verify High-Risk cohort selects patients strictly meeting risk score threshold >= 30.0."""
    with open("sql/cohorts/high_risk.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert len(df) > 0
    assert (df["risk_score"] >= 30.0).all()
    assert df["patient_key"].nunique() == len(df)
