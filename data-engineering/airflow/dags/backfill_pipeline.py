from datetime import datetime, timezone
import sys
from pathlib import Path

# Add data-engineering root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from airflow.config.airflow_config import AirflowDAG, AirflowPythonOperator, DEFAULT_TASK_ARGS
from src.orchestration.tracker import PipelineTracker
from src.cohorts.builder import build_all_cohorts
from src.metrics.calculator import calculate_all_metrics

def _validate_backfill_params(**context):
    dag_run = context.get("dag_run")
    conf = getattr(dag_run, "conf", {}) if dag_run else {}
    start_date = conf.get("start_date")
    end_date = conf.get("end_date")
    if start_date and end_date and start_date > end_date:
        raise ValueError(f"Invalid backfill window: start_date {start_date} > end_date {end_date}")

def _recompute_historical_cohorts(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    t = PipelineTracker()
    t.log_task_start(run_id, "recompute_cohorts")
    res = build_all_cohorts(run_id=run_id)
    t.log_task_end(run_id, "recompute_cohorts", "SUCCESS", rows_processed=sum(res.get("cohort_counts", {}).values()))

def _recompute_historical_metrics(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    t = PipelineTracker()
    t.log_task_start(run_id, "recompute_metrics")
    res = calculate_all_metrics(run_id=run_id)
    t.log_task_end(run_id, "recompute_metrics", "SUCCESS", rows_processed=res.get("total_calculated", 0))

# Initialize Backfill Historical Reprocessing DAG
dag = AirflowDAG(
    dag_id="backfill_pipeline",
    default_args=DEFAULT_TASK_ARGS,
    description="Parameterized Historical Healthcare Data Reprocessing and Recalculation DAG",
    schedule_interval=None, # Manual / External Trigger Only
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["healthcare", "backfill", "reprocessing", "manual"],
)

t_val = AirflowPythonOperator(
    task_id="validate_parameters",
    python_callable=_validate_backfill_params,
    dag=dag,
)

t_cohorts = AirflowPythonOperator(
    task_id="recompute_cohorts",
    python_callable=_recompute_historical_cohorts,
    dag=dag,
)

t_metrics = AirflowPythonOperator(
    task_id="recompute_metrics",
    python_callable=_recompute_historical_metrics,
    dag=dag,
)

# Dependencies
t_val >> t_cohorts >> t_metrics
