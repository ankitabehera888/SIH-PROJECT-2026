from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from src.database import engine
from src.extraction.extractor import extract_table, get_table_row_count, list_extractable_tables
from src.extraction.metadata import generate_extraction_metadata, save_manifest
from src.raw.writer import write_raw_parquet

def extract_snapshot(
    table_name: str,
    snapshot_date: Optional[str] = None,
    engine_instance=None
) -> Dict:
    """
    Executes a single-table snapshot extraction with hard row-count reconciliation.
    
    Steps:
    1. Query live PostgreSQL row count.
    2. Extract entire table into memory (read-only).
    3. Write compressed Parquet to data/raw/<table_name>/snapshot_<date>.parquet.
    4. Re-read Parquet file and reconcile exact row counts.
    5. Compute cryptographic SHA-256 and schema hash.
    6. Return complete audit metadata dictionary.
    """
    eng = engine_instance or engine
    date_str = snapshot_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # 1. Source row count
    source_count = get_table_row_count(table_name, engine_instance=eng)
    
    # 2. Extract into DataFrame
    df = extract_table(table_name, engine_instance=eng)
    extracted_count = len(df)
    
    # 3. Write Parquet
    parquet_path, file_size_bytes = write_raw_parquet(df, table_name, snapshot_date=date_str)
    
    # 4. Strict Row-Count Reconciliation
    df_recheck = pd.read_parquet(parquet_path, engine="pyarrow")
    parquet_count = len(df_recheck)
    
    if source_count != parquet_count:
        raise RuntimeError(
            f"CRITICAL RECONCILIATION FAILURE on '{table_name}': "
            f"PostgreSQL source count ({source_count}) != Parquet file count ({parquet_count}). "
            f"Extraction aborted."
        )
        
    # 5. Metadata generation
    meta = generate_extraction_metadata(
        table_name=table_name,
        source_row_count=source_count,
        extracted_row_count=parquet_count,
        df=df,
        file_path=parquet_path,
        file_size_bytes=file_size_bytes,
        status="success",
    )
    
    return meta

def extract_all_snapshots(
    tables: Optional[List[str]] = None,
    snapshot_date: Optional[str] = None,
    engine_instance=None
) -> Dict:
    """
    Extracts all operational tables, performs row-count reconciliation for each,
    and publishes the run manifest.
    """
    eng = engine_instance or engine
    date_str = snapshot_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_id = f"extract_{date_str}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
    
    target_tables = tables or list_extractable_tables(engine_instance=eng, include_system=True)
    
    results = []
    failed = []
    
    for table in target_tables:
        try:
            meta = extract_snapshot(table, snapshot_date=date_str, engine_instance=eng)
            results.append(meta)
        except Exception as e:
            failed.append({
                "table": table,
                "error": str(e),
                "status": "failed",
            })
            
    # Save extraction manifest
    latest_manifest, run_manifest = save_manifest(run_id=run_id, tables_metadata=results)
    
    return {
        "run_id": run_id,
        "total_attempted": len(target_tables),
        "successful_count": len(results),
        "failed_count": len(failed),
        "successful_tables": results,
        "failed_tables": failed,
        "manifest_path": str(latest_manifest),
    }
