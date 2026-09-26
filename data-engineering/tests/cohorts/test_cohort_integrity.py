from sqlalchemy import text
from src.database import engine

def test_cohort_membership_referential_integrity():
    """Verify zero orphan foreign keys in analytics.cohort_membership."""
    with engine.connect() as conn:
        # Patient FK
        p_orphans = conn.execute(text("""
            SELECT COUNT(*) FROM analytics.cohort_membership m
            LEFT JOIN analytics.dim_patient p ON m.patient_key = p.patient_key
            WHERE p.patient_key IS NULL;
        """)).scalar()
        assert p_orphans == 0, f"Found {p_orphans} orphan patient keys in cohort_membership"
        
        # Cohort FK
        c_orphans = conn.execute(text("""
            SELECT COUNT(*) FROM analytics.cohort_membership m
            LEFT JOIN analytics.cohort_registry r ON m.cohort_key = r.cohort_key
            WHERE r.cohort_key IS NULL;
        """)).scalar()
        assert c_orphans == 0, f"Found {c_orphans} orphan cohort keys in cohort_membership"

def test_cohort_membership_no_duplicates():
    """Verify zero duplicate memberships for (cohort_key, patient_key, index_date)."""
    with engine.connect() as conn:
        dup_count = conn.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT cohort_key, patient_key, index_date, COUNT(*)
                FROM analytics.cohort_membership
                GROUP BY cohort_key, patient_key, index_date
                HAVING COUNT(*) > 1
            ) sub;
        """)).scalar()
        assert dup_count == 0, f"Found {dup_count} duplicate patient cohort memberships"

def test_cohort_observation_window_validity():
    """Verify observation_end is strictly on or after observation_start."""
    with engine.connect() as conn:
        invalid_windows = conn.execute(text("""
            SELECT COUNT(*) FROM analytics.cohort_membership
            WHERE observation_end < observation_start;
        """)).scalar()
        assert invalid_windows == 0, f"Found {invalid_windows} memberships with inverted observation windows"
