from src.interoperability.fhir.observation import generate_fhir_vital_observations
from src.interoperability.validation import validate_fhir_observation

def test_generate_fhir_vital_observations_valid():
    """Verify valid vital metrics produce standard LOINC Observation resources."""
    sample_row = {
        "id": "vit-uuid-500",
        "patient_id": "pat-001",
        "encounter_id": "enc-001",
        "_vital_quality_status": "valid",
        "recorded_at": "2026-09-01T10:15:00Z",
        "systolic_bp": 120.0,
        "diastolic_bp": 80.0,
        "heart_rate": 72.0,
        "spo2": 98.0,
    }
    observations = generate_fhir_vital_observations(sample_row)
    
    assert len(observations) == 4
    loinc_codes = [o["code"]["coding"][0]["code"] for o in observations]
    assert "8480-6" in loinc_codes  # Systolic BP
    assert "8462-4" in loinc_codes  # Diastolic BP
    assert "8867-4" in loinc_codes  # Heart rate
    assert "2708-6" in loinc_codes  # SpO2
    
    for obs in observations:
        is_val, errors = validate_fhir_observation(obs)
        assert is_val, f"Validation errors: {errors}"
        assert obs["subject"]["reference"] == "Patient/pat-pat-001"
        assert obs["encounter"]["reference"] == "Encounter/enc-enc-001"

def test_generate_fhir_vital_observations_quarantined_when_invalid():
    """Verify that invalid vitals are QUARANTINED and NEVER exported as valid FHIR Observations."""
    invalid_sample_row = {
        "id": "vit-uuid-corrupted",
        "patient_id": "pat-001",
        "encounter_id": "enc-001",
        "_vital_quality_status": "invalid",
        "recorded_at": "2026-09-01T10:15:00Z",
        "spo2": 150.0,  # Physiologically impossible
    }
    observations = generate_fhir_vital_observations(invalid_sample_row)
    assert len(observations) == 0, "Invalid vital was exported instead of being quarantined!"
