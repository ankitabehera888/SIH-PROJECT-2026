from typing import Any, Dict, List
import pandas as pd
from src.interoperability.fhir.observation import generate_fhir_vital_observations

def map_vitals_to_fhir_observations(df_vitals: pd.DataFrame) -> List[Dict[str, Any]]:
    """Transforms staged vital records into standard FHIR R4 Observation resources."""
    all_observations = []
    for _, row in df_vitals.iterrows():
        try:
            obs_list = generate_fhir_vital_observations(row.to_dict())
            all_observations.extend(obs_list)
        except Exception:
            pass
    return all_observations
