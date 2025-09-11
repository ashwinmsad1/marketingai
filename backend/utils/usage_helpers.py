"""
Usage Tracking Helper Functions
Utility functions for common usage tracking operations
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from backend.core.config import settings


class UsageHelpers:
    """Helper functions for usage tracking and tier management"""
    
    @staticmethod
    def calculate_usage_percentage(current: int, limit: int) -> float:
        """Calculate usage percentage"""
        if limit <= 0:
            return 0.0
        return min((current / limit) * 100, 100.0)
    
    @staticmethod
    def get_tier_limits(tier: str) -> Dict[str, int]:
        """Get tier limits in a standardized format"""
        config = settings.get_tier_config(tier)
        return {
            "campaigns": config.get("campaigns_limit", 0),
            "ai_generations": config.get("ai_generations_limit", 0),  
            "ad_spend": config.get("ad_spend_monitoring_limit", 0)
        }
    
    @staticmethod
    def get_tier_features(tier: str) -> list:
        """Get available features for a tier"""
        config = settings.get_tier_config(tier)
        return config.get("features", [])
    
    @staticmethod
    def is_feature_available(tier: str, feature: str) -> bool:
        """Check if a feature is available in a tier"""
        features = UsageHelpers.get_tier_features(tier)
        return feature in features
    
    @staticmethod
    def get_next_reset_date(current_date: datetime = None) -> datetime:
        """Calculate next usage reset date (1st of next month)"""
        if current_date is None:
            current_date = datetime.utcnow()
        
        # Get next month
        if current_date.month == 12:
            next_year = current_date.year + 1
            next_month = 1
        else:
            next_year = current_date.year
            next_month = current_date.month + 1
        
        return datetime(next_year, next_month, settings.USAGE_RESET_DAY)
    
    @staticmethod
    def get_days_until_reset(current_date: datetime = None) -> int:
        """Get number of days until next usage reset"""
        if current_date is None:
            current_date = datetime.utcnow()
            
        next_reset = UsageHelpers.get_next_reset_date(current_date)
        return (next_reset - current_date).days
    
    @staticmethod
    def format_currency(amount: float, currency: str = "INR") -> str:
        """Format currency amounts for display"""
        if currency == "INR":
            if amount >= 100000:  # 1 lakh or more
                lakhs = amount / 100000
                return f"₹{lakhs:.1f}L"
            elif amount >= 1000:  # 1 thousand or more  
                thousands = amount / 1000
                return f"₹{thousands:.0f}K"
            else:
                return f"₹{amount:.0f}"
        else:
            return f"{amount:.2f} {currency}"
    
    @staticmethod
    def get_usage_status(percentage: float) -> Dict[str, Any]:
        """Get usage status information based on percentage"""
        if percentage >= 100:
            return {
                "status": "exceeded",
                "color": "red", 
                "message": "Limit exceeded",
                "severity": "critical"
            }
        elif percentage >= 95:
            return {
                "status": "critical",
                "color": "red",
                "message": "Near limit - action required",
                "severity": "high"
            }
        elif percentage >= 90:
            return {
                "status": "warning",
                "color": "orange",
                "message": "Approaching limit",
                "severity": "medium"
            }
        elif percentage >= 75:
            return {
                "status": "caution", 
                "color": "yellow",
                "message": "Moderate usage",
                "severity": "low"
            }
        else:
            return {
                "status": "normal",
                "color": "green",
                "message": "Usage within normal range",
                "severity": "none"
            }
    
    @staticmethod
    def generate_usage_warnings(usage_percentages: Dict[str, float]) -> list:
        """Generate usage warnings based on percentages"""
        warnings = []
        
        for metric, percentage in usage_percentages.items():
            status = UsageHelpers.get_usage_status(percentage)
            
            if status["severity"] in ["high", "critical"]:
                metric_name = metric.replace("_", " ").title()
                warnings.append({
                    "metric": metric,
                    "metric_name": metric_name,
                    "percentage": percentage,
                    "status": status,
                    "message": f"{metric_name}: {percentage:.1f}% used - {status['message']}"
                })
        
        return warnings
    
    @staticmethod
    def get_tier_upgrade_path(current_tier: str) -> Optional[str]:
        """Get the next tier in upgrade path"""
        upgrade_path = {
            "basic": "professional",
            "professional": "business", 
            "business": None  # No upgrade from business
        }
        return upgrade_path.get(current_tier)
    
    @staticmethod
    def calculate_tier_cost_difference(from_tier: str, to_tier: str, billing_cycle: str = "monthly") -> int:
        """Calculate cost difference between tiers"""
        from_price = settings.get_pricing_for_tier(from_tier, billing_cycle)
        to_price = settings.get_pricing_for_tier(to_tier, billing_cycle)
        return to_price - from_price
    
    @staticmethod
    def get_tier_comparison(tier1: str, tier2: str) -> Dict[str, Any]:
        """Compare two tiers and show differences"""
        config1 = settings.get_tier_config(tier1)
        config2 = settings.get_tier_config(tier2)
        
        comparison = {
            "tier1": tier1,
            "tier2": tier2,
            "differences": {
                "campaigns": {
                    "tier1": config1["campaigns_limit"],
                    "tier2": config2["campaigns_limit"],
                    "increase": config2["campaigns_limit"] - config1["campaigns_limit"]
                },
                "ai_generations": {
                    "tier1": config1["ai_generations_limit"],
                    "tier2": config2["ai_generations_limit"], 
                    "increase": config2["ai_generations_limit"] - config1["ai_generations_limit"]
                },
                "ad_spend": {
                    "tier1": config1["ad_spend_monitoring_limit"],
                    "tier2": config2["ad_spend_monitoring_limit"],
                    "increase": config2["ad_spend_monitoring_limit"] - config1["ad_spend_monitoring_limit"]
                }
            },
            "pricing": {
                "monthly_difference": UsageHelpers.calculate_tier_cost_difference(tier1, tier2, "monthly"),
                "annual_difference": UsageHelpers.calculate_tier_cost_difference(tier1, tier2, "annual")
            },
            "new_features": list(set(config2.get("features", [])) - set(config1.get("features", [])))
        }
        
        return comparison
    
    @staticmethod
    def estimate_monthly_cost(
        campaigns: int,
        ai_generations: int, 
        ad_spend: float
    ) -> Dict[str, Any]:
        """Estimate which tier would be most cost-effective for given usage"""
        
        tiers = ["basic", "professional", "business"]
        recommendations = []
        
        for tier in tiers:
            limits = UsageHelpers.get_tier_limits(tier)
            monthly_price = settings.get_pricing_for_tier(tier, "monthly")
            
            # Check if usage fits within tier limits
            fits = (
                campaigns <= limits["campaigns"] and
                ai_generations <= limits["ai_generations"] and
                ad_spend <= limits["ad_spend"]
            )
            
            recommendations.append({
                "tier": tier,
                "monthly_price": monthly_price,
                "fits": fits,
                "limits": limits,
                "usage_percentages": {
                    "campaigns": UsageHelpers.calculate_usage_percentage(campaigns, limits["campaigns"]),
                    "ai_generations": UsageHelpers.calculate_usage_percentage(ai_generations, limits["ai_generations"]),
                    "ad_spend": UsageHelpers.calculate_usage_percentage(ad_spend, limits["ad_spend"])
                }
            })
        
        # Find the most cost-effective tier that fits
        suitable_tiers = [r for r in recommendations if r["fits"]]
        
        if suitable_tiers:
            optimal_tier = min(suitable_tiers, key=lambda x: x["monthly_price"])
        else:
            # If no tier fits, recommend the highest tier
            optimal_tier = recommendations[-1]
        
        return {
            "estimated_usage": {
                "campaigns": campaigns,
                "ai_generations": ai_generations,
                "ad_spend": ad_spend
            },
            "tier_analysis": recommendations,
            "optimal_tier": optimal_tier,
            "monthly_cost": optimal_tier["monthly_price"],
            "recommendation": f"Based on your estimated usage, the {optimal_tier['tier'].title()} tier (₹{optimal_tier['monthly_price']:,}/month) would be most suitable."
        }