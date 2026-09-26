import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.integrations.daily import DailyService
from app.main import app

client = TestClient(app)


def test_daily_service_room_and_token_generation():
    daily = DailyService()
    room_name = f"test-room-{uuid.uuid4().hex[:8]}"

    room_data = daily.create_room(room_name)
    assert room_data["name"] == room_name
    assert room_data["privacy"] == "private"
    assert room_name in room_data["url"]

    # Token for doctor (is_owner=True)
    doc_token = daily.create_meeting_token(room_name, user_name="doctor@test.org", is_owner=True)
    assert "provider" in doc_token or len(doc_token) > 10

    # Token for patient (is_owner=False)
    pat_token = daily.create_meeting_token(room_name, user_name="patient@test.org", is_owner=False)
    assert "patient" in pat_token or len(pat_token) > 10
    assert doc_token != pat_token

    # Teardown room
    deleted = daily.delete_room(room_name)
    assert deleted is True


def test_daily_webhook_lifecycle_events():
    # 1. Setup minimal user and consultation
    email = f"webhook.doc.{uuid.uuid4().hex[:6]}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_uid = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"}).json()["access_token"]

    admin_email = f"webhook.admin.{uuid.uuid4().hex[:6]}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    fac_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Clinic {uuid.uuid4().hex[:4]}", "facility_code": f"WH_{uuid.uuid4().hex[:4]}", "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    pat_id = client.post(
        "/api/v1/patients",
        json={"first_name": f"Ram_{uuid.uuid4().hex[:4]}", "last_name": f"Verma_{uuid.uuid4().hex[:4]}", "date_of_birth": "1991-03-21", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    ).json()["id"]

    appt_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_uid,
            "facility_id": fac_id,
            "appointment_date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "15:00:00",
            "end_time": "15:30:00",
            "reason": "Follow-up",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    appt_id = appt_res.json()["id"]

    cons_res = client.post(
        f"/api/v1/appointments/{appt_id}/consultation",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    cons = cons_res.json()
    room_name = cons["room_name"]

    # 2. Simulate Daily webhook: meeting.started
    start_webhook = client.post(
        "/api/v1/webhooks/daily",
        json={"event": "meeting.started", "room": room_name},
    )
    assert start_webhook.status_code == 200
    assert start_webhook.json()["status"] == "PROCESSED"

    # Verify consultation status in DB updated to IN_PROGRESS
    cons_after_start = client.get(
        f"/api/v1/consultations/{cons['id']}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    ).json()
    assert cons_after_start["status"] == "IN_PROGRESS"

    # 3. Simulate Daily webhook: meeting.ended
    end_webhook = client.post(
        "/api/v1/webhooks/daily",
        json={"event": "meeting.ended", "room": room_name},
    )
    assert end_webhook.status_code == 200
    assert end_webhook.json()["status"] == "PROCESSED"

    # Verify consultation status in DB updated to COMPLETED
    cons_after_end = client.get(
        f"/api/v1/consultations/{cons['id']}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    ).json()
    assert cons_after_end["status"] == "COMPLETED"


def test_daily_webhook_participant_events_and_idempotency():
    # 1. Setup user and consultation
    email = f"wh.part.{uuid.uuid4().hex[:6]}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_uid = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"}).json()["access_token"]

    admin_email = f"wh.admin.{uuid.uuid4().hex[:6]}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    fac_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Clinic {uuid.uuid4().hex[:4]}", "facility_code": f"WH2_{uuid.uuid4().hex[:4]}", "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    pat_id = client.post(
        "/api/v1/patients",
        json={"first_name": f"Kiran_{uuid.uuid4().hex[:4]}", "last_name": f"Rao_{uuid.uuid4().hex[:4]}", "date_of_birth": "1995-05-12", "gender": "FEMALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    ).json()["id"]

    appt_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_uid,
            "facility_id": fac_id,
            "appointment_date": (date.today() + timedelta(days=2)).isoformat(),
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Consultation",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    appt_id = appt_res.json()["id"]

    cons_res = client.post(
        f"/api/v1/appointments/{appt_id}/consultation",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    cons = cons_res.json()
    room_name = cons["room_name"]

    # 2. Webhook: participant.joined
    event_id = f"evt_{uuid.uuid4().hex}"
    join_res = client.post(
        "/api/v1/webhooks/daily",
        json={
            "event": "participant.joined",
            "room": room_name,
            "payload": {
                "id": event_id,
                "participant": {
                    "user_id": doc_uid,
                    "role": "PROVIDER",
                },
            },
        },
    )
    assert join_res.status_code == 200
    assert join_res.json()["status"] == "PROCESSED"

    # 3. Idempotency: Duplicate delivery of participant.joined
    duplicate_res = client.post(
        "/api/v1/webhooks/daily",
        json={
            "event": "participant.joined",
            "room": room_name,
            "payload": {
                "id": event_id,
                "participant": {
                    "user_id": doc_uid,
                    "role": "PROVIDER",
                },
            },
        },
    )
    assert duplicate_res.status_code == 200
    assert duplicate_res.json()["status"] == "DUPLICATE_EVENT_IGNORED"

    # 4. Webhook: participant.left
    left_event_id = f"evt_left_{uuid.uuid4().hex}"
    left_res = client.post(
        "/api/v1/webhooks/daily",
        json={
            "event": "participant.left",
            "room": room_name,
            "payload": {
                "id": left_event_id,
                "participant": {
                    "user_id": doc_uid,
                },
            },
        },
    )
    assert left_res.status_code == 200
    assert left_res.json()["status"] == "PROCESSED"

    # 5. Verify participant status in database
    parts_res = client.get(
        f"/api/v1/consultations/{cons['id']}/participants",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert parts_res.status_code == 200
    p = next(p for p in parts_res.json() if p["user_id"] == doc_uid)
    assert p["connection_status"] == "DISCONNECTED"
    assert p["left_at"] is not None
