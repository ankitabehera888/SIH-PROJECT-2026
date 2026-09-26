from typing import Any, Dict, List
import pandas as pd
from src.interoperability.mapping.terminology import get_vital_terminology

def generate_fhir_vital_observations(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates FHIR R4 Observation resources for validated vital signs.
    
    CRITICAL RULE:
    Invalid vitals (quality_status == 'invalid') are QUARANTINED and NOT exported
    as valid FHIR Observations.
    """
    observations = []
    vital_id = str(row.get("id", ""))
    pid = str(row.get("patient_id", ""))
    enc_id = str(row.get("encounter_id", ""))
    
    # Check overall vital quality status
    quality_status = str(row.get("_vital_quality_status", "valid"))
    if quality_status == "invalid":
        # Quarantined: do not export corrupted or physiologically impossible data
        return []
        
    recorded_at = row.get("recorded_at")
    eff_datetime = pd.to_datetime(recorded_at).isoformat() if pd.notna(recorded_at) else None
    
    vital_keys = [
        "systolic_bp",
        "diastolic_bp",
        "heart_rate",
        "temperature",
        "spo2",
        "respiratory_rate"
    ]
    
    for v_key in vital_keys:
        # Use validated value only
        val = row.get(f"{v_key}_validated", row.get(v_key))
        if pd.isna(val) or val is None:
            continue
            
        term_info = get_vital_terminology(v_key)
        if not term_info:
            continue
            
        obs_id = f"obs-{vital_id}-{v_key.replace('_', '-')}"
        obs = {
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": term_info["loinc_code"],
                        "display": term_info["loinc_display"]
                    }
                ],
                "text": term_info["loinc_display"]
            },
            "subject": {
                "reference": f"Patient/pat-{pid}"
            },
            "valueQuantity": {
                "value": round(float(val), 2),
                "unit": term_info["display_unit"],
                "system": "http://unitsofmeasure.org",
                "code": term_info["ucum_unit"]
            }
        }
        
        if enc_id and enc_id != "None" and enc_id != "nan":
            obs["encounter"] = {
                "reference": f"Encounter/enc-{enc_id}"
            }
            
        if eff_datetime:
            obs["effectiveDateTime"] = eff_datetime
            
        observations.append(obs)
        
    return observations
