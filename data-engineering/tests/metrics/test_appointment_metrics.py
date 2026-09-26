import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_appointment_metrics_calculation():
    """Verify appointment metrics calculation and bounds."""
    with open("sql/metrics/appointment_metrics.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert not df.empty
    r = df.iloc[0]
    
    assert r["appointment_volume"] > 0
    assert 0.0 <= r["appointment_completion_rate"] <= 1.0
    assert 0.0 <= r["appointment_cancellation_rate"] <= 1.0
    assert 0.0 <= r["appointment_no_show_rate"] <= 1.0
    assert r["average_wait_minutes"] >= 0.0
    assert r["median_wait_minutes"] >= 0.0
