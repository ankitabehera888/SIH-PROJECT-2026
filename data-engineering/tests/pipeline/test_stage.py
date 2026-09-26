import logging
from src.pipeline.context import PipelineContext
from src.pipeline.stage import execute_staging

def test_execute_staging():
    """Verify execution of Step 3 staging and quality counts."""
    logger = logging.getLogger("test_stage")
    logger.setLevel(logging.INFO)
    ctx = PipelineContext()
    
    details = execute_staging(ctx, logger)
    assert len(details["tables_staged"]) >= 6
    assert "patients" in details["counts"]
    assert details["counts"]["patients"]["output_rows"] > 0
    assert ctx.step_statuses["stage"] == "success"
