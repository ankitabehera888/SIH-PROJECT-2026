from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.config import DATABASE_URL

# Create SQLAlchemy engine configured for read-only analytical workloads
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for querying."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_db_connection() -> dict:
    """Test PostgreSQL connectivity and return basic server metadata."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version(), current_database(), current_user;")).fetchone()
        return {
            "status": "connected",
            "version": result[0],
            "database": result[1],
            "user": result[2],
        }
