"""
Tier Enforcement Middleware for FastAPI
Ensures user subscription tier is properly set in request state
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import logging

from backend.database.connection import get_db
from backend.database.models import BillingSubscription, SubscriptionStatus
from backend.utils.request_utils import RequestUtils

logger = logging.getLogger(__name__)


class TierEnforcementMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that resolves user subscription tier and adds it to request state
    This enables proper tier enforcement in decorators and services
    """

    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/uploads",
            "/api/v1/auth/register",
            "/api/v1/auth/login"
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request to resolve user tier"""

        # Skip tier resolution using consolidated utility
        if RequestUtils.should_skip_middleware(request, self.skip_paths):
            return await call_next(request)

        try:
            # Extract user info from JWT token
            user_id, user_tier = await self._resolve_user_tier(request)

            # Set in request state for tier enforcement decorators
            request.state.user_id = user_id
            request.state.user_tier = user_tier

            logger.debug(f"Resolved user tier: {user_id} -> {user_tier}")

        except Exception as e:
            logger.debug(f"Could not resolve user tier: {e}")
            # Set defaults for unauthenticated users
            request.state.user_id = None
            request.state.user_tier = "basic"

        return await call_next(request)

    async def _resolve_user_tier(self, request: Request) -> tuple[str | None, str]:
        """Resolve user ID and subscription tier from JWT token and database"""

        # Extract user ID from JWT token using consolidated utility
        user_id = RequestUtils.extract_user_id_from_token(request)
        if not user_id:
            return None, "basic"

        # Get user's subscription tier from database
        try:
            db: Session = next(get_db())

            subscription = (
                db.query(BillingSubscription)
                .filter(
                    BillingSubscription.user_id == user_id,
                    BillingSubscription.status.in_([
                        SubscriptionStatus.ACTIVE,
                        SubscriptionStatus.TRIAL
                    ])
                )
                .first()
            )

            tier = subscription.tier.value if subscription else "basic"

            db.close()
            return user_id, tier

        except Exception as e:
            logger.error(f"Error resolving user tier for {user_id}: {e}")
            return user_id, "basic"

    # Removed: Duplicate utility method now available in RequestUtils