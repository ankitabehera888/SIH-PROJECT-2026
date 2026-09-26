# Healthcare Platform API - Phase 5 Encounters & Vitals
from fastapi import FastAPI, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.core.logging import RequestLoggingMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise Healthcare Platform Foundation API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.DEBUG,
)

# 1. Structured Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Standardized Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

from app.core.socket_manager import socket_app

# 4. API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# 5. Mount Socket.IO real-time event server
app.mount("/socket.io", socket_app)


# 5. Top-level convenience routes
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Handle browser favicon requests to avoid 404 in console logs."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health", tags=["Root"], include_in_schema=False)
def root_health():
    """Root health check redirecting to the canonical v1 health endpoint."""
    return {"status": "healthy", "version": "v1", "path": f"{settings.API_V1_STR}/health"}
