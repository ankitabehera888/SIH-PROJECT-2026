from src.interoperability.fhir.medication_request import generate_fhir_medication_request

def test_generate_fhir_medication_request_valid():
    """Verify FHIR MedicationRequest resource generation."""
    sample_row = {
        "id": "rx-uuid-999",
        "patient_id": "pat-001",
        "encounter_id": "enc-001",
        "status": "active",
        "notes": "Paracetamol 500mg TDS for 5 days",
        "created_at": "2026-09-01T10:20:00Z",
    }
    med_res = generate_fhir_medication_request(sample_row)
    
    assert med_res["resourceType"] == "MedicationRequest"
    assert med_res["id"] == "medrx-rx-uuid-999"
    assert med_res["status"] == "active"
    assert med_res["intent"] == "order"
    assert med_res["subject"]["reference"] == "Patient/pat-pat-001"
    assert med_res["encounter"]["reference"] == "Encounter/enc-enc-001"
    assert med_res["medicationCodeableConcept"]["text"] == "Paracetamol 500mg TDS for 5 days"
