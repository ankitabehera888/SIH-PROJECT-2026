from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_v1_database_health():
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_api_v1_redis_health():
    response = client.get("/api/v1/health/redis")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["redis"] == "connected"


def test_swagger_documentation():
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_v1_live_health():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_api_v1_ready_health():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["redis"] == "connected"

