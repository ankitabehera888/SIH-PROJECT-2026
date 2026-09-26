import uuid
from datetime import datetime, timezone
import pytest
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.integrations.email import get_email_provider
from app.integrations.sms import get_sms_provider
from app.models.notification import Notification, NotificationChannel, NotificationStatus, NotificationType
from app.models.user import User
from app.tasks.notification_tasks import send_notification_task
from app.tasks.test_tasks import test_background_task


@pytest.fixture(autouse=True)
def configure_celery_eager():
    """Ensure Celery tasks execute eagerly during automated tests."""
    original_eager = celery_app.conf.task_always_eager
    celery_app.conf.task_always_eager = True
    yield
    celery_app.conf.task_always_eager = original_eager


def create_test_user(email_prefix: str = "task.user") -> int:
    db = SessionLocal()
    try:
        email = f"{email_prefix}.{uuid.uuid4().hex[:6]}@hospital.org"
        user = User(
            email=email,
            password_hash="hashed_pw",
            role="PATIENT",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
    finally:
        db.close()


def test_test_background_task_executes():
    res = test_background_task.delay("Test message from pytest")
    assert res.status == "SUCCESS"
    val = res.get()
    assert val["status"] == "SUCCESS"
    assert val["received_message"] == "Test message from pytest"


def test_send_notification_task_email_delivery():
    user_id = create_test_user("task.email")
    db = SessionLocal()
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        notification_type=NotificationType.APPOINTMENT_REMINDER.value,
        channel=NotificationChannel.EMAIL.value,
        subject="Your Upcoming Appointment",
        message="Please log in to your patient portal for visit instructions.",
        status=NotificationStatus.PENDING.value,
    )
    db.add(notif)
    db.commit()
    notif_id = str(notif.id)
    db.close()

    # Reset mock provider
    email_prov = get_email_provider()
    email_prov.sent_emails.clear()

    # Dispatch Celery task
    async_res = send_notification_task.delay(notif_id)
    assert async_res.status == "SUCCESS"
    result = async_res.get()
    assert result["status"] == "SENT"
    assert result["channel"] == "EMAIL"
    assert result["provider_message_id"].startswith("mock-ses-")

    # Verify provider and DB state
    assert len(email_prov.sent_emails) == 1
    assert email_prov.sent_emails[0]["subject"] == "Your Upcoming Appointment"

    db2 = SessionLocal()
    updated = db2.get(Notification, uuid.UUID(notif_id))
    assert updated.status == NotificationStatus.SENT.value
    assert updated.sent_at is not None
    assert updated.provider_message_id is not None
    db2.close()


def test_send_notification_task_sms_delivery():
    user_id = create_test_user("task.sms")
    db = SessionLocal()
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        notification_type=NotificationType.PRESCRIPTION_ISSUED.value,
        channel=NotificationChannel.SMS.value,
        subject="Prescription Notice",
        message="A new prescription has been issued. Log in for instructions.",
        status=NotificationStatus.PENDING.value,
    )
    db.add(notif)
    db.commit()
    notif_id = str(notif.id)
    db.close()

    sms_prov = get_sms_provider()
    sms_prov.sent_sms.clear()

    async_res = send_notification_task.delay(notif_id)
    assert async_res.status == "SUCCESS"
    result = async_res.get()
    assert result["status"] == "SENT"
    assert result["channel"] == "SMS"
    assert result["provider_message_id"].startswith("mock-twilio-")

    assert len(sms_prov.sent_sms) == 1
    assert "new prescription" in sms_prov.sent_sms[0]["message"]


def test_send_notification_task_idempotency_no_duplicate_delivery():
    user_id = create_test_user("task.idempotent")
    db = SessionLocal()
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        notification_type=NotificationType.SYSTEM.value,
        channel=NotificationChannel.EMAIL.value,
        subject="One-Time Verification",
        message="Important security alert.",
        status=NotificationStatus.SENT.value,  # Already SENT
        sent_at=datetime.now(timezone.utc),
        provider_message_id="mock-existing-123",
    )
    db.add(notif)
    db.commit()
    notif_id = str(notif.id)
    db.close()

    email_prov = get_email_provider()
    email_prov.sent_emails.clear()

    # Re-dispatching task should not send email
    res = send_notification_task.delay(notif_id)
    result = res.get()
    assert result["status"] == "ALREADY_PROCESSED"
    assert len(email_prov.sent_emails) == 0


def test_send_notification_task_failure_records_failed_state():
    user_id = create_test_user("task.fail")
    db = SessionLocal()
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        notification_type=NotificationType.SYSTEM.value,
        channel=NotificationChannel.EMAIL.value,
        subject="Failure Test",
        message="Testing provider failure.",
        status=NotificationStatus.PENDING.value,
    )
    db.add(notif)
    db.commit()
    notif_id = str(notif.id)
    db.close()

    email_prov = get_email_provider()
    email_prov.should_fail = True
    try:
        # Task will attempt retries and then mark FAILED
        try:
            send_notification_task.delay(notif_id).get()
        except Exception:
            pass

        db2 = SessionLocal()
        failed_notif = db2.get(Notification, uuid.UUID(notif_id))
        assert failed_notif.status == NotificationStatus.FAILED.value
        assert failed_notif.failed_at is not None
        assert failed_notif.error_message is not None
        db2.close()
    finally:
        email_prov.should_fail = False
