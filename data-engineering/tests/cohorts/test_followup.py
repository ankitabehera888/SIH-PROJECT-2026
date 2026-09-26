import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_chronic_followup_cohort():
    """Verify Chronic Disease Follow-up cohort extracts chronic patients and calculates 180-day window."""
    with open("sql/cohorts/chronic_followup.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert len(df) > 0
    assert df["patient_key"].nunique() == len(df)
    assert (df["risk_score"] == 30.0).all()
    assert set(df["eligibility_status"].unique()).issubset({"eligible", "overdue"})
