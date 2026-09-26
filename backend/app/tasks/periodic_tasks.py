import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationChannel, NotificationStatus, NotificationType
from app.models.patient import Patient
from app.repositories.notification_repository import NotificationRepository
from app.tasks.notification_tasks import send_notification_task

logger = logging.getLogger("healthcare_platform.periodic_tasks")


@celery_app.task(name="app.tasks.periodic_tasks.check_upcoming_appointment_reminders")
def check_upcoming_appointment_reminders():
    """Periodic job finding appointments scheduled for tomorrow and queuing patient reminders."""
    db = SessionLocal()
    created_count = 0
    try:
        tomorrow = date.today() + timedelta(days=1)
        stmt = (
            select(Appointment)
            .where(
                Appointment.appointment_date == tomorrow,
                Appointment.status == AppointmentStatus.SCHEDULED.value,
            )
        )
        appointments = list(db.scalars(stmt).all())
        for app in appointments:
            patient = db.get(Patient, app.patient_id)
            if not patient or not patient.user_id:
                continue

            idempotency_key = f"REMINDER_APPT_{app.id}_{tomorrow.isoformat()}"
            existing = NotificationRepository.get_by_idempotency_key(db, idempotency_key)
            if existing:
                continue

            # Create in-app reminder
            notif = Notification(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationType.APPOINTMENT_REMINDER.value,
                channel=NotificationChannel.SMS.value,
                subject="Upcoming Appointment Reminder",
                message=f"Reminder: You have a scheduled appointment on {tomorrow.isoformat()} at {app.start_time.strftime('%H:%M')}. Please log in to your patient portal for instructions.",
                status=NotificationStatus.PENDING.value,
                related_entity_type="APPOINTMENT",
                related_entity_id=app.id,
                idempotency_key=idempotency_key,
            )
            db.add(notif)
            db.commit()
            db.refresh(notif)
            send_notification_task.delay(str(notif.id))
            created_count += 1

        logger.info(f"[check_upcoming_appointment_reminders] Queued {created_count} reminders for {tomorrow.isoformat()}")
        return {"status": "SUCCESS", "reminders_created": created_count}
    finally:
        db.close()


@celery_app.task(name="app.tasks.periodic_tasks.retry_failed_notifications")
def retry_failed_notifications():
    """Periodic job identifying transiently failed notifications and re-enqueuing them."""
    db = SessionLocal()
    requeued_count = 0
    try:
        stmt = select(Notification).where(
            Notification.status == NotificationStatus.FAILED.value,
            Notification.retry_count < 3,
        ).limit(50)
        failed_notifs = list(db.scalars(stmt).all())
        for notif in failed_notifs:
            notif.status = NotificationStatus.PENDING.value
            db.commit()
            send_notification_task.delay(str(notif.id))
            requeued_count += 1

        logger.info(f"[retry_failed_notifications] Re-queued {requeued_count} failed notifications")
        return {"status": "SUCCESS", "requeued": requeued_count}
    finally:
        db.close()
