"""
Logging Middleware for FastAPI
Provides request/response logging capabilities
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""

    def __init__(self, app, log_requests: bool = True, log_responses: bool = False):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log requests and responses"""

        start_time = time.time()

        # Log incoming request
        if self.log_requests:
            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                f"Incoming request: {request.method} {request.url.path} "
                f"from {client_ip} - User-Agent: {request.headers.get('user-agent', 'unknown')}"
            )

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        if self.log_responses or response.status_code >= 400:
            client_ip = request.client.host if request.client else "unknown"
            log_level = logging.WARNING if response.status_code >= 400 else logging.INFO

            logger.log(
                log_level,
                f"Response: {request.method} {request.url.path} "
                f"-> {response.status_code} in {process_time:.3f}s from {client_ip}"
            )

        return response