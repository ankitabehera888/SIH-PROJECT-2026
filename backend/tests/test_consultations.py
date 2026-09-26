import uuid
from datetime import date, time, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"consult.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_teleconsultation_environment():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_user_id = get_token_and_user("DOCTOR")
    pat_token, pat_user_id = get_token_and_user("PATIENT")
    other_pat_token, other_pat_user_id = get_token_and_user("PATIENT")
    other_doc_token, _ = get_token_and_user("DOCTOR")

    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_res = client.post(
        "/api/v1/facilities",
        json={
            "name": f"Telehealth Clinic {code}",
            "facility_code": code,
            "facility_type": "PHC",
            "address": "Rural District Sector 9",
            "phone": "+919876500000",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    fac_id = fac_res.json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={
            "user_id": pat_user_id,
            "first_name": f"Aarav_{uuid.uuid4().hex[:4]}",
            "last_name": f"Sharma_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1994-06-15",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    pat_id = pat_res.json()["id"]

    appt_date = (date.today() + timedelta(days=2)).isoformat()
    appt_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_user_id,
            "facility_id": fac_id,
            "appointment_date": appt_date,
            "start_time": "14:00:00",
            "end_time": "14:30:00",
            "appointment_type": "GENERAL_CONSULTATION",
            "reason": "Remote follow-up teleconsultation",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appt_id = appt_res.json()["id"]

    return {
        "admin_token": admin_token,
        "doc_token": doc_token,
        "doc_user_id": doc_user_id,
        "pat_token": pat_token,
        "pat_user_id": pat_user_id,
        "other_pat_token": other_pat_token,
        "other_doc_token": other_doc_token,
        "fac_id": fac_id,
        "pat_id": pat_id,
        "appt_id": appt_id,
    }


def test_create_teleconsultation_success():
    env = setup_teleconsultation_environment()

    res = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        json={"consultation_type": "VIDEO"},
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["appointment_id"] == env["appt_id"]
    assert data["status"] == "SCHEDULED"
    assert data["consultation_type"] == "VIDEO"
    assert data["room_name"].startswith("consultation-")
    assert "daily.co" in data["room_url"]


def test_duplicate_consultation_rejected():
    env = setup_teleconsultation_environment()

    # 1. Create first consultation
    client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        json={"consultation_type": "VIDEO"},
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )

    # 2. Duplicate attempt
    res2 = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        json={"consultation_type": "VIDEO"},
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert res2.status_code == 409
    assert "already exists" in res2.json()["error"]["message"].lower()


def test_patient_join_and_token_generation():
    env = setup_teleconsultation_environment()

    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()

    join_res = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )
    assert join_res.status_code == 200
    join_data = join_res.json()
    assert join_data["role"] == "PATIENT"
    assert join_data["room_name"] == cons["room_name"]
    assert "token" in join_data and len(join_data["token"]) > 10

    # Consultation status should now be READY (waiting for doctor)
    get_res = client.get(
        f"/api/v1/consultations/{cons['id']}",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )
    assert get_res.json()["status"] == "READY"


def test_unauthorized_patient_join_forbidden():
    env = setup_teleconsultation_environment()

    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()

    # Other patient attempts to join
    res = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['other_pat_token']}"},
    )
    assert res.status_code == 403
    assert "access denied" in res.json()["error"]["message"].lower()


def test_provider_join_transitions_to_in_progress():
    env = setup_teleconsultation_environment()

    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()

    # Patient joins first -> READY
    client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )

    # Provider joins -> transitions to IN_PROGRESS
    doc_join = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert doc_join.status_code == 200
    assert doc_join.json()["role"] == "PROVIDER"

    get_res = client.get(
        f"/api/v1/consultations/{cons['id']}",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert get_res.json()["status"] == "IN_PROGRESS"


def test_unassigned_doctor_join_forbidden():
    env = setup_teleconsultation_environment()

    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()

    # Doctor not assigned to this consultation
    res = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['other_doc_token']}"},
    )
    assert res.status_code == 403


def test_end_consultation_lifecycle():
    env = setup_teleconsultation_environment()

    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()

    client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )

    end_res = client.post(
        f"/api/v1/consultations/{cons['id']}/end",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert end_res.status_code == 200
    assert end_res.json()["status"] == "COMPLETED"

    # Further join attempts must be rejected
    rejoin_res = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )
    assert rejoin_res.status_code == 400


def test_cancel_consultation_lifecycle():
    env = setup_teleconsultation_environment()

    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()

    cancel_res = client.post(
        f"/api/v1/consultations/{cons['id']}/cancel",
        json={"reason": "Patient requested postponement"},
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    rejoin_res = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    )
    assert rejoin_res.status_code == 400


def test_complete_patient_to_doctor_teleconsultation_workflow_with_encounter():
    env = setup_teleconsultation_environment()

    # 1. Doctor creates consultation
    cons = client.post(
        f"/api/v1/appointments/{env['appt_id']}/consultation",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()
    assert cons["status"] == "SCHEDULED"

    # 2. Patient joins -> waiting room (READY)
    pat_join = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    ).json()
    assert pat_join["role"] == "PATIENT"

    ready_state = client.get(
        f"/api/v1/consultations/{cons['id']}",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    ).json()
    assert ready_state["status"] == "READY"

    # 3. Doctor joins -> session starts (IN_PROGRESS)
    doc_join = client.post(
        f"/api/v1/consultations/{cons['id']}/join",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()
    assert doc_join["role"] == "PROVIDER"

    in_progress_state = client.get(
        f"/api/v1/consultations/{cons['id']}",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    ).json()
    assert in_progress_state["status"] == "IN_PROGRESS"

    # 4. Doctor concludes session -> COMPLETED & automatically links/creates Encounter
    end_res = client.post(
        f"/api/v1/consultations/{cons['id']}/end",
        headers={"Authorization": f"Bearer {env['doc_token']}"},
    )
    assert end_res.status_code == 200
    ended_data = end_res.json()
    assert ended_data["status"] == "COMPLETED"
    assert ended_data["encounter_id"] is not None

    # Verify patient received Phase 9 notification feed
    notifs = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {env['pat_token']}"},
    ).json()
    assert notifs["total"] >= 1
    assert any("teleconsultation" in n["subject"].lower() for n in notifs["items"])

