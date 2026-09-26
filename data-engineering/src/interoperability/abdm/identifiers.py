from typing import Dict, List, Optional
import pandas as pd

def build_patient_identifier_mappings(
    df_staged_patients: pd.DataFrame,
    patient_key_map: Optional[Dict[str, int]] = None
) -> List[Dict]:
    """
    Builds decoupled 3-tier identity crosswalk for analytics.patient_identifier_map:
    Internal ID != FHIR Resource ID != ABDM ABHA ID.
    """
    mappings = []
    p_map = patient_key_map or {}
    
    for _, row in df_staged_patients.iterrows():
        pid = str(row["patient_id"])
        p_key = p_map.get(pid)
        source_pid = str(row.get("source_patient_id", pid))
        abha_id = row.get("abha_id")
        
        # 1. Hospital MRN
        mappings.append({
            "patient_key": p_key,
            "internal_patient_id": pid,
            "identifier_system": "https://hospital.org/mrn",
            "identifier_value": source_pid,
            "identifier_type": "MRN",
            "is_primary": False,
            "is_active": True,
        })
        
        # 2. FHIR Resource ID
        mappings.append({
            "patient_key": p_key,
            "internal_patient_id": pid,
            "identifier_system": "urn:ietf:rfc:3986",
            "identifier_value": f"pat-{pid}",
            "identifier_type": "FHIR_ID",
            "is_primary": False,
            "is_active": True,
        })
        
        # 3. National ABHA ID (if available)
        if pd.notna(abha_id) and abha_id is not None and str(abha_id).strip() != "":
            mappings.append({
                "patient_key": p_key,
                "internal_patient_id": pid,
                "identifier_system": "https://healthid.abdm.gov.in",
                "identifier_value": str(abha_id).strip(),
                "identifier_type": "ABHA_NUMBER",
                "is_primary": True,
                "is_active": True,
            })
            
    return mappings
