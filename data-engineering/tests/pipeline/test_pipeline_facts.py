import logging
from src.pipeline.context import PipelineContext
from src.pipeline.facts import execute_facts_loading

def test_execute_facts_loading():
    """Verify execution of Step 5 fact tables loading."""
    logger = logging.getLogger("test_facts")
    logger.setLevel(logging.INFO)
    ctx = PipelineContext()
    
    summary = execute_facts_loading(ctx, logger)
    assert summary["fact_appointment"] > 0
    assert summary["fact_encounter"] > 0
    assert summary["fact_referral"] > 0
    assert summary["fact_prescription"] > 0
    assert summary["fact_vital"] > 0
    assert ctx.step_statuses["facts"] == "success"
