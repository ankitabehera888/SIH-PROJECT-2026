import pytest
from sqlalchemy import text
from src.database import engine

def test_fact_appointment_integrity():
    """Verify fact_appointment row volume and key uniqueness."""
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT appointment_key) FROM analytics.fact_appointment;")).fetchone()
        count, distinct_keys = r
        assert count > 0
        assert count == distinct_keys

def test_fact_encounter_integrity():
    """Verify fact_encounter volume, key uniqueness, and non-negative durations."""
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT 
                COUNT(*), 
                COUNT(DISTINCT encounter_key),
                COUNT(*) FILTER (WHERE duration_minutes < 0)
            FROM analytics.fact_encounter;
        """)).fetchone()
        count, distinct_keys, negative_durations = r
        assert count > 0
        assert count == distinct_keys
        assert negative_durations == 0

def test_fact_referral_integrity():
    """Verify fact_referral volume, key uniqueness, and flags."""
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT 
                COUNT(*), 
                COUNT(DISTINCT referral_key),
                COUNT(*) FILTER (WHERE is_completed IS NULL)
            FROM analytics.fact_referral;
        """)).fetchone()
        count, distinct_keys, null_flags = r
        assert count > 0
        assert count == distinct_keys
        assert null_flags == 0

def test_fact_prescription_and_vital_integrity():
    """Verify fact_prescription and fact_vital volume and key uniqueness."""
    with engine.connect() as conn:
        rx_res = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT prescription_key) FROM analytics.fact_prescription;")).fetchone()
        assert rx_res[0] > 0
        assert rx_res[0] == rx_res[1]
        
        vit_res = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT vital_key) FROM analytics.fact_vital;")).fetchone()
        assert vit_res[0] > 0
        assert vit_res[0] == vit_res[1]
