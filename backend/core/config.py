"""
Core configuration for the AI Marketing Automation Platform
"""

import os
from typing import Optional, Dict, Any, List
try:
    from pydantic_settings import BaseSettings
    from pydantic import validator
except ImportError:
    from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "AI Marketing Automation Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Professional AI-powered marketing automation for Indian businesses"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: Optional[str] = None
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if v and (v == "your-secret-key-here" or v == "changeme" or len(v) < 16):
            raise ValueError('SECRET_KEY must be changed from default and be at least 16 characters long')
        return v
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/marketingai"
    
    # AI Service Keys
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPEN_ROUTER_API_KEY: Optional[str] = None
    
    # Meta/Facebook
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_REDIRECT_URI: Optional[str] = None
    
    # Payment (Indian market focused)
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://yourapp.com"
    ]
    
    # Budget Safety Limits (in Indian Rupees - realistic market values)
    BUDGET_VALIDATION_ENABLED: bool = True
    MAX_CAMPAIGN_BUDGET: float = 500000.0   # Maximum budget per campaign (₹5,00,000)
    MIN_CAMPAIGN_BUDGET: float = 1000.0     # Minimum budget per campaign (₹1,000)
    
    # Subscription Tier Budget Limits (monthly in INR - Indian market pricing)
    STARTER_MONTHLY_LIMIT: float = 25000.0      # ₹25,000/month for small businesses
    PROFESSIONAL_MONTHLY_LIMIT: float = 100000.0  # ₹1,00,000/month for growing businesses
    ENTERPRISE_MONTHLY_LIMIT: float = -1.0     # Unlimited for large enterprises
    
    # New Pricing Tiers Configuration (Final Implementation)
    PRICING_TIERS: Dict[str, Dict[str, Any]] = {
        "basic": {
            "name": "Basic",
            "price_monthly": 2999,
            "price_annual": 29990,  # 17% discount
            "campaigns_limit": 5,
            "ai_generations_limit": 150,  # Increased for customer satisfaction
            "ad_spend_monitoring_limit": 25000,  # ₹25,000
            "support_level": "email",
            "features": [
                "ai_campaign_creation",
                "meta_ads_automation", 
                "basic_analytics",
                "budget_monitoring",
                "email_support"
            ]
        },
        "professional": {
            "name": "Professional", 
            "price_monthly": 7999,
            "price_annual": 79990,  # 17% discount
            "campaigns_limit": 20,
            "ai_generations_limit": 500,  # Increased for customer satisfaction
            "ad_spend_monitoring_limit": 100000,  # ₹1,00,000
            "support_level": "email_priority",
            "features": [
                "ai_campaign_creation",
                "meta_ads_automation",
                "enhanced_analytics", 
                "advanced_budget_monitoring",
                "priority_email_support",
                "performance_tracking"
            ]
        },
        "business": {
            "name": "Business",
            "price_monthly": 19999,
            "price_annual": 199990,  # 17% discount  
            "campaigns_limit": 50,
            "ai_generations_limit": 1200,  # Increased for customer satisfaction
            "ad_spend_monitoring_limit": 500000,  # ₹5,00,000
            "support_level": "email_premium",
            "features": [
                "ai_campaign_creation",
                "meta_ads_automation",
                "full_analytics_suite",
                "comprehensive_budget_monitoring", 
                "premium_email_support",
                "advanced_performance_tracking",
                "data_export",
                "custom_reporting"
            ]
        }
    }
    
    # Usage tracking settings
    USAGE_RESET_DAY: int = 1  # Reset on 1st of each month
    USAGE_WARNING_THRESHOLDS: List[float] = [0.75, 0.9, 0.95]  # 75%, 90%, 95%
    
    @validator("DATABASE_URL", pre=True)
    def build_db_url(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://user:password@localhost:5432/marketingai"
    
    @validator("DEBUG", pre=True)
    def set_debug_mode(cls, v: str, values: dict) -> bool:
        return values.get("ENVIRONMENT", "development") == "development"
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: Optional[str]) -> str:
        """Validate SECRET_KEY is configured and secure"""
        if not v:
            return "default-key-for-testing-1234567890abcdefghijklmnop"  # Fallback for testing
        if v in ["your-secret-key-here", "", "secret", "change-me"]:
            raise ValueError(
                "SECRET_KEY must be configured with a secure random string. "
                "Use 'python -c \"import secrets; print(secrets.token_urlsafe(32))\"' to generate one."
            )
        if len(v) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters long for security.")
        return v
    
    @validator("ANTHROPIC_API_KEY", pre=True)
    def validate_anthropic_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate Anthropic API key format if provided"""
        if v and not v.startswith("sk-ant-"):
            raise ValueError("Invalid Anthropic API key format. Must start with 'sk-ant-'")
        return v
    
    # New Pricing Tier Helper Methods
    def get_tier_config(self, tier: str) -> dict:
        """Get configuration for specific tier"""
        return self.PRICING_TIERS.get(tier, self.PRICING_TIERS["basic"])
    
    def validate_tier_limits(self, tier: str, usage: dict) -> dict:
        """Validate if usage is within tier limits"""
        config = self.get_tier_config(tier)
        return {
            "campaigns_ok": usage.get("campaigns", 0) <= config["campaigns_limit"],
            "ai_generations_ok": usage.get("ai_generations", 0) <= config["ai_generations_limit"],
            "ad_spend_ok": usage.get("ad_spend", 0) <= config["ad_spend_monitoring_limit"]
        }
    
    def get_pricing_for_tier(self, tier: str, billing_cycle: str = "monthly") -> int:
        """Get pricing for specific tier and billing cycle"""
        config = self.get_tier_config(tier)
        return config[f"price_{billing_cycle}"]
    
    def is_ml_predictions_enabled(self) -> bool:
        """Check if ML predictions are enabled (Anthropic API key is configured)"""
        return bool(self.ANTHROPIC_API_KEY)
    
    def get_ml_config(self) -> dict:
        """Get ML-related configuration"""
        return {
            "enabled": self.is_ml_predictions_enabled(),
            "api_key_configured": bool(self.ANTHROPIC_API_KEY),
            "model_version": "claude-3.5-sonnet-20241022",
            "cache_ttl_hours": 24,
            "max_cache_entries": 1000,
            "fallback_enabled": True,
            "prediction_types": [
                "campaign_performance",
                "viral_potential", 
                "audience_response",
                "content_effectiveness",
                "budget_optimization"
            ],
            "supported_metrics": [
                "roi", "ctr", "conversion_rate", "engagement_rate",
                "reach", "impressions", "clicks", "cost_per_click",
                "cost_per_conversion", "share_rate", "comment_rate"
            ],
            "cache_cleanup_interval_hours": 6,
            "max_prediction_age_days": 30
        }
    
    def get_ml_prediction_limits(self, tier: str = "starter") -> dict:
        """Get ML prediction limits by subscription tier"""
        limits = {
            "starter": {
                "max_predictions_per_day": 10,
                "max_predictions_per_month": 100,
                "cache_enabled": True,
                "advanced_scenarios": False
            },
            "professional": {
                "max_predictions_per_day": 50,
                "max_predictions_per_month": 500,
                "cache_enabled": True,
                "advanced_scenarios": True
            },
            "enterprise": {
                "max_predictions_per_day": -1,  # Unlimited
                "max_predictions_per_month": -1,  # Unlimited
                "cache_enabled": True,
                "advanced_scenarios": True
            }
        }
        return limits.get(tier, limits["starter"])
    
    def get_budget_limits(self, tier: str = "starter") -> dict:
        """Get budget limits by subscription tier"""
        limits = {
            "starter": {
                "monthly_limit": self.STARTER_MONTHLY_LIMIT,
                "max_campaign_budget": min(self.MAX_CAMPAIGN_BUDGET, self.STARTER_MONTHLY_LIMIT),
                "min_campaign_budget": self.MIN_CAMPAIGN_BUDGET,
                "max_campaigns_per_month": 10,
                "requires_balance_check": True
            },
            "professional": {
                "monthly_limit": self.PROFESSIONAL_MONTHLY_LIMIT,
                "max_campaign_budget": min(self.MAX_CAMPAIGN_BUDGET, self.PROFESSIONAL_MONTHLY_LIMIT),
                "min_campaign_budget": self.MIN_CAMPAIGN_BUDGET,
                "max_campaigns_per_month": 50,
                "requires_balance_check": True
            },
            "enterprise": {
                "monthly_limit": self.ENTERPRISE_MONTHLY_LIMIT,  # -1 = unlimited
                "max_campaign_budget": self.MAX_CAMPAIGN_BUDGET,
                "min_campaign_budget": self.MIN_CAMPAIGN_BUDGET,
                "max_campaigns_per_month": -1,  # Unlimited
                "requires_balance_check": False  # Enterprise has credit terms
            }
        }
        return limits.get(tier, limits["starter"])

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()