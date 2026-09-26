from typing import Any, Dict, List
import pandas as pd
from src.interoperability.fhir.patient import generate_fhir_patient

def map_patients_to_fhir(df_patients: pd.DataFrame) -> List[Dict[str, Any]]:
    """Transforms staged patient records into FHIR R4 Patient resources."""
    fhir_patients = []
    for _, row in df_patients.iterrows():
        try:
            res = generate_fhir_patient(row.to_dict())
            fhir_patients.append(res)
        except Exception:
            pass
    return fhir_patients
