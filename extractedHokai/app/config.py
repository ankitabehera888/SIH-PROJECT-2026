"""Application configuration classes for different environments."""

import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration shared across all environments."""

    DEBUG = False
    TESTING = False

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medassist.db")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-change-me-in-production")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
    OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID", "")
    OPENAI_MODEL_PRIMARY = os.getenv("OPENAI_MODEL_PRIMARY", "gpt-4o")
    OPENAI_MODEL_FAST = os.getenv("OPENAI_MODEL_FAST", "gpt-4o-mini")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    TESTING = True
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    pass


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config():
    """Get configuration based on environment variable."""
    env = os.getenv("APP_ENV", "development")
    return config_map.get(env, DevelopmentConfig)()
