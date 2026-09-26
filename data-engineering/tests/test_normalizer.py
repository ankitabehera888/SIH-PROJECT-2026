import pandas as pd
from src.staging.normalizer import (
    normalize_string_series,
    standardize_code_series,
    normalize_phone_series,
    normalize_email_series,
    normalize_uuid_series,
)

def test_string_trimming_and_casing():
    """Verify string whitespace trimming and casing normalization."""
    # Status code normalization
    s = pd.Series(["  COMPLETED  ", "completed", " Completed ", None])
    norm = normalize_string_series(s, lowercase=True)
    assert norm.iloc[0] == "completed"
    assert norm.iloc[1] == "completed"
    assert norm.iloc[2] == "completed"
    assert pd.isna(norm.iloc[3])

    # Name trimming without lowercase
    names = pd.Series(["  Dr. Anjali Sharma  ", "Rajesh  Kumar  "])
    norm_names = normalize_string_series(names, lowercase=False)
    assert norm_names.iloc[0] == "Dr. Anjali Sharma"
    assert norm_names.iloc[1] == "Rajesh Kumar"

def test_code_standardization():
    """Verify mapping of clinical codes to canonical representations."""
    mapping = {"done": "completed", "complete": "completed", "completed": "completed", "cancelled": "cancelled"}
    s = pd.Series(["DONE", " complete ", "Completed", "other_status"])
    standardized = standardize_code_series(s, mapping)
    assert standardized.iloc[0] == "completed"
    assert standardized.iloc[1] == "completed"
    assert standardized.iloc[2] == "completed"
    assert standardized.iloc[3] == "other_status"

def test_phone_normalization():
    """Verify phone formatting into phone_raw and standard E.164 phone_normalized."""
    phones = pd.Series(["9876543210", "+91 98765 43210", "09876543210", None])
    raw, norm = normalize_phone_series(phones)
    assert raw.iloc[0] == "9876543210"
    assert norm.iloc[0] == "+919876543210"
    assert norm.iloc[1] == "+919876543210"
    assert norm.iloc[2] == "+919876543210"
    assert pd.isna(raw.iloc[3])
    assert pd.isna(norm.iloc[3])

def test_email_normalization():
    """Verify email lowercasing and syntax validation."""
    emails = pd.Series([" USER@Example.COM ", "patient@hospital.org", "invalid_email_at_dot_com", None])
    norm, valid = normalize_email_series(emails)
    assert norm.iloc[0] == "user@example.com"
    assert bool(valid.iloc[0]) is True
    assert norm.iloc[1] == "patient@hospital.org"
    assert bool(valid.iloc[1]) is True
    assert bool(valid.iloc[2]) is False
    assert pd.isna(norm.iloc[3])
    assert bool(valid.iloc[3]) is True  # Missing is acceptable

def test_uuid_normalization():
    """Verify conversion of raw 16-byte binary UUIDs to standard 36-char UUID strings."""
    import uuid
    u = uuid.uuid4()
    binary_uuid = u.bytes
    s = pd.Series([binary_uuid, str(u), None])
    norm = normalize_uuid_series(s)
    assert norm.iloc[0] == str(u).lower()
    assert norm.iloc[1] == str(u).lower()
    assert pd.isna(norm.iloc[2])
