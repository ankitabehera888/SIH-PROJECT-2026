import logging
from src.pipeline.context import PipelineContext
from src.pipeline.extract import execute_extraction

def test_execute_extraction():
    """Verify execution of Step 1 extraction and context metrics logging."""
    logger = logging.getLogger("test_extract")
    logger.setLevel(logging.INFO)
    ctx = PipelineContext()
    
    details = execute_extraction(ctx, logger)
    assert details["total_rows_extracted"] > 0
    assert details["total_tables_extracted"] >= 20
    assert ctx.step_statuses["extract"] == "success"
