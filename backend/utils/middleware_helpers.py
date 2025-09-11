"""
Middleware Helper Functions
Utilities for working with tier enforcement middleware
"""

from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class UsageTrackingSetupMiddleware(BaseHTTPMiddleware):
    """Middleware to set up user context for tier enforcement"""
    
    async def dispatch(self, request: Request, call_next):
        """Set up user context from authentication"""
        
        # In a real implementation, this would extract user info from JWT token
        # For now, we'll use dummy values or headers for testing
        
        # Extract user info (from headers in development, JWT in production)
        user_id = request.headers.get('x-user-id')
        user_tier = request.headers.get('x-user-tier', 'basic')
        
        # Set user context in request state for tier enforcement decorators
        if user_id:
            request.state.user_id = user_id
            request.state.user_tier = user_tier
        
        response = await call_next(request)
        return response


class TierEnforcementResponseHelper:
    """Helper for creating standardized tier enforcement responses"""
    
    @staticmethod
    def create_limit_exceeded_response(
        message: str,
        current_tier: str,
        suggested_tier: Optional[str] = None,
        usage_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized response for limit exceeded errors"""
        
        response = {
            "error": "tier_limit_exceeded",
            "message": message,
            "current_tier": current_tier,
            "timestamp": "2024-01-01T00:00:00Z",  # Would use datetime.utcnow() in real implementation
            "error_code": "TIER_LIMIT_EXCEEDED"
        }
        
        if suggested_tier:
            response["upgrade_suggestion"] = {
                "suggested_tier": suggested_tier,
                "upgrade_url": f"/subscription/upgrade/{suggested_tier}",
                "benefits": get_tier_benefits(suggested_tier)
            }
        
        if usage_info:
            response["usage_details"] = usage_info
        
        return response
    
    @staticmethod
    def create_feature_unavailable_response(
        feature: str,
        current_tier: str,
        required_tier: str
    ) -> Dict[str, Any]:
        """Create response for feature not available in current tier"""
        
        return {
            "error": "feature_unavailable",
            "message": f"Feature '{feature}' requires {required_tier} tier or higher",
            "current_tier": current_tier,
            "required_tier": required_tier,
            "feature": feature,
            "upgrade_suggestion": {
                "suggested_tier": required_tier,
                "upgrade_url": f"/subscription/upgrade/{required_tier}",
                "benefits": get_tier_benefits(required_tier)
            },
            "error_code": "FEATURE_UNAVAILABLE"
        }
    
    @staticmethod
    def create_usage_warning_response(
        warnings: list,
        current_tier: str
    ) -> Dict[str, Any]:
        """Create response for usage warnings"""
        
        return {
            "status": "warning",
            "message": "Approaching tier limits",
            "current_tier": current_tier,
            "warnings": warnings,
            "recommendations": [
                "Consider upgrading your subscription tier",
                "Monitor your usage to avoid interruptions",
                "Contact support if you need assistance"
            ]
        }


def get_tier_benefits(tier: str) -> list:
    """Get benefits list for a tier (used in upgrade suggestions)"""
    
    benefits = {
        "professional": [
            "20 campaigns per month (vs 5 in Basic)",
            "500 AI generations per month (vs 150 in Basic)",
            "₹1,00,000 ad spend monitoring (vs ₹25,000 in Basic)",
            "Priority email support",
            "Enhanced analytics",
            "Performance tracking"
        ],
        "business": [
            "50 campaigns per month (vs 20 in Professional)",
            "1,200 AI generations per month (vs 500 in Professional)",
            "₹5,00,000 ad spend monitoring (vs ₹1,00,000 in Professional)",
            "Premium email support",
            "Full analytics suite",
            "Advanced performance tracking",
            "Data export capabilities",
            "Custom reporting"
        ]
    }
    
    return benefits.get(tier, [])


class UsageAlertHelper:
    """Helper for generating usage alerts and notifications"""
    
    @staticmethod
    def should_send_alert(usage_percentage: float, tier: str) -> bool:
        """Determine if an alert should be sent based on usage percentage"""
        
        # Send alerts at different thresholds based on tier
        alert_thresholds = {
            "basic": [75, 90, 95, 100],      # More frequent alerts for basic tier
            "professional": [80, 95, 100],   # Less frequent for professional
            "business": [90, 100]            # Minimal alerts for business
        }
        
        thresholds = alert_thresholds.get(tier, [90, 100])
        return any(usage_percentage >= threshold for threshold in thresholds)
    
    @staticmethod
    def generate_alert_message(
        metric: str,
        usage_percentage: float,
        current_tier: str
    ) -> Dict[str, Any]:
        """Generate an alert message for usage approaching limits"""
        
        urgency = "high" if usage_percentage >= 95 else "medium" if usage_percentage >= 90 else "low"
        
        message_templates = {
            "campaigns": "You've used {:.1f}% of your campaign creation limit",
            "ai_generations": "You've used {:.1f}% of your AI generation limit", 
            "ad_spend": "You've used {:.1f}% of your ad spend monitoring limit"
        }
        
        base_message = message_templates.get(metric, "You've used {:.1f}% of your {} limit")
        
        return {
            "type": "usage_alert",
            "urgency": urgency,
            "metric": metric,
            "usage_percentage": usage_percentage,
            "message": base_message.format(usage_percentage),
            "current_tier": current_tier,
            "recommendations": get_usage_recommendations(metric, usage_percentage, current_tier),
            "action_required": usage_percentage >= 95
        }
    
    @staticmethod
    def get_bulk_alerts(usage_summary: Dict[str, Any]) -> list:
        """Generate all relevant alerts for a user's current usage"""
        
        alerts = []
        tier = usage_summary.get("current_tier", "basic")
        usage_percentages = usage_summary.get("usage_percentages", {})
        
        for metric, percentage in usage_percentages.items():
            if UsageAlertHelper.should_send_alert(percentage, tier):
                alert = UsageAlertHelper.generate_alert_message(metric, percentage, tier)
                alerts.append(alert)
        
        return alerts


def get_usage_recommendations(metric: str, usage_percentage: float, tier: str) -> list:
    """Get usage recommendations based on metric and usage level"""
    
    recommendations = []
    
    if usage_percentage >= 95:
        recommendations.append("Immediate action required - limit will be reached soon")
        if tier != "business":
            recommendations.append("Consider upgrading your subscription tier")
    elif usage_percentage >= 90:
        recommendations.append("Monitor usage closely to avoid hitting limits")
        recommendations.append("Plan upgrade if usage continues to grow")
    elif usage_percentage >= 75:
        recommendations.append("Usage is approaching limits")
        recommendations.append("Review your monthly usage patterns")
    
    # Metric-specific recommendations
    if metric == "campaigns":
        if usage_percentage >= 80:
            recommendations.append("Consider consolidating similar campaigns")
            recommendations.append("Archive completed campaigns to free up quota")
    elif metric == "ai_generations":
        if usage_percentage >= 80:
            recommendations.append("Reuse existing AI-generated content when possible")
            recommendations.append("Optimize prompts to reduce generation attempts")
    elif metric == "ad_spend":
        if usage_percentage >= 80:
            recommendations.append("Review ad spend allocation across campaigns")
            recommendations.append("Consider pausing underperforming campaigns")
    
    return recommendations


class TierUpgradeHelper:
    """Helper for tier upgrade workflows"""
    
    @staticmethod
    def calculate_upgrade_benefits(current_tier: str, target_tier: str) -> Dict[str, Any]:
        """Calculate the benefits of upgrading from current to target tier"""
        
        from backend.utils.usage_helpers import UsageHelpers
        
        comparison = UsageHelpers.get_tier_comparison(current_tier, target_tier)
        
        return {
            "current_tier": current_tier,
            "target_tier": target_tier,
            "limit_increases": {
                "campaigns": comparison["differences"]["campaigns"]["increase"],
                "ai_generations": comparison["differences"]["ai_generations"]["increase"],
                "ad_spend": comparison["differences"]["ad_spend"]["increase"]
            },
            "new_features": comparison["new_features"],
            "cost": {
                "monthly_increase": comparison["pricing"]["monthly_difference"],
                "annual_increase": comparison["pricing"]["annual_difference"]
            }
        }
    
    @staticmethod
    def get_upgrade_urgency(usage_summary: Dict[str, Any]) -> str:
        """Determine upgrade urgency based on usage patterns"""
        
        usage_percentages = usage_summary.get("usage_percentages", {})
        max_usage = max(usage_percentages.values()) if usage_percentages else 0
        
        if max_usage >= 100:
            return "critical"  # Already exceeded limits
        elif max_usage >= 95:
            return "high"      # Very close to limits
        elif max_usage >= 85:
            return "medium"    # Approaching limits
        elif max_usage >= 70:
            return "low"       # Getting close
        else:
            return "none"      # Plenty of room
    
    @staticmethod
    def suggest_optimal_tier(
        projected_usage: Dict[str, Any],
        current_tier: str
    ) -> Dict[str, Any]:
        """Suggest optimal tier based on projected usage"""
        
        from backend.utils.usage_helpers import UsageHelpers
        
        estimate = UsageHelpers.estimate_monthly_cost(
            campaigns=projected_usage.get("campaigns", 0),
            ai_generations=projected_usage.get("ai_generations", 0),
            ad_spend=projected_usage.get("ad_spend", 0.0)
        )
        
        optimal_tier = estimate["optimal_tier"]["tier"]
        
        return {
            "current_tier": current_tier,
            "recommended_tier": optimal_tier,
            "reason": estimate["recommendation"],
            "cost_analysis": estimate,
            "upgrade_needed": optimal_tier != current_tier,
            "urgency": TierUpgradeHelper.get_upgrade_urgency({"usage_percentages": projected_usage})
        }