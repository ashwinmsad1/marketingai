"""
Rate Limiting Middleware for FastAPI
Integrates with RateLimitService to enforce API rate limits
"""

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import time
import logging

from backend.database.connection import get_db
from backend.services.rate_limit_service import RateLimitService
from backend.utils.request_utils import RequestUtils
from backend.core.exceptions import rate_limit_exception

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for API rate limiting
    Applies different rate limits based on user subscription tier
    """

    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.skip_paths = skip_paths

    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting"""

        # Skip rate limiting using consolidated utility
        if RequestUtils.should_skip_middleware(request, self.skip_paths):
            return await call_next(request)

        try:
            # Get database session
            db: Session = next(get_db())

            # Initialize rate limit service
            rate_limit_service = RateLimitService(db)

            # Extract user info using consolidated utilities
            user_id = RequestUtils.extract_user_id_from_token(request)
            ip_address = RequestUtils.get_client_ip(request)
            user_agent = RequestUtils.get_user_agent(request)
            endpoint = request.url.path

            # Check rate limit
            is_allowed, rate_limit_info = rate_limit_service.check_rate_limit(
                endpoint=endpoint,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # If blocked, return rate limit error
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded: {user_id or ip_address} on {endpoint} "
                    f"({rate_limit_info.get('requests_made', 0)}/{rate_limit_info.get('requests_limit', 0)})"
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": "Too many requests. Please try again later.",
                        "details": {
                            "requests_made": rate_limit_info.get("requests_made", 0),
                            "requests_limit": rate_limit_info.get("requests_limit", 0),
                            "reset_time": rate_limit_info.get("reset_time").isoformat() if rate_limit_info.get("reset_time") else None,
                            "blocked_until": rate_limit_info.get("blocked_until").isoformat() if rate_limit_info.get("blocked_until") else None
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_limit_info.get("requests_limit", 0)),
                        "X-RateLimit-Remaining": str(rate_limit_info.get("requests_remaining", 0)),
                        "X-RateLimit-Reset": str(int(rate_limit_info.get("reset_time", time.time()).timestamp())) if rate_limit_info.get("reset_time") else "0",
                        "Retry-After": str(int((rate_limit_info.get("blocked_until", time.time()) - time.time()).total_seconds())) if rate_limit_info.get("blocked_until") else "60"
                    }
                )

            # Process the request
            response = await call_next(request)

            # Add rate limit headers to successful responses
            if rate_limit_info and not rate_limit_info.get("error"):
                response.headers["X-RateLimit-Limit"] = str(rate_limit_info.get("requests_limit", 0))
                response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.get("requests_remaining", 0))
                if rate_limit_info.get("reset_time"):
                    response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info["reset_time"].timestamp()))

            return response

        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # In case of error, allow the request (fail open)
            return await call_next(request)

        finally:
            # Close database session
            try:
                db.close()
            except:
                pass

    # Removed: Duplicate utility methods now available in RequestUtils