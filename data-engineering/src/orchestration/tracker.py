from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text
from src.database import engine as default_engine

class PipelineTracker:
    """Manages operational pipeline state and task run history in PostgreSQL."""

    def __init__(self, engine_instance=None):
        self.engine = engine_instance or default_engine

    def create_pipeline_run(self, run_id: str, dag_id: str, execution_date: Optional[datetime] = None):
        """Initializes a new pipeline execution record."""
        exec_date = execution_date or datetime.now(timezone.utc)
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO analytics.pipeline_runs (
                    run_id, dag_id, execution_date, start_time, status
                ) VALUES (
                    :run_id, :dag_id, :exec_date, CURRENT_TIMESTAMP, 'RUNNING'
                ) ON CONFLICT (run_id) DO UPDATE SET
                    status = 'RUNNING',
                    start_time = CURRENT_TIMESTAMP;
            """), {"run_id": run_id, "dag_id": dag_id, "exec_date": exec_date})

    def update_pipeline_run(
        self,
        run_id: str,
        status: str,
        records_extracted: int = 0,
        records_staged: int = 0,
        records_loaded: int = 0,
        quality_score: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """Updates final pipeline execution status and summary metrics."""
        with self.engine.begin() as conn:
            conn.execute(text("""
                UPDATE analytics.pipeline_runs
                SET
                    end_time = CURRENT_TIMESTAMP,
                    status = :status,
                    records_extracted = :ext,
                    records_staged = :stg,
                    records_loaded = :lod,
                    quality_score = :score,
                    error_message = :err
                WHERE run_id = :run_id;
            """), {
                "run_id": run_id,
                "status": status,
                "ext": records_extracted,
                "stg": records_staged,
                "lod": records_loaded,
                "score": quality_score,
                "err": error_message
            })

    def log_task_start(self, run_id: str, task_name: str) -> int:
        """Logs the start of a pipeline task and returns its task run key."""
        with self.engine.begin() as conn:
            key = conn.execute(text("""
                INSERT INTO analytics.pipeline_task_runs (
                    run_id, task_name, start_time, status
                ) VALUES (
                    :run_id, :task_name, CURRENT_TIMESTAMP, 'RUNNING'
                ) RETURNING task_run_key;
            """), {"run_id": run_id, "task_name": task_name}).scalar()
            return key

    def log_task_end(
        self,
        run_id: str,
        task_name: str,
        status: str,
        rows_processed: int = 0,
        error_message: Optional[str] = None
    ):
        """Updates task execution record on completion."""
        with self.engine.begin() as conn:
            conn.execute(text("""
                UPDATE analytics.pipeline_task_runs
                SET
                    end_time = CURRENT_TIMESTAMP,
                    status = :status,
                    rows_processed = :rows,
                    error_message = :err
                WHERE run_id = :run_id AND task_name = :task_name;
            """), {
                "run_id": run_id,
                "task_name": task_name,
                "status": status,
                "rows": rows_processed,
                "err": error_message
            })
