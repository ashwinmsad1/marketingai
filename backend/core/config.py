"""
Core configuration for the AI Marketing Automation Platform

CLEANED UP VERSION:
- Removed duplicate SECRET_KEY validator
- Removed unused API keys (OpenAI, OpenRouter)
- Removed duplicate monthly limit constants (use PRICING_TIERS instead)
- Removed redundant get_budget_limits and get_ml_prediction_limits methods
- Consolidated all pricing configuration into single PRICING_TIERS source of truth
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
    JWT_ALGORITHM: str = "HS256"
    
    # Removed: Duplicate SECRET_KEY validator (see line 157)
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/marketingai"
    
    # AI Service Keys
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    # Removed: OPENAI_API_KEY and OPEN_ROUTER_API_KEY (unused)
    
    # Meta/Facebook
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_REDIRECT_URI: Optional[str] = None
    META_ACCESS_TOKEN: Optional[str] = None
    META_AD_ACCOUNT_ID: Optional[str] = None
    INSTAGRAM_BUSINESS_ID: Optional[str] = None
    
    # Meta API Configuration
    META_API_VERSION: str = "v21.0"
    META_API_TIMEOUT: int = 30
    META_API_RETRY_COUNT: int = 3
    
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
    
    # Removed: Duplicate monthly limits (use PRICING_TIERS['tier']['ad_spend_monitoring_limit'] instead)
    
    # Pricing Tiers Configuration
    PRICING_TIERS: Dict[str, Dict[str, Any]] = {
        "basic": {
            "name": "Basic",
            "price_monthly": 2999,
            "price_annual": 29990,  # 17% discount
            "campaigns_limit": 5,
            "ai_generations_limit": 150,
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
            "ai_generations_limit": 500,
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
            "ai_generations_limit": 1200,
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
    
    # Removed: get_ml_prediction_limits method (unused - ML prediction limits can be added to PRICING_TIERS if needed)
    
    # Removed: get_budget_limits method (use PRICING_TIERS directly - data already available there)

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()