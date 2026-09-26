from typing import Any, Dict, List, Set, Tuple

def validate_fhir_patient(res: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates required FHIR R4 Patient elements."""
    errors = []
    if res.get("resourceType") != "Patient":
        errors.append("Invalid resourceType; expected Patient")
    if not res.get("id"):
        errors.append("Missing Patient id")
    if not res.get("identifier"):
        errors.append("Patient identifier list is empty")
    if "gender" not in res:
        errors.append("Missing gender")
    return len(errors) == 0, errors

def validate_fhir_encounter(res: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates required FHIR R4 Encounter elements."""
    errors = []
    if res.get("resourceType") != "Encounter":
        errors.append("Invalid resourceType; expected Encounter")
    if not res.get("id"):
        errors.append("Missing Encounter id")
    if not res.get("status"):
        errors.append("Missing Encounter status")
    if not res.get("subject", {}).get("reference"):
        errors.append("Missing Encounter subject reference")
    return len(errors) == 0, errors

def validate_fhir_observation(res: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates required FHIR R4 Observation elements."""
    errors = []
    if res.get("resourceType") != "Observation":
        errors.append("Invalid resourceType; expected Observation")
    if not res.get("id"):
        errors.append("Missing Observation id")
    if not res.get("status"):
        errors.append("Missing Observation status")
    if not res.get("code", {}).get("coding"):
        errors.append("Missing Observation code coding")
    if not res.get("subject", {}).get("reference"):
        errors.append("Missing Observation subject reference")
    vq = res.get("valueQuantity", {})
    if vq.get("value") is None:
        errors.append("Missing Observation valueQuantity value")
    return len(errors) == 0, errors

def validate_referential_integrity(
    patients: List[Dict[str, Any]],
    encounters: List[Dict[str, Any]],
    observations: List[Dict[str, Any]],
    medications: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """
    Verifies that 100% of FHIR internal references resolve:
    - Observation.subject -> Patient
    - Observation.encounter -> Encounter
    - MedicationRequest.subject -> Patient
    - MedicationRequest.encounter -> Encounter
    - Encounter.subject -> Patient
    """
    errors = []
    patient_ids = {p["id"] for p in patients if "id" in p}
    encounter_ids = {e["id"] for e in encounters if "id" in e}
    
    # 1. Encounter -> Patient
    for enc in encounters:
        subj = enc.get("subject", {}).get("reference", "")
        if subj.startswith("Patient/"):
            target_id = subj.split("/", 1)[1]
            if target_id not in patient_ids:
                errors.append(f"Encounter/{enc.get('id')} references missing {subj}")
                
    # 2. Observation -> Patient & Encounter
    for obs in observations:
        subj = obs.get("subject", {}).get("reference", "")
        if subj.startswith("Patient/"):
            target_id = subj.split("/", 1)[1]
            if target_id not in patient_ids:
                errors.append(f"Observation/{obs.get('id')} references missing {subj}")
                
        enc_ref = obs.get("encounter", {}).get("reference", "")
        if enc_ref.startswith("Encounter/"):
            target_enc = enc_ref.split("/", 1)[1]
            if target_enc not in encounter_ids:
                errors.append(f"Observation/{obs.get('id')} references missing {enc_ref}")
                
    # 3. MedicationRequest -> Patient & Encounter
    for med in medications:
        subj = med.get("subject", {}).get("reference", "")
        if subj.startswith("Patient/"):
            target_id = subj.split("/", 1)[1]
            if target_id not in patient_ids:
                errors.append(f"MedicationRequest/{med.get('id')} references missing {subj}")
                
        enc_ref = med.get("encounter", {}).get("reference", "")
        if enc_ref.startswith("Encounter/"):
            target_enc = enc_ref.split("/", 1)[1]
            if target_enc not in encounter_ids:
                errors.append(f"MedicationRequest/{med.get('id')} references missing {enc_ref}")
                
    return len(errors) == 0, errors
