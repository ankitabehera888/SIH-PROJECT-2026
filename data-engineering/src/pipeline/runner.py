import logging
import sys
import time
from typing import Dict, Optional

from src.pipeline.context import PipelineContext
from src.pipeline.logger import setup_pipeline_logger
from src.pipeline.extract import execute_extraction
from src.pipeline.raw_validation import execute_raw_validation
from src.pipeline.stage import execute_staging
from src.pipeline.dimensions import execute_dimensions_loading
from src.pipeline.facts import execute_facts_loading
from src.pipeline.reconcile import execute_reconciliation

def run_pipeline(
    context: Optional[PipelineContext] = None,
    logger: Optional[logging.Logger] = None,
    engine_instance=None
) -> PipelineContext:
    """
    Executes the entire Healthcare Platform ETL/ELT Pipeline:
    [1/6] Extracting source data
    [2/6] Validating raw data
    [3/6] Building staging
    [4/6] Loading dimensions
    [5/6] Loading facts
    [6/6] Reconciliation & audit
    
    Guarantees:
    - Critical failures stop downstream execution immediately.
    - Idempotent execution (repeated runs produce identical outputs without duplication).
    - Writes execution manifest under metadata/runs/<run_id>.json.
    - Updates metadata/pipeline_state.json.
    """
    ctx = context or PipelineContext()
    log = logger or setup_pipeline_logger(ctx.run_id)
    
    log.info("=" * 70)
    log.info(f"HEALTHCARE DATA PIPELINE -- RUN ID: {ctx.run_id}")
    log.info("=" * 70)
    
    steps = [
        ("extract", "Extracting source data", lambda: execute_extraction(ctx, log)),
        ("raw_validation", "Validating raw data", lambda: execute_raw_validation(ctx, log)),
        ("stage", "Building staging layer", lambda: execute_staging(ctx, log)),
        ("dimensions", "Loading dimensions", lambda: execute_dimensions_loading(ctx, log, engine_instance)),
        ("facts", "Loading facts", lambda: execute_facts_loading(ctx, log, engine_instance)),
        ("reconcile", "Reconciliation & audits", lambda: execute_reconciliation(ctx, log, engine_instance)),
    ]
    
    start_time = time.time()
    for idx, (step_key, step_desc, step_func) in enumerate(steps, start=1):
        ctx.current_step = idx
        step_header = f"[{idx}/6] {step_desc} "
        padded_header = f"{step_header:.<45} "
        
        try:
            step_func()
            log.info(f"{padded_header} SUCCESS")
        except Exception as e:
            log.error(f"{padded_header} FAILED: {e}")
            ctx.mark_finished(status="failed")
            log.error(f"Pipeline stopped at step {idx}/6 ({step_key}). Failure contained.")
            return ctx
            
    duration = time.time() - start_time
    ctx.mark_finished(status="success")
    log.info("=" * 70)
    log.info(f"PIPELINE COMPLETED SUCCESSFULLY in {duration:.2f} seconds.")
    log.info(f"Manifest written: metadata/runs/{ctx.run_id}.json")
    log.info("=" * 70)
    return ctx
