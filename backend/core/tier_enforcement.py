"""
Tier Enforcement Middleware for AI Marketing Automation Platform
Provides middleware and decorators for enforcing subscription tier limits
"""

from functools import wraps
from typing import Dict, Any, Callable, Optional
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from services.usage_tracking_service import UsageTrackingService
from database.connection import get_db
from core.config import settings


class TierEnforcementError(HTTPException):
    """Custom exception for tier limit violations"""
    
    def __init__(
        self, 
        detail: str,
        current_tier: str,
        suggested_tier: Optional[str] = None,
        usage_info: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=429, detail=detail)
        self.current_tier = current_tier
        self.suggested_tier = suggested_tier
        self.usage_info = usage_info or {}


class TierEnforcementMiddleware:
    """Middleware for enforcing subscription tier limits"""
    
    @staticmethod
    def check_campaign_creation_limit(
        user_id: str, 
        current_tier: str,
        db: Session
    ) -> Dict[str, Any]:
        """Check if user can create a new campaign"""
        
        action_check = UsageTrackingService.check_action_allowed(
            db=db,
            user_id=user_id,
            action="create_campaign"
        )
        
        if not action_check["allowed"]:
            raise TierEnforcementError(
                detail=f"Campaign creation limit reached. {action_check.get('reason', '')}",
                current_tier=current_tier,
                suggested_tier=action_check.get("upgrade_suggestion"),
                usage_info=action_check
            )
        
        return action_check
    
    @staticmethod
    def check_ai_generation_limit(
        user_id: str,
        current_tier: str, 
        db: Session,
        generation_type: str = "image"
    ) -> Dict[str, Any]:
        """Check if user can generate AI content"""
        
        action_check = UsageTrackingService.check_action_allowed(
            db=db,
            user_id=user_id,
            action="generate_ai_content"
        )
        
        if not action_check["allowed"]:
            raise TierEnforcementError(
                detail=f"AI generation limit reached. {action_check.get('reason', '')}",
                current_tier=current_tier,
                suggested_tier=action_check.get("upgrade_suggestion"),
                usage_info=action_check
            )
        
        return action_check
    
    @staticmethod
    def check_ad_spend_limit(
        user_id: str,
        current_tier: str,
        db: Session,
        additional_spend: float = 0.0
    ) -> Dict[str, Any]:
        """Check if user can monitor additional ad spend"""
        
        action_check = UsageTrackingService.check_action_allowed(
            db=db,
            user_id=user_id,
            action="monitor_ad_spend"
        )
        
        # Check if additional spend would exceed limits
        if additional_spend > 0:
            current_spend = action_check["usage"]["ad_spend"]
            limit = action_check["limits"]["ad_spend"]
            
            if current_spend + additional_spend > limit:
                raise TierEnforcementError(
                    detail=f"Additional ad spend of ₹{additional_spend:,.0f} would exceed limit. Current: ₹{current_spend:,.0f}, Limit: ₹{limit:,.0f}",
                    current_tier=current_tier,
                    suggested_tier=action_check.get("upgrade_suggestion"),
                    usage_info=action_check
                )
        
        elif not action_check["allowed"]:
            raise TierEnforcementError(
                detail=f"Ad spend monitoring limit reached. {action_check.get('reason', '')}",
                current_tier=current_tier,
                suggested_tier=action_check.get("upgrade_suggestion"), 
                usage_info=action_check
            )
        
        return action_check
    
    @staticmethod
    def check_feature_access(
        user_id: str,
        current_tier: str,
        feature: str,
        db: Session
    ) -> Dict[str, Any]:
        """Check if user has access to a specific feature"""
        
        from utils.usage_helpers import UsageHelpers
        
        # Check if feature is available in tier
        if not UsageHelpers.is_feature_available(current_tier, feature):
            upgrade_tier = UsageHelpers.get_tier_upgrade_path(current_tier)
            
            raise TierEnforcementError(
                detail=f"Feature '{feature}' not available in {current_tier} tier",
                current_tier=current_tier,
                suggested_tier=upgrade_tier,
                usage_info={"feature": feature, "required_for": upgrade_tier}
            )
        
        # For usage-tracked features, check limits
        tracked_features = ["analytics_export", "custom_report", "api_call"]
        if feature in tracked_features:
            # Get current usage to verify limits aren't exceeded
            usage_summary = UsageTrackingService.get_usage_summary(db, user_id)
            
            feature_usage_map = {
                "analytics_export": usage_summary["usage"]["breakdown"]["analytics_exports"],
                "custom_report": usage_summary["usage"]["breakdown"]["custom_reports"],
                "api_call": usage_summary["usage"]["breakdown"]["api_calls"]
            }
            
            # For now, allow unlimited usage of features within tier
            # Could add specific feature limits here in future
        
        return {"allowed": True, "feature": feature, "tier": current_tier}


def require_tier(min_tier: str):
    """Decorator to require a minimum subscription tier"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and db from function arguments
            request = None
            db = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, Session):
                    db = arg
            
            # Also check kwargs
            if not request:
                request = kwargs.get('request')
            if not db:
                db = kwargs.get('db')
            
            if not request or not db:
                raise HTTPException(
                    status_code=500, 
                    detail="Missing request or database session for tier enforcement"
                )
            
            # Get user info (this would be extracted from JWT token in real implementation)
            user_id = getattr(request.state, 'user_id', None)
            current_tier = getattr(request.state, 'user_tier', 'basic')
            
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required for tier enforcement"
                )
            
            # Check tier hierarchy
            tier_hierarchy = {"basic": 1, "professional": 2, "business": 3}
            min_tier_level = tier_hierarchy.get(min_tier, 1)
            current_tier_level = tier_hierarchy.get(current_tier, 1)
            
            if current_tier_level < min_tier_level:
                from utils.usage_helpers import UsageHelpers
                upgrade_tier = UsageHelpers.get_tier_upgrade_path(current_tier)
                
                raise TierEnforcementError(
                    detail=f"This feature requires {min_tier} tier or higher. Current tier: {current_tier}",
                    current_tier=current_tier,
                    suggested_tier=upgrade_tier or min_tier,
                    usage_info={"required_tier": min_tier}
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def enforce_campaign_limit(func: Callable) -> Callable:
    """Decorator to enforce campaign creation limits"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract necessary parameters
        request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
        db = kwargs.get('db') or next((arg for arg in args if isinstance(arg, Session)), None)
        
        if not request or not db:
            raise HTTPException(status_code=500, detail="Missing request or database session")
        
        user_id = getattr(request.state, 'user_id', None)
        current_tier = getattr(request.state, 'user_tier', 'basic')
        
        if user_id:
            TierEnforcementMiddleware.check_campaign_creation_limit(
                user_id=user_id,
                current_tier=current_tier,
                db=db
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def enforce_ai_generation_limit(generation_type: str = "image"):
    """Decorator to enforce AI generation limits"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract necessary parameters
            request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
            db = kwargs.get('db') or next((arg for arg in args if isinstance(arg, Session)), None)
            
            if not request or not db:
                raise HTTPException(status_code=500, detail="Missing request or database session")
            
            user_id = getattr(request.state, 'user_id', None)
            current_tier = getattr(request.state, 'user_tier', 'basic')
            
            if user_id:
                TierEnforcementMiddleware.check_ai_generation_limit(
                    user_id=user_id,
                    current_tier=current_tier,
                    db=db,
                    generation_type=generation_type
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def enforce_ad_spend_limit(func: Callable) -> Callable:
    """Decorator to enforce ad spend monitoring limits"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract necessary parameters
        request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
        db = kwargs.get('db') or next((arg for arg in args if isinstance(arg, Session)), None)
        
        if not request or not db:
            raise HTTPException(status_code=500, detail="Missing request or database session")
        
        user_id = getattr(request.state, 'user_id', None)
        current_tier = getattr(request.state, 'user_tier', 'basic')
        
        # Extract additional spend from request body or params
        additional_spend = 0.0
        if hasattr(request, 'json') and request.json():
            additional_spend = request.json().get('budget', 0.0)
        
        if user_id:
            TierEnforcementMiddleware.check_ad_spend_limit(
                user_id=user_id,
                current_tier=current_tier,
                db=db,
                additional_spend=additional_spend
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def track_usage_on_success(action: str, **tracking_kwargs):
    """Decorator to track usage after successful action completion"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the original function first
            result = await func(*args, **kwargs)
            
            # If successful, track the usage
            try:
                request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
                db = kwargs.get('db') or next((arg for arg in args if isinstance(arg, Session)), None)
                
                if request and db:
                    user_id = getattr(request.state, 'user_id', None)
                    current_tier = getattr(request.state, 'user_tier', 'basic')
                    
                    if user_id:
                        if action == "campaign_creation":
                            UsageTrackingService.track_campaign_creation(
                                db=db,
                                user_id=user_id,
                                current_tier=current_tier
                            )
                        elif action == "ai_generation":
                            generation_type = tracking_kwargs.get('generation_type', 'image')
                            UsageTrackingService.track_ai_generation(
                                db=db,
                                user_id=user_id,
                                generation_type=generation_type,
                                current_tier=current_tier
                            )
                        elif action == "ad_spend":
                            spend_amount = tracking_kwargs.get('spend_amount', 0.0)
                            # Extract spend from result or request
                            if hasattr(result, 'budget'):
                                spend_amount = result.budget
                            elif isinstance(result, dict) and 'budget' in result:
                                spend_amount = result['budget']
                            
                            if spend_amount > 0:
                                UsageTrackingService.track_ad_spend(
                                    db=db,
                                    user_id=user_id,
                                    spend_amount=spend_amount,
                                    current_tier=current_tier
                                )
                        elif action == "feature_usage":
                            feature_type = tracking_kwargs.get('feature_type')
                            if feature_type:
                                UsageTrackingService.track_feature_usage(
                                    db=db,
                                    user_id=user_id,
                                    feature_type=feature_type,
                                    current_tier=current_tier
                                )
            
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Warning: Failed to track usage for {action}: {e}")
            
            return result
        
        return wrapper
    
    return decorator


# Convenience decorators that combine enforcement and tracking
def campaign_creation_guard(func: Callable) -> Callable:
    """Complete guard for campaign creation - enforce limit + track usage"""
    return track_usage_on_success("campaign_creation")(
        enforce_campaign_limit(func)
    )


def ai_generation_guard(generation_type: str = "image"):
    """Complete guard for AI generation - enforce limit + track usage"""
    def decorator(func: Callable) -> Callable:
        return track_usage_on_success(
            "ai_generation", 
            generation_type=generation_type
        )(
            enforce_ai_generation_limit(generation_type)(func)
        )
    return decorator


def ad_spend_guard(func: Callable) -> Callable:
    """Complete guard for ad spend - enforce limit + track usage"""
    return track_usage_on_success("ad_spend")(
        enforce_ad_spend_limit(func)
    )


def feature_usage_guard(feature_type: str):
    """Complete guard for feature usage - check access + track usage"""
    def decorator(func: Callable) -> Callable:
        return track_usage_on_success(
            "feature_usage",
            feature_type=feature_type
        )(
            require_tier("basic")(func)  # All features require at least basic tier
        )
    return decorator