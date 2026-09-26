import uuid
from datetime import date, time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token_and_user(role: str = "DOCTOR"):
    email = f"ref.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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


def setup_facilities_and_encounter():
    admin_token, _ = get_token_and_user("ADMIN")
    doc_token, doc_id = get_token_and_user("DOCTOR")

    # 1. Referring Facility (PHC)
    phc_code = f"PHC-{uuid.uuid4().hex[:5].upper()}"
    phc_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Rural PHC {phc_code}", "facility_code": phc_code, "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    phc_id = phc_res.json()["id"]

    # 2. Receiving Facility (District Hospital)
    dh_code = f"DH-{uuid.uuid4().hex[:5].upper()}"
    dh_res = client.post(
        "/api/v1/facilities",
        json={"name": f"District Hospital {dh_code}", "facility_code": dh_code, "facility_type": "DISTRICT_HOSPITAL"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    dh_id = dh_res.json()["id"]

    # 3. Patient
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"RefPat{uuid.uuid4().hex[:4]}",
            "last_name": f"Test{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1994-03-21",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    patient_id = pat_res.json()["id"]

    # 4. Appointment & Encounter at PHC
    today_str = date.today().isoformat()
    hour = (uuid.uuid4().int % 12) + 8
    app_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": patient_id,
            "provider_id": doc_id,
            "facility_id": phc_id,
            "appointment_date": today_str,
            "start_time": f"{hour:02d}:00:00",
            "end_time": f"{hour:02d}:30:00",
            "reason": "Chest discomfort and ECG changes",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    appointment_id = app_res.json()["id"]

    enc_res = client.post(
        f"/api/v1/appointments/{appointment_id}/encounter",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    encounter_id = enc_res.json()["id"]

    return {
        "admin_token": admin_token,
        "doc_token": doc_token,
        "doc_id": doc_id,
        "phc_id": phc_id,
        "dh_id": dh_id,
        "patient_id": patient_id,
        "encounter_id": encounter_id,
    }


def test_create_referral_from_encounter_success():
    ctx = setup_facilities_and_encounter()

    payload = {
        "receiving_facility_id": ctx["dh_id"],
        "referral_type": "SPECIALIST",
        "priority": "URGENT",
        "requested_specialty": "CARDIOLOGY",
        "reason": "Abnormal ST segment on ECG, needs echocardiogram and specialist evaluation",
        "clinical_summary": "Patient presented with angina symptoms.",
    }
    ref_res = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json=payload,
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert ref_res.status_code == 201
    ref = ref_res.json()
    assert ref["status"] == "SENT"
    assert ref["patient_id"] == ctx["patient_id"]
    assert ref["encounter_id"] == ctx["encounter_id"]
    assert ref["referring_facility_id"] == ctx["phc_id"]
    assert ref["receiving_facility_id"] == ctx["dh_id"]
    assert ref["priority"] == "URGENT"
    assert ref["requested_specialty"] == "CARDIOLOGY"
    assert "id" in ref


def test_referral_to_same_facility_rejected():
    ctx = setup_facilities_and_encounter()

    # Attempting to refer to the same PHC where encounter took place
    payload = {
        "receiving_facility_id": ctx["phc_id"],
        "reason": "Invalid self referral",
    }
    ref_res = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json=payload,
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert ref_res.status_code == 400
    assert ref_res.json()["error"]["code"] == "REFERRAL_FACILITY_IDENTICAL"


def test_facility_incoming_and_outgoing_queues():
    ctx = setup_facilities_and_encounter()

    # Create referral from PHC to DH
    client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json={"receiving_facility_id": ctx["dh_id"], "reason": "Surgical consult"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )

    # 1. Outgoing queue from PHC
    out_res = client.get(
        f"/api/v1/facilities/{ctx['phc_id']}/referrals/outgoing",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert out_res.status_code == 200
    assert out_res.json()["total"] >= 1
    assert any(r["receiving_facility_id"] == ctx["dh_id"] for r in out_res.json()["items"])

    # 2. Incoming queue at DH
    in_res = client.get(
        f"/api/v1/facilities/{ctx['dh_id']}/referrals/incoming",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert in_res.status_code == 200
    assert in_res.json()["total"] >= 1
    assert any(r["referring_facility_id"] == ctx["phc_id"] for r in in_res.json()["items"])


def test_full_referral_lifecycle_accept_schedule_complete():
    ctx = setup_facilities_and_encounter()

    # 1. Create referral (SENT)
    ref = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json={"receiving_facility_id": ctx["dh_id"], "reason": "Cardiology consult"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()
    ref_id = ref["id"]

    # 2. Accept (SENT -> ACCEPTED)
    accept_res = client.post(
        f"/api/v1/referrals/{ref_id}/accept",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "ACCEPTED"
    assert accept_res.json()["accepted_at"] is not None

    # 3. Schedule (ACCEPTED -> SCHEDULED)
    sched_res = client.post(
        f"/api/v1/referrals/{ref_id}/schedule",
        json={"scheduled_date": "2026-09-15", "scheduled_time": "10:30:00"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert sched_res.status_code == 200
    assert sched_res.json()["status"] == "SCHEDULED"
    assert sched_res.json()["scheduled_date"] == "2026-09-15"

    # 4. Complete with outcome (SCHEDULED -> COMPLETED)
    comp_res = client.post(
        f"/api/v1/referrals/{ref_id}/complete",
        json={
            "outcome_status": "COMPLETED",
            "outcome_notes": "Coronary angiogram performed. Medical therapy prescribed.",
            "follow_up_required": True,
            "follow_up_date": "2026-10-15",
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert comp_res.status_code == 200
    comp = comp_res.json()
    assert comp["status"] == "COMPLETED"
    assert comp["outcome_status"] == "COMPLETED"
    assert comp["completed_at"] is not None
    assert comp["follow_up_required"] is True


def test_reject_referral_with_reason():
    ctx = setup_facilities_and_encounter()

    # Create referral
    ref_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json={"receiving_facility_id": ctx["dh_id"], "reason": "Dermatology subspecialty"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    # Reject
    rej_res = client.post(
        f"/api/v1/referrals/{ref_id}/reject",
        json={"reason": "Dermatology subspecialty currently unavailable at District Hospital"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert rej_res.status_code == 200
    rej = rej_res.json()
    assert rej["status"] == "REJECTED"
    assert "unavailable" in rej["rejection_reason"]


def test_cancel_referral_with_reason():
    ctx = setup_facilities_and_encounter()

    # Create referral
    ref_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json={"receiving_facility_id": ctx["dh_id"], "reason": "Patient assessment"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    # Cancel
    canc_res = client.post(
        f"/api/v1/referrals/{ref_id}/cancel",
        json={"reason": "Patient symptoms resolved spontaneously"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert canc_res.status_code == 200
    assert canc_res.json()["status"] == "CANCELLED"
    assert canc_res.json()["cancellation_reason"] == "Patient symptoms resolved spontaneously"


def test_invalid_state_transitions_rejected():
    ctx = setup_facilities_and_encounter()

    # Create referral (SENT)
    ref_id = client.post(
        f"/api/v1/encounters/{ctx['encounter_id']}/referral",
        json={"receiving_facility_id": ctx["dh_id"], "reason": "State transition test"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    # Invalid: Try to schedule directly without accepting (SENT -> SCHEDULED)
    bad_sched = client.post(
        f"/api/v1/referrals/{ref_id}/schedule",
        json={"scheduled_date": "2026-09-15", "scheduled_time": "10:30:00"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert bad_sched.status_code == 400
    assert bad_sched.json()["error"]["code"] == "INVALID_REFERRAL_TRANSITION"

    # Reject referral (SENT -> REJECTED)
    client.post(
        f"/api/v1/referrals/{ref_id}/reject",
        json={"reason": "Specialty unavailable"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )

    # Invalid: Try to complete a REJECTED referral
    bad_comp = client.post(
        f"/api/v1/referrals/{ref_id}/complete",
        json={"outcome_status": "COMPLETED", "outcome_notes": "Impossible transition"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    assert bad_comp.status_code == 400
    assert bad_comp.json()["error"]["code"] == "INVALID_REFERRAL_TRANSITION"


def test_patient_resource_authorization_cross_access_forbidden():
    ctx = setup_facilities_and_encounter()

    # Create two patient accounts
    p1_token, p1_uid = get_token_and_user("PATIENT")
    p2_token, p2_uid = get_token_and_user("PATIENT")

    # Link Patient 1 entity to p1_uid
    p1_entity_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": f"P1_{uuid.uuid4().hex[:4]}",
            "last_name": f"Self_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "1992-01-01",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    )
    p1_entity_id = p1_entity_res.json()["id"]

    # Manually associate patient entity with user 1 in DB or create encounter for Patient 1
    today_str = date.today().isoformat()
    hour = (uuid.uuid4().int % 12) + 8
    a_id = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": p1_entity_id,
            "provider_id": ctx["doc_id"],
            "facility_id": ctx["phc_id"],
            "appointment_date": today_str,
            "start_time": f"{hour:02d}:00:00",
            "end_time": f"{hour:02d}:30:00",
        },
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    enc_id = client.post(
        f"/api/v1/appointments/{a_id}/encounter",
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    ref_id = client.post(
        f"/api/v1/encounters/{enc_id}/referral",
        json={"receiving_facility_id": ctx["dh_id"], "reason": "Specialist consult"},
        headers={"Authorization": f"Bearer {ctx['doc_token']}"},
    ).json()["id"]

    # Patient 2 attempts to view Patient 1's referral -> 403 Forbidden
    cross_res = client.get(
        f"/api/v1/referrals/{ref_id}",
        headers={"Authorization": f"Bearer {p2_token}"},
    )
    assert cross_res.status_code == 403
    assert cross_res.json()["error"]["code"] == "FORBIDDEN"
