import uuid
from datetime import date
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"lab.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_clinical_encounter_for_diagnostics():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    nurse_token, _ = get_token_and_user("NURSE")

    # 1. Facility
    code = f"FAC-{uuid.uuid4().hex[:6].upper()}"
    fac_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Lab Facility {code}", "facility_code": code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    facility_id = fac_res.json()["id"]

    # 2. Patient
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"LabPat{uuid.uuid4().hex[:4]}",
            "last_name": f"Test{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1993-02-18",
            "gender": "MALE",
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
            "reason": "Fatigue and pallor evaluation",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appointment_id = app_res.json()["id"]

    enc_res = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    encounter_id = enc_res.json()["id"]

    # 4. Create Diagnostic Test
    test_code = f"CBC_{uuid.uuid4().hex[:4].upper()}"
    test_res = client.post(
        "/api/v1/diagnostic-tests",
        json={
            "code": test_code,
            "name": "Complete Blood Count",
            "category": "HEMATOLOGY",
            "specimen_type": "EDTA_BLOOD",
            "description": "Routine blood cell evaluation",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    test_id = test_res.json()["id"]

    return {
        "admin_token": admin_token,
        "doc_token": doc_token,
        "doc_id": doc_id,
        "nurse_token": nurse_token,
        "facility_id": facility_id,
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "test_id": test_id,
    }


def test_create_diagnostic_test_catalog_entry():
    admin_token, _ = get_token_and_user("ADMIN")
    code = f"GLU_{uuid.uuid4().hex[:4].upper()}"
    res = client.post(
        "/api/v1/diagnostic-tests",
        json={
            "code": code,
            "name": "Fasting Blood Glucose",
            "category": "BIOCHEMISTRY",
            "specimen_type": "SERUM",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201
    assert res.json()["code"] == code


def test_create_diagnostic_order_from_encounter():
    ctx = setup_clinical_encounter_for_diagnostics()

    payload = {
        "items": [
            {
                "diagnostic_test_id": ctx["test_id"],
                "notes": "Suspected iron deficiency anemia",
            }
        ],
        "priority": "URGENT",
        "notes": "Expedite CBC processing",
    }
    res = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/diagnostic-orders",
        json=payload,
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res.status_code == 201
    order = res.json()
    assert order["status"] == "ORDERED"
    assert order["priority"] == "URGENT"
    assert order["patient_id"] == ctx["patient_id"]
    assert len(order["items"]) == 1
    assert order["items"][0]["status"] == "PENDING"


def test_diagnostic_order_retrieval_and_patient_history():
    ctx = setup_clinical_encounter_for_diagnostics()

    order_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/diagnostic-orders",
        json={"items": [{"diagnostic_test_id": ctx["test_id"]}]},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    # 1. Get by ID
    get_res = client.get(
        f"/api/v1/diagnostic-orders/{order_id}",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["id"] == order_id

    # 2. Patient history
    hist_res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/diagnostic-orders",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert hist_res.status_code == 200
    assert hist_res.json()["total"] >= 1
    assert any(o["id"] == order_id for o in hist_res.json()["items"])


def test_record_and_verify_diagnostic_result():
    ctx = setup_clinical_encounter_for_diagnostics()

    # Create order
    order = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/diagnostic-orders",
        json={"items": [{"diagnostic_test_id": ctx["test_id"]}]},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()
    item_id = order["items"][0]["id"]

    # Record lab result
    res_payload = {
        "result_value": "13.8",
        "unit": "g/dL",
        "reference_range": "12.0 - 16.0",
        "abnormal_flag": False,
        "notes": "Hemoglobin within normal adult female parameters",
    }
    rec_res = client.post(
        f"/api/v1/diagnostic-order-items/{item_id}/result",
        json=res_payload,
        headers={"Authorization": f"Bearer {ctx['nurse_token']}"},
    )
    assert rec_res.status_code == 201
    result = rec_res.json()
    assert result["result_value"] == "13.8"
    assert result["unit"] == "g/dL"
    assert result["result_status"] == "FINAL"
    assert result["verified_at"] is not None

    # Retrieve result
    get_res = client.get(
        f"/api/v1/diagnostic-order-items/{item_id}/result",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["result_value"] == "13.8"

    # Duplicate result rejected -> 409
    dup_res = client.post(
        f"/api/v1/diagnostic-order-items/{item_id}/result",
        json=res_payload,
        headers={"Authorization": f"Bearer {ctx['nurse_token']}"},
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "CONFLICT"


def test_cancel_diagnostic_order():
    ctx = setup_clinical_encounter_for_diagnostics()

    order_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/diagnostic-orders",
        json={"items": [{"diagnostic_test_id": ctx["test_id"]}]},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    canc_res = client.post(
        f"/api/v1/diagnostic-orders/{order_id}/cancel",
        json={"reason": "Sample hemolyzed, clinical decision to cancel"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert canc_res.status_code == 200
    assert canc_res.json()["status"] == "CANCELLED"
    assert "hemolyzed" in canc_res.json()["cancellation_reason"]


def test_patient_cross_access_to_diagnostic_order_forbidden():
    ctx = setup_clinical_encounter_for_diagnostics()

    order_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/diagnostic-orders",
        json={"items": [{"diagnostic_test_id": ctx["test_id"]}]},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    other_patient_token, _ = get_token_and_user("PATIENT")
    cross_res = client.get(
        f"/api/v1/diagnostic-orders/{order_id}",
        headers={"Authorization": f"Bearer {other_patient_token}"},
    )
    assert cross_res.status_code == 403
    assert cross_res.json()["error"]["code"] == "FORBIDDEN"
