from typing import Any, Dict
import pandas as pd

def generate_fhir_encounter(row: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a standard FHIR R4 Encounter resource from staged encounter data."""
    enc_id = str(row.get("id", ""))
    pid = str(row.get("patient_id", ""))
    
    # Status mapping to FHIR EncounterStatus
    status_raw = str(row.get("status", "completed")).lower()
    status_map = {
        "completed": "finished",
        "in_progress": "in-progress",
        "planned": "planned",
        "cancelled": "cancelled"
    }
    fhir_status = status_map.get(status_raw, "finished")
    
    started_at = row.get("started_at")
    ended_at = row.get("ended_at")
    
    period = {}
    if pd.notna(started_at) and started_at is not None:
        period["start"] = pd.to_datetime(started_at).isoformat()
    if pd.notna(ended_at) and ended_at is not None:
        period["end"] = pd.to_datetime(ended_at).isoformat()
        
    resource = {
        "resourceType": "Encounter",
        "id": f"enc-{enc_id}",
        "status": fhir_status,
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory"
        },
        "subject": {
            "reference": f"Patient/pat-{pid}"
        },
    }
    if period:
        resource["period"] = period
        
    return resource
