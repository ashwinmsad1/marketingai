"""
Rate limiting service for API endpoints
Implements request throttling to prevent abuse and automated attacks
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

from backend.database.models import User, RateLimitRecord
from backend.core.config import settings
from backend.core.exceptions import RateLimitError, rate_limit_exception

logger = logging.getLogger(__name__)

class RateLimitService:
    """Service for managing API rate limits"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def check_rate_limit(
        self, 
        endpoint: str, 
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request should be rate limited
        
        Args:
            endpoint: API endpoint being accessed
            user_id: User ID (if authenticated)
            ip_address: Client IP address
            user_agent: User agent string
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            # Get rate limits for endpoint
            limits = self._get_rate_limits(endpoint, user_id)
            
            if not limits:
                # No rate limiting for this endpoint
                return True, {}
            
            # Check current window
            now = datetime.utcnow()
            window_start = self._get_window_start(now, limits["window_minutes"])
            
            # Find or create rate limit record
            record = self._get_or_create_record(
                endpoint=endpoint,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                window_start=window_start,
                limits=limits
            )
            
            # Check if currently blocked
            if record.is_blocked and record.blocked_until and record.blocked_until > now:
                logger.warning(f"Request blocked for {user_id or ip_address} on {endpoint}")
                return False, {
                    "blocked": True,
                    "blocked_until": record.blocked_until,
                    "requests_made": record.requests_made,
                    "requests_limit": record.requests_limit
                }
            
            # Clear block if expired
            if record.is_blocked and record.blocked_until and record.blocked_until <= now:
                record.is_blocked = False
                record.blocked_until = None
                
            # Check if within limits
            if record.requests_made >= record.requests_limit:
                # Block the user/IP
                record.is_blocked = True
                record.blocked_until = window_start + timedelta(minutes=limits["window_minutes"])
                
                logger.warning(
                    f"Rate limit exceeded for {user_id or ip_address} on {endpoint}: "
                    f"{record.requests_made}/{record.requests_limit}"
                )
                
                self.db.commit()
                
                return False, {
                    "blocked": True,
                    "blocked_until": record.blocked_until,
                    "requests_made": record.requests_made,
                    "requests_limit": record.requests_limit
                }
            
            # Increment request count
            record.requests_made += 1
            record.updated_at = now
            
            self.db.commit()
            
            # Return success with rate limit info
            return True, {
                "blocked": False,
                "requests_made": record.requests_made,
                "requests_limit": record.requests_limit,
                "requests_remaining": record.requests_limit - record.requests_made,
                "reset_time": window_start + timedelta(minutes=limits["window_minutes"])
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # In case of error, allow the request (fail open)
            return True, {"error": "Rate limit check failed"}
    
    def _get_rate_limits(self, endpoint: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get rate limits for endpoint and user"""
        
        # Base rate limits by endpoint
        base_limits = {
            "/api/v1/campaigns/create": {
                "anonymous": {"requests": 5, "window_minutes": 60},
                "authenticated": {"requests": 20, "window_minutes": 60},
                "starter": {"requests": 20, "window_minutes": 60},
                "professional": {"requests": 50, "window_minutes": 60},
                "enterprise": {"requests": 100, "window_minutes": 60}
            },
            "/api/v1/auth/login": {
                "anonymous": {"requests": 10, "window_minutes": 15},
                "authenticated": {"requests": 10, "window_minutes": 15}
            },
            "/api/v1/auth/register": {
                "anonymous": {"requests": 3, "window_minutes": 60},
                "authenticated": {"requests": 3, "window_minutes": 60}
            },
            "default": {
                "anonymous": {"requests": 60, "window_minutes": 60},
                "authenticated": {"requests": 120, "window_minutes": 60},
                "starter": {"requests": 120, "window_minutes": 60},
                "professional": {"requests": 300, "window_minutes": 60},
                "enterprise": {"requests": 600, "window_minutes": 60}
            }
        }
        
        # Get endpoint-specific limits or default
        endpoint_limits = base_limits.get(endpoint, base_limits["default"])
        
        # Determine user tier
        if not user_id:
            tier = "anonymous"
        else:
            tier = self._get_user_tier(user_id)
        
        # Get limits for tier
        tier_limits = endpoint_limits.get(tier, endpoint_limits.get("authenticated", endpoint_limits.get("anonymous")))
        
        if not tier_limits:
            return None
            
        return {
            "requests": tier_limits["requests"],
            "window_minutes": tier_limits["window_minutes"]
        }
    
    def _get_user_tier(self, user_id: str) -> str:
        """Get user's subscription tier"""
        from backend.database.models import BillingSubscription
        
        subscription = (
            self.db.query(BillingSubscription)
            .filter(
                BillingSubscription.user_id == user_id,
                BillingSubscription.status.in_(["active", "trial"])
            )
            .first()
        )
        
        return subscription.tier.value if subscription else "starter"
    
    def _get_window_start(self, now: datetime, window_minutes: int) -> datetime:
        """Calculate the start of the current rate limiting window"""
        minutes_since_epoch = int(now.timestamp() // 60)
        window_start_minutes = (minutes_since_epoch // window_minutes) * window_minutes
        return datetime.utcfromtimestamp(window_start_minutes * 60)
    
    def _get_or_create_record(
        self,
        endpoint: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        window_start: datetime,
        limits: Dict
    ) -> RateLimitRecord:
        """Get existing rate limit record or create new one"""
        
        # Try to find existing record
        record = (
            self.db.query(RateLimitRecord)
            .filter(
                and_(
                    RateLimitRecord.endpoint == endpoint,
                    RateLimitRecord.user_id == user_id,
                    RateLimitRecord.window_start == window_start
                )
            )
            .first()
        )
        
        if record:
            return record
        
        # Create new record
        record = RateLimitRecord(
            user_id=user_id,
            endpoint=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            requests_made=0,
            requests_limit=limits["requests"],
            window_start=window_start,
            window_duration_minutes=limits["window_minutes"]
        )
        
        self.db.add(record)
        self.db.commit()
        
        return record
    
    def reset_rate_limit(self, user_id: Optional[str] = None, ip_address: Optional[str] = None) -> bool:
        """Reset rate limits for user or IP (admin function)"""
        try:
            query = self.db.query(RateLimitRecord)
            
            if user_id:
                query = query.filter(RateLimitRecord.user_id == user_id)
            elif ip_address:
                query = query.filter(RateLimitRecord.ip_address == ip_address)
            else:
                return False
            
            # Update all matching records
            query.update({
                RateLimitRecord.is_blocked: False,
                RateLimitRecord.blocked_until: None,
                RateLimitRecord.requests_made: 0
            })
            
            self.db.commit()
            logger.info(f"Reset rate limits for {user_id or ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting rate limits: {str(e)}")
            self.db.rollback()
            return False
    
    def get_rate_limit_status(self, user_id: str, endpoint: Optional[str] = None) -> Dict:
        """Get current rate limit status for user"""
        try:
            query = (
                self.db.query(RateLimitRecord)
                .filter(RateLimitRecord.user_id == user_id)
            )
            
            if endpoint:
                query = query.filter(RateLimitRecord.endpoint == endpoint)
            
            records = query.all()
            
            status = {
                "user_id": user_id,
                "endpoints": {},
                "is_blocked": False
            }
            
            now = datetime.utcnow()
            
            for record in records:
                # Check if window is still active
                window_end = record.window_start + timedelta(minutes=record.window_duration_minutes)
                is_active = now < window_end
                
                is_blocked = (
                    record.is_blocked and 
                    record.blocked_until and 
                    record.blocked_until > now
                )
                
                status["endpoints"][record.endpoint] = {
                    "requests_made": record.requests_made,
                    "requests_limit": record.requests_limit,
                    "requests_remaining": max(0, record.requests_limit - record.requests_made) if is_active else record.requests_limit,
                    "window_start": record.window_start,
                    "window_end": window_end,
                    "is_active_window": is_active,
                    "is_blocked": is_blocked,
                    "blocked_until": record.blocked_until
                }
                
                if is_blocked:
                    status["is_blocked"] = True
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_old_records(self, days_old: int = 7) -> int:
        """Clean up old rate limit records"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            
            deleted = (
                self.db.query(RateLimitRecord)
                .filter(RateLimitRecord.created_at < cutoff)
                .delete()
            )
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted} old rate limit records")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up rate limit records: {str(e)}")
            self.db.rollback()
            return 0