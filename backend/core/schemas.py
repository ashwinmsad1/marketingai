"""
Pydantic schemas for request/response validation and budget safety controls
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class SubscriptionTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class CampaignType(str, Enum):
    QUICK = "quick"
    IMAGE = "image"
    VIDEO = "video"
    VIRAL = "viral"
    CUSTOM = "custom"

class PlatformName(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"

class BudgetValidationError(Exception):
    """Custom exception for budget validation errors"""
    pass

class PlatformSettings(BaseModel):
    """Platform-specific settings for campaigns"""
    facebook: bool = False
    instagram: bool = False

    @root_validator
    def validate_at_least_one_platform(cls, values):
        """Ensure at least one platform is selected"""
        if not any(values.values()):
            raise ValueError("At least one platform must be selected")
        return values

class CampaignBudget(BaseModel):
    """Budget configuration with safety validations"""
    daily_budget: Optional[float] = Field(None, ge=1.0, description="Daily budget in USD")
    total_budget: Optional[float] = Field(None, ge=1.0, description="Total campaign budget in USD")
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="Campaign duration in days")

    @root_validator
    def validate_budget_consistency(cls, values):
        """Validate budget consistency and safety limits"""
        daily = values.get('daily_budget')
        total = values.get('total_budget')
        duration = values.get('duration_days')
        
        # Ensure at least one budget type is specified
        if not daily and not total:
            raise ValueError("Either daily_budget or total_budget must be specified")
        
        # If both are specified, ensure consistency
        if daily and total and duration:
            expected_total = daily * duration
            if abs(expected_total - total) > 0.01:  # Allow small rounding differences
                raise ValueError(f"Budget inconsistency: {daily} * {duration} days = {expected_total}, but total_budget is {total}")
        
        # Calculate missing values
        if daily and duration and not total:
            values['total_budget'] = daily * duration
        elif total and duration and not daily:
            values['daily_budget'] = total / duration
            
        return values
    
    @validator('daily_budget')
    def validate_daily_budget_limit(cls, v):
        """Validate daily budget doesn't exceed safety limits"""
        if v and v > 20000:  # ₹20,000 daily limit for safety
            raise ValueError("Daily budget cannot exceed ₹20,000 for safety reasons")
        return v
    
    @validator('total_budget')
    def validate_total_budget_limit(cls, v):
        """Validate total budget doesn't exceed safety limits"""
        if v and v > 500000:  # ₹5,00,000 total limit for safety
            raise ValueError("Total budget cannot exceed ₹5,00,000 for safety reasons")
        return v

class CampaignTargeting(BaseModel):
    """Campaign targeting configuration"""
    age_min: Optional[int] = Field(None, ge=13, le=65, description="Minimum age for targeting")
    age_max: Optional[int] = Field(None, ge=13, le=65, description="Maximum age for targeting") 
    locations: Optional[List[str]] = Field(default_factory=list, description="Geographic targeting")
    interests: Optional[List[str]] = Field(default_factory=list, description="Interest targeting")
    custom_audiences: Optional[List[str]] = Field(default_factory=list, description="Custom audience IDs")

    @root_validator
    def validate_age_range(cls, values):
        """Ensure age range is valid"""
        age_min = values.get('age_min')
        age_max = values.get('age_max')
        
        if age_min and age_max and age_min > age_max:
            raise ValueError("age_min cannot be greater than age_max")
        
        return values

class CampaignCreateRequest(BaseModel):
    """Request model for campaign creation with comprehensive validation"""
    
    # Basic campaign info
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, max_length=1000, description="Campaign description")
    type: CampaignType = Field(default=CampaignType.QUICK, description="Campaign type")
    
    # Content
    prompt: str = Field(..., min_length=10, max_length=2000, description="Content generation prompt")
    caption: Optional[str] = Field(None, max_length=2200, description="Social media caption")
    style: Optional[str] = Field("cinematic", description="Visual style for content")
    aspect_ratio: Optional[str] = Field("16:9", description="Aspect ratio for video content")
    
    # Custom campaign fields (for CUSTOM type)
    business_description: Optional[str] = Field(None, max_length=1500, description="User's business description")
    target_audience: Optional[str] = Field(None, max_length=1000, description="Target audience description")
    campaign_goal: Optional[str] = Field(None, description="Campaign objective/goal")
    
    # Platform configuration
    platforms: PlatformSettings = Field(..., description="Platform selection")
    
    # Budget and targeting
    budget: CampaignBudget = Field(..., description="Budget configuration")
    targeting: Optional[CampaignTargeting] = Field(default_factory=CampaignTargeting, description="Targeting settings")
    
    # Advanced settings
    auto_optimization: bool = Field(True, description="Enable automatic optimization")
    schedule_start: Optional[datetime] = Field(None, description="Campaign start time")
    schedule_end: Optional[datetime] = Field(None, description="Campaign end time")

    @validator('prompt')
    def validate_prompt_content(cls, v):
        """Validate prompt content for safety and quality"""
        # Check for minimum meaningful content
        if len(v.strip()) < 10:
            raise ValueError("Prompt must be at least 10 characters long")
        
        # Basic content safety checks (extend as needed)
        prohibited_words = ['spam', 'scam', 'fake', 'illegal']
        if any(word in v.lower() for word in prohibited_words):
            raise ValueError("Prompt contains prohibited content")
        
        return v.strip()
    
    @validator('caption')
    def validate_caption_length(cls, v):
        """Validate caption meets platform requirements"""
        if v and len(v) > 2200:  # Instagram/Facebook limit
            raise ValueError("Caption cannot exceed 2,200 characters")
        return v
    
    @root_validator
    def validate_schedule(cls, values):
        """Validate campaign scheduling"""
        start = values.get('schedule_start')
        end = values.get('schedule_end')
        
        if start and end:
            if start >= end:
                raise ValueError("Campaign start time must be before end time")
            
            # Don't allow campaigns longer than 1 year
            if (end - start).days > 365:
                raise ValueError("Campaign duration cannot exceed 365 days")
        
        return values

class BudgetValidationResult(BaseModel):
    """Result of budget validation checks"""
    is_valid: bool
    remaining_budget: float
    monthly_limit: float
    campaigns_this_month: int
    max_campaigns_per_month: int
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

class CampaignResponse(BaseModel):
    """Response model for campaign operations"""
    success: bool
    message: Optional[str] = None
    campaign_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    budget_validation: Optional[BudgetValidationResult] = None
    warnings: List[str] = Field(default_factory=list)

class RateLimitInfo(BaseModel):
    """Rate limiting information"""
    requests_remaining: int
    reset_time: datetime
    requests_per_minute: int

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    rate_limit_info: Optional[RateLimitInfo] = None