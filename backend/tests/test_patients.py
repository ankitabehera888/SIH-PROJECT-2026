import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token(role: str = "DOCTOR") -> str:
    email = f"staff.{role.lower()}.{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPassword123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return login_res.json()["access_token"]


def test_create_patient_success():
    token = get_auth_token("DOCTOR")
    payload = {
        "first_name": "Ravi",
        "middle_name": "Kumar",
        "last_name": f"Sharma{uuid.uuid4().hex[:4]}",
        "date_of_birth": "1995-05-15",
        "gender": "MALE",
        "phone": "+919876543210",
        "email": f"ravi.{uuid.uuid4().hex[:6]}@example.com",
        "address": "Primary Health Centre District A, Village 1",
        "emergency_contact_name": "Sunita Sharma",
        "emergency_contact_phone": "+919876543211",
    }
    response = client.post(
        "/api/v1/patients",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["gender"] == "MALE"
    assert data["is_active"] is True
    assert "id" in data
    assert data["patient_number"].startswith("PAT-")
    assert data["created_by"] is not None


def test_get_patient_by_id():
    token = get_auth_token("DOCTOR")
    unique_last = f"Pat{uuid.uuid4().hex[:6]}"
    create_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": "Amina",
            "last_name": unique_last,
            "date_of_birth": "1990-11-20",
            "gender": "FEMALE",
            "phone": "+919811223344",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    patient_id = create_res.json()["id"]

    get_res = client.get(
        f"/api/v1/patients/{patient_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["id"] == patient_id
    assert get_res.json()["first_name"] == "Amina"


def test_get_nonexistent_patient_returns_404():
    token = get_auth_token("DOCTOR")
    random_uuid = str(uuid.uuid4())
    res = client.get(
        f"/api/v1/patients/{random_uuid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"


def test_update_patient():
    token = get_auth_token("NURSE")
    create_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": "Dev",
            "last_name": f"Patel{uuid.uuid4().hex[:6]}",
            "date_of_birth": "1988-03-12",
            "gender": "MALE",
            "phone": "+919777888999",
            "address": "Old Address",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    patient_id = create_res.json()["id"]

    update_payload = {
        "phone": "+919111222333",
        "address": "Updated Village Road, PHC Zone",
    }
    update_res = client.patch(
        f"/api/v1/patients/{patient_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["phone"] == "+919111222333"
    assert updated["address"] == update_payload["address"]
    assert updated["first_name"] == "Dev"  # unchanged


def test_soft_deactivate_patient():
    token = get_auth_token("ADMIN")
    create_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": "ToDeactivate",
            "last_name": f"Test{uuid.uuid4().hex[:6]}",
            "date_of_birth": "2000-01-01",
            "gender": "OTHER",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    patient_id = create_res.json()["id"]

    del_res = client.delete(
        f"/api/v1/patients/{patient_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["is_active"] is False

    # Record still exists in database as inactive
    get_res = client.get(
        f"/api/v1/patients/{patient_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["is_active"] is False


def test_list_patients_pagination():
    token = get_auth_token("DOCTOR")
    res = client.get(
        "/api/v1/patients?page=1&page_size=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert "total_pages" in data


def test_search_patients():
    token = get_auth_token("DOCTOR")
    unique_suffix = uuid.uuid4().hex[:6]
    first_name = f"SearchFirst{unique_suffix}"
    last_name = f"SearchLast{unique_suffix}"
    client.post(
        "/api/v1/patients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": "1992-07-04",
            "gender": "FEMALE",
            "phone": "+919444555666",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    search_res = client.get(
        f"/api/v1/patients/search?q={unique_suffix}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search_res.status_code == 200
    results = search_res.json()["items"]
    assert len(results) >= 1
    assert any(p["last_name"] == last_name for p in results)


def test_duplicate_patient_detection():
    token = get_auth_token("DOCTOR")
    unique_phone = f"+919{uuid.uuid4().int % 1000000000:09d}"
    last_name = f"DupTest{uuid.uuid4().hex[:6]}"
    payload = {
        "first_name": "UniqueDuplicate",
        "last_name": last_name,
        "date_of_birth": "1994-06-15",
        "gender": "MALE",
        "phone": unique_phone,
    }

    # First registration
    res1 = client.post(
        "/api/v1/patients",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 201

    # Second registration with matching signals (Name + DOB + Phone)
    res2 = client.post(
        "/api/v1/patients",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"
    assert "duplicate" in data["error"]["message"].lower()


def test_validation_dob_in_future_rejected():
    token = get_auth_token("DOCTOR")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    res = client.post(
        "/api/v1/patients",
        json={
            "first_name": "Future",
            "last_name": "Baby",
            "date_of_birth": tomorrow,
            "gender": "FEMALE",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_unauthenticated_request_rejected():
    res = client.get("/api/v1/patients")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"


def test_patient_role_cannot_deactivate_patient():
    patient_token = get_auth_token("PATIENT")
    doctor_token = get_auth_token("DOCTOR")

    # Create a patient as Doctor
    create_res = client.post(
        "/api/v1/patients",
        json={
            "first_name": "Protected",
            "last_name": f"Record{uuid.uuid4().hex[:6]}",
            "date_of_birth": "1996-08-10",
            "gender": "MALE",
        },
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    p_id = create_res.json()["id"]

    # Attempt to delete with PATIENT role token
    del_res = client.delete(
        f"/api/v1/patients/{p_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert del_res.status_code == 403
    assert del_res.json()["error"]["code"] == "FORBIDDEN"
