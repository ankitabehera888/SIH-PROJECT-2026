import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"encounter.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_appointment_for_encounter(admin_token: str, doc_token: str, doc_id: int):
    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Facility {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    facility_id = fac_res.json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"EncounterPat{uuid.uuid4().hex[:4]}",
            "last_name": f"Test{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1990-04-12",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    patient_id = pat_res.json()["id"]

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
            "reason": "Acute abdominal pain",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    return facility_id, patient_id, app_res.json()["id"]


def test_create_encounter_from_appointment():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, patient_id, appointment_id = setup_appointment_for_encounter(admin_token, doc_token, doc_id)

    enc_res = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert enc_res.status_code == 201
    enc = enc_res.json()
    assert enc["appointment_id"] == appointment_id
    assert enc["patient_id"] == patient_id
    assert enc["status"] == "IN_PROGRESS"
    assert enc["started_at"] is not None
    assert enc["chief_complaint"] == "Acute abdominal pain"

    # Verify appointment advanced to IN_CONSULTATION
    app_res = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert app_res.json()["status"] == "IN_CONSULTATION"


def test_duplicate_encounter_creation_rejected():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, patient_id, appointment_id = setup_appointment_for_encounter(admin_token, doc_token, doc_id)

    # First encounter
    res1 = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res1.status_code == 201

    # Duplicate creation attempt -> 409 Conflict
    res2 = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res2.status_code == 409
    assert res2.json()["error"]["code"] == "CONFLICT"


def test_get_encounter_details():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, patient_id, appointment_id = setup_appointment_for_encounter(admin_token, doc_token, doc_id)

    enc_id = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    get_res = client.get(
        f"/api/v1/encounters/{enc_id}",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["id"] == enc_id


def test_update_encounter_notes():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, patient_id, appointment_id = setup_appointment_for_encounter(admin_token, doc_token, doc_id)

    enc_id = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    update_res = client.patch(
        f"/api/v1/encounters/{enc_id}",
        json={
            "chief_complaint": "Acute epigastric pain",
            "clinical_notes": "Abdomen soft, tenderness in epigastrium. Suspect gastritis.",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["chief_complaint"] == "Acute epigastric pain"
    assert "gastritis" in update_res.json()["clinical_notes"]


def test_complete_encounter_and_lock():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, patient_id, appointment_id = setup_appointment_for_encounter(admin_token, doc_token, doc_id)

    enc_id = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    # Complete encounter
    comp_res = client.post(
        f"/api/v1/encounters/{enc_id}/complete",
        json={"clinical_notes": "Prescribed antacids, review in 3 days."},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert comp_res.status_code == 200
    completed_enc = comp_res.json()
    assert completed_enc["status"] == "COMPLETED"
    assert completed_enc["ended_at"] is not None

    # Verify modifying completed encounter is blocked
    patch_res = client.patch(
        f"/api/v1/encounters/{enc_id}",
        json={"clinical_notes": "Unauthorized edit after completion"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert patch_res.status_code == 400
    assert patch_res.json()["error"]["code"] == "ENCOUNTER_LOCKED"


def test_patient_longitudinal_encounter_history():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    facility_id, patient_id, appointment_id = setup_appointment_for_encounter(admin_token, doc_token, doc_id)

    # Create encounter for patient
    client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    history_res = client.get(
        f"/api/v1/patients/{patient_id}/encounters",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["total"] >= 1
    assert any(e["patient_id"] == patient_id for e in history["items"])
