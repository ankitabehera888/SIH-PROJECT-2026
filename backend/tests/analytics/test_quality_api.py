import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token(role: str = "ADMIN") -> str:
    email = f"quality.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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

def test_quality_summary_admin_success():
    """Verify ADMIN user can access platform data quality summary."""
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/quality/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data
    assert "status" in data
    assert "checks" in data
    assert data["checks"]["total"] >= 0

def test_quality_alerts_admin_success():
    """Verify ADMIN user can list active and resolved quality alerts."""
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/quality/alerts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

def test_quality_summary_doctor_forbidden():
    """Verify DOCTOR role cannot access admin quality diagnostics (403)."""
    token = get_auth_token("DOCTOR")
    response = client.get(
        "/api/v1/analytics/quality/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

def test_quality_summary_patient_forbidden():
    """Verify PATIENT role cannot access admin quality diagnostics (403)."""
    token = get_auth_token("PATIENT")
    response = client.get(
        "/api/v1/analytics/quality/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
