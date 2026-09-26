import uuid
from datetime import date
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"vitals.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_in_progress_encounter(admin_token: str, doc_token: str, doc_id: int):
    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Vitals Facility {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    facility_id = fac_res.json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"VitalPat{uuid.uuid4().hex[:4]}",
            "last_name": f"Test{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1988-08-08",
            "gender": "FEMALE",
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
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appointment_id = app_res.json()["id"]

    enc_res = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    return enc_res.json()["id"]


def test_record_vitals_success():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    enc_id = setup_in_progress_encounter(admin_token, doc_token, doc_id)

    payload = {
        "temperature": 37.4,
        "heart_rate": 78,
        "respiratory_rate": 16,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "spo2": 98.5,
        "weight": 68.0,
        "height": 172.0,
        "notes": "Patient calm, sitting position.",
    }
    v_res = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json=payload,
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert v_res.status_code == 201
    data = v_res.json()
    assert data["temperature"] == 37.4
    assert data["heart_rate"] == 78
    assert data["systolic_bp"] == 120
    assert data["diastolic_bp"] == 80
    assert data["spo2"] == 98.5
    assert "id" in data
    assert "recorded_at" in data


def test_multiple_vitals_recorded_during_same_encounter():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    enc_id = setup_in_progress_encounter(admin_token, doc_token, doc_id)

    # Initial measurement
    client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"systolic_bp": 145, "diastolic_bp": 92, "heart_rate": 95},
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # Post-rest measurement 15 mins later
    client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"systolic_bp": 130, "diastolic_bp": 85, "heart_rate": 80},
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # Retrieve all vitals for encounter
    list_res = client.get(
        f"/api/v1/encounters/{enc_id}/vitals",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert list_res.status_code == 200
    vitals_list = list_res.json()
    assert vitals_list["total"] == 2
    assert len(vitals_list["items"]) == 2


def test_vitals_physiological_range_validations():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    enc_id = setup_in_progress_encounter(admin_token, doc_token, doc_id)

    # 1. Temperature impossible (> 45 C)
    res_temp = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"temperature": 55.0},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res_temp.status_code == 422

    # 2. Heart rate negative
    res_hr = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"heart_rate": -15},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res_hr.status_code == 422

    # 3. SpO2 > 100%
    res_spo2 = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"spo2": 105.0},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res_spo2.status_code == 422

    # 4. Inverted blood pressure (diastolic >= systolic)
    res_bp = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"systolic_bp": 80, "diastolic_bp": 120},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res_bp.status_code == 422


def test_record_vitals_on_completed_encounter_rejected():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    enc_id = setup_in_progress_encounter(admin_token, doc_token, doc_id)

    # Complete encounter
    client.post(
        f"/api/v1/encounters/{enc_id}/complete",
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # Attempt to record vitals after completion -> 400
    res = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"temperature": 37.0},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "ENCOUNTER_LOCKED"
