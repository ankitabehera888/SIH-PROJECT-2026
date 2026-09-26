from airflow.dags.healthcare_data_pipeline import dag as main_dag
from airflow.dags.quality_monitoring import dag as monitoring_dag
from airflow.dags.backfill_pipeline import dag as backfill_dag

def test_main_pipeline_dependency_chain():
    """Verify strict end-to-end task dependency order for main pipeline."""
    task_map = main_dag.task_dict
    
    # extract -> raw_validation
    assert task_map["raw_validation"] in task_map["extract"].downstream_list
    # raw_validation -> staging
    assert task_map["staging"] in task_map["raw_validation"].downstream_list
    # staging -> load_dimensions
    assert task_map["load_dimensions"] in task_map["staging"].downstream_list
    # load_dimensions -> load_facts
    assert task_map["load_facts"] in task_map["load_dimensions"].downstream_list
    # load_facts -> build_cohorts
    assert task_map["build_cohorts"] in task_map["load_facts"].downstream_list
    # build_cohorts -> build_metrics
    assert task_map["build_metrics"] in task_map["build_cohorts"].downstream_list
    # build_metrics -> quality_monitoring
    assert task_map["quality_monitoring"] in task_map["build_metrics"].downstream_list
    # quality_monitoring -> publish
    assert task_map["publish"] in task_map["quality_monitoring"].downstream_list

def test_quality_monitoring_dependencies():
    """Verify monitoring DAG dependency order."""
    task_map = monitoring_dag.task_dict
    assert task_map["anomaly_detection"] in task_map["check_freshness"].downstream_list
    assert task_map["quality_suite"] in task_map["anomaly_detection"].downstream_list

def test_backfill_dependencies():
    """Verify backfill DAG dependency order."""
    task_map = backfill_dag.task_dict
    assert task_map["recompute_cohorts"] in task_map["validate_parameters"].downstream_list
    assert task_map["recompute_metrics"] in task_map["recompute_cohorts"].downstream_list
