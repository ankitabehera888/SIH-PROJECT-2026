from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

# Default Airflow configuration arguments
DEFAULT_TASK_ARGS: Dict[str, Any] = {
    "owner": "healthcare_platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=45),
}

# Standalone / Compatibility Mock Classes for Windows & Testing without Native Airflow
class MockTask:
    def __init__(self, task_id: str, python_callable: Optional[Callable] = None, dag=None, **kwargs):
        self.task_id = task_id
        self.python_callable = python_callable
        self.dag = dag
        self.retries = kwargs.get("retries", DEFAULT_TASK_ARGS["retries"])
        self.retry_delay = kwargs.get("retry_delay", DEFAULT_TASK_ARGS["retry_delay"])
        self.execution_timeout = kwargs.get("execution_timeout", DEFAULT_TASK_ARGS["execution_timeout"])
        self.upstream_list: List["MockTask"] = []
        self.downstream_list: List["MockTask"] = []
        if dag:
            dag.tasks.append(self)

    def __rshift__(self, other):
        """Implements >> operator for downstream dependencies."""
        if isinstance(other, MockTask):
            if other not in self.downstream_list:
                self.downstream_list.append(other)
            if self not in other.upstream_list:
                other.upstream_list.append(self)
        elif isinstance(other, (list, tuple)):
            for item in other:
                self >> item
        return other

    def __lshift__(self, other):
        """Implements << operator for upstream dependencies."""
        if isinstance(other, MockTask):
            other >> self
        elif isinstance(other, (list, tuple)):
            for item in other:
                item >> self
        return other


class MockDAG:
    def __init__(
        self,
        dag_id: str,
        default_args: Optional[Dict[str, Any]] = None,
        description: str = "",
        schedule_interval: Any = None,
        start_date: Optional[datetime] = None,
        catchup: bool = False,
        max_active_runs: int = 1,
        tags: Optional[List[str]] = None,
    ):
        self.dag_id = dag_id
        self.default_args = default_args or DEFAULT_TASK_ARGS
        self.description = description
        self.schedule_interval = schedule_interval
        self.start_date = start_date or datetime(2026, 1, 1)
        self.catchup = catchup
        self.max_active_runs = max_active_runs
        self.tags = tags or []
        self.tasks: List[MockTask] = []

    def get_task(self, task_id: str) -> Optional[MockTask]:
        for t in self.tasks:
            if t.task_id == task_id:
                return t
        return None

    @property
    def task_dict(self) -> Dict[str, MockTask]:
        return {t.task_id: t for t in self.tasks}


# Try importing real Airflow; if not present, use MockDAG and MockTask
try:
    from airflow import DAG as AirflowDAG
    from airflow.operators.python import PythonOperator as AirflowPythonOperator
    HAS_AIRFLOW = True
except ImportError:
    AirflowDAG = MockDAG
    AirflowPythonOperator = MockTask
    HAS_AIRFLOW = False
