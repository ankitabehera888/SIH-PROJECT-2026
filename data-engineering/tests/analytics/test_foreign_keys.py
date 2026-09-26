import pytest
from sqlalchemy import text
from src.database import engine

def test_fact_encounter_foreign_keys():
    """Assert zero orphan foreign keys in fact_encounter."""
    with engine.connect() as conn:
        # Patient FK
        p_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_encounter e
            LEFT JOIN analytics.dim_patient p ON e.patient_key = p.patient_key
            WHERE e.patient_key IS NOT NULL AND p.patient_key IS NULL;
        """)).scalar()
        assert p_orphans == 0

        # Facility FK
        f_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_encounter e
            LEFT JOIN analytics.dim_facility f ON e.facility_key = f.facility_key
            WHERE e.facility_key IS NOT NULL AND f.facility_key IS NULL;
        """)).scalar()
        assert f_orphans == 0

        # Date FK
        d_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_encounter e
            LEFT JOIN analytics.dim_date d ON e.date_key = d.date_key
            WHERE e.date_key IS NOT NULL AND d.date_key IS NULL;
        """)).scalar()
        assert d_orphans == 0

def test_fact_referral_foreign_keys():
    """Assert zero orphan foreign keys in fact_referral."""
    with engine.connect() as conn:
        p_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_referral r
            LEFT JOIN analytics.dim_patient p ON r.patient_key = p.patient_key
            WHERE r.patient_key IS NOT NULL AND p.patient_key IS NULL;
        """)).scalar()
        assert p_orphans == 0

def test_fact_prescription_and_vital_foreign_keys():
    """Assert zero orphan encounter foreign keys in prescription and vital facts."""
    with engine.connect() as conn:
        rx_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_prescription rx
            LEFT JOIN analytics.fact_encounter e ON rx.encounter_key = e.encounter_key
            WHERE rx.encounter_key IS NOT NULL AND e.encounter_key IS NULL;
        """)).scalar()
        assert rx_orphans == 0

        vit_orphans = conn.execute(text("""
            SELECT COUNT(*) 
            FROM analytics.fact_vital v
            LEFT JOIN analytics.fact_encounter e ON v.encounter_key = e.encounter_key
            WHERE v.encounter_key IS NOT NULL AND e.encounter_key IS NULL;
        """)).scalar()
        assert vit_orphans == 0
