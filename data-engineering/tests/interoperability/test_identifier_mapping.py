import pandas as pd
from src.interoperability.abdm.identifiers import build_patient_identifier_mappings

def test_patient_identifier_mapping_separation():
    """Verify internal UUID is decoupled from MRN, FHIR ID, and ABHA ID."""
    df_sample = pd.DataFrame([
        {
            "patient_id": "uuid-1234",
            "source_patient_id": "MRN-5555",
            "abha_id": "91-0000-1111-2222",
        },
        {
            "patient_id": "uuid-5678",
            "source_patient_id": "MRN-6666",
            "abha_id": None,
        }
    ])
    patient_key_map = {"uuid-1234": 101, "uuid-5678": 102}
    
    mappings = build_patient_identifier_mappings(df_sample, patient_key_map)
    
    # Check patient 1 has 3 mappings: MRN, FHIR_ID, and ABHA_NUMBER
    p1_mappings = [m for m in mappings if m["internal_patient_id"] == "uuid-1234"]
    assert len(p1_mappings) == 3
    types = {m["identifier_type"] for m in p1_mappings}
    assert types == {"MRN", "FHIR_ID", "ABHA_NUMBER"}
    
    # Check patient 2 without ABHA has 2 mappings: MRN and FHIR_ID
    p2_mappings = [m for m in mappings if m["internal_patient_id"] == "uuid-5678"]
    assert len(p2_mappings) == 2
    types2 = {m["identifier_type"] for m in p2_mappings}
    assert types2 == {"MRN", "FHIR_ID"}
