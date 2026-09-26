import pytest
from sqlalchemy import text
from src.database import engine

def test_dim_date_range_and_uniqueness():
    """Verify dim_date covers 2020 to 2030 with unique date_key."""
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT date_key), MIN(full_date), MAX(full_date) FROM analytics.dim_date;")).fetchone()
        count, distinct_keys, min_d, max_d = r
        assert count == 4018
        assert count == distinct_keys
        assert str(min_d) == "2020-01-01"
        assert str(max_d) == "2030-12-31"

def test_dim_patient_pii_exclusion():
    """Verify dim_patient strictly excludes direct PII (name, phone, email, address)."""
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT patient_key) FROM analytics.dim_patient;")).fetchone()
        count, distinct_keys = r
        assert count > 0
        assert count == distinct_keys
        
        # Verify schema column names
        cols_res = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'analytics' AND table_name = 'dim_patient';
        """)).fetchall()
        col_names = [row[0] for row in cols_res]
        
        # Mandatory PII exclusions
        assert "first_name" not in col_names
        assert "last_name" not in col_names
        assert "phone" not in col_names
        assert "email" not in col_names
        assert "address" not in col_names
        
        # Mandatory analytical inclusions
        assert "patient_key" in col_names
        assert "patient_id" in col_names
        assert "age_band" in col_names

def test_dim_facility_and_provider_keys():
    """Verify uniqueness of facility and provider surrogate keys."""
    with engine.connect() as conn:
        f_res = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT facility_key) FROM analytics.dim_facility;")).fetchone()
        assert f_res[0] > 0
        assert f_res[0] == f_res[1]
        
        pr_res = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT provider_key) FROM analytics.dim_provider;")).fetchone()
        assert pr_res[0] > 0
        assert pr_res[0] == pr_res[1]
