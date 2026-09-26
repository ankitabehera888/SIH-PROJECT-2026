import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token(role: str) -> str:
    email = f"rbac.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
    password = "SecurePassword123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return login_res.json()["access_token"]

def test_unauthenticated_request_fails():
    """Verify that unauthenticated requests to analytics endpoints return 401."""
    response = client.get("/api/v1/analytics/dashboard/overview")
    assert response.status_code == 401

def test_patient_role_forbidden():
    """Verify that PATIENT role users cannot access population analytics (403)."""
    token = get_auth_token("PATIENT")
    response = client.get(
        "/api/v1/analytics/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

def test_doctor_role_allowed():
    """Verify DOCTOR role has access to operational analytics."""
    token = get_auth_token("DOCTOR")
    response = client.get(
        "/api/v1/analytics/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

def test_nurse_role_allowed():
    """Verify NURSE role has access to operational analytics."""
    token = get_auth_token("NURSE")
    response = client.get(
        "/api/v1/analytics/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

def test_admin_role_allowed():
    """Verify ADMIN role has full access to analytics."""
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
