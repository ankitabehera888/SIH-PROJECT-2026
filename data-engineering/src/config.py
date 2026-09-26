import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for data-engineering
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

DB_USER = os.getenv("DB_USER", "healthcare")
DB_PASSWORD = os.getenv("DB_PASSWORD", "healthcare_dev_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healthcare_dev")

# Prefer psycopg (v3) or fallback to psycopg2
DEFAULT_DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
