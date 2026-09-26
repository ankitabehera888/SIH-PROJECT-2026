from src.interoperability.validation import validate_referential_integrity

def test_referential_integrity_success():
    """Verify validate_referential_integrity returns True when all references exist."""
    patients = [{"resourceType": "Patient", "id": "pat-001"}]
    encounters = [{"resourceType": "Encounter", "id": "enc-101", "subject": {"reference": "Patient/pat-001"}}]
    observations = [{
        "resourceType": "Observation",
        "id": "obs-201",
        "subject": {"reference": "Patient/pat-001"},
        "encounter": {"reference": "Encounter/enc-101"}
    }]
    medications = [{
        "resourceType": "MedicationRequest",
        "id": "med-301",
        "subject": {"reference": "Patient/pat-001"},
        "encounter": {"reference": "Encounter/enc-101"}
    }]
    
    is_valid, errors = validate_referential_integrity(patients, encounters, observations, medications)
    assert is_valid
    assert len(errors) == 0

def test_referential_integrity_detects_broken_links():
    """Verify broken patient and encounter links are caught and reported."""
    patients = [{"resourceType": "Patient", "id": "pat-001"}]
    encounters = [{"resourceType": "Encounter", "id": "enc-101", "subject": {"reference": "Patient/pat-001"}}]
    # Observation referencing non-existent Patient/pat-999 and Encounter/enc-999
    broken_observations = [{
        "resourceType": "Observation",
        "id": "obs-broken",
        "subject": {"reference": "Patient/pat-999"},
        "encounter": {"reference": "Encounter/enc-999"}
    }]
    
    is_valid, errors = validate_referential_integrity(patients, encounters, broken_observations, [])
    assert not is_valid
    assert len(errors) == 2
    assert any("Patient/pat-999" in e for e in errors)
    assert any("Encounter/enc-999" in e for e in errors)
