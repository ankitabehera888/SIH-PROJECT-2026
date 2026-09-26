import uuid
from datetime import date, datetime, timezone
import pytest
from fastapi.testclient import TestClient
from app.core.celery_app import celery_app
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def configure_celery_eager():
    original_eager = celery_app.conf.task_always_eager
    celery_app.conf.task_always_eager = True
    yield
    celery_app.conf.task_always_eager = original_eager


def get_token_and_user(role: str = "PATIENT"):
    email = f"notif.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
    password = "SecurePassword123"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )
    user_id = reg_res.json()["id"]
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]
    return token, user_id


def test_enqueue_test_background_task_endpoint():
    res = client.post(
        "/api/v1/notifications/test-background-task",
        json={"message": "Verification from API"},
    )
    assert res.status_code == 202
    data = res.json()
    assert data["status"] == "QUEUED"
    assert data["task_id"] is not None
    assert data["message"] == "Verification from API"


def test_list_notifications_and_unread_count():
    token, user_id = get_token_and_user("PATIENT")
    headers = {"Authorization": f"Bearer {token}"}

    # Initial list is empty
    res = client.get("/api/v1/notifications", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 0

    badge_res = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert badge_res.status_code == 200
    assert badge_res.json()["unread_count"] == 0

    # Trigger notification via service
    from app.db.session import SessionLocal
    from app.schemas.notification import NotificationChannelEnum, NotificationCreate, NotificationTypeEnum
    from app.services.notification_service import NotificationService

    db = SessionLocal()
    svc = NotificationService(db)
    notif = svc.create_and_dispatch(
        NotificationCreate(
            user_id=user_id,
            notification_type=NotificationTypeEnum.SYSTEM,
            channel=NotificationChannelEnum.IN_APP,
            subject="Welcome to Portal",
            message="Your account is active.",
        )
    )
    db.close()
    assert notif is not None

    # Check list has 1 item and unread count is 1
    res2 = client.get("/api/v1/notifications", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["total"] == 1
    item = res2.json()["items"][0]
    assert item["id"] == str(notif.id)
    assert item["is_read"] is False

    badge2 = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert badge2.json()["unread_count"] == 1

    # Mark as read
    read_res = client.post(f"/api/v1/notifications/{notif.id}/read", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    badge3 = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert badge3.json()["unread_count"] == 0


def test_user_cannot_view_another_user_notification():
    token1, user1_id = get_token_and_user("PATIENT")
    token2, _ = get_token_and_user("PATIENT")

    from app.db.session import SessionLocal
    from app.schemas.notification import NotificationChannelEnum, NotificationCreate, NotificationTypeEnum
    from app.services.notification_service import NotificationService

    db = SessionLocal()
    svc = NotificationService(db)
    notif = svc.create_and_dispatch(
        NotificationCreate(
            user_id=user1_id,
            notification_type=NotificationTypeEnum.SYSTEM,
            channel=NotificationChannelEnum.IN_APP,
            subject="Private Notice",
            message="Only for user 1",
        )
    )
    db.close()

    # User 1 can view
    res1 = client.get(f"/api/v1/notifications/{notif.id}", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200

    # User 2 receives 403 Forbidden
    res2 = client.get(f"/api/v1/notifications/{notif.id}", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 403
    assert res2.json()["error"]["code"] == "FORBIDDEN"


def test_notification_preferences_get_and_update():
    token, _ = get_token_and_user("PATIENT")
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch default preferences
    pref_res = client.get("/api/v1/notifications/preferences", headers=headers)
    assert pref_res.status_code == 200
    pref = pref_res.json()
    assert pref["email_enabled"] is True
    assert pref["sms_enabled"] is True

    # Update preferences: disable SMS, set preferred phone
    update_res = client.put(
        "/api/v1/notifications/preferences",
        json={"sms_enabled": False, "preferred_phone": "+19998887777"},
        headers=headers,
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["sms_enabled"] is False
    assert updated["preferred_phone"] == "+19998887777"
    assert updated["email_enabled"] is True


def test_cancel_pending_notification():
    token, user_id = get_token_and_user("PATIENT")
    headers = {"Authorization": f"Bearer {token}"}

    from app.db.session import SessionLocal
    from app.models.notification import Notification, NotificationStatus, NotificationType
    db = SessionLocal()
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        notification_type=NotificationType.SYSTEM.value,
        channel="IN_APP",
        subject="Pending Reminder",
        message="Cancel me before transmission.",
        status=NotificationStatus.PENDING.value,
    )
    db.add(notif)
    db.commit()
    notif_id = str(notif.id)
    db.close()

    cancel_res = client.post(f"/api/v1/notifications/{notif_id}/cancel", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"


def test_clinical_event_notification_triggers():
    doc_token, doc_id = get_token_and_user("DOCTOR")
    pat_token, pat_user_id = get_token_and_user("PATIENT")

    # 1. Register facility and patient
    code = f"F9_{uuid.uuid4().hex[:4].upper()}"
    admin_token, _ = get_token_and_user("ADMIN")
    fac_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Hospital {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()["id"]

    pat = client.post(
        "/api/v1/patients",
        json={
            "user_id": pat_user_id,
            "first_name": f"Kavita_{uuid.uuid4().hex[:4]}",
            "last_name": f"Rao_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1992-04-10",
            "gender": "FEMALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    pat_id = pat["id"]

    # 2. Trigger notification service helpers
    from app.db.session import SessionLocal
    from app.models.appointment import Appointment
    from app.models.diagnostic_result import DiagnosticResult
    from app.models.patient import Patient
    from app.models.prescription import Prescription
    from app.models.referral import Referral
    from app.services.notification_service import NotificationService

    db = SessionLocal()
    svc = NotificationService(db)
    patient_model = db.get(Patient, uuid.UUID(pat_id))

    # Trigger appointment reminder
    app_dummy = Appointment(
        id=uuid.uuid4(),
        patient_id=patient_model.id,
        facility_id=uuid.UUID(fac_id),
        provider_id=doc_id,
        appointment_date=date.today(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
    )
    n_app = svc.notify_appointment_reminder(app_dummy, patient_model)
    assert n_app is not None
    assert n_app.notification_type == "APPOINTMENT_REMINDER"

    # Trigger prescription notice
    rx_dummy = Prescription(id=uuid.uuid4(), patient_id=patient_model.id)
    n_rx = svc.notify_prescription_issued(rx_dummy, patient_model)
    assert n_rx is not None
    assert n_rx.notification_type == "PRESCRIPTION_ISSUED"

    # Trigger diagnostic notice
    diag_dummy = DiagnosticResult(id=uuid.uuid4(), patient_id=patient_model.id)
    n_diag = svc.notify_diagnostic_result_available(diag_dummy, patient_model)
    assert n_diag is not None
    assert n_diag.notification_type == "DIAGNOSTIC_RESULT_AVAILABLE"
    # Ensure sensitive clinical finding is not in the text
    assert "findings have been verified" in n_diag.message

    db.close()

    # Patient checks their notification feed
    feed_res = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {pat_token}"})
    assert feed_res.status_code == 200
    assert feed_res.json()["total"] >= 3
