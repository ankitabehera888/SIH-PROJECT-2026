import pytest
from src.extraction.snapshot import extract_snapshot

def test_snapshot_reconciliation_pass():
    """Assert that live table extraction perfectly reconciles with 0 variance."""
    meta = extract_snapshot("facilities", snapshot_date="2026-09-02")
    assert meta["status"] == "success"
    assert meta["reconciliation_status"] == "RECONCILED"
    assert meta["reconciliation_variance"] == 0
    assert meta["source_row_count"] == meta["extracted_row_count"]
    assert meta["file_size_bytes"] > 0
    assert meta["sha256"] is not None

def test_reconciliation_critical_failure_triggers(monkeypatch):
    """Assert that a simulated mismatch between PostgreSQL and Parquet triggers a hard failure."""
    from src.extraction import snapshot
    
    # Mock source count returning artificially inflated count (+10)
    original_get_count = snapshot.get_table_row_count
    monkeypatch.setattr(snapshot, "get_table_row_count", lambda table, engine_instance=None: original_get_count(table, engine_instance) + 10)
    
    with pytest.raises(RuntimeError) as excinfo:
        snapshot.extract_snapshot("facilities", snapshot_date="2026-09-02")
        
    assert "CRITICAL RECONCILIATION FAILURE" in str(excinfo.value)
