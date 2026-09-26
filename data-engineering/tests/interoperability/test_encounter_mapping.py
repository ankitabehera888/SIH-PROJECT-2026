from src.interoperability.fhir.encounter import generate_fhir_encounter
from src.interoperability.validation import validate_fhir_encounter

def test_generate_fhir_encounter_valid():
    """Verify FHIR Encounter resource generation, class, status, and period."""
    sample_row = {
        "id": "enc-uuid-101",
        "patient_id": "test-uuid-001",
        "status": "completed",
        "started_at": "2026-09-01T10:00:00Z",
        "ended_at": "2026-09-01T10:30:00Z",
    }
    encounter_res = generate_fhir_encounter(sample_row)
    
    assert encounter_res["resourceType"] == "Encounter"
    assert encounter_res["id"] == "enc-enc-uuid-101"
    assert encounter_res["status"] == "finished"
    assert encounter_res["class"]["code"] == "AMB"
    assert encounter_res["subject"]["reference"] == "Patient/pat-test-uuid-001"
    assert "start" in encounter_res["period"]
    
    is_valid, errors = validate_fhir_encounter(encounter_res)
    assert is_valid, f"Validation errors: {errors}"
