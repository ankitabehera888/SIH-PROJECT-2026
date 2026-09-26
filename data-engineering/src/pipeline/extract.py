import logging
from typing import Dict
from src.extraction.snapshot import extract_all_snapshots
from src.pipeline.context import PipelineContext

def execute_extraction(context: PipelineContext, logger: logging.Logger) -> Dict:
    """Step 1: Executes complete database snapshot extraction to immutable RAW Parquet files."""
    logger.info("Starting Step 1: RAW Data Extraction from PostgreSQL...")
    
    try:
        res = extract_all_snapshots()
        total_rows = sum(t.get("extracted_row_count", 0) for t in res.get("successful_tables", []))
        details = {
            "manifest_path": res.get("manifest_path", ""),
            "total_tables_extracted": res.get("successful_count", 0),
            "total_rows_extracted": total_rows,
        }
        context.record_step("extract", "success", details)
        logger.info(f"Step 1 completed successfully. Total rows extracted: {total_rows:,} across {res.get('successful_count', 0)} tables.")
        return details
    except Exception as e:
        logger.error(f"Step 1 Extraction failed: {e}")
        context.record_error("extract", str(e))
        raise
