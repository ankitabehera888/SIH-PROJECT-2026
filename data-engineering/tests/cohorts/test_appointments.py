import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_missed_appointments_cohort():
    """Verify Missed Appointments cohort extracts patients with cancelled or no-show visits."""
    with open("sql/cohorts/missed_appointments.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert len(df) > 0
    assert df["patient_key"].nunique() == len(df)
    assert (df["risk_score"] == 15.0).all()
