import time
from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.test_tasks.test_background_task", bind=True)
def test_background_task(self, message: str):
    """Harmless test task proving FastAPI -> Redis -> Celery Worker pipeline."""
    task_id = self.request.id
    time.sleep(0.5)
    return {
        "status": "SUCCESS",
        "task_id": task_id,
        "received_message": message,
    }
