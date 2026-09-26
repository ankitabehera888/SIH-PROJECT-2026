import json
from pathlib import Path
from src.pipeline.context import PipelineContext

def test_pipeline_context_initialization():
    """Verify PipelineContext default fields, timestamp format, and initial status."""
    ctx = PipelineContext()
    assert len(ctx.run_id) >= 15  # YYYYMMDD_HHMMSS
    assert ctx.status == "running"
    assert ctx.current_step == 0
    assert len(ctx.errors) == 0

def test_pipeline_context_step_recording():
    """Verify recording step status and error tracking."""
    ctx = PipelineContext()
    ctx.record_step("extract", "success", {"rows": 100})
    assert ctx.step_statuses["extract"] == "success"
    assert ctx.metrics["extract"]["rows"] == 100
    
    ctx.record_error("stage", "Simulated validation error")
    assert ctx.status == "failed"
    assert len(ctx.errors) == 1
    assert ctx.errors[0]["step"] == "stage"

def test_pipeline_manifest_and_state_persistence(tmp_path, monkeypatch):
    """Verify that mark_finished creates an immutable manifest JSON file and updates pipeline state."""
    ctx = PipelineContext()
    ctx.record_step("extract", "success")
    ctx.mark_finished(status="success")
    
    manifest_path = Path("metadata/runs") / f"{ctx.run_id}.json"
    assert manifest_path.exists()
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["run_id"] == ctx.run_id
    assert data["status"] == "success"
    assert "extract" in data["steps"]

    state_path = Path("metadata/pipeline_state.json")
    assert state_path.exists()
