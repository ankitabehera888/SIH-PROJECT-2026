from typing import Any, Dict
import pandas as pd

def generate_fhir_patient(row: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a standard FHIR R4 Patient resource from staged patient data."""
    pid = str(row.get("patient_id", row.get("id", "")))
    source_pid = str(row.get("source_patient_id", row.get("patient_number", pid)))
    abha_id = row.get("abha_id")
    
    identifiers = [
        {
            "use": "usual",
            "system": "https://hospital.org/mrn",
            "value": source_pid
        }
    ]
    
    if pd.notna(abha_id) and abha_id is not None and str(abha_id).strip() != "":
        identifiers.append({
            "use": "official",
            "system": "https://healthid.abdm.gov.in",
            "value": str(abha_id).strip()
        })
        
    gender = str(row.get("gender", "unknown")).lower()
    if gender not in ("male", "female", "other", "unknown"):
        gender = "unknown"
        
    dob = row.get("date_of_birth")
    birth_date = str(dob)[:10] if pd.notna(dob) and dob is not None else None
    
    resource = {
        "resourceType": "Patient",
        "id": f"pat-{pid}",
        "identifier": identifiers,
        "active": True,
        "gender": gender,
    }
    if birth_date:
        resource["birthDate"] = birth_date
        
    return resource
