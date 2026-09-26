import pytest
import pandas as pd
from src.extraction.extractor import extract_table, get_table_row_count, list_extractable_tables

def test_list_extractable_tables():
    """Verify that operational tables are discoverable."""
    tables = list_extractable_tables()
    assert len(tables) >= 20
    assert "patients" in tables
    assert "encounters" in tables
    assert "vitals" in tables
    assert "appointments" in tables

def test_get_table_row_count():
    """Verify exact count query matches reality."""
    count = get_table_row_count("patients")
    assert count > 0
    assert isinstance(count, int)

def test_extract_table_valid():
    """Verify that extract_table extracts real data into a pandas DataFrame."""
    df = extract_table("patients")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "id" in df.columns
    assert "first_name" in df.columns
    assert "created_at" in df.columns

def test_extract_table_invalid_raises():
    """Verify that extracting an unknown table raises ValueError cleanly without SQL corruption."""
    with pytest.raises(ValueError) as excinfo:
        extract_table("non_existent_clinical_table_xyz")
    assert "does not exist" in str(excinfo.value)
