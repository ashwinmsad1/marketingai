"""
Request utility functions for middleware and services
Consolidates common request processing logic to avoid duplication
"""

from fastapi import Request
from typing import Optional
import logging

from backend.auth.jwt_handler import JWTHandler

logger = logging.getLogger(__name__)


class RequestUtils:
    """Utility class for common request processing operations"""

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        Extract real client IP address from request
        Handles various proxy headers and load balancer configurations
        """
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Get the first IP in the chain (real client IP)
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header (common in some proxy setups)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # Check CloudFlare connecting IP
        cf_connecting_ip = request.headers.get("cf-connecting-ip")
        if cf_connecting_ip:
            return cf_connecting_ip.strip()

        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"

    @staticmethod
    def extract_user_id_from_token(request: Request) -> Optional[str]:
        """
        Extract user ID from JWT token in Authorization header
        Returns None if no token or invalid token
        """
        try:
            # Get authorization header
            authorization = request.headers.get("authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None

            # Extract token
            token = authorization.split(" ")[1]

            # Decode token using JWTHandler
            jwt_handler = JWTHandler()
            token_data = jwt_handler.verify_token(token)

            return token_data.user_id if token_data else None

        except Exception as e:
            logger.debug(f"Could not extract user ID from token: {e}")
            return None

    @staticmethod
    def get_user_agent(request: Request) -> str:
        """Extract user agent string from request"""
        return request.headers.get("user-agent", "unknown")

    @staticmethod
    def get_request_id(request: Request) -> str:
        """Get or generate a request ID for tracking"""
        request_id = request.headers.get("x-request-id")
        if not request_id:
            # Generate request ID based on timestamp if not provided
            import time
            request_id = f"req-{int(time.time() * 1000)}"
        return request_id

    @staticmethod
    def is_static_resource(request: Request) -> bool:
        """Check if request is for a static resource"""
        static_extensions = {".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf"}
        path = request.url.path.lower()
        return any(path.endswith(ext) for ext in static_extensions)

    @staticmethod
    def should_skip_middleware(request: Request, skip_paths: list = None) -> bool:
        """
        Check if middleware should be skipped for this request
        Common paths that typically skip middleware processing
        """
        if skip_paths is None:
            skip_paths = [
                "/health",
                "/",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/uploads",
                "/favicon.ico"
            ]

        path = request.url.path

        # Check if path matches any skip patterns
        if any(path.startswith(skip_path) for skip_path in skip_paths):
            return True

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return True

        # Skip static resources
        if RequestUtils.is_static_resource(request):
            return True

        return False