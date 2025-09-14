"""
FastAPI middleware for security and utilities
(Rate limiting moved to backend/middleware/rate_limit_middleware.py to avoid duplication)
"""

from fastapi import Request, Response
import logging
import time
from typing import Callable

logger = logging.getLogger(__name__)

# Removed: Duplicate RateLimitMiddleware class - now using backend/middleware/rate_limit_middleware.py


class SecurityMiddleware:
    """Security headers and basic protection middleware"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
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


class LoggingMiddleware:
    """Request/response logging middleware"""
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = False):
        self.app = app
        self.log_requests = log_requests
        self.log_responses = log_responses
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
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