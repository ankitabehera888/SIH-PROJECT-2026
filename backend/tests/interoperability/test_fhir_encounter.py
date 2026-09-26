from datetime import date, timedelta
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fhir_encounter_practitioner_organization_appointment():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Admin, Doctor, Facility, Patient
    admin_email = f"admin.enc.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    doc_email = f"dr.enc.{u_suffix}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_id = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    fac_res = client.post(
        "/api/v1/facilities",
        json={"name": f"Hospital {u_suffix}", "facility_code": f"KDH_{u_suffix}", "facility_type": "DISTRICT_HOSPITAL"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    )
    fac_id = fac_res.json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Suresh_{u_suffix}", "last_name": f"Kumar_{u_suffix}", "date_of_birth": "1985-11-20", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat_res.status_code == 201
    pat_id = pat_res.json()["id"]

    # 2. Appointment
    appt_res = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac_id,
            "appointment_date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "11:00:00",
            "end_time": "11:30:00",
            "reason": "Cardiology Consultation",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert appt_res.status_code == 201
    appt_id = appt_res.json()["id"]

    # 3. Encounter (Include required patient_id, provider_id, facility_id)
    enc_res = client.post(
        "/api/v1/encounters",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac_id,
            "appointment_id": appt_id,
            "encounter_type": "OUTPATIENT",
            "chief_complaint": "Persistent chest tightness on exertion",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert enc_res.status_code == 201
    enc_id = enc_res.json()["id"]

    # Test FHIR Practitioner
    doc_fhir = client.get(f"/api/v1/fhir/Practitioner/{doc_id}", headers={"Authorization": f"Bearer {doc_tok}"})
    assert doc_fhir.status_code == 200
    assert doc_fhir.json()["resourceType"] == "Practitioner"
    assert doc_fhir.json()["id"] == str(doc_id)

    # Test FHIR Organization
    org_fhir = client.get(f"/api/v1/fhir/Organization/{fac_id}", headers={"Authorization": f"Bearer {doc_tok}"})
    assert org_fhir.status_code == 200
    assert org_fhir.json()["resourceType"] == "Organization"
    assert org_fhir.json()["id"] == fac_id

    # Test FHIR Appointment
    appt_fhir = client.get(f"/api/v1/fhir/Appointment/{appt_id}", headers={"Authorization": f"Bearer {doc_tok}"})
    assert appt_fhir.status_code == 200
    assert appt_fhir.json()["resourceType"] == "Appointment"
    assert appt_fhir.json()["id"] == appt_id
    assert any(p["actor"]["reference"] == f"Patient/{pat_id}" for p in appt_fhir.json()["participant"])

    # Test FHIR Encounter
    enc_fhir = client.get(f"/api/v1/fhir/Encounter/{enc_id}", headers={"Authorization": f"Bearer {doc_tok}"})
    assert enc_fhir.status_code == 200
    enc_data = enc_fhir.json()
    assert enc_data["resourceType"] == "Encounter"
    assert enc_data["id"] == enc_id
    assert enc_data["subject"]["reference"] == f"Patient/{pat_id}"
    assert enc_data["serviceProvider"]["reference"] == f"Organization/{fac_id}"
    assert enc_data["reasonCode"][0]["text"] == "Persistent chest tightness on exertion"
