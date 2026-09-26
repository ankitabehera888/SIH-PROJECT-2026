import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token(role: str = "ADMIN") -> str:
    email = f"kpi.{role.lower()}.{uuid.uuid4().hex[:8]}@hospital.org"
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

def test_get_kpi_success():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/kpis?metric_code=appointment_volume",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metric_code"] == "appointment_volume"
    assert data["metric_type"] == "COUNT"
    assert data["value"] is not None

def test_get_kpi_not_found():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/kpis?metric_code=non_existent_metric",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

def test_get_kpi_invalid_dates():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/kpis?metric_code=appointment_volume&start_date=2026-12-31&end_date=2026-01-01",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400

def test_get_kpi_timeseries():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/kpis/timeseries?metric_code=appointment_volume&interval=month",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metric_code"] == "appointment_volume"
    assert data["interval"] == "month"
    assert isinstance(data["data"], list)

def test_get_kpi_comparison():
    token = get_auth_token("ADMIN")
    response = client.get(
        "/api/v1/analytics/kpis/compare?metric_code=encounter_volume&group_by=facility",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metric_code"] == "encounter_volume"
    assert data["group_by"] == "facility"
    assert isinstance(data["data"], list)
