import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
METADATA_DIR = BASE_DIR / "metadata"

def calculate_sha256(file_path: Path) -> str:
    """Calculates cryptographic SHA-256 hash of a file for tamper-evident auditability."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def calculate_schema_hash(df: pd.DataFrame) -> str:
    """Calculates a deterministic MD5 hash of column names and data types."""
    schema_repr = "|".join([f"{col}:{str(dtype)}" for col, dtype in zip(df.columns, df.dtypes)])
    return hashlib.md5(schema_repr.encode("utf-8")).hexdigest()

def generate_extraction_metadata(
    table_name: str,
    source_row_count: int,
    extracted_row_count: int,
    df: pd.DataFrame,
    file_path: Path,
    file_size_bytes: int,
    status: str = "success",
    source_database: str = "healthcare_dev"
) -> Dict:
    """Constructs structured audit metadata for an extraction event."""
    file_sha256 = calculate_sha256(file_path) if file_path.exists() else None
    schema_hash = calculate_schema_hash(df)
    is_reconciled = (source_row_count == extracted_row_count)
    
    # Store relative path for portability
    try:
        rel_path = str(file_path.relative_to(BASE_DIR)).replace("\\", "/")
    except Exception:
        rel_path = str(file_path)
        
    return {
        "source_database": source_database,
        "source_table": table_name,
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_row_count": source_row_count,
        "extracted_row_count": extracted_row_count,
        "reconciliation_variance": extracted_row_count - source_row_count,
        "reconciliation_status": "RECONCILED" if is_reconciled else "MISMATCH_FAILED",
        "column_count": len(df.columns),
        "columns": [{"name": col, "dtype": str(dtype)} for col, dtype in zip(df.columns, df.dtypes)],
        "schema_hash": schema_hash,
        "file_path": rel_path,
        "file_size_bytes": file_size_bytes,
        "sha256": file_sha256,
        "status": status if is_reconciled else "failed",
    }

def save_manifest(
    run_id: str,
    tables_metadata: List[Dict],
    output_dir: Optional[Path] = None,
    source_database: str = "healthcare_dev"
) -> Tuple[Path, Path]:
    """
    Saves extraction manifest files:
    1. metadata/extraction_manifest.json (current pointer)
    2. metadata/extraction_<run_date>.json (historical audit run log)
    """
    target_dir = output_dir or METADATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    total_tables = len(tables_metadata)
    total_rows = sum(t.get("extracted_row_count", 0) for t in tables_metadata)
    all_reconciled = all(t.get("reconciliation_status") == "RECONCILED" for t in tables_metadata)
    
    manifest_payload = {
        "run_id": run_id,
        "source": source_database,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tables": total_tables,
        "total_rows_extracted": total_rows,
        "reconciliation_all_pass": all_reconciled,
        "status": "success" if all_reconciled else "failed",
        "tables": tables_metadata,
    }
    
    # 1. Latest manifest
    latest_file = target_dir / "extraction_manifest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)
        
    # 2. Historical dated run file
    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_file = target_dir / f"extraction_{date_tag}.json"
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)
        
    return latest_file, run_file
