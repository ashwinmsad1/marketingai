"""
Security Middleware for FastAPI
Adds security headers and basic protections
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security headers and basic protection middleware"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers and basic protections"""

        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add CORS headers if needed (FastAPI CORS middleware usually handles this)
        if request.method == "OPTIONS":
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        # Add request ID for tracking
        request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")
        response.headers["X-Request-ID"] = request_id

        # Add API version
        response.headers["X-API-Version"] = "1.0.0"

        return response