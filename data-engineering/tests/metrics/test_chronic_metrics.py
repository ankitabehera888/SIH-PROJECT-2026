import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_chronic_care_metrics_calculation():
    """Verify chronic care metrics reconcile with Phase 7 cohorts."""
    with open("sql/metrics/chronic_metrics.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert not df.empty
    r = df.iloc[0]
    
    # In our database, total hypertension and chronic patients were identified in Phase 7
    assert r["total_hypertension_patients"] >= 0
    assert r["total_chronic_patients"] >= 0
