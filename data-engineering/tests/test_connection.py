from src.database import test_db_connection as check_db_conn

def test_postgresql_connection():
    """Assert that the data engineering environment can connect to the operational PostgreSQL database."""
    info = check_db_conn()
    assert info["status"] == "connected"
    assert info["database"] == "healthcare_dev"
    assert info["user"] == "healthcare"
    assert "PostgreSQL" in info["version"]
