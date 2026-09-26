"""FastAPI application entry point for MedAssist AI.

This module creates the FastAPI application, registers routes,
and initializes the database.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.symptoms import router as symptoms_router
from app.services.symptom_service import init_db

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — runs on startup and shutdown."""
    logger.info("Starting MedAssist AI application")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down MedAssist AI application")


app = FastAPI(
    title="MedAssist AI",
    description="AI-powered medical assistant platform with symptom analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(symptoms_router)


@app.get("/")
async def root():
    """Root endpoint with basic app info."""
    return {
        "name": "MedAssist AI",
        "version": "1.0.0",
        "description": "AI-powered medical assistant platform",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "symptoms": "/api/v1/symptoms",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "medassist-ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
