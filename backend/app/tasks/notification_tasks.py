import logging
import uuid
from celery.exceptions import MaxRetriesExceededError
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.integrations.email import get_email_provider
from app.integrations.sms import get_sms_provider
from app.models.notification import NotificationChannel, NotificationStatus
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository

logger = logging.getLogger("healthcare_platform.notification_tasks")


@celery_app.task(
    name="app.tasks.notification_tasks.send_notification_task",
    bind=True,
    max_retries=3,
    default_retry_delay=2,
)
def send_notification_task(self, notification_id: str):
    """Celery background worker task for reliable multi-channel notification dispatch.
    
    Includes:
    - Idempotency guard (prevents redundant external message dispatches)
    - Channel routing (IN_APP, EMAIL, SMS)
    - Automatic exponential backoff retry on transient network errors
    - Failure state recording on max retries exhaustion
    """
    db = SessionLocal()
    try:
        notif_uuid = uuid.UUID(notification_id)
        notification = NotificationRepository.get_by_id(db, notif_uuid)
        if not notification:
            logger.warning(f"[send_notification_task] Notification {notification_id} not found in database.")
            return {"status": "NOT_FOUND", "notification_id": notification_id}

        # Idempotency check: Do not re-dispatch already finalized notifications
        if notification.status in (NotificationStatus.SENT.value, NotificationStatus.CANCELLED.value):
            logger.info(f"[send_notification_task] Idempotency guard: Notification {notification_id} is already {notification.status}.")
            return {"status": "ALREADY_PROCESSED", "notification_status": notification.status}

        # Mark QUEUED
        NotificationRepository.mark_queued(db, notif_uuid)

        user = db.get(User, notification.user_id)
        pref = NotificationRepository.get_or_create_preferences(db, notification.user_id)

        provider_message_id = None

        if notification.channel == NotificationChannel.EMAIL.value:
            dest_email = pref.preferred_email or (user.email if user else "patient@hospital.org")
            email_provider = get_email_provider()
            provider_message_id = email_provider.send_email(
                to_email=dest_email,
                subject=notification.subject,
                message=notification.message,
            )

        elif notification.channel == NotificationChannel.SMS.value:
            dest_phone = pref.preferred_phone or "+15551234567"
            sms_provider = get_sms_provider()
            provider_message_id = sms_provider.send_sms(
                to_phone=dest_phone,
                message=notification.message,
            )

        elif notification.channel == NotificationChannel.IN_APP.value:
            provider_message_id = f"in-app-{uuid.uuid4().hex[:8]}"

        # Mark SENT
        NotificationRepository.mark_sent(db, notif_uuid, provider_message_id=provider_message_id)
        logger.info(f"[send_notification_task] Successfully delivered {notification.channel} notification {notification_id}")
        return {
            "status": "SENT",
            "notification_id": notification_id,
            "channel": notification.channel,
            "provider_message_id": provider_message_id,
        }

    except Exception as exc:
        logger.error(f"[send_notification_task] Delivery failed for {notification_id}: {exc}")
        retries = self.request.retries
        if retries < self.max_retries:
            countdown = 2 ** retries
            logger.info(f"[send_notification_task] Scheduling retry {retries + 1}/{self.max_retries} in {countdown}s")
            raise self.retry(exc=exc, countdown=countdown)
        else:
            NotificationRepository.mark_failed(
                db,
                notif_uuid,
                error_message=str(exc),
                retry_count=retries,
            )
            return {
                "status": "FAILED",
                "notification_id": notification_id,
                "error": str(exc),
                "retry_count": retries,
            }
    finally:
        db.close()
