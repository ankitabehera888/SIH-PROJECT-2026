import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import NotificationService
from app.tasks.test_tasks import test_background_task

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class TestBackgroundTaskRequest(BaseModel):
    message: str = "Test asynchronous task execution via Celery and Redis"


class TestBackgroundTaskResponse(BaseModel):
    status: str
    task_id: str
    message: str


@router.post(
    "/test-background-task",
    response_model=TestBackgroundTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue test background task to Celery worker",
)
def enqueue_test_background_task(payload: TestBackgroundTaskRequest):
    """Demonstrates non-blocking asynchronous job dispatch from FastAPI to Celery via Redis broker."""
    async_res = test_background_task.delay(payload.message)
    return TestBackgroundTaskResponse(
        status="QUEUED",
        task_id=async_res.id,
        message=payload.message,
    )


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Get authenticated user's notification list",
)
def list_notifications(
    channel: Optional[str] = Query(None, description="Filter by channel: IN_APP, EMAIL, SMS"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated notification feed strictly scoped to the authenticated user."""
    service = NotificationService(db)
    return service.list_user_notifications(
        user_id=current_user.id,
        channel=channel,
        is_read=is_read,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/unread-count",
    response_model=NotificationUnreadCountResponse,
    summary="Get unread notification count badge",
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Badge counter endpoint for frontend navigation notifications icon."""
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)
    return NotificationUnreadCountResponse(unread_count=count)


@router.get(
    "/preferences",
    response_model=NotificationPreferenceResponse,
    summary="Get user's notification preferences",
)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve communication preferences (Email, SMS, In-App toggles) for the current user."""
    service = NotificationService(db)
    return service.get_preferences(current_user.id)


@router.put(
    "/preferences",
    response_model=NotificationPreferenceResponse,
    summary="Update user's notification preferences",
)
def update_preferences(
    update_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update communication preferences for the current user."""
    service = NotificationService(db)
    return service.update_preferences(current_user.id, update_data)


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification detail by ID",
)
def get_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve notification details with strict user resource-ownership protection."""
    service = NotificationService(db)
    return service.get_notification_by_id(notification_id, current_user)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
def mark_as_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge and mark a notification as read with a timestamp."""
    service = NotificationService(db)
    return service.mark_as_read(notification_id, current_user)


@router.post(
    "/{notification_id}/cancel",
    response_model=NotificationResponse,
    summary="Cancel scheduled or pending notification",
)
def cancel_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending notification prior to transmission."""
    service = NotificationService(db)
    return service.cancel_notification(notification_id, current_user)
