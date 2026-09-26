import logging
from src.pipeline.context import PipelineContext
from src.pipeline.dimensions import execute_dimensions_loading

def test_execute_dimensions_loading():
    """Verify execution of Step 4 dimension loading."""
    logger = logging.getLogger("test_dims")
    logger.setLevel(logging.INFO)
    ctx = PipelineContext()
    
    summary = execute_dimensions_loading(ctx, logger)
    assert summary["dim_date"] == 4018
    assert summary["dim_patient"] > 0
    assert summary["dim_facility"] > 0
    assert summary["dim_provider"] > 0
    assert ctx.step_statuses["dimensions"] == "success"
