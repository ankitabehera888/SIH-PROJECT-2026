from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

# Base directory for data-engineering
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

def get_raw_storage_path(table_name: str, snapshot_date: Optional[str] = None) -> Path:
    """Returns the standardized Parquet storage path: data/raw/<table_name>/snapshot_<date>.parquet"""
    date_str = snapshot_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    table_dir = RAW_DATA_DIR / table_name
    table_dir.mkdir(parents=True, exist_ok=True)
    return table_dir / f"snapshot_{date_str}.parquet"

def write_raw_parquet(
    df: pd.DataFrame,
    table_name: str,
    snapshot_date: Optional[str] = None,
    compression: str = "snappy"
) -> Tuple[Path, int]:
    """
    Writes extracted DataFrame to an immutable Parquet raw snapshot.
    
    Guarantees:
    - Creates necessary subdirectory structure automatically.
    - Uses PyArrow engine with snappy compression.
    - Preserves schema types and column order.
    - Returns target Path and exact file size in bytes.
    """
    output_path = get_raw_storage_path(table_name, snapshot_date)
    
    # Write Parquet with pyarrow engine
    df.to_parquet(
        output_path,
        engine="pyarrow",
        compression=compression,
        index=False,
    )
    
    file_size_bytes = output_path.stat().st_size
    return output_path, file_size_bytes
