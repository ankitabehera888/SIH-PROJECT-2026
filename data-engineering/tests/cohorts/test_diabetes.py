import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_diabetes_cohort_structure_and_execution():
    """Verify Diabetes SQL definition executes and conforms to schema requirements."""
    with open("sql/cohorts/diabetes.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    # Check expected columns
    expected_cols = {"patient_key", "index_date", "observation_start", "observation_end", "eligibility_status", "risk_score"}
    assert expected_cols.issubset(set(df.columns))
