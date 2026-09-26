from pathlib import Path
import pandas as pd
from src.raw.writer import write_raw_parquet, get_raw_storage_path

def test_get_raw_storage_path():
    """Verify deterministic snapshot path naming."""
    path = get_raw_storage_path("test_table", snapshot_date="2026-09-02")
    assert path.name == "snapshot_2026-09-02.parquet"
    assert "test_table" in str(path)

def test_write_raw_parquet(tmp_path):
    """Verify Parquet serialization, type preservation, and reading back."""
    df_sample = pd.DataFrame({
        "patient_id": ["p1", "p2", "p3"],
        "age": [25, 42, 67],
        "systolic": [120, 135, 140],
        "is_active": [True, False, True]
    })
    
    path, size_bytes = write_raw_parquet(df_sample, "test_patients", snapshot_date="2026-09-02")
    assert path.exists()
    assert size_bytes > 0
    
    # Read back and verify exact schema
    df_read = pd.read_parquet(path)
    assert len(df_read) == 3
    assert list(df_read.columns) == ["patient_id", "age", "systolic", "is_active"]
    assert df_read["age"].tolist() == [25, 42, 67]
    assert df_read["is_active"].tolist() == [True, False, True]
