import uuid
from datetime import date, datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"rec.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_complete_patient_history():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")
    pat_token, pat_user_id = get_token_and_user("PATIENT")

    # 1. Primary facility & Receiving facility
    code1 = f"PHC-{uuid.uuid4().hex[:4].upper()}"
    code2 = f"DH-{uuid.uuid4().hex[:4].upper()}"
    f1_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Rural PHC {code1}", "facility_code": code1, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()["id"]
    f2_id = client.post(
        "/api/v1/facilities",
        json={"name": f"District Hospital {code2}", "facility_code": code2, "facility_type": "DISTRICT_HOSPITAL"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()["id"]

    # 2. Patient linked to user
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "user_id": pat_user_id,
            "first_name": f"Ravi_{uuid.uuid4().hex[:4]}",
            "last_name": f"Patel_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1985-05-15",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    patient_id = pat_res.json()["id"]

    # 3. Appointment & Encounter
    today_str = date.today().isoformat()
    hour = (uuid.uuid4().int % 10) + 8
    app_id = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient_id,
            "provider_id": doc_id,
            "facility_id": f1_id,
            "appointment_date": today_str,
            "start_time": f"{hour:02d}:00:00",
            "end_time": f"{hour:02d}:30:00",
            "reason": "Chest pain and hypertension",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    enc_id = client.post(
        f"/api/v1/appointments/{app_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    # 4. Record Vitals
    client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={
            "temperature_c": 37.2,
            "heart_rate": 84,
            "respiratory_rate": 18,
            "systolic_bp": 140,
            "diastolic_bp": 90,
            "spo2": 97,
            "weight_kg": 72.5,
            "height_cm": 175.0,
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # 5. Medication & Prescription
    med_id = client.post(
        "/api/v1/medications",
        json={
            "name": f"Amlodipine {uuid.uuid4().hex[:4]}",
            "generic_name": "Amlodipine Besylate",
            "strength": "5 mg",
            "dosage_form": "TABLET",
            "route": "ORAL",
            "unit": "mg",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    client.post(
        f"/api/v1/encounters/{enc_id}/prescriptions",
        json={
            "items": [
                {
                    "medication_id": med_id,
                    "dosage": "5 mg (1 tablet)",
                    "frequency": "ONCE_DAILY",
                    "duration": 30,
                    "duration_unit": "DAYS",
                    "route": "ORAL",
                    "quantity": 30,
                    "instructions": "Take every morning",
                }
            ],
            "notes": "Anti-hypertensive therapy",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # 6. Diagnostic Test & Order with Result
    test_code = f"ECG_{uuid.uuid4().hex[:4].upper()}"
    test_id = client.post(
        "/api/v1/diagnostic-tests",
        json={
            "code": test_code,
            "name": "12-Lead Electrocardiogram",
            "category": "CARDIOLOGY",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()["id"]

    order = client.post(
        f"/api/v1/encounters/{enc_id}/diagnostic-orders",
        json={
            "items": [{"diagnostic_test_id": test_id, "notes": "Rule out acute coronary event"}],
            "priority": "URGENT",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    ).json()
    order_item_id = order["items"][0]["id"]

    client.post(
        f"/api/v1/diagnostic-order-items/{order_item_id}/result",
        json={
            "result_value": "Sinus rhythm with LVH criteria",
            "unit": None,
            "reference_range": "Normal Sinus Rhythm",
            "abnormal_flag": True,
            "notes": "Cardiology referral advised",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    # 7. Care Transfer Referral
    client.post(
        f"/api/v1/encounters/{enc_id}/referral",
        json={
            "receiving_facility_id": f2_id,
            "referral_type": "SPECIALIST",
            "priority": "URGENT",
            "reason": "Cardiology specialist consult for LVH",
            "requested_specialty": "CARDIOLOGY",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )

    return {
        "admin_token": admin_token,
        "doc_token": doc_token,
        "pat_token": pat_token,
        "patient_id": patient_id,
        "encounter_id": enc_id,
        "appointment_id": app_id,
    }


def test_patient_record_empty_history():
    doc_token, _ = get_token_and_user("DOCTOR")
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"Empty_{uuid.uuid4().hex[:4]}",
            "last_name": f"Patient_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "2000-01-01",
            "gender": "OTHER",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    patient_id = pat_res.json()["id"]

    res = client.get(
        f"/api/v1/patients/{patient_id}/record",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["patient"]["id"] == patient_id
    assert data["summary"]["total_encounters"] == 0
    assert data["summary"]["total_prescriptions"] == 0
    assert data["summary"]["total_diagnostic_orders"] == 0
    assert data["summary"]["total_referrals"] == 0
    assert data["summary"]["total_appointments"] == 0
    assert data["timeline"] == []
    assert data["encounters"] == []


def test_patient_record_full_assembled_history():
    ctx = setup_complete_patient_history()

    res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/record",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res.status_code == 200
    rec = res.json()

    # Check patient demographics
    assert rec["patient"]["id"] == ctx["patient_id"]

    # Check summaries
    summary = rec["summary"]
    assert summary["total_encounters"] >= 1
    assert summary["total_vitals_recorded"] >= 1
    assert summary["total_prescriptions"] >= 1
    assert summary["total_diagnostic_orders"] >= 1
    assert summary["total_referrals"] >= 1
    assert summary["total_appointments"] >= 1
    assert summary["last_encounter_at"] is not None

    # Check collections
    assert len(rec["encounters"]) >= 1
    assert len(rec["prescriptions"]) >= 1
    assert len(rec["diagnostic_orders"]) >= 1
    assert len(rec["referrals"]) >= 1
    assert len(rec["appointments"]) >= 1
    assert len(rec["timeline"]) >= 5


def test_timeline_chronological_ordering():
    ctx = setup_complete_patient_history()

    res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res.status_code == 200
    timeline = res.json()["items"]
    assert len(timeline) >= 5

    # Verify descending chronological ordering (newest first)
    for i in range(len(timeline) - 1):
        d1 = datetime.fromisoformat(timeline[i]["event_date"].replace("Z", "+00:00"))
        d2 = datetime.fromisoformat(timeline[i + 1]["event_date"].replace("Z", "+00:00"))
        assert d1 >= d2


def test_timeline_event_type_filtering():
    ctx = setup_complete_patient_history()

    # 1. Filter by ENCOUNTER
    res_enc = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline?event_type=ENCOUNTER",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res_enc.status_code == 200
    assert len(res_enc.json()["items"]) >= 1
    assert all(e["event_type"] == "ENCOUNTER" for e in res_enc.json()["items"])

    # 2. Filter by PRESCRIPTION
    res_rx = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline?event_type=PRESCRIPTION",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res_rx.status_code == 200
    assert len(res_rx.json()["items"]) >= 1
    assert all(e["event_type"] == "PRESCRIPTION" for e in res_rx.json()["items"])

    # 3. Filter by DIAGNOSTIC_RESULT
    res_res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline?event_type=DIAGNOSTIC_RESULT",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res_res.status_code == 200
    assert len(res_res.json()["items"]) >= 1
    assert all(e["event_type"] == "DIAGNOSTIC_RESULT" for e in res_res.json()["items"])


def test_timeline_date_range_filtering():
    ctx = setup_complete_patient_history()

    # Past date range should return 0 events
    past_from = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
    past_to = (datetime.now(timezone.utc) - timedelta(days=300)).isoformat()

    res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline?from_date={past_from}&to_date={past_to}",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert res.status_code == 200
    assert res.json()["total"] == 0
    assert len(res.json()["items"]) == 0


def test_timeline_pagination():
    ctx = setup_complete_patient_history()

    p1 = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline?page=1&page_size=2",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()
    assert len(p1["items"]) == 2
    assert p1["total"] >= 5
    assert p1["page"] == 1

    p2 = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline?page=2&page_size=2",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()
    assert len(p2["items"]) == 2
    assert p2["page"] == 2
    assert p1["items"][0]["event_id"] != p2["items"][0]["event_id"]


def test_patient_can_access_own_longitudinal_record():
    ctx = setup_complete_patient_history()

    res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/record",
        headers={"Authorization": f"Bearer {ctx['pat_token']}"},
    )
    assert res.status_code == 200
    assert res.json()["patient"]["id"] == ctx["patient_id"]


def test_patient_cannot_access_another_patient_record():
    ctx = setup_complete_patient_history()

    # Create second unrelated patient
    other_token, _ = get_token_and_user("PATIENT")

    res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/record",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"

    timeline_res = client.get(
        f"/api/v1/patients/{ctx['patient_id']}/timeline",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert timeline_res.status_code == 403
    assert timeline_res.json()["error"]["code"] == "FORBIDDEN"


def test_nonexistent_patient_returns_404():
    doc_token, _ = get_token_and_user("DOCTOR")
    fake_id = uuid.uuid4()
    res = client.get(
        f"/api/v1/patients/{fake_id}/record",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"
