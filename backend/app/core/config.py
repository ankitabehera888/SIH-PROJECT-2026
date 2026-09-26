from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Healthcare Platform API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg://healthcare:healthcare_dev_password@localhost:5432/healthcare_dev"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Daily.co WebRTC Video
    DAILY_API_KEY: str = "mock-daily-api-key-for-development"
    DAILY_API_URL: str = "https://api.daily.co/v1"
    DAILY_DOMAIN: str = "https://telehealth-demo.daily.co"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # JWT Authentication
    JWT_SECRET_KEY: str = "supersecret-dev-jwt-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Voice AI
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None
    OPENAI_WHISPER_MODEL: str = "gpt-4o-mini-transcribe"
    OPENAI_TTS_MODEL: str = "gpt-4o-mini-tts"
    OPENAI_MODEL_FAST: str = "gpt-4o-mini"


settings = Settings()
