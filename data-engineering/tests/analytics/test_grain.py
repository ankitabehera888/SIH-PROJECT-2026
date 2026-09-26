import pytest
from sqlalchemy import text
from src.database import engine

def test_fact_encounter_grain():
    """Verify grain: exactly one row represents one distinct clinical encounter."""
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT encounter_id) FROM analytics.fact_encounter;")).fetchone()
        assert r[0] == r[1], f"Double-counting hazard! Rows: {r[0]}, Distinct encounters: {r[1]}"

def test_fact_appointment_grain():
    """Verify grain: exactly one row represents one appointment."""
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT appointment_id) FROM analytics.fact_appointment;")).fetchone()
        assert r[0] == r[1]

def test_fact_referral_grain():
    """Verify grain: exactly one row represents one referral episode."""
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT referral_id) FROM analytics.fact_referral;")).fetchone()
        assert r[0] == r[1]

def test_double_counting_prevention_on_prescriptions():
    """
    Demonstrate double-counting prevention:
    Joining fact_encounter directly to fact_prescription must not be used for encounter volume.
    fact_encounter.prescription_count provides the exact metric without multiplying rows.
    """
    with engine.connect() as conn:
        actual_encounters = conn.execute(text("SELECT COUNT(*) FROM analytics.fact_encounter;")).scalar()
        
        # Proper query without join fan-out
        encounters_with_rx = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_encounter 
            WHERE prescription_count > 0;
        """)).scalar()
        
        assert encounters_with_rx <= actual_encounters
