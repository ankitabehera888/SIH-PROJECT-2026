from datetime import date, timedelta
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fhir_medication_and_medication_request():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Doctor, Patient, Facility, Encounter
    admin_email = f"admin.med.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": admin_email, "password": "SecurePassword123", "role": "ADMIN"})
    admin_tok = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "SecurePassword123"}).json()["access_token"]

    doc_email = f"dr.med.{u_suffix}@hospital.org"
    doc_res = client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_id = doc_res.json()["id"]
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    fac_id = client.post(
        "/api/v1/facilities",
        json={"name": f"Kakkanad Clinic {u_suffix}", "facility_code": f"KKN_{u_suffix}", "facility_type": "PHC"},
        headers={"Authorization": f"Bearer {admin_tok}"},
    ).json()["id"]

    pat_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Pooja_{u_suffix}", "last_name": f"Iyer_{u_suffix}", "date_of_birth": "1993-02-10", "gender": "FEMALE"},
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
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Infection consultation",
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

    # 2. Create Medication Catalog Entry
    med_res = client.post(
        "/api/v1/medications",
        json={
            "name": f"Amoxicillin_{u_suffix}",
            "generic_name": "Amoxicillin Trihydrate",
            "dosage_form": "Capsule",
            "strength": "500mg",
        },
        headers={"Authorization": f"Bearer {admin_tok}"},
    )
    med_id = med_res.json()["id"]

    # 3. Create Prescription with item
    rx_res = client.post(
        f"/api/v1/encounters/{enc_id}/prescriptions",
        json={
            "items": [
                {
                    "medication_id": med_id,
                    "dosage": "500mg",
                    "frequency": "THRICE_DAILY",
                    "duration": 5,
                    "duration_unit": "DAYS",
                    "route": "ORAL",
                    "quantity": 15,
                    "instructions": "Take 1 capsule 3 times daily after meals",
                }
            ]
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert rx_res.status_code == 201
    item_id = rx_res.json()["items"][0]["id"]

    # 4. Test FHIR Medication
    fhir_med = client.get(
        f"/api/v1/fhir/Medication/{med_id}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert fhir_med.status_code == 200
    assert fhir_med.json()["resourceType"] == "Medication"
    assert fhir_med.json()["id"] == med_id

    # 5. Test FHIR MedicationRequest
    fhir_rx = client.get(
        f"/api/v1/fhir/MedicationRequest/{item_id}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert fhir_rx.status_code == 200
    rx_data = fhir_rx.json()
    assert rx_data["resourceType"] == "MedicationRequest"
    assert rx_data["id"] == item_id
    assert rx_data["status"] == "active"
    assert rx_data["intent"] == "order"
    assert rx_data["subject"]["reference"] == f"Patient/{pat_id}"
    assert rx_data["encounter"]["reference"] == f"Encounter/{enc_id}"
    assert rx_data["dosageInstruction"][0]["text"] == "Take 1 capsule 3 times daily after meals"
    assert rx_data["dispenseRequest"]["quantity"]["value"] == 15
