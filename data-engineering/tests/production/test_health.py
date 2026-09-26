from src.database import engine
from sqlalchemy import text

def test_postgresql_liveness():
    """Verify PostgreSQL database responds to simple ping query."""
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1;")).scalar()
        assert res == 1

def test_database_schema_readiness():
    """Verify critical schemas exist and are queryable."""
    with engine.connect() as conn:
        schemas = conn.execute(text("SELECT schema_name FROM information_schema.schemata;")).scalars().all()
        assert "public" in schemas
        assert "analytics" in schemas
