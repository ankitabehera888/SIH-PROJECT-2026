import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"staff.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def create_test_facility(admin_token: str) -> str:
    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    res = client.post(
        "/api/v1/facilities",
        json={"name": f"Queue Facility {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    return res.json()["id"]


def setup_appointment(admin_token: str, doc_token: str, doc_id: int):
    facility_id = create_test_facility(admin_token)

    # Create Patient
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"QueuePatient{uuid.uuid4().hex[:4]}",
            "last_name": f"Test{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1991-05-20",
            "gender": "FEMALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert pat_res.status_code == 201
    patient_id = pat_res.json()["id"]

    # Book Appointment for Today
    today_str = date.today().isoformat()
    hour = (uuid.uuid4().int % 12) + 8
    app_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": today_str,
            "start_time": f"{hour:02d}:00:00",
            "end_time": f"{hour:02d}:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert app_res.status_code == 201
    return facility_id, patient_id, app_res.json()["id"]


def test_check_in_creates_queue_entry():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, _, appointment_id = setup_appointment(admin_token, doc_token, doc_id)

    check_in_res = client.post(
        f"/api/v1/appointments/{appointment_id}/check-in",
        json={"priority": "NORMAL"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert check_in_res.status_code == 201
    q_data = check_in_res.json()
    assert q_data["queue_number"].startswith("Q")
    assert q_data["status"] == "WAITING"
    assert q_data["priority"] == "NORMAL"
    assert "checked_in_at" in q_data

    # Verify appointment advanced to WAITING
    app_res = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert app_res.json()["status"] == "WAITING"


def test_duplicate_check_in_rejected():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, _, appointment_id = setup_appointment(admin_token, doc_token, doc_id)

    # First check-in
    res1 = client.post(
        f"/api/v1/appointments/{appointment_id}/check-in",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res1.status_code == 201

    # Second check-in for same appointment -> 400 or 409
    res2 = client.post(
        f"/api/v1/appointments/{appointment_id}/check-in",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res2.status_code in [400, 409]


def test_priority_queue_ordering():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")

    # Create Facility
    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Triage PHC {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    facility_id = fac_res.json()["id"]

    # Book Patient 1 (NORMAL)
    p1_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Normal{uuid.uuid4().hex[:4]}", "last_name": f"Case{uuid.uuid4().hex[:4]}", "date_of_birth": "1990-01-01", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert p1_res.status_code == 201
    p1 = p1_res.json()["id"]
    a1 = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": p1,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": date.today().isoformat(),
            "start_time": "09:00:00",
            "end_time": "09:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    # Book Patient 2 (URGENT)
    p2_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Urgent{uuid.uuid4().hex[:4]}", "last_name": f"Case{uuid.uuid4().hex[:4]}", "date_of_birth": "1985-02-02", "gender": "FEMALE"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert p2_res.status_code == 201
    p2 = p2_res.json()["id"]
    a2 = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": p2,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": date.today().isoformat(),
            "start_time": "09:30:00",
            "end_time": "10:00:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    # Check in Patient 1 as NORMAL
    client.post(
        f"/api/v1/appointments/{a1}/check-in",
        json={"priority": "NORMAL"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # Check in Patient 2 as URGENT (arrived second)
    q2_entry = client.post(
        f"/api/v1/appointments/{a2}/check-in",
        json={"priority": "URGENT"},
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()

    # Call Next: Patient 2 (URGENT) must be called first even though they arrived second!
    call_res = client.post(
        f"/api/v1/queues/{facility_id}/call-next",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert call_res.status_code == 200
    assert call_res.json()["priority"] == "URGENT"
    assert call_res.json()["id"] == q2_entry["id"]


def test_full_consultation_lifecycle():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, _, appointment_id = setup_appointment(admin_token, doc_token, doc_id)

    # 1. Check in -> WAITING
    q_entry = client.post(
        f"/api/v1/appointments/{appointment_id}/check-in",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    q_id = q_entry["id"]

    # 2. Call next -> CALLED
    called = client.post(
        f"/api/v1/queues/{facility_id}/call-next",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    assert called["id"] == q_id
    assert called["status"] == "CALLED"
    assert called["called_at"] is not None

    # 3. Start consultation -> IN_CONSULTATION
    started = client.post(
        f"/api/v1/queues/{q_id}/start",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    assert started["status"] == "IN_CONSULTATION"
    assert started["consultation_started_at"] is not None

    # Verify appointment also reflects IN_CONSULTATION
    app_state = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    assert app_state["status"] == "IN_CONSULTATION"

    # 4. Complete consultation -> COMPLETED
    completed = client.post(
        f"/api/v1/queues/{q_id}/complete",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    assert completed["status"] == "COMPLETED"
    assert completed["completed_at"] is not None

    # Verify appointment also reflects COMPLETED
    app_final = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    assert app_final["status"] == "COMPLETED"


def test_patient_role_cannot_call_next():
    patient_token, _ = get_token_and_user("PATIENT")
    admin_token, _ = get_token_and_user("ADMIN")
    fac_id = create_test_facility(admin_token)

    # Patient attempts to call next patient in queue -> 403 Forbidden
    res = client.post(
        f"/api/v1/queues/{fac_id}/call-next",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"
