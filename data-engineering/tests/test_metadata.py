import json
from pathlib import Path
import pandas as pd
from src.extraction.metadata import calculate_sha256, calculate_schema_hash, generate_extraction_metadata, save_manifest

def test_calculate_sha256(tmp_path):
    """Assert deterministic SHA-256 calculation."""
    test_file = tmp_path / "sample.bin"
    test_file.write_bytes(b"Healthcare Platform Data Engineering Audit Test")
    
    hash1 = calculate_sha256(test_file)
    hash2 = calculate_sha256(test_file)
    assert hash1 == hash2
    assert len(hash1) == 64

def test_calculate_schema_hash():
    """Assert deterministic schema hash."""
    df1 = pd.DataFrame({"col_a": [1, 2], "col_b": ["x", "y"]})
    df2 = pd.DataFrame({"col_a": [10, 20], "col_b": ["m", "n"]})
    assert calculate_schema_hash(df1) == calculate_schema_hash(df2)

def test_save_manifest(tmp_path):
    """Assert manifest generation structure."""
    dummy_meta = [{
        "source_table": "patients",
        "source_row_count": 833,
        "extracted_row_count": 833,
        "reconciliation_status": "RECONCILED",
        "sha256": "abcdef123456",
        "status": "success",
    }]
    
    latest, run_log = save_manifest("run_test_01", dummy_meta, output_dir=tmp_path)
    assert latest.exists()
    assert run_log.exists()
    
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["run_id"] == "run_test_01"
    assert data["total_tables"] == 1
    assert data["total_rows_extracted"] == 833
    assert data["status"] == "success"
