from datetime import date, timedelta
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fhir_diagnostics_and_referral_service_requests():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Admin, Doctor, Facility A & B, Patient
    admin_email = f"admin.diag.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    doc_email = f"dr.diag.{u_suffix}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_id = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    fac1_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Kaloor PHC {u_suffix}", "facility_code": f"KLR_{u_suffix}", "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    fac2_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Ernakulam District Hospital {u_suffix}", "facility_code": f"EKM_{u_suffix}", "facility_type": "DISTRICT_HOSPITAL"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Deepak_{u_suffix}", "last_name": f"Menon_{u_suffix}", "date_of_birth": "1978-09-05", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat_res.status_code == 201
    pat_id = pat_res.json()["id"]

    appt_id = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac1_id,
            "appointment_date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "reason": "Routine Checkup",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    ).json()["id"]

    enc_res = client.post(
        "/api/v1/encounters",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac1_id,
            "appointment_id": appt_id,
            "encounter_type": "OUTPATIENT",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert enc_res.status_code == 201
    enc_id = enc_res.json()["id"]

    # 2. Create Diagnostic Test & Diagnostic Order
    test_res = client.post(
        "/api/v1/diagnostic-tests",
        json={"name": f"CBC_{u_suffix}", "code": f"CBC_{u_suffix}", "category": "LABORATORY"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    )
    test_id = test_res.json()["id"]

    order_res = client.post(
        f"/api/v1/encounters/{enc_id}/diagnostic-orders",
        json={"priority": "URGENT", "items": [{"diagnostic_test_id": test_id}]},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert order_res.status_code == 201
    order_id = order_res.json()["id"]
    item_id = order_res.json()["items"][0]["id"]

    # Record Diagnostic Result
    res_post = client.post(
        f"/api/v1/diagnostic-order-items/{item_id}/result",
        json={
            "result_value": "14.2",
            "unit": "g/dL",
            "reference_range": "13.5 - 17.5 g/dL",
            "abnormal_flag": False,
            "result_status": "FINAL",
            "notes": "Hemoglobin within normal physiological parameters",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert res_post.status_code == 201

    # 3. Create Clinical Referral
    ref_res = client.post(
        f"/api/v1/encounters/{enc_id}/referral",
        json={
            "receiving_facility_id": fac2_id,
            "referral_type": "SPECIALIST",
            "priority": "ROUTINE",
            "reason": "Cardiology evaluation and echocardiogram",
            "clinical_summary": "Mild exertional dyspnea, normal CBC",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert ref_res.status_code == 201
    ref_id = ref_res.json()["id"]

    # 4. Verify FHIR ServiceRequest for Diagnostic Order
    diag_sr = client.get(
        f"/api/v1/fhir/ServiceRequest/{order_id}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert diag_sr.status_code == 200
    assert diag_sr.json()["resourceType"] == "ServiceRequest"
    assert diag_sr.json()["id"] == order_id
    assert diag_sr.json()["priority"] == "urgent"

    # 5. Verify FHIR ServiceRequest for Referral
    ref_sr = client.get(
        f"/api/v1/fhir/ServiceRequest/{ref_id}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert ref_sr.status_code == 200
    assert ref_sr.json()["resourceType"] == "ServiceRequest"
    assert ref_sr.json()["id"] == ref_id
    assert ref_sr.json()["performer"][0]["reference"] == f"Organization/{fac2_id}"

    # 6. Verify FHIR DiagnosticReport
    dr_res = client.get(
        f"/api/v1/fhir/DiagnosticReport/{order_id}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert dr_res.status_code == 200
    dr_data = dr_res.json()
    assert dr_data["resourceType"] == "DiagnosticReport"
    assert dr_data["id"] == order_id
    assert dr_data["status"] == "final"
    assert len(dr_data.get("result", [])) >= 1
