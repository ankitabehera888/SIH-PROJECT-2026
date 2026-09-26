from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.db.session import check_db_connection, check_redis_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse, RedisHealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="API Health Check")
def get_api_health():
    """Verify that the FastAPI application is alive."""
    return HealthResponse(status="healthy")


@router.get("/database", response_model=DatabaseHealthResponse, summary="Database Health Check")
def get_database_health():
    """Verify PostgreSQL connectivity via SQLAlchemy."""
    is_connected = check_db_connection()
    if not is_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected"},
        )
    return DatabaseHealthResponse(status="healthy", database="connected")


@router.get("/redis", response_model=RedisHealthResponse, summary="Redis Health Check")
def get_redis_health():
    """Verify Redis container connectivity."""
    is_connected = check_redis_connection()
    if not is_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "redis": "disconnected"},
        )
    return RedisHealthResponse(status="healthy", redis="connected")


@router.get("/live", summary="Process Liveness Probe")
def get_liveness():
    """Kubernetes / Docker Liveness probe verifying process is responsive."""
    return {"status": "alive"}


@router.get("/ready", summary="Dependency Readiness Probe")
def get_readiness():
    """Kubernetes / Docker Readiness probe verifying active database and cache connectivity."""
    db_ok = check_db_connection()
    redis_ok = check_redis_connection()
    
    if not db_ok or not redis_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "connected" if db_ok else "disconnected",
                "redis": "connected" if redis_ok else "disconnected",
            },
        )
    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected",
    }

