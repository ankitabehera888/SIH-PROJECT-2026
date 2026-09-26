from src.profiling.validation import validate_clinical_values, get_validation_summary

def test_clinical_bounds_summary():
    """Assert that clinical vital signs summary produces records for all physiological domains."""
    df_summary = get_validation_summary()
    assert not df_summary.empty
    expected_vitals = [
        "Systolic Blood Pressure",
        "Diastolic Blood Pressure",
        "Heart Rate",
        "Body Temperature",
        "Oxygen Saturation",
        "Respiratory Rate",
    ]
    for v in expected_vitals:
        assert v in df_summary["Vital_Sign"].values, f"Missing vital metric: {v}"

def test_operational_vitals_validity():
    """Assert that all live vitals recorded in the operational database conform to physiological boundaries."""
    df_invalid = validate_clinical_values()
    assert len(df_invalid) == 0, f"Physiologically impossible vitals detected:\n{df_invalid}"
