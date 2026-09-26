import logging
import sys
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure standard structured logger
logger = logging.getLogger("healthcare_platform")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging.
    
    Adheres to healthcare privacy standards: logs HTTP metadata (method, endpoint,
    status code, latency, request ID) without logging sensitive PHI payloads.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"req_id={request_id} method={request.method} path={request.url.path} "
            f"status={response.status_code} duration={duration_ms:.2f}ms"
        )
        response.headers["X-Request-ID"] = request_id
        return response
