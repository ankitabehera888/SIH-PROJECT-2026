import uuid
from datetime import timedelta
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def test_user_registration_success():
    email = f"doctor.{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "StrongPassword123",
        "role": "DOCTOR",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email.lower()
    assert data["role"] == "DOCTOR"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    # Ensure password or password_hash is NEVER exposed in the API response
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_registration_conflict():
    email = f"duplicate.{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "Password123",
        "role": "PATIENT",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt second registration with same email
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"


def test_password_stored_as_argon2_hash_not_plaintext():
    email = f"security.{uuid.uuid4().hex[:8]}@example.com"
    raw_password = "SuperSecretPassword123"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": raw_password, "role": "PATIENT"},
    )
    assert reg_res.status_code == 201

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        assert user.password_hash != raw_password
        assert user.password_hash.startswith("$argon2id$")
    finally:
        db.close()


def test_login_success_and_token_generation():
    email = f"login.{uuid.uuid4().hex[:8]}@example.com"
    password = "MySecurePassword123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": "DOCTOR"},
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_failure_wrong_password():
    email = f"wrongpass.{uuid.uuid4().hex[:8]}@example.com"
    password = "CorrectPassword123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": "NURSE"},
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword123"},
    )
    assert login_res.status_code == 401
    assert login_res.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_failure_nonexistent_user():
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": f"nobody.{uuid.uuid4().hex[:8]}@example.com", "password": "Password123"},
    )
    assert login_res.status_code == 401
    assert login_res.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_me_with_valid_token():
    email = f"me.{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": "PATIENT"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]

    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email
    assert me_data["role"] == "PATIENT"


def test_get_me_missing_token_returns_401():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_me_invalid_token_returns_401():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_me_expired_token_returns_401():
    expired_token = create_access_token(
        user_id=1,
        role="PATIENT",
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert "expired" in response.json()["error"]["message"].lower()


def test_refresh_token_lifecycle():
    email = f"refresh.{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": "ADMIN"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    refresh_token = login_res.json()["refresh_token"]

    ref_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()
    assert "refresh_token" in ref_res.json()


def test_inactive_user_rejected():
    email = f"inactive.{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": "PATIENT"},
    )
    user_id = reg_res.json()["id"]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        user.is_active = False
        db.commit()
    finally:
        db.close()

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 401
    assert "disabled" in login_res.json()["error"]["message"].lower()


def test_rbac_doctor_and_patient_access_control():
    doc_email = f"doctor.{uuid.uuid4().hex[:8]}@example.com"
    pat_email = f"patient.{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"

    # Register Doctor
    client.post(
        "/api/v1/auth/register",
        json={"email": doc_email, "password": password, "role": "DOCTOR"},
    )
    doc_login = client.post(
        "/api/v1/auth/login",
        json={"email": doc_email, "password": password},
    )
    doc_token = doc_login.json()["access_token"]

    # Register Patient
    client.post(
        "/api/v1/auth/register",
        json={"email": pat_email, "password": password, "role": "PATIENT"},
    )
    pat_login = client.post(
        "/api/v1/auth/login",
        json={"email": pat_email, "password": password},
    )
    pat_token = pat_login.json()["access_token"]

    # 1. Doctor accesses doctor-only -> 200
    doc_on_doc = client.get(
        "/api/v1/test/doctor-only",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert doc_on_doc.status_code == 200

    # 2. Patient accesses doctor-only -> 403 Forbidden
    pat_on_doc = client.get(
        "/api/v1/test/doctor-only",
        headers={"Authorization": f"Bearer {pat_token}"},
    )
    assert pat_on_doc.status_code == 403
    assert pat_on_doc.json()["error"]["code"] == "FORBIDDEN"

    # 3. Patient accesses patient-only -> 200
    pat_on_pat = client.get(
        "/api/v1/test/patient-only",
        headers={"Authorization": f"Bearer {pat_token}"},
    )
    assert pat_on_pat.status_code == 200

    # 4. Doctor accesses patient-only -> 403 Forbidden
    doc_on_pat = client.get(
        "/api/v1/test/patient-only",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert doc_on_pat.status_code == 403
    assert doc_on_pat.json()["error"]["code"] == "FORBIDDEN"
