import uuid
from datetime import date
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"rx.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_clinical_encounter():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")

    # 1. Facility
    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Prescription Facility {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    facility_id = fac_res.json()["id"]

    # 2. Patient
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"RxPat{uuid.uuid4().hex[:4]}",
            "last_name": f"Test{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1991-07-14",
            "gender": "FEMALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    patient_id = pat_res.json()["id"]

    # 3. Appointment & Encounter
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
            "reason": "Upper respiratory tract infection",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appointment_id = app_res.json()["id"]

    enc_res = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    encounter_id = enc_res.json()["id"]

    # 4. Create Active Medication
    med_res = client.post(
        "/api/v1/medications",
        json={
            "name": f"Amoxicillin {uuid.uuid4().hex[:4]}",
            "generic_name": "Amoxicillin Trihydrate",
            "strength": "500 mg",
            "dosage_form": "CAPSULE",
            "route": "ORAL",
            "unit": "mg",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    medication_id = med_res.json()["id"]

    return {
        "admin_token": admin_token,
        "doc_token": doc_token,
        "doc_id": doc_id,
        "facility_id": facility_id,
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "medication_id": medication_id,
    }


def test_create_medication_catalog_entry():
    admin_token, _ = get_token_and_user("ADMIN")
    res = client.post(
        "/api/v1/medications",
        json={
            "name": f"Paracetamol {uuid.uuid4().hex[:4]}",
            "generic_name": "Paracetamol",
            "strength": "650 mg",
            "dosage_form": "TABLET",
            "route": "ORAL",
            "unit": "mg",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201
    assert "id" in res.json()
    assert res.json()["dosage_form"] == "TABLET"


def test_create_prescription_from_encounter_with_items():
    ctx = setup_clinical_encounter()

    payload = {
        "items": [
            {
                "medication_id": ctx["medication_id"],
                "dosage": "500 mg (1 capsule)",
                "frequency": "THREE_TIMES_DAILY",
                "duration": 7,
                "duration_unit": "DAYS",
                "route": "ORAL",
                "quantity": 21,
                "instructions": "Take after meals with water",
                "notes": "Complete the full antibiotic course",
            }
        ],
        "notes": "Return if fever does not subside in 48 hours.",
    }
    res = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/prescriptions",
        json=payload,
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res.status_code == 201
    rx = res.json()
    assert rx["status"] == "ISSUED"
    assert rx["patient_id"] == ctx["patient_id"]
    assert rx["encounter_id"] == ctx["encounter_id"]
    assert len(rx["items"]) == 1
    assert rx["items"][0]["quantity"] == 21
    assert rx["items"][0]["medication_id"] == ctx["medication_id"]


def test_inactive_medication_prescription_rejected():
    ctx = setup_clinical_encounter()

    # Create inactive medication
    inactive_med = client.post(
        "/api/v1/medications",
        json={
            "name": f"Discontinued Med {uuid.uuid4().hex[:4]}",
            "generic_name": "Old Chemical",
            "strength": "10 mg",
            "dosage_form": "TABLET",
            "is_active": False,
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    res = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/prescriptions",
        json={
            "items": [
                {
                    "medication_id": inactive_med,
                    "dosage": "10 mg",
                    "frequency": "ONCE_DAILY",
                    "duration": 3,
                    "duration_unit": "DAYS",
                    "quantity": 3,
                }
            ]
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "MEDICATION_INACTIVE"


def test_prescription_retrieval_and_patient_history():
    ctx = setup_clinical_encounter()

    # Create prescription
    create_res = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/prescriptions",
        json={
            "items": [
                {
                    "medication_id": ctx["medication_id"],
                    "dosage": "500 mg",
                    "frequency": "TWICE_DAILY",
                    "duration": 5,
                    "quantity": 10,
                }
            ]
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    rx_id = create_res.json()["id"]

    # 1. Get by ID
    get_res = client.get(
        f"/api/v1/prescriptions/{rx_id}",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["id"] == rx_id

    # 2. Patient prescription history
    history_res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/prescriptions",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert history_res.status_code == 200
    assert history_res.json()["total"] >= 1
    assert any(p["id"] == rx_id for p in history_res.json()["items"])


def test_cancel_prescription_with_reason():
    ctx = setup_clinical_encounter()

    rx_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/prescriptions",
        json={
            "items": [
                {
                    "medication_id": ctx["medication_id"],
                    "dosage": "500 mg",
                    "frequency": "ONCE_DAILY",
                    "duration": 5,
                    "quantity": 5,
                }
            ]
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    cancel_res = client.post(
        f"/api/v1/prescriptions/{rx_id}/cancel",
        json={"reason": "Patient reported adverse reaction to penicillin class"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert "adverse reaction" in cancel_res.json()["cancellation_reason"]


def test_patient_cross_access_to_prescription_forbidden():
    ctx = setup_clinical_encounter()

    rx_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/prescriptions",
        json={
            "items": [
                {
                    "medication_id": ctx["medication_id"],
                    "dosage": "500 mg",
                    "frequency": "ONCE_DAILY",
                    "duration": 3,
                    "quantity": 3,
                }
            ]
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    # Unrelated patient account attempts to view
    other_patient_token, _ = get_token_and_user("PATIENT")
    cross_res = client.get(
        f"/api/v1/prescriptions/{rx_id}",
        headers={"Authorization": f"Bearer {other_patient_token}"},
    )
    assert cross_res.status_code == 403
    assert cross_res.json()["error"]["code"] == "FORBIDDEN"
