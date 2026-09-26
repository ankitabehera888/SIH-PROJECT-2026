import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token(role: str = "ADMIN") -> str:
    email = f"dash.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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

def test_dashboard_overview():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "appointments" in data
    assert "encounters" in data
    assert "referrals" in data
    assert "chronic_care" in data
    assert "access" in data

def test_appointments_summary():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/appointments/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "appointment_volume" in data
    assert "completion_rate" in data

def test_appointments_trends():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/appointments/trends",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

def test_referrals_summary():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/referrals/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "referral_volume" in data
    assert "completion_rate" in data

def test_referrals_aging():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/referrals/aging",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "buckets" in data
    assert len(data["buckets"]) == 5

def test_facilities_analytics_pagination():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/facilities?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data
    assert len(data["data"]) <= 10

def test_geography_analytics():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/geography?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data

def test_cohorts_summary():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/cohorts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
