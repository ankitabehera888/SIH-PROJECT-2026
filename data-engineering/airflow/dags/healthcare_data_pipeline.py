from datetime import datetime, timezone
import sys
from pathlib import Path

# Add data-engineering root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from airflow.config.airflow_config import AirflowDAG, AirflowPythonOperator, DEFAULT_TASK_ARGS
from src.orchestration.tasks import (
    task_extract,
    task_raw_validation,
    task_staging,
    task_dimensions,
    task_facts,
    task_cohorts,
    task_metrics,
    task_quality_monitoring,
    task_publish,
)
from src.orchestration.tracker import PipelineTracker

def _run_extract(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tracker = PipelineTracker()
    tracker.create_pipeline_run(run_id, "healthcare_data_pipeline")
    task_extract(run_id, tracker)

def _run_raw_validation(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_raw_validation(run_id)

def _run_staging(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_staging(run_id)

def _run_dimensions(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_dimensions(run_id)

def _run_facts(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_facts(run_id)

def _run_cohorts(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_cohorts(run_id)

def _run_metrics(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_metrics(run_id)

def _run_quality_monitoring(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_quality_monitoring(run_id)

def _run_publish(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_publish(run_id)
    tracker = PipelineTracker()
    tracker.update_pipeline_run(run_id, "SUCCESS")

# Initialize Master Daily Healthcare Data Pipeline DAG
dag = AirflowDAG(
    dag_id="healthcare_data_pipeline",
    default_args=DEFAULT_TASK_ARGS,
    description="End-to-End Orchestrated Daily Healthcare ETL, Cohort, Metric & Quality Pipeline",
    schedule_interval="0 2 * * *", # Daily at 02:00
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["healthcare", "etl", "analytics", "production"],
)

# Define tasks
t_extract = AirflowPythonOperator(
    task_id="extract",
    python_callable=_run_extract,
    dag=dag,
)

t_raw_val = AirflowPythonOperator(
    task_id="raw_validation",
    python_callable=_run_raw_validation,
    dag=dag,
)

t_stage = AirflowPythonOperator(
    task_id="staging",
    python_callable=_run_staging,
    dag=dag,
)

t_dims = AirflowPythonOperator(
    task_id="load_dimensions",
    python_callable=_run_dimensions,
    dag=dag,
)

t_facts = AirflowPythonOperator(
    task_id="load_facts",
    python_callable=_run_facts,
    dag=dag,
)

t_cohorts = AirflowPythonOperator(
    task_id="build_cohorts",
    python_callable=_run_cohorts,
    dag=dag,
)

t_metrics = AirflowPythonOperator(
    task_id="build_metrics",
    python_callable=_run_metrics,
    dag=dag,
)

t_quality = AirflowPythonOperator(
    task_id="quality_monitoring",
    python_callable=_run_quality_monitoring,
    dag=dag,
)

t_publish = AirflowPythonOperator(
    task_id="publish",
    python_callable=_run_publish,
    dag=dag,
)

# Configure Strict Sequential Dependency Graph
t_extract >> t_raw_val >> t_stage >> t_dims >> t_facts >> t_cohorts >> t_metrics >> t_quality >> t_publish
