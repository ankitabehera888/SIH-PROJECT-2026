from src.profiling.integrity import check_referential_integrity

def test_referential_integrity_all_pass():
    """Assert that every foreign key relationship in the database passes with 0 orphans."""
    df = check_referential_integrity()
    assert not df.empty
    assert len(df) >= 15
    failing = df[df["Status"] != "PASS"]
    assert len(failing) == 0, f"Failing foreign key relationships found:\n{failing}"

def test_critical_clinical_chains_intact():
    """Assert that patient -> encounter -> vitals and prescription chains have zero broken keys."""
    df = check_referential_integrity()
    vital_rel = df[df["Relationship"] == "vitals -> encounters"].iloc[0]
    assert vital_rel["Invalid_Orphan_Records"] == 0
    assert vital_rel["Status"] == "PASS"

    rx_rel = df[df["Relationship"] == "prescriptions -> encounters"].iloc[0]
    assert rx_rel["Invalid_Orphan_Records"] == 0
    assert rx_rel["Status"] == "PASS"
