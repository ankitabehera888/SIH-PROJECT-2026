import numpy as np
import pandas as pd
from src.staging.validators import validate_vitals_non_destructive
from src.staging.cleaner import clean_patients, attach_lineage

def test_vitals_invalid_spo2_non_destructive():
    """Assert SpO2 = 150% preserves raw value, sets validated to NaN, and flags invalid."""
    df_raw = pd.DataFrame({
        "id": ["v1", "v2"],
        "spo2": [98.0, 150.0],
        "heart_rate": [72, 80]
    })
    
    df_clean = validate_vitals_non_destructive(df_raw)
    assert df_clean["spo2_raw"].iloc[0] == 98.0
    assert df_clean["spo2_validated"].iloc[0] == 98.0
    assert df_clean["_vital_quality_status"].iloc[0] == "valid"

    # Invalid record
    assert df_clean["spo2_raw"].iloc[1] == 150.0
    assert np.isnan(df_clean["spo2_validated"].iloc[1])
    assert df_clean["_vital_quality_status"].iloc[1] == "invalid"

def test_vitals_inverted_blood_pressure():
    """Assert systolic <= diastolic triggers invalid status and sets validated to NaN."""
    df_raw = pd.DataFrame({
        "id": ["v1"],
        "systolic_bp": [90],
        "diastolic_bp": [120]  # Inverted
    })
    df_clean = validate_vitals_non_destructive(df_raw)
    assert df_clean["systolic_bp_raw"].iloc[0] == 90
    assert df_clean["diastolic_bp_raw"].iloc[0] == 120
    assert np.isnan(df_clean["systolic_bp_validated"].iloc[0])
    assert np.isnan(df_clean["diastolic_bp_validated"].iloc[0])
    assert df_clean["_vital_quality_status"].iloc[0] == "invalid"

def test_patient_identifier_separation():
    """Assert internal patient_id, abha_id, and source_patient_id are segregated."""
    df_patients = pd.DataFrame({
        "id": ["p-uuid-1"],
        "patient_number": ["PAT-1001"],
        "first_name": ["Amit"],
        "last_name": ["Patel"],
        "gender": ["male"],
        "phone": ["9876543210"],
        "email": ["amit@example.com"]
    })
    df_identifiers = pd.DataFrame({
        "patient_id": ["p-uuid-1"],
        "system": ["https://abdm.gov.in/abha"],
        "value": ["14-1234-5678-9012"]
    })
    
    df_staged = clean_patients(df_patients, df_identifiers=df_identifiers, config={})
    assert df_staged["patient_id"].iloc[0] == "p-uuid-1"
    assert df_staged["source_patient_id"].iloc[0] == "PAT-1001"
    assert df_staged["abha_id"].iloc[0] == "14-1234-5678-9012"
    assert "phone_normalized" in df_staged.columns
    assert "_data_quality_status" in df_staged.columns

def test_lineage_metadata_attachment():
    """Assert lineage columns are correctly attached to any staged DataFrame."""
    df = pd.DataFrame({"val": [1, 2]})
    df_lineage = attach_lineage(df, "test_table", "test.parquet", "run_123")
    assert "_source_table" in df_lineage.columns
    assert df_lineage["_source_table"].iloc[0] == "test_table"
    assert df_lineage["_source_file"].iloc[0] == "test.parquet"
    assert df_lineage["_extraction_run_id"].iloc[0] == "run_123"
    assert "_staged_at" in df_lineage.columns
    assert df_lineage["_data_quality_status"].iloc[0] == "valid"
