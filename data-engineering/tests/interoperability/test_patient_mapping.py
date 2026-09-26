from src.interoperability.fhir.patient import generate_fhir_patient
from src.interoperability.validation import validate_fhir_patient

def test_generate_fhir_patient_valid():
    """Verify FHIR Patient resource generation and compliance."""
    sample_row = {
        "patient_id": "test-uuid-001",
        "source_patient_id": "MRN-12345",
        "abha_id": "91-1234-5678-9012",
        "gender": "male",
        "date_of_birth": "1985-05-15",
    }
    patient_res = generate_fhir_patient(sample_row)
    
    assert patient_res["resourceType"] == "Patient"
    assert patient_res["id"] == "pat-test-uuid-001"
    assert patient_res["gender"] == "male"
    assert patient_res["birthDate"] == "1985-05-15"
    
    # Check identifiers: both MRN and ABHA must be present
    systems = [i["system"] for i in patient_res["identifier"]]
    assert "https://hospital.org/mrn" in systems
    assert "https://healthid.abdm.gov.in" in systems
    
    is_valid, errors = validate_fhir_patient(patient_res)
    assert is_valid, f"Validation errors: {errors}"
