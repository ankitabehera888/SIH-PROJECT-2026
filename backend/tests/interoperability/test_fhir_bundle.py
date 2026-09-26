from datetime import date, timedelta
import random
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_complete_patient_longitudinal_fhir_bundle_and_async_export():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Admin, Doctor, Facility, Patient
    admin_email = f"admin.bnd.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    doc_email = f"dr.bnd.{u_suffix}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_id = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    fac_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Fort Kochi Hospital {u_suffix}", "facility_code": f"FKH_{u_suffix}", "facility_type": "RURAL_HOSPITAL"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Aarav_{u_suffix}", "last_name": f"Pillai_{u_suffix}", "date_of_birth": "1990-05-18", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat_res.status_code == 201
    pat_id = pat_res.json()["id"]

    # Link ABHA ID (pure numeric digits)
    digits = f"{random.randint(100000000000, 999999999999)}"
    abha_val = f"14-{digits[:4]}-{digits[4:8]}-{digits[8:12]}"
    client.post(
        f"/api/v1/interoperability/patients/{pat_id}/identifiers",
        json={"system": "https://healthid.abdm.gov.in", "value": abha_val, "identifier_type": "ABHA_NUMBER"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )

    # Schedule Appointment & Encounter
    appt_id = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac_id,
            "appointment_date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Comprehensive Health Check",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    ).json()["id"]

    enc_res = client.post(
        "/api/v1/encounters",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac_id,
            "appointment_id": appt_id,
            "encounter_type": "OUTPATIENT",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert enc_res.status_code == 201
    enc_id = enc_res.json()["id"]

    # Record Vitals
    client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={"systolic_bp": 120, "diastolic_bp": 80, "heart_rate": 72, "temperature": 36.8},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )

    # 2. Query Complete Longitudinal FHIR Bundle
    bundle_res = client.get(
        f"/api/v1/fhir/patient/{pat_id}/bundle?bundle_type=collection",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert bundle_res.status_code == 200
    bundle = bundle_res.json()

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"
    assert bundle["total"] >= 4  # Patient, Encounter, Practitioner, Organization, Observations...
    assert len(bundle["entry"]) == bundle["total"]

    # Verify all entries have valid fullUrl and resourceType
    resource_types = set()
    for entry in bundle["entry"]:
        assert entry["fullUrl"].startswith("urn:uuid:")
        res = entry["resource"]
        assert "resourceType" in res
        resource_types.add(res["resourceType"])

    assert "Patient" in resource_types
    assert "Encounter" in resource_types
    assert "Observation" in resource_types

    # 3. Test Asynchronous Celery Bundle Export
    async_res = client.post(
        f"/api/v1/fhir/patient/{pat_id}/export-async",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert async_res.status_code == 202
    async_data = async_res.json()
    assert async_data["status"] == "ACCEPTED"
    assert "task_id" in async_data
