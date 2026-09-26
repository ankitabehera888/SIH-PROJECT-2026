from src.interoperability.mapping.terminology import (
    get_vital_terminology,
    get_all_terminology_mappings,
    LOINC_SYSTEM,
    UCUM_SYSTEM,
)

def test_vital_terminology_lookup():
    """Verify standard LOINC codes and UCUM units are returned for standard vitals."""
    spo2_info = get_vital_terminology("spo2")
    assert spo2_info is not None
    assert spo2_info["loinc_code"] == "2708-6"
    assert spo2_info["ucum_unit"] == "%"
    
    hr_info = get_vital_terminology("heart_rate")
    assert hr_info is not None
    assert hr_info["loinc_code"] == "8867-4"
    assert hr_info["ucum_unit"] == "/min"

def test_unknown_terminology_returns_none_not_fake_code():
    """Verify unknown vitals return None rather than arbitrary made-up codes."""
    unknown_info = get_vital_terminology("non_existent_vital_metric")
    assert unknown_info is None

def test_all_terminology_mappings_structure():
    """Verify all pre-seeded terminology mappings have valid domain, code, and systems."""
    terms = get_all_terminology_mappings()
    assert len(terms) >= 10
    for t in terms:
        assert t["mapping_status"] == "mapped"
        assert t["target_system"] in (LOINC_SYSTEM, "http://hl7.org/fhir/encounter-status")
        assert len(t["target_code"]) > 0
