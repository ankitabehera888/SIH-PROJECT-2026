import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"part.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_test_consultation():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_user_id = get_token_and_user("DOCTOR")
    pat_token, pat_user_id = get_token_and_user("PATIENT")
    nurse_token, nurse_user_id = get_token_and_user("NURSE")

    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_id = client.post(
        "/api/v1/facilities",
        json={
            "name": f"Rural Health Centre {code}",
            "facility_code": code,
            "facility_type": "PHC",
            "address": "Tribal Sector 1",
            "phone": "+919876512345",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()["id"]

    pat_id = client.post(
        "/api/v1/patients",
        json={
            "user_id": pat_user_id,
            "first_name": f"Pooja_{uuid.uuid4().hex[:4]}",
            "last_name": f"Nair_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1998-11-20",
            "gender": "FEMALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    appt_date = (date.today() + timedelta(days=3)).isoformat()
    appt_id = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_user_id,
            "facility_id": fac_id,
            "appointment_date": appt_date,
            "start_time": "11:00:00",
            "end_time": "11:30:00",
            "appointment_type": "GENERAL_CONSULTATION",
            "reason": "Routine tele-checkup",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    cons_id = client.post(
        f"/api/v1/appointments/{appt_id}/consultation",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    return {
        "cons_id": cons_id,
        "doc_token": doc_token,
        "doc_user_id": doc_user_id,
        "pat_token": pat_token,
        "pat_user_id": pat_user_id,
        "nurse_token": nurse_token,
        "nurse_user_id": nurse_user_id,
    }


def test_participant_attendance_recording_and_duration():
    env = setup_test_consultation()

    # 1. Patient joins
    client.post(
        f"/api/v1/consultations/{env['cons_id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )

    # 2. Doctor joins
    client.post(
        f"/api/v1/consultations/{env['cons_id']}/join",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )

    # 3. Check participants list
    parts_res = client.get(
        f"/api/v1/consultations/{env['cons_id']}/participants",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert parts_res.status_code == 200
    parts = parts_res.json()
    assert len(parts) == 2

    patient_part = next(p for p in parts if p["role"] == "PATIENT")
    assert patient_part["connection_status"] == "CONNECTED"
    assert patient_part["joined_at"] is not None

    provider_part = next(p for p in parts if p["role"] == "PROVIDER")
    assert provider_part["connection_status"] == "CONNECTED"
    assert provider_part["joined_at"] is not None

    # 4. End consultation -> active participants marked disconnected and duration logged
    client.post(
        f"/api/v1/consultations/{env['cons_id']}/end",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )

    parts_res2 = client.get(
        f"/api/v1/consultations/{env['cons_id']}/participants",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    parts2 = parts_res2.json()
    for p in parts2:
        assert p["connection_status"] == "DISCONNECTED"
        assert p["left_at"] is not None
        assert p["duration_seconds"] >= 0


def test_assisted_teleconsultation_with_health_worker():
    env = setup_test_consultation()

    # Nurse / Rural Health Worker joins to assist the patient
    nurse_join = client.post(
        f"/api/v1/consultations/{env['cons_id']}/join",
        headers={"Authorization": f"Bearer {env['nurse_token']}"},
    )
    assert nurse_join.status_code == 200
    assert nurse_join.json()["role"] == "HEALTH_WORKER"

    parts_res = client.get(
        f"/api/v1/consultations/{env['cons_id']}/participants",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert any(p["role"] == "HEALTH_WORKER" for p in parts_res.json())


def test_participant_reconnect_handling():
    env = setup_test_consultation()

    # Initial join
    client.post(
        f"/api/v1/consultations/{env['cons_id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )

    # Rejoin (simulating page reload or network recovery)
    rejoin_res = client.post(
        f"/api/v1/consultations/{env['cons_id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )
    assert rejoin_res.status_code == 200

    parts_res = client.get(
        f"/api/v1/consultations/{env['cons_id']}/participants",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )
    pat_part = next(p for p in parts_res.json() if p["role"] == "PATIENT")
    assert pat_part["reconnect_count"] == 1
    assert pat_part["connection_status"] == "CONNECTED"
