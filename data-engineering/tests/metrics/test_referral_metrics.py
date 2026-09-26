import pandas as pd
from sqlalchemy import text
from src.database import engine

def test_referral_metrics_calculation():
    """Verify referral metrics, completion and pending rate parity, and turnaround days."""
    with open("sql/metrics/referral_metrics.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
        
    assert not df.empty
    r = df.iloc[0]
    
    assert r["referral_volume"] > 0
    assert 0.0 <= r["referral_completion_rate"] <= 1.0
    assert 0.0 <= r["referral_pending_rate"] <= 1.0
    # Parity check: completion rate + pending rate must equal 1.0 (or 100%)
    assert round(r["referral_completion_rate"] + r["referral_pending_rate"], 2) == 1.0
    assert r["avg_referral_completion_days"] >= 0.0
