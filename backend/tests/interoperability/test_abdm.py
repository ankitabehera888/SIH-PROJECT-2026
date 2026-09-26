import random
import uuid
from fastapi.testclient import TestClient
from app.interoperability.abdm.identity import ABDMIdentityService
from app.main import app

client = TestClient(app)


def test_abdm_identity_validation_helpers():
    # Valid 14-digit ABHA
    assert ABDMIdentityService.validate_abha_number("14-1234-5678-9012") is True
    assert ABDMIdentityService.validate_abha_number("14123456789012") is True
    # Invalid length or chars
    assert ABDMIdentityService.validate_abha_number("14-1234-5678") is False
    assert ABDMIdentityService.validate_abha_number("14-1234-ABCD-9012") is False

    # Valid ABHA addresses
    assert ABDMIdentityService.validate_abha_address("anita.sharma@abdm") is True
    assert ABDMIdentityService.validate_abha_address("user123_test@sbx") is True
    # Invalid addresses
    assert ABDMIdentityService.validate_abha_address("invalid@gmail.com") is False
    assert ABDMIdentityService.validate_abha_address("ab@abdm") is False  # Too short


def test_abdm_linkage_duplicate_prevention_and_consent_lifecycle():
    u_suffix = uuid.uuid4().hex[:6]
    # 1. Setup Doctor & 2 Patients
    doc_email = f"dr.abdm.{u_suffix}@hospital.org"
    client.post("/api/v1/auth/register", json={"email": doc_email, "password": "SecurePassword123", "role": "DOCTOR"})
    doc_tok = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "SecurePassword123"}).json()["access_token"]

    pat1_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Vikram_{u_suffix}", "last_name": f"Seth_{u_suffix}", "date_of_birth": "1985-08-10", "gender": "MALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat1_res.status_code == 201
    pat1_id = pat1_res.json()["id"]

    pat2_res = client.post(
        "/api/v1/patients",
        json={"first_name": f"Kavita_{u_suffix}", "last_name": f"Roy_{u_suffix}", "date_of_birth": "1991-03-22", "gender": "FEMALE"},
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert pat2_res.status_code == 201
    pat2_id = pat2_res.json()["id"]

    # 2. Link ABHA to Patient 1 (pure numeric digits)
    digits = f"{random.randint(100000000000, 999999999999)}"
    abha_num = f"14-{digits[:4]}-{digits[4:8]}-{digits[8:12]}"
    link_res = client.post(
        f"/api/v1/interoperability/patients/{pat1_id}/identifiers",
        json={
            "system": "https://healthid.abdm.gov.in",
            "value": abha_num,
            "identifier_type": "ABHA_NUMBER",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert link_res.status_code == 201
    assert link_res.json()["value"] == abha_num

    # 3. Duplicate Prevention: Attempting to link same ABHA to Patient 2 must fail with 409 Conflict
    dup_res = client.post(
        f"/api/v1/interoperability/patients/{pat2_id}/identifiers",
        json={
            "system": "https://healthid.abdm.gov.in",
            "value": abha_num,
            "identifier_type": "ABHA_NUMBER",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert dup_res.status_code == 409

    # 4. Consent Lifecycle
    consent_res = client.post(
        "/api/v1/interoperability/consents",
        json={
            "patient_id": pat1_id,
            "purpose": "CARE_MANAGEMENT",
            "scope": "ALL",
            "notes": "Patient authorized complete longitudinal exchange for cardiology consultation",
        },
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert consent_res.status_code == 201
    consent_id = consent_res.json()["id"]
    assert consent_res.json()["status"] == "GRANTED"

    # Revoke Consent
    revoke_res = client.post(
        f"/api/v1/interoperability/consents/{consent_id}/revoke",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert revoke_res.status_code == 200
    assert revoke_res.json()["status"] == "REVOKED"
    assert revoke_res.json()["revoked_at"] is not None

    # 5. ABDM Gateway Verification Simulation
    verify_res = client.get(
        f"/api/v1/interoperability/abdm/verify-abha/14-1234-5678-9012",
        headers={"Authorization": f"Bearer {doc_tok}"},
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "VERIFIED"
