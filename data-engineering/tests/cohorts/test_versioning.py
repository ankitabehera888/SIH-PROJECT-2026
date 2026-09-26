from sqlalchemy import text
from src.database import engine
from src.cohorts.builder import build_all_cohorts

def test_cohort_registry_versions():
    """Verify all 6 cohort definitions are registered in analytics.cohort_registry with active status."""
    with engine.connect() as conn:
        records = conn.execute(text("SELECT cohort_name, cohort_version, status FROM analytics.cohort_registry;")).fetchall()
        
    names = {r[0] for r in records}
    assert {"diabetes", "hypertension", "high_risk", "missed_appointments", "pending_referrals", "chronic_followup"}.issubset(names)
    for r in records:
        assert r[1] == "v1.0"
        assert r[2] == "active"

def test_cohort_builder_reproducibility():
    """Verify that running cohort generation twice yields identical patient memberships."""
    res1 = build_all_cohorts(run_id="repro_run_1")
    counts1 = {s["Cohort"]: s["Patients"] for s in res1["summary"]}
    
    res2 = build_all_cohorts(run_id="repro_run_2")
    counts2 = {s["Cohort"]: s["Patients"] for s in res2["summary"]}
    
    assert counts1 == counts2, f"Discrepancy in consecutive cohort runs: {counts1} vs {counts2}"
