from typing import Dict, List, Optional

LOINC_SYSTEM = "http://loinc.org"
UCUM_SYSTEM = "http://unitsofmeasure.org"
SNOMED_SYSTEM = "http://snomed.info/sct"

VITAL_TERMINOLOGY_MAP = {
    "systolic_bp": {
        "loinc_code": "8480-6",
        "loinc_display": "Systolic blood pressure",
        "ucum_unit": "mm[Hg]",
        "display_unit": "mmHg"
    },
    "diastolic_bp": {
        "loinc_code": "8462-4",
        "loinc_display": "Diastolic blood pressure",
        "ucum_unit": "mm[Hg]",
        "display_unit": "mmHg"
    },
    "heart_rate": {
        "loinc_code": "8867-4",
        "loinc_display": "Heart rate",
        "ucum_unit": "/min",
        "display_unit": "bpm"
    },
    "temperature": {
        "loinc_code": "8310-5",
        "loinc_display": "Body temperature",
        "ucum_unit": "Cel",
        "display_unit": "°C"
    },
    "spo2": {
        "loinc_code": "2708-6",
        "loinc_display": "Oxygen saturation in Arterial blood",
        "ucum_unit": "%",
        "display_unit": "%"
    },
    "respiratory_rate": {
        "loinc_code": "9279-1",
        "loinc_display": "Respiratory rate",
        "ucum_unit": "/min",
        "display_unit": "breaths/min"
    },
}

ENCOUNTER_STATUS_MAP = {
    "planned": "planned",
    "in_progress": "in-progress",
    "completed": "finished",
    "cancelled": "cancelled",
}

def get_vital_terminology(vital_name: str) -> Optional[Dict[str, str]]:
    """Returns canonical LOINC code and UCUM unit for standard vital measurements."""
    return VITAL_TERMINOLOGY_MAP.get(vital_name.lower())

def get_all_terminology_mappings() -> List[Dict]:
    """Returns all standard crosswalk records for populating analytics.terminology_map."""
    records = []
    
    # Vitals
    for v_key, info in VITAL_TERMINOLOGY_MAP.items():
        records.append({
            "domain": "vitals",
            "source_system": "internal_db",
            "source_code": v_key,
            "source_display": v_key.replace("_", " ").title(),
            "target_system": LOINC_SYSTEM,
            "target_code": info["loinc_code"],
            "target_display": info["loinc_display"],
            "mapping_status": "mapped",
            "mapping_version": "1.0",
        })
        
    # Encounter statuses
    for src_st, target_st in ENCOUNTER_STATUS_MAP.items():
        records.append({
            "domain": "encounter_status",
            "source_system": "internal_db",
            "source_code": src_st,
            "source_display": src_st.replace("_", " ").title(),
            "target_system": "http://hl7.org/fhir/encounter-status",
            "target_code": target_st,
            "target_display": target_st.capitalize(),
            "mapping_status": "mapped",
            "mapping_version": "1.0",
        })
        
    return records
