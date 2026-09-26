import pytest
from sqlalchemy import text
from src.database import engine

def test_query_patient_encounters():
    """Verify analytical query: encounters per patient."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
                p.patient_key,
                COUNT(*) AS encounter_count
            FROM analytics.fact_encounter e
            JOIN analytics.dim_patient p
                ON e.patient_key = p.patient_key
            GROUP BY p.patient_key
            LIMIT 10;
        """)).fetchall()
        assert len(rows) > 0
        for r in rows:
            assert r[1] >= 1

def test_query_referral_completion_metrics():
    """Verify analytical query: referral completion rate and average completion time."""
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT
                COUNT(*) AS total_referrals,
                SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) AS completed,
                AVG(completion_days) FILTER (WHERE is_completed = TRUE) AS avg_completion_days
            FROM analytics.fact_referral;
        """)).fetchone()
        total, completed, avg_days = r
        assert total > 0
        assert completed >= 0
        assert completed <= total

def test_query_facility_workload():
    """Verify analytical query: encounters by facility."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
                f.facility_name,
                COUNT(*) AS encounters
            FROM analytics.fact_encounter e
            JOIN analytics.dim_facility f
                ON e.facility_key = f.facility_key
            GROUP BY f.facility_name
            ORDER BY encounters DESC
            LIMIT 5;
        """)).fetchall()
        assert len(rows) > 0
        top_name, top_count = rows[0]
        assert top_count >= 1
