from typing import Any, Dict, List
import pandas as pd

def calculate_observation_dates(index_date: str, window_days: int) -> Dict[str, str]:
    """Calculates observation window start and end dates relative to the index date."""
    dt = pd.to_datetime(index_date)
    obs_start = dt.strftime("%Y-%m-%d")
    obs_end = (dt + pd.Timedelta(days=window_days)).strftime("%Y-%m-%d")
    return {
        "observation_start": obs_start,
        "observation_end": obs_end,
    }

def calculate_patient_risk_score(
    has_chronic_condition: bool = False,
    has_pending_referral: bool = False,
    has_abnormal_vitals: bool = False,
    encounter_count: int = 0
) -> float:
    """Calculates multi-factor clinical risk score."""
    score = 0.0
    if has_chronic_condition:
        score += 20.0
    if has_pending_referral:
        score += 15.0
    if has_abnormal_vitals:
        score += 10.0
    if encounter_count >= 2:
        score += 10.0
    return score
