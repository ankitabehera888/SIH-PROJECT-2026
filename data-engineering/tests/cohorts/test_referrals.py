import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_pending_referrals_cohort():
    """Verify Pending Referrals cohort tracks active unresolved care transfers."""
    with open("sql/cohorts/pending_referrals.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert len(df) > 0
    assert df["patient_key"].nunique() == len(df)
    assert (df["risk_score"] == 25.0).all()
