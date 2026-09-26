import logging
from src.pipeline.context import PipelineContext
from src.pipeline.reconcile import execute_reconciliation

def test_execute_reconciliation():
    """Verify execution of Step 6 multi-layer reconciliation and zero orphans."""
    logger = logging.getLogger("test_reconcile")
    logger.setLevel(logging.INFO)
    ctx = PipelineContext()
    
    details = execute_reconciliation(ctx, logger)
    assert details["encounter_patient_orphans"] == 0
    assert len(details["summary"]) >= 5
    assert ctx.step_statuses["reconcile"] in ("success", "warning")
