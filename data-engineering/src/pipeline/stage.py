import logging
from typing import Dict
from src.staging.pipeline import run_staging_pipeline
from src.pipeline.context import PipelineContext

def execute_staging(context: PipelineContext, logger: logging.Logger) -> Dict:
    """Step 3: Executes data staging, normalization, clinical validation, and quality auditing."""
    logger.info("Starting Step 3: STAGING & Cleaning Pipeline...")
    
    try:
        result = run_staging_pipeline(run_id=context.run_id)
        df_rep = result["report_df"]
        
        staged_counts = {}
        for _, r in df_rep.iterrows():
            staged_counts[r["Table"]] = {
                "input_rows": int(r["Input_Rows"]),
                "output_rows": int(r["Output_Rows"]),
                "valid_rows": int(r["Valid_Rows"]),
                "duplicates_flagged": int(r["Duplicates_Flagged"]),
                "orphans_flagged": int(r["Orphans_Flagged"]),
            }
            logger.info(f"Staged {r['Table']}: {r['Output_Rows']:,} rows ({r['Valid_Rows']:,} valid, {r['Duplicates_Flagged']} dups, {r['Orphans_Flagged']} orphans)")
            
        details = {
            "tables_staged": result["tables_staged"],
            "report_path": result["report_path"],
            "counts": staged_counts,
        }
        context.record_step("stage", "success", details)
        logger.info("Step 3 completed successfully. Staging outputs written.")
        return details
    except Exception as e:
        logger.error(f"Step 3 Staging failed: {e}")
        context.record_error("stage", str(e))
        raise
