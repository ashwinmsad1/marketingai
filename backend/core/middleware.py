"""
FastAPI middleware for rate limiting and security
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import time
from typing import Callable

from app.dependencies import get_db
from services.rate_limit_service import RateLimitService
from core.exceptions import rate_limit_exception

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app, enabled: bool = True):
        self.app = app
        self.enabled = enabled
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for certain paths
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/favicon.ico"
        ]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        try:
            # Get database session
            db: Session = next(get_db())
            
            # Initialize rate limit service
            rate_limit_service = RateLimitService(db)
            
            # Extract request information
            endpoint = request.url.path
            method = request.method
            full_endpoint = f"{method} {endpoint}"
            
            # Get user ID from request if available
            user_id = None
            if hasattr(request.state, "user") and request.state.user:
                user_id = request.state.user.id
            
            # Get client information
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            
            # Check rate limit
            is_allowed, rate_info = rate_limit_service.check_rate_limit(
                endpoint=full_endpoint,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # If rate limited, return 429 error
            if not is_allowed:
                retry_after = 60  # Default retry after 1 minute
                if "blocked_until" in rate_info:
                    retry_after = max(1, int((rate_info["blocked_until"] - datetime.utcnow()).total_seconds()))
                
                logger.warning(
                    f"Rate limit exceeded for {user_id or ip_address} on {full_endpoint}"
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": "Rate limit exceeded",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "details": {
                            "requests_made": rate_info.get("requests_made", 0),
                            "requests_limit": rate_info.get("requests_limit", 0),
                            "retry_after_seconds": retry_after
                        }
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(rate_info.get("requests_limit", 0)),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(rate_info.get("blocked_until", datetime.utcnow()).timestamp()))
                    }
                )
            
            # Process request
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add rate limit headers to response
            if "requests_remaining" in rate_info:
                response.headers["X-RateLimit-Limit"] = str(rate_info.get("requests_limit", 0))
                response.headers["X-RateLimit-Remaining"] = str(rate_info.get("requests_remaining", 0))
                
                if "reset_time" in rate_info:
                    response.headers["X-RateLimit-Reset"] = str(int(rate_info["reset_time"].timestamp()))
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            # Close database session
            db.close()
            
            return response
            
        except Exception as e:
            logger.error(f"Error in rate limit middleware: {str(e)}")
            # In case of error, allow the request to proceed
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers (from load balancers, proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"


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