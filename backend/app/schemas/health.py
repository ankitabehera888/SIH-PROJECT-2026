from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "healthy"


class DatabaseHealthResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"


class RedisHealthResponse(BaseModel):
    status: str = "healthy"
    redis: str = "connected"
