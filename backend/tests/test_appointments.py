import uuid
from datetime import date, time, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"user.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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
        json={
            "name": f"Test PHC {code}",
            "facility_code": code,
            "facility_type": "PHC",
            "address": "Rural District Sector 4",
            "phone": "+919876500000",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201
    return res.json()["id"]


def create_test_patient(doctor_token: str, user_id: int = None) -> str:
    res = client.post(
        "/api/v1/patients",
        json={
            "first_name": "Karan",
            "last_name": f"Verma{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1993-04-10",
            "gender": "MALE",
            "phone": f"+919{uuid.uuid4().int % 1000000000:09d}",
        },
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_facility_creation_and_listing():
    admin_token, _ = get_token_and_user("ADMIN")
    facility_id = create_test_facility(admin_token)

    list_res = client.get(
        "/api/v1/facilities",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


def test_appointment_booking_success():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id = create_test_facility(admin_token)
    patient_id = create_test_patient(doc_token)

    app_date = (date.today() + timedelta(days=2)).isoformat()
    payload = {
        "patient_id": patient_id,
        "provider_id": doc_id,
        "facility_id": facility_id,
        "appointment_date": app_date,
        "start_time": "10:00:00",
        "end_time": "10:30:00",
        "appointment_type": "GENERAL_CONSULTATION",
        "reason": "Persistent seasonal cough",
    }
    res = client.post(
        "/api/v1/appointments",
        json=payload,
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "SCHEDULED"
    assert data["provider_id"] == doc_id
    assert data["patient_id"] == patient_id
    assert "id" in data


def test_appointment_overlap_conflict_detection():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id = create_test_facility(admin_token)
    patient1_id = create_test_patient(doc_token)
    patient2_id = create_test_patient(doc_token)

    target_date = (date.today() + timedelta(days=3)).isoformat()

    # Slot 1: 10:00 -> 10:30
    res1 = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient1_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": target_date,
            "start_time": "10:00:00",
            "end_time": "10:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res1.status_code == 201

    # Overlapping Slot 2: 10:15 -> 10:45 for SAME provider on SAME date -> 409 Conflict
    res2 = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient2_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": target_date,
            "start_time": "10:15:00",
            "end_time": "10:45:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"
    assert "conflict" in data["error"]["message"].lower() or "already booked" in data["error"]["message"].lower()


def test_appointment_invalid_time_range_rejected():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id = create_test_facility(admin_token)
    patient_id = create_test_patient(doc_token)

    app_date = (date.today() + timedelta(days=2)).isoformat()
    # start_time later than end_time
    res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": app_date,
            "start_time": "11:00:00",
            "end_time": "10:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INVALID_TIME_RANGE"


def test_appointment_rescheduling():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id = create_test_facility(admin_token)
    patient_id = create_test_patient(doc_token)

    date1 = (date.today() + timedelta(days=4)).isoformat()
    date2 = (date.today() + timedelta(days=5)).isoformat()

    create_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": date1,
            "start_time": "09:00:00",
            "end_time": "09:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appointment_id = create_res.json()["id"]

    # Reschedule to date2, 14:00
    resched_res = client.post(
        f"/api/v1/appointments/{appointment_id}/reschedule",
        json={
            "appointment_date": date2,
            "start_time": "14:00:00",
            "end_time": "14:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert resched_res.status_code == 200
    assert resched_res.json()["appointment_date"] == date2
    assert resched_res.json()["start_time"] == "14:00:00"


def test_appointment_cancellation():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id = create_test_facility(admin_token)
    patient_id = create_test_patient(doc_token)

    app_date = (date.today() + timedelta(days=6)).isoformat()
    create_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": app_date,
            "start_time": "15:00:00",
            "end_time": "15:30:00",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appointment_id = create_res.json()["id"]

    cancel_res = client.post(
        f"/api/v1/appointments/{appointment_id}/cancel",
        json={"reason": "Patient had transport difficulties"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert cancel_res.json()["cancellation_reason"] == "Patient had transport difficulties"


def test_patient_resource_authorization_cross_access_forbidden():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    patient1_token, p1_user_id = get_token_and_user("PATIENT")
    patient2_token, p2_user_id = get_token_and_user("PATIENT")

    facility_id = create_test_facility(admin_token)

    # Register Patient entity linked to user 1
    p1_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"PatientOne{uuid.uuid4().hex[:4]}",
            "last_name": f"Self{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1990-01-01",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert p1_res.status_code == 201
    p1_id = p1_res.json()["id"]

    # Book appointment for Patient 1
    app_date = (date.today() + timedelta(days=7)).isoformat()
    create_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": p1_id,
            "provider_id": doc_id,
            "facility_id": facility_id,
            "appointment_date": app_date,
            "start_time": "16:00:00",
            "end_time": "16:30:00",
        },
        headers={"Authorization": f"Bearer {patient1_token}"},
    )
    app_id = create_res.json()["id"]

    # Patient 1 can view own appointment
    ok_res = client.get(
        f"/api/v1/appointments/{app_id}",
        headers={"Authorization": f"Bearer {patient1_token}"},
    )
    assert ok_res.status_code == 200

    # Patient 2 attempts to view Patient 1's appointment -> 403 Forbidden
    forbidden_res = client.get(
        f"/api/v1/appointments/{app_id}",
        headers={"Authorization": f"Bearer {patient2_token}"},
    )
    assert forbidden_res.status_code == 403
    assert forbidden_res.json()["error"]["code"] == "FORBIDDEN"
