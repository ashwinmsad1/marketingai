"""
Usage Tracking Service for AI Marketing Automation Platform
Provides high-level usage tracking and tier enforcement functionality
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.crud import UsageTrackingCRUD
from backend.database.models import UsageTracking, User
from backend.core.config import settings


class UsageTrackingService:
    """Service for managing usage tracking and tier enforcement"""
    
    @staticmethod
    def track_campaign_creation(db: Session, user_id: str, current_tier: str = "basic") -> Dict[str, Any]:
        """Track campaign creation and check limits"""
        # Update usage
        usage = UsageTrackingCRUD.create_or_update_usage(
            db=db,
            user_id=user_id,
            current_tier=current_tier,
            campaigns_created=1
        )
        
        # Check if within limits
        limits_check = UsageTrackingCRUD.check_tier_limits(db, user_id, settings)
        
        return {
            "usage_updated": True,
            "current_usage": {
                "campaigns": usage.campaigns_created,
                "ai_generations": usage.ai_generations_used,
                "ad_spend": usage.ad_spend_monitored
            },
            "within_limits": limits_check["within_limits"],
            "warnings": limits_check["warnings"],
            "limits_status": limits_check
        }
    
    @staticmethod
    def track_ai_generation(
        db: Session, 
        user_id: str, 
        generation_type: str = "image",
        current_tier: str = "basic"
    ) -> Dict[str, Any]:
        """Track AI content generation and check limits"""
        
        # Update usage based on generation type
        increments = {"ai_generations_used": 1}
        
        if generation_type == "image":
            increments["images_generated"] = 1
        elif generation_type == "video": 
            increments["videos_generated"] = 1
        elif generation_type == "text":
            increments["text_generations"] = 1
        
        usage = UsageTrackingCRUD.create_or_update_usage(
            db=db,
            user_id=user_id,
            current_tier=current_tier,
            **increments
        )
        
        # Check limits
        limits_check = UsageTrackingCRUD.check_tier_limits(db, user_id, settings)
        
        return {
            "usage_updated": True,
            "generation_type": generation_type,
            "current_usage": {
                "total_ai_generations": usage.ai_generations_used,
                "images_generated": usage.images_generated,
                "videos_generated": usage.videos_generated,
                "text_generations": usage.text_generations
            },
            "within_limits": limits_check["within_limits"],
            "warnings": limits_check["warnings"],
            "limits_status": limits_check
        }
    
    @staticmethod
    def track_ad_spend(
        db: Session,
        user_id: str,
        spend_amount: float,
        current_tier: str = "basic"
    ) -> Dict[str, Any]:
        """Track ad spend monitoring and check limits"""
        
        usage = UsageTrackingCRUD.create_or_update_usage(
            db=db,
            user_id=user_id,
            current_tier=current_tier,
            ad_spend_monitored=spend_amount
        )
        
        # Check limits
        limits_check = UsageTrackingCRUD.check_tier_limits(db, user_id, settings)
        
        return {
            "usage_updated": True,
            "spend_tracked": spend_amount,
            "total_spend_monitored": usage.ad_spend_monitored,
            "within_limits": limits_check["within_limits"],
            "warnings": limits_check["warnings"],
            "limits_status": limits_check
        }
    
    @staticmethod
    def track_feature_usage(
        db: Session,
        user_id: str,
        feature_type: str,
        current_tier: str = "basic"
    ) -> Dict[str, Any]:
        """Track usage of tier-specific features"""
        
        increments = {}
        if feature_type == "analytics_export":
            increments["analytics_exports"] = 1
        elif feature_type == "custom_report":
            increments["custom_reports_generated"] = 1
        elif feature_type == "api_call":
            increments["api_calls_made"] = 1
        else:
            return {"error": f"Unknown feature type: {feature_type}"}
        
        usage = UsageTrackingCRUD.create_or_update_usage(
            db=db,
            user_id=user_id,
            current_tier=current_tier,
            **increments
        )
        
        # Check limits
        limits_check = UsageTrackingCRUD.check_tier_limits(db, user_id, settings)
        
        return {
            "usage_updated": True,
            "feature_used": feature_type,
            "current_feature_usage": {
                "analytics_exports": usage.analytics_exports,
                "custom_reports": usage.custom_reports_generated,
                "api_calls": usage.api_calls_made
            },
            "within_limits": limits_check["within_limits"],
            "warnings": limits_check["warnings"],
            "limits_status": limits_check
        }
    
    @staticmethod
    def get_usage_summary(db: Session, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage summary for a user"""
        
        usage = UsageTrackingCRUD.get_current_usage(db, user_id)
        if not usage:
            return {
                "user_id": user_id,
                "current_period": None,
                "usage": {},
                "limits": {},
                "tier": "basic"
            }
        
        # Get limits check
        limits_check = UsageTrackingCRUD.check_tier_limits(db, user_id, settings)
        
        # Calculate days remaining in period
        days_remaining = (usage.period_end - datetime.utcnow()).days
        
        return {
            "user_id": user_id,
            "current_tier": usage.current_tier,
            "period_info": {
                "start": usage.period_start,
                "end": usage.period_end,
                "days_remaining": max(0, days_remaining),
                "billing_cycle": usage.billing_cycle
            },
            "usage": {
                "campaigns_created": usage.campaigns_created,
                "ai_generations_used": usage.ai_generations_used,
                "ad_spend_monitored": usage.ad_spend_monitored,
                "breakdown": {
                    "images_generated": usage.images_generated,
                    "videos_generated": usage.videos_generated,
                    "text_generations": usage.text_generations,
                    "analytics_exports": usage.analytics_exports,
                    "custom_reports": usage.custom_reports_generated,
                    "api_calls": usage.api_calls_made
                }
            },
            "limits": limits_check["limits"],
            "usage_percentages": limits_check["usage_percentages"],
            "within_limits": limits_check["within_limits"],
            "warnings": limits_check["warnings"],
            "validation": limits_check["validation"]
        }
    
    @staticmethod
    def check_action_allowed(db: Session, user_id: str, action: str) -> Dict[str, Any]:
        """Check if a specific action is allowed based on current usage"""
        
        limits_check = UsageTrackingCRUD.check_tier_limits(db, user_id, settings)
        
        # Map actions to validation checks
        action_mapping = {
            "create_campaign": "campaigns_ok",
            "generate_ai_content": "ai_generations_ok",
            "monitor_ad_spend": "ad_spend_ok"
        }
        
        if action not in action_mapping:
            return {
                "allowed": False,
                "reason": f"Unknown action: {action}"
            }
        
        validation_key = action_mapping[action]
        is_allowed = limits_check["validation"].get(validation_key, False)
        
        result = {
            "action": action,
            "allowed": is_allowed,
            "current_tier": limits_check["tier"],
            "usage": limits_check["usage"],
            "limits": limits_check["limits"]
        }
        
        if not is_allowed:
            if action == "create_campaign":
                result["reason"] = f"Campaign limit reached ({limits_check['usage']['campaigns']}/{limits_check['limits']['campaigns']})"
            elif action == "generate_ai_content":
                result["reason"] = f"AI generation limit reached ({limits_check['usage']['ai_generations']}/{limits_check['limits']['ai_generations']})"
            elif action == "monitor_ad_spend":
                result["reason"] = f"Ad spend monitoring limit reached (₹{limits_check['usage']['ad_spend']}/₹{limits_check['limits']['ad_spend']})"
            
            # Suggest upgrade
            current_tier = limits_check["tier"]
            if current_tier == "basic":
                result["upgrade_suggestion"] = "professional"
            elif current_tier == "professional":
                result["upgrade_suggestion"] = "business"
        
        return result
    
    @staticmethod
    def get_tier_recommendations(db: Session, user_id: str) -> Dict[str, Any]:
        """Get tier recommendations based on usage patterns"""
        
        usage_summary = UsageTrackingService.get_usage_summary(db, user_id)
        current_tier = usage_summary["current_tier"]
        usage_pct = usage_summary["usage_percentages"]
        
        recommendations = []
        
        # Check if user is hitting limits frequently
        high_usage_threshold = 80  # 80% or more
        
        if current_tier == "basic":
            if (usage_pct.get("campaigns", 0) >= high_usage_threshold or 
                usage_pct.get("ai_generations", 0) >= high_usage_threshold):
                recommendations.append({
                    "suggested_tier": "professional",
                    "reason": "You're approaching limits on your current plan",
                    "benefits": [
                        "20 campaigns vs 5 campaigns", 
                        "500 AI generations vs 150",
                        "₹1L ad spend monitoring vs ₹25K"
                    ],
                    "price_difference": 5000  # ₹7999 - ₹2999
                })
        
        elif current_tier == "professional":
            if (usage_pct.get("campaigns", 0) >= high_usage_threshold or 
                usage_pct.get("ai_generations", 0) >= high_usage_threshold):
                recommendations.append({
                    "suggested_tier": "business", 
                    "reason": "Scale up for enterprise-level marketing",
                    "benefits": [
                        "50 campaigns vs 20 campaigns",
                        "1,200 AI generations vs 500", 
                        "₹5L ad spend monitoring vs ₹1L",
                        "Advanced analytics and reporting"
                    ],
                    "price_difference": 12000  # ₹19999 - ₹7999
                })
        
        return {
            "current_tier": current_tier,
            "usage_analysis": usage_summary,
            "recommendations": recommendations,
            "optimal_tier": current_tier if not recommendations else recommendations[0]["suggested_tier"]
        }
    
    @staticmethod 
    def reset_usage_period(db: Session, user_id: str) -> Dict[str, Any]:
        """Reset usage for new billing period (typically called by scheduler)"""
        
        try:
            new_usage = UsageTrackingCRUD.reset_usage_period(db, user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "new_period_start": new_usage.period_start,
                "new_period_end": new_usage.period_end,
                "reset_count": new_usage.reset_count,
                "message": "Usage period reset successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "message": "Failed to reset usage period"
            }