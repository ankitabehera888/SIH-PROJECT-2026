from datetime import timedelta
from airflow.dags.healthcare_data_pipeline import dag as main_dag

def test_task_retries_configured():
    """Verify all critical tasks have at least 1 retry and retry delay >= 5 minutes."""
    for task in main_dag.tasks:
        assert task.retries >= 1, f"Task '{task.task_id}' must have at least 1 retry."
        assert task.retry_delay >= timedelta(minutes=5), f"Task '{task.task_id}' retry delay must be >= 5m."

def test_task_execution_timeouts():
    """Verify tasks have finite execution timeouts defined to prevent pipeline hangs."""
    for task in main_dag.tasks:
        assert task.execution_timeout is not None, f"Task '{task.task_id}' must have execution_timeout defined."
        assert task.execution_timeout <= timedelta(hours=2)
