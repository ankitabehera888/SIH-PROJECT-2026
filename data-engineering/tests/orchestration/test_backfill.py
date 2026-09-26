import pytest
from src.orchestration.tracker import PipelineTracker
from airflow.dags.backfill_pipeline import _validate_backfill_params
from src.database import engine
from sqlalchemy import text

def test_backfill_parameter_validation_success():
    """Verify valid date intervals pass parameter validation."""
    class MockDagRun:
        conf = {"start_date": "2026-01-01", "end_date": "2026-01-31"}

    # Should not raise
    _validate_backfill_params(dag_run=MockDagRun())

def test_backfill_parameter_validation_failure():
    """Verify inverted date boundaries raise ValueError."""
    class MockDagRun:
        conf = {"start_date": "2026-12-31", "end_date": "2026-01-01"}

    with pytest.raises(ValueError, match="Invalid backfill window"):
        _validate_backfill_params(dag_run=MockDagRun())

def test_pipeline_tracker_database_lifecycle():
    """Verify PipelineTracker records runs and task states in PostgreSQL."""
    tracker = PipelineTracker(engine)
    test_run_id = "test_orchestration_run_001"

    # 1. Create run
    tracker.create_pipeline_run(test_run_id, "test_dag")
    
    # 2. Log task start
    tracker.log_task_start(test_run_id, "test_extract_task")
    
    # 3. Log task end
    tracker.log_task_end(test_run_id, "test_extract_task", "SUCCESS", rows_processed=150)
    
    # 4. Update run completion
    tracker.update_pipeline_run(test_run_id, "SUCCESS", records_extracted=150, records_staged=150, records_loaded=150, quality_score=100.0)

    # 5. Verify records in database
    with engine.connect() as conn:
        run_row = conn.execute(text(
            "SELECT status, records_extracted, quality_score FROM analytics.pipeline_runs WHERE run_id = :rid;"
        ), {"rid": test_run_id}).fetchone()
        assert run_row[0] == "SUCCESS"
        assert run_row[1] == 150
        assert float(run_row[2]) == 100.0

        task_row = conn.execute(text(
            "SELECT status, rows_processed FROM analytics.pipeline_task_runs WHERE run_id = :rid AND task_name = 'test_extract_task';"
        ), {"rid": test_run_id}).fetchone()
        assert task_row[0] == "SUCCESS"
        assert task_row[1] == 150
