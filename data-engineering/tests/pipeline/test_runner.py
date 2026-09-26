import logging
import pytest
from sqlalchemy import text
from src.database import engine
from src.pipeline.context import PipelineContext
from src.pipeline.runner import run_pipeline

def test_pipeline_runner_end_to_end():
    """Verify full pipeline executes cleanly and outputs success manifest."""
    ctx = PipelineContext()
    result_ctx = run_pipeline(context=ctx)
    assert result_ctx.status == "success"
    assert result_ctx.current_step == 6
    assert len(result_ctx.errors) == 0

def test_pipeline_runner_idempotency():
    """Verify that running the pipeline twice does not duplicate fact or dimension records."""
    # Count rows before
    with engine.connect() as conn:
        count_appt_1 = conn.execute(text("SELECT COUNT(*) FROM analytics.fact_appointment;")).scalar()
        count_enc_1 = conn.execute(text("SELECT COUNT(*) FROM analytics.fact_encounter;")).scalar()
        count_pat_1 = conn.execute(text("SELECT COUNT(*) FROM analytics.dim_patient;")).scalar()
        
    # Run pipeline again
    ctx2 = run_pipeline()
    assert ctx2.status == "success"
    
    # Count rows after
    with engine.connect() as conn:
        count_appt_2 = conn.execute(text("SELECT COUNT(*) FROM analytics.fact_appointment;")).scalar()
        count_enc_2 = conn.execute(text("SELECT COUNT(*) FROM analytics.fact_encounter;")).scalar()
        count_pat_2 = conn.execute(text("SELECT COUNT(*) FROM analytics.dim_patient;")).scalar()
        
    assert count_appt_1 == count_appt_2, f"Appointments duplicated: {count_appt_1} vs {count_appt_2}"
    assert count_enc_1 == count_enc_2, f"Encounters duplicated: {count_enc_1} vs {count_enc_2}"
    assert count_pat_1 == count_pat_2, f"Patients duplicated: {count_pat_1} vs {count_pat_2}"

def test_pipeline_failure_containment(monkeypatch):
    """Verify that if an early step fails, downstream processing immediately halts."""
    from src.pipeline import runner
    
    # Mock raw validation to trigger a failure
    def mock_failing_validation(ctx, log):
        raise RuntimeError("Controlled test failure in Step 2: raw validation")
        
    monkeypatch.setattr(runner, "execute_raw_validation", mock_failing_validation)
    
    ctx = PipelineContext()
    res_ctx = runner.run_pipeline(context=ctx)
    
    assert res_ctx.status == "failed"
    assert res_ctx.current_step == 2
    # Downstream steps must not have run
    assert "dimensions" not in res_ctx.step_statuses
    assert "facts" not in res_ctx.step_statuses
    assert "reconcile" not in res_ctx.step_statuses
