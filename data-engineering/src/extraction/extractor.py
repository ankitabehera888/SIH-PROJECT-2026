from typing import List, Optional
import pandas as pd
from sqlalchemy import inspect, text
from src.database import engine

def list_extractable_tables(engine_instance=None, include_system: bool = False) -> List[str]:
    """Returns sorted list of tables available in the operational database."""
    eng = engine_instance or engine
    inspector = inspect(eng)
    tables = sorted(inspector.get_table_names(schema="public"))
    if not include_system:
        tables = [t for t in tables if t != "alembic_version"]
    return tables

def get_table_row_count(table_name: str, engine_instance=None) -> int:
    """Queries exact row count from the operational source table for reconciliation."""
    eng = engine_instance or engine
    inspector = inspect(eng)
    valid_tables = inspector.get_table_names(schema="public")
    if table_name not in valid_tables:
        raise ValueError(f"Table '{table_name}' does not exist in PostgreSQL schema 'public'.")
        
    with eng.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        return int(count)

def extract_table(table_name: str, engine_instance=None) -> pd.DataFrame:
    """
    Extracts an entire operational table into a pandas DataFrame in read-only mode.
    
    Guarantees:
    - Never modifies, updates, or locks source tables.
    - Preserves native SQL types, timestamps, and column nullabilities.
    - Validates table existence before querying.
    """
    eng = engine_instance or engine
    inspector = inspect(eng)
    valid_tables = inspector.get_table_names(schema="public")
    
    if table_name not in valid_tables:
        raise ValueError(
            f"Extraction rejected: Table '{table_name}' does not exist in PostgreSQL schema 'public'. "
            f"Available tables: {', '.join(sorted(valid_tables))}"
        )
        
    # Read entire table cleanly using read_sql_table
    df = pd.read_sql_table(table_name, con=eng)
    return df
