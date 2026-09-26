import re
import uuid
from typing import Dict, List, Optional, Tuple
import pandas as pd

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def normalize_uuid_series(series: pd.Series) -> pd.Series:
    """Converts 16-byte binary UUIDs, uuid.UUID objects, or strings to canonical UUID string format."""
    def to_uuid_str(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        if isinstance(val, bytes):
            if len(val) == 16:
                try:
                    return str(uuid.UUID(bytes=val)).lower()
                except Exception:
                    return val.hex()
            return val.hex()
        elif isinstance(val, uuid.UUID):
            return str(val).lower()
        s = str(val).strip()
        return s.lower() if s != "" else None
        
    return series.apply(to_uuid_str)

def normalize_string_series(series: pd.Series, lowercase: bool = False) -> pd.Series:
    """Trims leading/trailing whitespace and optionally normalizes to lowercase."""
    def clean_str(val):
        if pd.isna(val) or val is None:
            return None
        s = str(val).strip()
        s = re.sub(r"\s+", " ", s)
        return s.lower() if lowercase else s
        
    return series.apply(clean_str)

def standardize_code_series(series: pd.Series, mapping: Dict[str, str]) -> pd.Series:
    """Maps status and categorical codes to canonical standardized vocabularies."""
    def map_code(val):
        if pd.isna(val) or val is None:
            return "unknown"
        norm_key = str(val).strip().lower()
        return mapping.get(norm_key, norm_key)
        
    return series.apply(map_code)

def normalize_phone_series(series: pd.Series) -> Tuple[pd.Series, pd.Series]:
    """
    Standardizes phone numbers while strictly preserving provenance.
    
    Returns:
    - phone_raw: exact original value trimmed
    - phone_normalized: standardized E.164 string (+91...) or None
    """
    raw_list = []
    norm_list = []
    
    for val in series:
        if pd.isna(val) or val is None or str(val).strip() == "":
            raw_list.append(None)
            norm_list.append(None)
            continue
            
        raw_val = str(val).strip()
        raw_list.append(raw_val)
        
        # Remove whitespace, hyphens, parentheses
        digits_only = re.sub(r"[^\d+]", "", raw_val)
        
        # Handle Indian numbering format (+91, 0, or 10-digit)
        if digits_only.startswith("+91") and len(digits_only) == 13:
            norm_val = digits_only
        elif digits_only.startswith("91") and len(digits_only) == 12:
            norm_val = f"+{digits_only}"
        elif digits_only.startswith("0") and len(digits_only) == 11:
            norm_val = f"+91{digits_only[1:]}"
        elif len(digits_only) == 10 and digits_only.isdigit():
            norm_val = f"+91{digits_only}"
        else:
            # Non-standard or foreign number, retain cleaned string
            norm_val = digits_only if digits_only.startswith("+") else f"+{digits_only}"
            
        norm_list.append(norm_val)
        
    return pd.Series(raw_list, index=series.index), pd.Series(norm_list, index=series.index)

def normalize_email_series(series: pd.Series) -> Tuple[pd.Series, pd.Series]:
    """
    Normalizes email addresses to lowercase and validates syntax.
    
    Returns:
    - email_normalized: trimmed and lowercased email string
    - email_is_valid: boolean indicating RFC syntax validity
    """
    norm_list = []
    valid_list = []
    
    for val in series:
        if pd.isna(val) or val is None or str(val).strip() == "":
            norm_list.append(None)
            valid_list.append(True)  # Missing email is acceptable, not invalid syntax
            continue
            
        cleaned = str(val).strip().lower()
        norm_list.append(cleaned)
        is_valid = bool(EMAIL_REGEX.match(cleaned))
        valid_list.append(is_valid)
        
    return pd.Series(norm_list, index=series.index), pd.Series(valid_list, index=series.index)

def standardize_timestamps_utc(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Standardizes date/time columns into ISO-8601 UTC representation."""
    df_out = df.copy()
    for col in columns:
        if col in df_out.columns:
            df_out[col] = pd.to_datetime(df_out[col], utc=True, errors="coerce")
    return df_out
