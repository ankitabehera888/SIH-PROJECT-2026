from airflow.dags.healthcare_data_pipeline import dag as main_dag
from airflow.dags.quality_monitoring import dag as monitoring_dag
from airflow.dags.backfill_pipeline import dag as backfill_dag

def test_main_healthcare_dag_structure():
    """Verify main healthcare data pipeline DAG configuration."""
    assert main_dag.dag_id == "healthcare_data_pipeline"
    assert main_dag.schedule_interval == "0 2 * * *"
    assert main_dag.catchup is False
    assert main_dag.max_active_runs == 1
    assert len(main_dag.tasks) == 9

def test_quality_monitoring_dag_structure():
    """Verify independent continuous quality monitoring DAG configuration."""
    assert monitoring_dag.dag_id == "quality_monitoring"
    assert monitoring_dag.schedule_interval == "0 */6 * * *"
    assert len(monitoring_dag.tasks) == 3

def test_backfill_dag_structure():
    """Verify backfill pipeline DAG configuration."""
    assert backfill_dag.dag_id == "backfill_pipeline"
    assert backfill_dag.schedule_interval is None  # Manual trigger only
    assert len(backfill_dag.tasks) == 3
