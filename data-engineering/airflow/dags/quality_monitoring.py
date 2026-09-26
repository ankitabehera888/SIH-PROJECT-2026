from datetime import datetime, timezone
import sys
from pathlib import Path

# Add data-engineering root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from airflow.config.airflow_config import AirflowDAG, AirflowPythonOperator, DEFAULT_TASK_ARGS
from src.monitoring.freshness import run_freshness_checks
from src.monitoring.anomaly import run_volume_checks, run_kpi_anomaly_checks
from src.monitoring.runner import run_quality_monitoring_pipeline
from src.orchestration.tracker import PipelineTracker

def _check_freshness(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    t = PipelineTracker()
    t.log_task_start(run_id, "check_freshness")
    results = run_freshness_checks()
    t.log_task_end(run_id, "check_freshness", "SUCCESS", rows_processed=len(results))

def _run_anomaly_detection(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    t = PipelineTracker()
    t.log_task_start(run_id, "anomaly_detection")
    v_res = run_volume_checks()
    k_res = run_kpi_anomaly_checks()
    total_anomalies = len(v_res) + len(k_res)
    t.log_task_end(run_id, "anomaly_detection", "SUCCESS", rows_processed=total_anomalies)

def _run_monitoring_suite(**context):
    run_id = context.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    t = PipelineTracker()
    t.log_task_start(run_id, "quality_suite")
    res = run_quality_monitoring_pipeline(run_id=run_id)
    t.log_task_end(run_id, "quality_suite", "SUCCESS", rows_processed=res["total_checks"])

# Initialize Independent Quality Monitoring DAG
dag = AirflowDAG(
    dag_id="quality_monitoring",
    default_args=DEFAULT_TASK_ARGS,
    description="Independent Continuous Healthcare Data Quality and Freshness Monitoring DAG",
    schedule_interval="0 */6 * * *", # Every 6 hours
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["healthcare", "monitoring", "quality", "alerts"],
)

t_fresh = AirflowPythonOperator(
    task_id="check_freshness",
    python_callable=_check_freshness,
    dag=dag,
)

t_anom = AirflowPythonOperator(
    task_id="anomaly_detection",
    python_callable=_run_anomaly_detection,
    dag=dag,
)

t_suite = AirflowPythonOperator(
    task_id="quality_suite",
    python_callable=_run_monitoring_suite,
    dag=dag,
)

# Dependencies
t_fresh >> t_anom >> t_suite
