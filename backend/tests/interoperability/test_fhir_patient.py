import random
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fhir_patient_mapping_and_security():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Doctor & Patient
    doc_email = f"dr.fhir.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    pat_email = f"pat.fhir.{u_suffix}@hospital.org"
    pat_u_res = client.post("/api/v1/auth/register", json={"email": pat_email, "password": "SecurePassword123", "role": "PATIENT"})
    pat_tok = client.post("/api/v1/auth/login", json={"email": pat_email, "password": "SecurePassword123"}).json()["access_token"]

    first_name = f"Meera_{u_suffix}"
    last_name = f"Nair_{u_suffix}"
    phone_num = f"+919{random.randint(100000000, 999999999)}"

    pat_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": "1992-07-14",
            "gender": "FEMALE",
            "phone": phone_num,
            "email": pat_email,
            "address": "123 Green Avenue, Kochi, Kerala",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat_res.status_code == 201
    patient_id = pat_res.json()["id"]

    # Link patient record to patient user account
    client.patch(
        f"/api/v1/patients/{patient_id}",
        json={"user_id": pat_u_res.json()["id"]},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )

    # 2. Link ABHA Number (14 numeric digits)
    digits = f"{random.randint(100000000000, 999999999999)}"
    abha_val = f"14-{digits[:4]}-{digits[4:8]}-{digits[8:12]}"
    link_res = client.post(
        f"/api/v1/interoperability/patients/{patient_id}/identifiers",
        json={
            "system": "https://healthid.abdm.gov.in",
            "value": abha_val,
            "identifier_type": "ABHA_NUMBER",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert link_res.status_code == 201

    # 3. Query FHIR Patient resource as Doctor
    fhir_res = client.get(
        f"/api/v1/fhir/Patient/{patient_id}",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert fhir_res.status_code == 200
    data = fhir_res.json()

    assert data["resourceType"] == "Patient"
    assert data["id"] == patient_id
    assert data["gender"] == "female"
    assert data["birthDate"] == "1992-07-14"
    assert data["name"][0]["family"] == last_name
    assert data["name"][0]["given"] == [first_name]
    assert any(i["value"] == abha_val for i in data["identifier"])
    assert any(t["value"] == phone_num for t in data.get("telecom", []))

    # 4. Query FHIR Patient as Authorized Patient
    pat_fhir_res = client.get(
        f"/api/v1/fhir/Patient/{patient_id}",
        headers={"Authorization": f"Bearer {pat_tok}"},
    )
    assert pat_fhir_res.status_code == 200
    assert pat_fhir_res.json()["id"] == patient_id

    # 5. Security: Unauthorized Patient B cannot access Patient A's FHIR record
    unauth_email = f"unauth.{uuid.uuid4().hex[:6]}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": unauth_email, "password": "SecurePassword123", "role": "PATIENT"})
    unauth_tok = client.post("/api/v1/auth/login", json={"email": unauth_email, "password": "SecurePassword123"}).json()["access_token"]

    forbidden_res = client.get(
        f"/api/v1/fhir/Patient/{patient_id}",
        headers={"Authorization": f"Bearer {unauth_tok}"},
    )
    assert forbidden_res.status_code == 403
