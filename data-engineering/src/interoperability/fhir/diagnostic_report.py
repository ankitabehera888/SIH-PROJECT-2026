from typing import Any, Dict
import pandas as pd

def generate_fhir_diagnostic_report(row: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a standard FHIR R4 DiagnosticReport resource."""
    diag_id = str(row.get("id", ""))
    pid = str(row.get("patient_id", ""))
    enc_id = str(row.get("encounter_id", ""))
    
    status_raw = str(row.get("status", "final")).lower()
    fhir_status = "final" if status_raw in ("final", "completed") else "preliminary"
    
    created_at = row.get("created_at", row.get("ordered_at"))
    eff_datetime = pd.to_datetime(created_at).isoformat() if pd.notna(created_at) else None
    
    resource = {
        "resourceType": "DiagnosticReport",
        "id": f"diag-{diag_id}",
        "status": fhir_status,
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "11502-2",
                    "display": "Laboratory report"
                }
            ],
            "text": "Clinical Laboratory Diagnostic Report"
        },
        "subject": {
            "reference": f"Patient/pat-{pid}"
        },
    }
    
    if enc_id and enc_id != "None" and enc_id != "nan":
        resource["encounter"] = {
            "reference": f"Encounter/enc-{enc_id}"
        }
        
    if eff_datetime:
        resource["effectiveDateTime"] = eff_datetime
        
    return resource
