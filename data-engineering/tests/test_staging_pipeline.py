import hashlib
from pathlib import Path
import pandas as pd
from src.staging.cleaner import clean_encounters
from src.staging.pipeline import run_staging_pipeline, get_latest_raw_file

def test_end_to_end_staging_pipeline():
    """Assert full pipeline runs and outputs Parquet datasets."""
    result = run_staging_pipeline()
    assert len(result["tables_staged"]) >= 6
    assert Path(result["report_path"]).exists()
    
    # Verify patients staged
    patients_file = Path("data/staging/patients/patients.parquet")
    assert patients_file.exists()
    df_p = pd.read_parquet(patients_file)
    assert len(df_p) > 0
    assert "_data_quality_status" in df_p.columns

def test_raw_data_remains_untouched():
    """Assert that RAW input Parquet files are never modified by staging transformations."""
    raw_file = get_latest_raw_file("patients")
    assert raw_file is not None and raw_file.exists()
    
    # Compute SHA-256 before
    h_before = hashlib.sha256(raw_file.read_bytes()).hexdigest()
    
    # Run staging
    run_staging_pipeline()
    
    # Compute SHA-256 after
    h_after = hashlib.sha256(raw_file.read_bytes()).hexdigest()
    assert h_before == h_after, "CRITICAL: Raw file was modified during staging execution!"

def test_orphan_detection_in_encounters():
    """Assert that encounters referencing non-existent patients receive 'orphan' status."""
    df_encounters = pd.DataFrame({
        "id": ["enc-1", "enc-2"],
        "patient_id": ["existing-p1", "phantom-patient-999"],
        "status": ["completed", "in_progress"]
    })
    df_patients = pd.DataFrame({
        "patient_id": ["existing-p1"]
    })
    
    df_staged = clean_encounters(df_encounters, df_patients=df_patients, config={})
    assert df_staged["_data_quality_status"].iloc[0] == "valid"
    assert df_staged["_data_quality_status"].iloc[1] == "orphan"

def test_staging_idempotency():
    """Assert that executing the pipeline multiple times does not accumulate duplicate records."""
    run1 = run_staging_pipeline()
    p_file = Path("data/staging/patients/patients.parquet")
    count_run1 = len(pd.read_parquet(p_file))
    
    run2 = run_staging_pipeline()
    count_run2 = len(pd.read_parquet(p_file))
    
    assert count_run1 == count_run2, f"Pipeline is not idempotent! Run 1 had {count_run1}, Run 2 had {count_run2}"
