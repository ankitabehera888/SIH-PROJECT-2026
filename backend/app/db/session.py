from typing import Generator
from redis import Redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy 2.0 Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides an isolated database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verify active PostgreSQL connectivity with a ping query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False


def check_redis_connection() -> bool:
    """Verify active Redis connectivity with a ping."""
    try:
        client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        return client.ping()
    except Exception as e:
        print(f"Redis connection check failed: {e}")
        return False
