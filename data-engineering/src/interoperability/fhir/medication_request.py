from typing import Any, Dict
import pandas as pd

def generate_fhir_medication_request(row: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a standard FHIR R4 MedicationRequest resource from staged prescription data."""
    rx_id = str(row.get("id", ""))
    pid = str(row.get("patient_id", ""))
    enc_id = str(row.get("encounter_id", ""))
    
    created_at = row.get("created_at", row.get("prescribed_at"))
    authored_on = pd.to_datetime(created_at).isoformat() if pd.notna(created_at) else None
    
    status = str(row.get("status", "active")).lower()
    fhir_status = "active" if status in ("active", "issued") else "completed" if status == "completed" else "cancelled"
    
    resource = {
        "resourceType": "MedicationRequest",
        "id": f"medrx-{rx_id}",
        "status": fhir_status,
        "intent": "order",
        "subject": {
            "reference": f"Patient/pat-{pid}"
        },
        "medicationCodeableConcept": {
            "text": str(row.get("notes", "Prescribed Clinical Medication"))
        }
    }
    
    if enc_id and enc_id != "None" and enc_id != "nan":
        resource["encounter"] = {
            "reference": f"Encounter/enc-{enc_id}"
        }
        
    if authored_on:
        resource["authoredOn"] = authored_on
        
    return resource
