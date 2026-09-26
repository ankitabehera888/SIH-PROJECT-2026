import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_hypertension_cohort_population():
    """Verify Hypertension cohort identifies patients with diagnosis or elevated blood pressure."""
    with open("sql/cohorts/hypertension.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert len(df) > 0
    assert df["patient_key"].nunique() == len(df)
    assert (df["risk_score"] == 20.0).all()
    assert (df["eligibility_status"] == "eligible").all()
