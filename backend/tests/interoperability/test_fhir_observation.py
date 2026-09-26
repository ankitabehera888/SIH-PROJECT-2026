from datetime import date, timedelta
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fhir_observation_vitals_blood_pressure_components():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Doctor, Patient, Facility, Encounter
    admin_email = f"admin.obs.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    doc_email = f"dr.obs.{u_suffix}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_id = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    fac_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Aluva PHC {u_suffix}", "facility_code": f"ALV_{u_suffix}", "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Rohan_{u_suffix}", "last_name": f"Das_{u_suffix}", "date_of_birth": "1988-04-12", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat_res.status_code == 201
    pat_id = pat_res.json()["id"]

    appt_id = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": pat_id,
            "provider_id": doc_id,
            "facility_id": fac_id,
            "appointment_date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "14:00:00",
            "end_time": "14:30:00",
            "reason": "Vitals Check",
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

    # 2. Record Vitals with Blood Pressure, Heart Rate, Temp, SpO2
    vital_res = client.post(
        f"/api/v1/encounters/{enc_id}/vitals",
        json={
            "systolic_bp": 128,
            "diastolic_bp": 84,
            "heart_rate": 76,
            "temperature": 37.1,
            "oxygen_saturation": 98.5,
            "respiratory_rate": 16,
            "weight": 72.5,
            "height": 175.0,
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert vital_res.status_code == 201
    vital_id = vital_res.json()["id"]

    # 3. Query FHIR Observation for Blood Pressure Panel
    bp_obs = client.get(
        f"/api/v1/fhir/Observation/{vital_id}-bp",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert bp_obs.status_code == 200
    bp_data = bp_obs.json()

    assert bp_data["resourceType"] == "Observation"
    assert bp_data["status"] == "final"
    assert bp_data["code"]["coding"][0]["code"] == "85354-9"  # LOINC Blood pressure panel
    assert len(bp_data["component"]) == 2

    # Verify systolic component
    systolic = next(c for c in bp_data["component"] if c["code"]["coding"][0]["code"] == "8480-6")
    assert systolic["valueQuantity"]["value"] == 128
    assert systolic["valueQuantity"]["unit"] == "mmHg"

    # Verify diastolic component
    diastolic = next(c for c in bp_data["component"] if c["code"]["coding"][0]["code"] == "8462-4")
    assert diastolic["valueQuantity"]["value"] == 84
    assert diastolic["valueQuantity"]["unit"] == "mmHg"

    # 4. Query FHIR Observation for Heart Rate
    hr_obs = client.get(
        f"/api/v1/fhir/Observation/{vital_id}-hr",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert hr_obs.status_code == 200
    assert hr_obs.json()["code"]["coding"][0]["code"] == "8867-4"
    assert hr_obs.json()["valueQuantity"]["value"] == 76
