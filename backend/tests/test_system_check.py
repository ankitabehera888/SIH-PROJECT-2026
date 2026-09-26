from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_list_system_checks():
    payload = {
        "check_name": "automated_pipeline_verification",
        "status": "operational",
    }
    response = client.post("/api/v1/system-checks", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["check_name"] == payload["check_name"]
    assert created["status"] == payload["status"]
    assert "id" in created
    assert "created_at" in created

    # Test GET by ID
    get_res = client.get(f"/api/v1/system-checks/{created['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == created["id"]

    # Test GET all
    list_res = client.get("/api/v1/system-checks")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_system_check_not_found():
    response = client.get("/api/v1/system-checks/99999999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"


def test_validation_error_envelope():
    # check_name is required; sending empty payload should trigger 422 with standard envelope
    response = client.post("/api/v1/system-checks", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]
