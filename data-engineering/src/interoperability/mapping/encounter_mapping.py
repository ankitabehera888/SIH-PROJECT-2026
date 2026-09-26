from typing import Any, Dict, List
import pandas as pd
from src.interoperability.fhir.encounter import generate_fhir_encounter

def map_encounters_to_fhir(df_encounters: pd.DataFrame) -> List[Dict[str, Any]]:
    """Transforms staged encounter records into FHIR R4 Encounter resources."""
    fhir_encounters = []
    for _, row in df_encounters.iterrows():
        try:
            res = generate_fhir_encounter(row.to_dict())
            fhir_encounters.append(res)
        except Exception:
            pass
    return fhir_encounters
