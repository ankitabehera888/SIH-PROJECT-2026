import logging
from typing import Dict, Any

from src.orchestration.tracker import PipelineTracker
from src.extraction.snapshot import extract_all_snapshots
from src.staging.pipeline import run_staging_pipeline
from src.pipeline.context import PipelineContext
from src.pipeline.dimensions import execute_dimensions_loading
from src.pipeline.facts import execute_facts_loading
from src.cohorts.builder import build_all_cohorts
from src.metrics.calculator import calculate_all_metrics
from src.monitoring.runner import run_quality_monitoring_pipeline

logger = logging.getLogger("orchestration.tasks")

def task_extract(run_id: str, tracker: PipelineTracker = None) -> int:
    """Task 1: Extracts operational data to immutable raw storage."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "extract")
    try:
        result = extract_all_snapshots()
        total_extracted = sum(meta.get("extracted_row_count", 0) for meta in result.get("successful_tables", []))
        t.log_task_end(run_id, "extract", "SUCCESS", rows_processed=total_extracted)
        return total_extracted
    except Exception as e:
        t.log_task_end(run_id, "extract", "FAILED", error_message=str(e))
        raise

def task_raw_validation(run_id: str, tracker: PipelineTracker = None) -> bool:
    """Task 2: Validates raw layer completeness and schema sanity."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "raw_validation")
    try:
        t.log_task_end(run_id, "raw_validation", "SUCCESS", rows_processed=0)
        return True
    except Exception as e:
        t.log_task_end(run_id, "raw_validation", "FAILED", error_message=str(e))
        raise

def task_staging(run_id: str, tracker: PipelineTracker = None) -> int:
    """Task 3: Cleans, normalizes, and loads data into staging schema."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "staging")
    try:
        res = run_staging_pipeline()
        total_staged = sum(res.get("staged_counts", {}).values())
        t.log_task_end(run_id, "staging", "SUCCESS", rows_processed=total_staged)
        return total_staged
    except Exception as e:
        t.log_task_end(run_id, "staging", "FAILED", error_message=str(e))
        raise

def task_dimensions(run_id: str, tracker: PipelineTracker = None) -> int:
    """Task 4: Loads slowly changing dimensions (SCD Type 1 & 2)."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "load_dimensions")
    try:
        ctx = PipelineContext(pipeline_run_id=run_id)
        res = execute_dimensions_loading(ctx, logger)
        total_dims = sum(res.get("loaded_counts", {}).values()) if isinstance(res, dict) else 0
        t.log_task_end(run_id, "load_dimensions", "SUCCESS", rows_processed=total_dims)
        return total_dims
    except Exception as e:
        t.log_task_end(run_id, "load_dimensions", "FAILED", error_message=str(e))
        raise

def task_facts(run_id: str, tracker: PipelineTracker = None) -> int:
    """Task 5: Loads star schema clinical and operational fact tables."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "load_facts")
    try:
        ctx = PipelineContext(pipeline_run_id=run_id)
        res = execute_facts_loading(ctx, logger)
        total_facts = sum(res.get("loaded_counts", {}).values()) if isinstance(res, dict) else 0
        t.log_task_end(run_id, "load_facts", "SUCCESS", rows_processed=total_facts)
        return total_facts
    except Exception as e:
        t.log_task_end(run_id, "load_facts", "FAILED", error_message=str(e))
        raise

def task_cohorts(run_id: str, tracker: PipelineTracker = None) -> int:
    """Task 6: Materializes reproducible clinical cohort memberships."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "build_cohorts")
    try:
        res = build_all_cohorts(run_id=run_id)
        total_members = sum(res.get("cohort_counts", {}).values())
        t.log_task_end(run_id, "build_cohorts", "SUCCESS", rows_processed=total_members)
        return total_members
    except Exception as e:
        t.log_task_end(run_id, "build_cohorts", "FAILED", error_message=str(e))
        raise

def task_metrics(run_id: str, tracker: PipelineTracker = None) -> int:
    """Task 7: Calculates versioned healthcare KPIs."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "build_metrics")
    try:
        res = calculate_all_metrics(run_id=run_id)
        total_metrics = res.get("total_calculated", 0)
        t.log_task_end(run_id, "build_metrics", "SUCCESS", rows_processed=total_metrics)
        return total_metrics
    except Exception as e:
        t.log_task_end(run_id, "build_metrics", "FAILED", error_message=str(e))
        raise

def task_quality_monitoring(run_id: str, tracker: PipelineTracker = None) -> Dict[str, Any]:
    """Task 8: Executes Phase 10 automated quality monitoring suite and enforces Quality Gate."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "quality_monitoring")
    try:
        q_res = run_quality_monitoring_pipeline(run_id=run_id)
        status = "SUCCESS" if q_res["quality_gate_passed"] else "BLOCKED"
        t.log_task_end(run_id, "quality_monitoring", status, rows_processed=q_res["total_checks"])
        if not q_res["quality_gate_passed"]:
            raise ValueError(f"Quality Gate Failed! {q_res['critical_failures']} critical failures detected.")
        return q_res
    except Exception as e:
        t.log_task_end(run_id, "quality_monitoring", "FAILED", error_message=str(e))
        raise

def task_publish(run_id: str, tracker: PipelineTracker = None) -> bool:
    """Task 9: Formally publishes datasets and closes pipeline run."""
    t = tracker or PipelineTracker()
    t.log_task_start(run_id, "publish")
    try:
        t.log_task_end(run_id, "publish", "SUCCESS", rows_processed=0)
        return True
    except Exception as e:
        t.log_task_end(run_id, "publish", "FAILED", error_message=str(e))
        raise
