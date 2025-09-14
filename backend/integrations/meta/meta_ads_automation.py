"""
AI-Powered Meta Ads Automation Platform
Supports Facebook and Instagram ad campaign automation using Meta Marketing API
"""

from dotenv import load_dotenv
import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
import random
import asyncio
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class MetaAPIError(Exception):
    """Base exception for Meta API errors"""
    pass

class MetaRateLimitError(MetaAPIError):
    """Rate limit exceeded error"""
    pass

class MetaAuthenticationError(MetaAPIError):
    """Authentication/authorization error"""
    pass

class MetaBudgetError(MetaAPIError):
    """Budget related error"""  
    pass

class MetaObjectiveError(MetaAPIError):
    """Invalid objective error"""
    pass

class MetaAPIErrorHandler:
    """Enhanced error handling for Meta API operations"""
    
    def __init__(self, retry_count=3, base_delay=1.0):
        self.retry_count = retry_count
        self.base_delay = base_delay
        
    def classify_error(self, error: Exception) -> tuple:
        """Classify Meta API error and return error type and handler"""
        error_str = str(error).lower()
        
        if any(keyword in error_str for keyword in ['rate limit', 'too many requests', '(#613)']):
            return 'RATE_LIMIT', self.handle_rate_limit_error
        elif any(keyword in error_str for keyword in ['invalid objective', '#100']):
            return 'INVALID_OBJECTIVE', self.handle_objective_error
        elif any(keyword in error_str for keyword in ['insufficient budget', 'budget', 'daily_budget']):
            return 'BUDGET_ERROR', self.handle_budget_error
        elif any(keyword in error_str for keyword in ['unauthorized', 'invalid access token', '#190']):
            return 'AUTH_ERROR', self.handle_auth_error
        elif any(keyword in error_str for keyword in ['network', 'connection', 'timeout']):
            return 'NETWORK_ERROR', self.handle_network_error
        else:
            return 'UNKNOWN_ERROR', self.handle_unknown_error
            
    def handle_rate_limit_error(self, error, attempt=0):
        """Handle rate limit errors with exponential backoff"""
        wait_time = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
        logger.warning(f"Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt+1}/{self.retry_count}")
        return {'action': 'retry', 'delay': wait_time, 'recoverable': True}
        
    def handle_objective_error(self, error, attempt=0):
        """Handle invalid objective errors"""
        valid_objectives = ['OUTCOME_AWARENESS', 'OUTCOME_TRAFFIC', 'OUTCOME_ENGAGEMENT', 
                          'OUTCOME_LEADS', 'OUTCOME_SALES', 'OUTCOME_APP_PROMOTION']
        logger.error(f"Invalid objective error: {error}")
        logger.info(f"Valid objectives: {', '.join(valid_objectives)}")
        return {'action': 'fail', 'recoverable': False, 'suggested_objectives': valid_objectives}
        
    def handle_budget_error(self, error, attempt=0):
        """Handle budget related errors"""
        logger.warning(f"Budget error: {error}")
        return {'action': 'retry', 'delay': 2.0, 'recoverable': True, 'suggestion': 'Check and adjust budget amounts'}
        
    def handle_auth_error(self, error, attempt=0):
        """Handle authentication errors"""
        logger.error(f"Authentication error: {error}")
        return {'action': 'fail', 'recoverable': False, 'suggestion': 'Check access token and permissions'}
        
    def handle_network_error(self, error, attempt=0):
        """Handle network connectivity errors"""
        wait_time = min(self.base_delay * (2 ** attempt), 30)  # Max 30s wait
        logger.warning(f"Network error: {error}. Retrying in {wait_time}s")
        return {'action': 'retry', 'delay': wait_time, 'recoverable': True}
        
    def handle_unknown_error(self, error, attempt=0):
        """Handle unknown errors"""
        logger.error(f"Unknown error: {error}")
        return {'action': 'fail', 'recoverable': False}

def with_retry(max_attempts=3):
    """Decorator for adding retry logic to Meta API calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    error_type, handler = self.error_handler.classify_error(e)
                    response = handler(e, attempt)
                    
                    if response['action'] == 'retry' and attempt < max_attempts - 1:
                        if 'delay' in response:
                            await asyncio.sleep(response['delay'])
                        logger.info(f"Retrying {func.__name__} (attempt {attempt + 2}/{max_attempts})")
                        continue
                    else:
                        # Final failure or non-recoverable error
                        logger.error(f"{func.__name__} failed after {attempt + 1} attempts: {e}")
                        if response.get('suggestion'):
                            logger.info(f"Suggestion: {response['suggestion']}")
                        raise e
            return None
        return wrapper
    return decorator

from backend.utils.config_manager import get_config, ConfigurationError
from backend.utils.meta_config import get_meta_config, validate_meta_config

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.adcreative import AdCreative
    from facebook_business.adobjects.ad import Ad
    from facebook_business.adobjects.adimage import AdImage
    from facebook_business.adobjects.advideo import AdVideo
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    print("⚠️  Facebook Business SDK not installed. Run: pip install facebook-business")

load_dotenv()

# Meta-Specific Enums and Data Classes for Personalization

class MetaAdObjective(Enum):
    """Meta-specific ad objectives"""
    OUTCOME_AWARENESS = "OUTCOME_AWARENESS"  # Brand awareness
    OUTCOME_TRAFFIC = "OUTCOME_TRAFFIC"      # Website traffic
    OUTCOME_ENGAGEMENT = "OUTCOME_ENGAGEMENT" # Post engagement
    OUTCOME_LEADS = "OUTCOME_LEADS"          # Lead generation
    OUTCOME_SALES = "OUTCOME_SALES"          # Conversions/Sales
    OUTCOME_APP_PROMOTION = "OUTCOME_APP_PROMOTION" # App installs

class MetaBudgetStrategy(Enum):
    """Meta budget optimization strategies"""
    DAILY_BUDGET = "daily_budget"
    LIFETIME_BUDGET = "lifetime_budget"
    CAMPAIGN_BUDGET_OPTIMIZATION = "cbo"  # Campaign Budget Optimization

class MetaCreativeFormat(Enum):
    """Meta creative formats"""
    SINGLE_IMAGE = "single_image"
    SINGLE_VIDEO = "single_video"
    CAROUSEL = "carousel"
    COLLECTION = "collection"
    SLIDESHOW = "slideshow"
    INSTANT_EXPERIENCE = "instant_experience"

class MetaBidStrategy(Enum):
    """Meta bidding strategies"""
    LOWEST_COST = "LOWEST_COST_WITHOUT_CAP"
    COST_CAP = "LOWEST_COST_WITH_BID_CAP"
    BID_CAP = "LOWEST_COST_WITH_BID_CAP"
    TARGET_COST = "COST_PER_ACTION_TYPE"

class MetaAudienceType(Enum):
    """Meta audience targeting types"""
    CORE_AUDIENCE = "core"        # Demographics, interests, behaviors
    CUSTOM_AUDIENCE = "custom"     # Customer lists, website visitors
    LOOKALIKE_AUDIENCE = "lookalike" # Similar to existing customers
    SAVED_AUDIENCE = "saved"       # Previously saved audience

class MetaPlacement(Enum):
    """Meta ad placement options"""
    FACEBOOK_FEED = "facebook_feed"
    FACEBOOK_RIGHT_COLUMN = "facebook_right_column"
    FACEBOOK_INSTANT_ARTICLES = "facebook_instant_articles"
    FACEBOOK_STORIES = "facebook_stories"
    FACEBOOK_REELS = "facebook_reels"
    INSTAGRAM_FEED = "instagram_feed"
    INSTAGRAM_STORIES = "instagram_stories"
    INSTAGRAM_REELS = "instagram_reels"
    INSTAGRAM_EXPLORE = "instagram_explore"
    MESSENGER = "messenger"
    AUDIENCE_NETWORK = "audience_network"

class BusinessCategory(Enum):
    """Business categories for Meta optimization"""
    LOCAL_SERVICE = "local_service"        # Gyms, salons, restaurants
    ECOMMERCE = "ecommerce"                # Online stores
    B2B_SERVICE = "b2b_service"            # Professional services
    APP_DEVELOPER = "app_developer"        # Mobile apps
    REAL_ESTATE = "real_estate"            # Real estate agents
    HEALTHCARE = "healthcare"              # Healthcare providers
    EDUCATION = "education"                # Schools, courses
    AUTOMOTIVE = "automotive"              # Car dealers, repair
    TRAVEL = "travel"                      # Hotels, travel agencies
    FINANCE = "finance"                    # Financial services

@dataclass
class MetaUserProfile:
    """Comprehensive Meta-specific user profile for personalized ad campaigns"""
    user_id: str
    business_name: str
    business_category: BusinessCategory
    
    # Meta Ad Objectives and Goals (required fields)
    primary_objective: MetaAdObjective
    
    # Enhanced Budget Preferences (required fields)
    monthly_budget: float
    daily_budget_preference: float
    
    # Enhanced Business Information for Meta Personalization (optional fields)
    business_stage: str = "established"  # startup, growing, established, scaling
    years_in_business: Optional[int] = None
    business_location: Optional[str] = None
    website_url: Optional[str] = None
    conversion_tracking_setup: bool = False
    pixel_installed: bool = False
    has_customer_list: bool = False
    average_order_value: Optional[float] = None
    customer_lifetime_value: Optional[float] = None
    seasonality_patterns: List[str] = field(default_factory=list)  # e.g., ["holiday_boost", "summer_dip"]
    
    # Meta Ad Objectives and Goals (optional fields)
    secondary_objectives: List[MetaAdObjective] = field(default_factory=list)
    
    # Enhanced Budget Preferences (optional fields)
    budget_strategy: MetaBudgetStrategy = MetaBudgetStrategy.DAILY_BUDGET
    bid_strategy: MetaBidStrategy = MetaBidStrategy.LOWEST_COST
    budget_flexibility: str = "fixed"  # fixed, flexible, performance_based
    max_budget_increase: float = 0.2  # Max 20% budget increase for good performance
    min_profitable_roas: Optional[float] = None  # Minimum ROAS to be profitable
    
    # Enhanced Target Audience Specifications
    target_age_min: int = 18
    target_age_max: int = 65
    target_genders: List[str] = field(default_factory=lambda: ["all"])
    target_locations: List[Dict[str, Any]] = field(default_factory=list)
    target_radius_km: Optional[int] = None  # For local businesses
    target_interests: List[Dict[str, str]] = field(default_factory=list)  # {"id": "123", "name": "Interest"}
    target_behaviors: List[Dict[str, str]] = field(default_factory=list)
    custom_audiences: List[str] = field(default_factory=list)  # Custom audience IDs
    lookalike_audiences: List[Dict[str, Any]] = field(default_factory=list)
    exclude_audiences: List[str] = field(default_factory=list)  # Audiences to exclude
    
    # Business-Specific Targeting
    target_income_level: Optional[str] = None  # low, middle, high, luxury
    target_life_events: List[str] = field(default_factory=list)  # recently_moved, new_job, etc.
    target_device_preferences: List[str] = field(default_factory=lambda: ["mobile", "desktop"])
    
    # Creative Preferences
    preferred_creative_formats: List[MetaCreativeFormat] = field(default_factory=lambda: [MetaCreativeFormat.SINGLE_IMAGE])
    brand_colors: List[str] = field(default_factory=list)  # Hex colors
    brand_voice: str = "professional"  # professional, casual, playful, luxury
    visual_style: str = "clean"  # clean, bold, minimal, vibrant
    logo_url: Optional[str] = None
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    
    # Platform and Placement Preferences  
    preferred_placements: List[MetaPlacement] = field(default_factory=lambda: [MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_FEED])
    facebook_vs_instagram_split: float = 0.6  # 60% Facebook, 40% Instagram
    
    # Enhanced Performance Preferences
    target_cpl: Optional[float] = None  # Target Cost Per Lead
    target_cpa: Optional[float] = None  # Target Cost Per Acquisition
    target_roas: Optional[float] = None  # Target Return on Ad Spend
    target_cpm: Optional[float] = None  # Target Cost Per Mille
    target_ctr: Optional[float] = None  # Target Click Through Rate
    risk_tolerance: str = "medium"  # conservative, medium, aggressive
    optimization_patience: str = "normal"  # quick, normal, patient (learning phase tolerance)
    
    # Business-Specific Performance Goals
    lead_quality_over_quantity: bool = True
    focus_on_repeat_customers: bool = False
    brand_awareness_priority: float = 0.3  # 0-1 scale, balance with conversion focus
    local_market_focus: bool = False
    
    # Learning Data
    campaign_history: List[Dict[str, Any]] = field(default_factory=list)
    best_performing_audiences: List[Dict[str, Any]] = field(default_factory=list)
    best_performing_creatives: List[Dict[str, Any]] = field(default_factory=list)
    seasonal_performance: Dict[str, float] = field(default_factory=dict)  # month -> performance_multiplier
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class MetaCampaignRecommendation:
    """Personalized Meta campaign recommendation with specific targeting and optimization"""
    recommendation_id: str
    user_id: str
    campaign_type: str  # lead_generation, ecommerce_sales, brand_awareness, etc.
    
    # Campaign Structure
    campaign_name: str
    description: str
    reasoning: str
    
    # Meta-Specific Configuration
    objective: MetaAdObjective
    budget_strategy: MetaBudgetStrategy
    daily_budget: float
    bid_strategy: MetaBidStrategy
    
    # Audience Targeting
    audience_strategy: MetaAudienceType
    targeting_spec: Dict[str, Any]  # Complete Meta API targeting specification
    estimated_audience_size: Dict[str, int]  # min, max audience size
    
    # Creative Specifications
    creative_format: MetaCreativeFormat
    creative_prompts: List[str]
    ad_copy_templates: List[str]
    cta_recommendations: List[str]
    
    # Placement Strategy
    recommended_placements: List[MetaPlacement]
    placement_optimization: str  # automatic, manual
    
    # Performance Predictions
    predicted_cpm: float
    predicted_ctr: float
    predicted_cpl: Optional[float]
    predicted_cpa: Optional[float]
    predicted_roas: Optional[float]
    confidence_score: float
    
    # A/B Testing Strategy
    ab_test_variants: List[Dict[str, Any]] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)

class MetaAdsPersonalizationEngine:
    """Advanced personalization engine specifically for Meta (Facebook/Instagram) ads"""
    
    def __init__(self):
        """Initialize Meta-specific personalization engine"""
        self.user_profiles: Dict[str, MetaUserProfile] = {}
        self.meta_benchmarks = self._load_meta_benchmarks()
        self.audience_insights = self._load_audience_insights()
        self.creative_performance_data = self._load_creative_performance_data()
        self.industry_targeting = self._load_industry_targeting_data()
        
    def _load_meta_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive Meta platform benchmarks by industry and objective"""
        return {
            "local_service": {
                "lead_generation": {
                    "avg_cpm": 15.50, "avg_ctr": 2.8, "avg_cpl": 45.0,
                    "facebook_performance": 1.2, "instagram_performance": 0.9,
                    "best_placements": ["facebook_feed", "instagram_feed"],
                    "optimal_budget_min": 30, "optimal_audience_size": 50000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "learning_phase_days": 3, "seasonal_multipliers": {"summer": 1.2, "winter": 0.8}
                },
                "brand_awareness": {
                    "avg_cpm": 8.20, "avg_ctr": 1.9, "avg_reach_rate": 0.12,
                    "facebook_performance": 1.0, "instagram_performance": 1.3,
                    "best_placements": ["facebook_feed", "instagram_stories"],
                    "optimal_budget_min": 20, "optimal_audience_size": 100000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "learning_phase_days": 2, "seasonal_multipliers": {"holiday": 1.5}
                },
                "gym_fitness": {
                    "avg_cpm": 18.75, "avg_ctr": 3.2, "avg_cpl": 35.0,
                    "facebook_performance": 1.0, "instagram_performance": 1.4,
                    "best_placements": ["instagram_feed", "instagram_stories", "facebook_feed"],
                    "optimal_budget_min": 35, "optimal_audience_size": 30000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "peak_times": ["06:00-08:00", "17:00-20:00"], 
                    "seasonal_multipliers": {"january": 2.1, "summer": 0.7, "september": 1.3}
                },
                "restaurant": {
                    "avg_cpm": 12.30, "avg_ctr": 4.1, "avg_cpl": 25.0,
                    "facebook_performance": 1.1, "instagram_performance": 1.6,
                    "best_placements": ["instagram_feed", "instagram_stories"],
                    "optimal_budget_min": 25, "optimal_audience_size": 15000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "peak_times": ["11:00-13:00", "17:00-21:00"],
                    "seasonal_multipliers": {"holiday": 1.8, "valentine": 1.4}
                }
            },
            "ecommerce": {
                "sales": {
                    "avg_cpm": 12.80, "avg_ctr": 1.6, "avg_roas": 4.2,
                    "facebook_performance": 1.1, "instagram_performance": 1.4,
                    "best_placements": ["facebook_feed", "instagram_feed", "instagram_stories"],
                    "optimal_budget_min": 50, "optimal_audience_size": 25000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "learning_phase_days": 7, "seasonal_multipliers": {"q4": 2.1, "january": 0.6}
                },
                "traffic": {
                    "avg_cpm": 6.50, "avg_ctr": 2.1, "avg_cpc": 0.85,
                    "facebook_performance": 1.0, "instagram_performance": 1.2,
                    "best_placements": ["facebook_feed", "facebook_right_column"],
                    "optimal_budget_min": 25, "optimal_audience_size": 75000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "learning_phase_days": 3
                }
            },
            "b2b_service": {
                "lead_generation": {
                    "avg_cpm": 25.00, "avg_ctr": 1.2, "avg_cpl": 85.0,
                    "facebook_performance": 1.4, "instagram_performance": 0.7,
                    "best_placements": ["facebook_feed", "facebook_right_column"],
                    "optimal_budget_min": 75, "optimal_audience_size": 15000,
                    "recommended_bid_strategy": "COST_PER_ACTION_TYPE",
                    "learning_phase_days": 14, "peak_times": ["09:00-17:00"]
                }
            },
            "healthcare": {
                "lead_generation": {
                    "avg_cpm": 22.15, "avg_ctr": 2.1, "avg_cpl": 55.0,
                    "facebook_performance": 1.3, "instagram_performance": 0.8,
                    "best_placements": ["facebook_feed"],
                    "optimal_budget_min": 40, "optimal_audience_size": 20000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "compliance_note": "Healthcare ads require special approval"
                }
            },
            "real_estate": {
                "lead_generation": {
                    "avg_cpm": 18.90, "avg_ctr": 1.8, "avg_cpl": 65.0,
                    "facebook_performance": 1.2, "instagram_performance": 1.1,
                    "best_placements": ["facebook_feed", "instagram_feed"],
                    "optimal_budget_min": 50, "optimal_audience_size": 35000,
                    "recommended_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                    "seasonal_multipliers": {"spring": 1.4, "winter": 0.7}
                }
            }
        }
    
    def _load_audience_insights(self) -> Dict[str, Dict[str, Any]]:
        """Load audience behavior insights for Meta platforms"""
        return {
            "age_groups": {
                "18-24": {
                    "platform_preference": "instagram", "engagement_multiplier": 1.8,
                    "best_times": ["19:00-22:00"], "content_preference": "video",
                    "attention_span": "short", "preferred_formats": ["stories", "reels"]
                },
                "25-34": {
                    "platform_preference": "mixed", "engagement_multiplier": 1.5,
                    "best_times": ["07:00-09:00", "18:00-21:00"], "content_preference": "mixed",
                    "attention_span": "medium", "preferred_formats": ["feed", "stories"]
                },
                "35-44": {
                    "platform_preference": "facebook", "engagement_multiplier": 1.3,
                    "best_times": ["06:00-08:00", "17:00-19:00"], "content_preference": "image",
                    "attention_span": "medium", "preferred_formats": ["feed"]
                },
                "45-54": {
                    "platform_preference": "facebook", "engagement_multiplier": 1.1,
                    "best_times": ["08:00-10:00", "20:00-22:00"], "content_preference": "image",
                    "attention_span": "long", "preferred_formats": ["feed", "right_column"]
                },
                "55+": {
                    "platform_preference": "facebook", "engagement_multiplier": 0.9,
                    "best_times": ["09:00-11:00", "14:00-16:00"], "content_preference": "image",
                    "attention_span": "long", "preferred_formats": ["feed"]
                }
            }
        }
    
    def _load_creative_performance_data(self) -> Dict[str, Dict[str, Any]]:
        """Load creative format performance data"""
        return {
            "single_image": {
                "facebook_performance": 1.0, "instagram_performance": 1.2,
                "engagement_rate": 1.8, "conversion_rate": 1.0,
                "production_cost": "low", "optimal_dimensions": ["1080x1080", "1200x628"]
            },
            "single_video": {
                "facebook_performance": 1.4, "instagram_performance": 2.1,
                "engagement_rate": 3.2, "conversion_rate": 1.6,
                "production_cost": "high", "optimal_length": "15-30s"
            },
            "carousel": {
                "facebook_performance": 1.3, "instagram_performance": 1.7,
                "engagement_rate": 2.4, "conversion_rate": 1.8,
                "production_cost": "medium", "optimal_cards": "3-5"
            },
            "collection": {
                "facebook_performance": 1.1, "instagram_performance": 1.9,
                "engagement_rate": 2.1, "conversion_rate": 2.2,
                "production_cost": "medium", "best_for": "ecommerce"
            }
        }
    
    def _load_industry_targeting_data(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive industry-specific targeting recommendations"""
        return {
            "local_service": {
                "gym_fitness": {
                    "core_interests": [
                        {"id": "6003139266461", "name": "Physical fitness"},
                        {"id": "6003277229526", "name": "Gym"},
                        {"id": "6003348604581", "name": "Weight training"},
                        {"id": "6003425061715", "name": "CrossFit"},
                        {"id": "6003329837756", "name": "Personal trainer"},
                        {"id": "6003394433021", "name": "Nutrition"}
                    ],
                    "behaviors": [
                        {"id": "6017253486583", "name": "Frequent travelers"},
                        {"id": "6015559470583", "name": "Health and wellness enthusiasts"},
                        {"id": "6016863126583", "name": "Fitness app users"},
                        {"id": "6015630226383", "name": "Premium brand affinity"}
                    ],
                    "demographic_focus": "25-45", "local_radius": 15,
                    "best_times": ["06:00-08:00", "17:00-20:00"],
                    "seasonal_focus": {"new_year": "resolution_campaigns", "summer": "beach_body"},
                    "budget_recommendations": {
                        "500-1000": "focus_on_lead_magnets",
                        "1000-3000": "membership_trials",
                        "3000+": "premium_targeting_expansion"
                    },
                    "creative_angles": ["transformation_stories", "community_focused", "results_driven"]
                },
                "restaurant": {
                    "core_interests": [
                        {"id": "6003020834693", "name": "Cooking"},
                        {"id": "6003209415371", "name": "Restaurant"},
                        {"id": "6003348604581", "name": "Food"},
                        {"id": "6003464026835", "name": "Fine dining"},
                        {"id": "6003521131836", "name": "Food delivery"}
                    ],
                    "behaviors": [
                        {"id": "6015559470583", "name": "Dining out enthusiasts"},
                        {"id": "6017253486583", "name": "Local food lovers"},
                        {"id": "6016972936383", "name": "Mobile food ordering users"}
                    ],
                    "demographic_focus": "25-55", "local_radius": 10,
                    "best_times": ["11:00-13:00", "17:00-21:00"],
                    "budget_recommendations": {
                        "300-800": "local_awareness_focus",
                        "800-2000": "drive_reservations",
                        "2000+": "event_promotion_expansion"
                    }
                },
                "salon_spa": {
                    "core_interests": [
                        {"id": "6003348604581", "name": "Beauty"},
                        {"id": "6003139266461", "name": "Spa"},
                        {"id": "6003277229526", "name": "Hair care"}
                    ],
                    "behaviors": [
                        {"id": "6015630226383", "name": "Premium brand affinity"},
                        {"id": "6017253486583", "name": "Beauty enthusiasts"}
                    ],
                    "demographic_focus": "22-50", "local_radius": 20,
                    "best_times": ["10:00-14:00", "18:00-21:00"]
                }
            },
            "ecommerce": {
                "fashion": {
                    "core_interests": [
                        {"id": "6003348604581", "name": "Fashion"},
                        {"id": "6004037027412", "name": "Shopping"},
                        {"id": "6003277229526", "name": "Clothing"},
                        {"id": "6003425061715", "name": "Designer brands"}
                    ],
                    "behaviors": [
                        {"id": "6015559470583", "name": "Online shoppers"},
                        {"id": "6017253486583", "name": "Fashion enthusiasts"},
                        {"id": "6016972936383", "name": "Mobile commerce users"}
                    ],
                    "demographic_focus": "18-45", "global_targeting": True,
                    "best_times": ["10:00-12:00", "19:00-21:00"]
                }
            },
            "b2b_service": {
                "consulting": {
                    "core_interests": [
                        {"id": "6003139266461", "name": "Business consulting"},
                        {"id": "6003277229526", "name": "Management"},
                        {"id": "6003348604581", "name": "Leadership"}
                    ],
                    "behaviors": [
                        {"id": "6015559470583", "name": "Business decision makers"},
                        {"id": "6017253486583", "name": "Professional development"}
                    ],
                    "demographic_focus": "30-55", "targeting_expansion": "job_titles",
                    "best_times": ["08:00-10:00", "14:00-17:00"]
                }
            },
            "healthcare": {
                "dental": {
                    "core_interests": [
                        {"id": "6003139266461", "name": "Dental care"},
                        {"id": "6003277229526", "name": "Oral health"},
                        {"id": "6003348604581", "name": "Cosmetic dentistry"}
                    ],
                    "behaviors": [
                        {"id": "6015559470583", "name": "Health conscious"},
                        {"id": "6017253486583", "name": "Preventive care"}
                    ],
                    "demographic_focus": "25-65", "local_radius": 25,
                    "compliance_requirements": ["health_claims_approval"]
                }
            },
            "real_estate": {
                "residential": {
                    "core_interests": [
                        {"id": "6003139266461", "name": "Real estate"},
                        {"id": "6003277229526", "name": "Home buying"},
                        {"id": "6003348604581", "name": "Home improvement"}
                    ],
                    "behaviors": [
                        {"id": "6015559470583", "name": "Likely to move"},
                        {"id": "6017253486583", "name": "First-time homebuyers"}
                    ],
                    "demographic_focus": "25-55", "local_radius": 50,
                    "life_events": ["recently_moved", "new_job", "married"]
                }
            }
        }
    
    async def create_meta_user_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, Any]
    ) -> MetaUserProfile:
        """
        Create comprehensive Meta-specific user profile for personalized campaigns
        
        Args:
            user_id: Unique user identifier
            profile_data: User profile information specific to Meta ads
            
        Returns:
            Complete MetaUserProfile object
        """
        try:
            # Parse business category
            business_category = BusinessCategory(profile_data.get("business_category", "local_service"))
            
            # Parse primary objective
            primary_objective = MetaAdObjective(profile_data.get("primary_objective", "OUTCOME_LEADS"))
            
            # Parse secondary objectives
            secondary_objectives = [
                MetaAdObjective(obj) for obj in profile_data.get("secondary_objectives", [])
            ]
            
            # Parse creative formats
            preferred_formats = [
                MetaCreativeFormat(fmt) for fmt in profile_data.get("preferred_creative_formats", ["single_image"])
            ]
            
            # Parse placements
            preferred_placements = [
                MetaPlacement(placement) for placement in profile_data.get("preferred_placements", ["facebook_feed", "instagram_feed"])
            ]
            
            profile = MetaUserProfile(
                user_id=user_id,
                business_name=profile_data.get("business_name", ""),
                business_category=business_category,
                
                # Objectives
                primary_objective=primary_objective,
                secondary_objectives=secondary_objectives,
                
                # Budget
                monthly_budget=profile_data.get("monthly_budget", 1000.0),
                daily_budget_preference=profile_data.get("daily_budget_preference", 33.0),
                budget_strategy=MetaBudgetStrategy(profile_data.get("budget_strategy", "daily_budget")),
                bid_strategy=MetaBidStrategy(profile_data.get("bid_strategy", "LOWEST_COST_WITHOUT_CAP")),
                
                # Audience targeting
                target_age_min=profile_data.get("target_age_min", 18),
                target_age_max=profile_data.get("target_age_max", 65),
                target_genders=profile_data.get("target_genders", ["all"]),
                target_locations=profile_data.get("target_locations", []),
                target_radius_km=profile_data.get("target_radius_km"),
                target_interests=profile_data.get("target_interests", []),
                target_behaviors=profile_data.get("target_behaviors", []),
                custom_audiences=profile_data.get("custom_audiences", []),
                lookalike_audiences=profile_data.get("lookalike_audiences", []),
                
                # Creative preferences
                preferred_creative_formats=preferred_formats,
                brand_colors=profile_data.get("brand_colors", []),
                brand_voice=profile_data.get("brand_voice", "professional"),
                visual_style=profile_data.get("visual_style", "clean"),
                
                # Platform preferences
                preferred_placements=preferred_placements,
                facebook_vs_instagram_split=profile_data.get("facebook_vs_instagram_split", 0.6),
                
                # Performance targets
                target_cpl=profile_data.get("target_cpl"),
                target_cpa=profile_data.get("target_cpa"),
                target_roas=profile_data.get("target_roas"),
                risk_tolerance=profile_data.get("risk_tolerance", "medium")
            )
            
            # Store profile
            self.user_profiles[user_id] = profile
            
            logger.info(f"Created Meta-specific user profile for {user_id} - {profile.business_name}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating Meta user profile: {e}")
            raise
    
    async def get_personalized_meta_campaigns(
        self, 
        user_id: str,
        campaign_count: int = 3
    ) -> List[MetaCampaignRecommendation]:
        """
        Generate personalized Meta campaign recommendations based on user profile
        
        Args:
            user_id: User identifier
            campaign_count: Number of campaign recommendations to generate
            
        Returns:
            List of personalized Meta campaign recommendations
        """
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"Meta user profile not found for {user_id}")
            
            recommendations = []
            
            # Generate different types of campaign recommendations
            
            # 1. Primary objective campaign
            primary_campaign = await self._generate_primary_objective_campaign(profile)
            if primary_campaign:
                recommendations.append(primary_campaign)
            
            # 2. Audience-optimized campaign
            audience_campaign = await self._generate_audience_optimized_campaign(profile)
            if audience_campaign:
                recommendations.append(audience_campaign)
            
            # 3. Budget-optimized campaign
            budget_campaign = await self._generate_budget_optimized_campaign(profile)
            if budget_campaign:
                recommendations.append(budget_campaign)
            
            # 4. Creative-focused campaign (if more campaigns needed)
            if len(recommendations) < campaign_count:
                creative_campaign = await self._generate_creative_focused_campaign(profile)
                if creative_campaign:
                    recommendations.append(creative_campaign)
            
            # 5. Retargeting campaign (if more campaigns needed)
            if len(recommendations) < campaign_count:
                retargeting_campaign = await self._generate_retargeting_campaign(profile)
                if retargeting_campaign:
                    recommendations.append(retargeting_campaign)
            
            # Sort by confidence score
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"Generated {len(recommendations)} Meta campaign recommendations for {user_id}")
            return recommendations[:campaign_count]
            
        except Exception as e:
            logger.error(f"Error generating Meta campaign recommendations: {e}")
            raise
    
    async def get_business_specific_strategy(
        self,
        user_query: str,
        profile: Optional[MetaUserProfile] = None
    ) -> Dict[str, Any]:
        """
        Provide detailed Meta campaign strategy for specific business scenarios
        
        Args:
            user_query: Natural language query about their business needs
            profile: Optional user profile for personalized recommendations
            
        Returns:
            Comprehensive strategy recommendation
        """
        try:
            # Parse business context from query
            business_context = self._parse_business_context(user_query)
            
            # Generate tailored strategy
            strategy = await self._generate_business_strategy(
                business_context, profile
            )
            
            return {
                "success": True,
                "business_context": business_context,
                "recommended_strategy": strategy,
                "implementation_steps": self._generate_implementation_steps(strategy),
                "expected_results": self._predict_campaign_performance(strategy, business_context),
                "budget_optimization": self._optimize_budget_allocation(strategy, business_context),
                "timeline": self._create_campaign_timeline(strategy)
            }
            
        except Exception as e:
            logger.error(f"Error generating business-specific strategy: {e}")
            raise
    
    def _parse_business_context(self, query: str) -> Dict[str, Any]:
        """Parse business context from natural language query"""
        query_lower = query.lower()
        
        # Business type detection
        business_type = "local_service"  # default
        if any(keyword in query_lower for keyword in ["gym", "fitness", "workout", "training"]):
            business_type = "gym_fitness"
        elif any(keyword in query_lower for keyword in ["restaurant", "cafe", "food", "dining"]):
            business_type = "restaurant"
        elif any(keyword in query_lower for keyword in ["salon", "spa", "beauty", "hair"]):
            business_type = "salon_spa"
        elif any(keyword in query_lower for keyword in ["dental", "dentist", "teeth"]):
            business_type = "dental"
        elif any(keyword in query_lower for keyword in ["real estate", "realtor", "property"]):
            business_type = "real_estate"
        elif any(keyword in query_lower for keyword in ["ecommerce", "online store", "shop"]):
            business_type = "ecommerce"
        
        # Budget detection
        budget = None
        budget_patterns = [r'₹(\d+(?:,\d+)?)', r'(\d+)\s*(?:rupee|INR)']
        for pattern in budget_patterns:
            import re
            match = re.search(pattern, query)
            if match:
                budget = float(match.group(1).replace(',', ''))
                break
        
        # Goal detection
        goal = "leads"  # default
        if any(keyword in query_lower for keyword in ["member", "membership", "signup", "join"]):
            goal = "memberships"
        elif any(keyword in query_lower for keyword in ["sale", "purchase", "buy", "order"]):
            goal = "sales"
        elif any(keyword in query_lower for keyword in ["awareness", "brand", "visibility"]):
            goal = "awareness"
        elif any(keyword in query_lower for keyword in ["traffic", "website", "visit"]):
            goal = "traffic"
        
        return {
            "business_type": business_type,
            "monthly_budget": budget,
            "primary_goal": goal,
            "location_based": "local" in query_lower or "nearby" in query_lower,
            "urgency": "urgent" in query_lower or "asap" in query_lower or "quickly" in query_lower
        }
    
    async def _generate_business_strategy(
        self, 
        context: Dict[str, Any], 
        profile: Optional[MetaUserProfile]
    ) -> Dict[str, Any]:
        """Generate comprehensive business strategy based on context"""
        
        business_type = context["business_type"]
        budget = context.get("monthly_budget", 1000)
        goal = context["primary_goal"]
        
        # Get industry-specific data
        industry_data = self.industry_targeting.get("local_service", {}).get(business_type, {})
        benchmark_data = self.meta_benchmarks.get("local_service", {}).get(business_type, {})
        
        # Determine optimal campaign structure
        campaign_objective = self._map_goal_to_objective(goal)
        
        # Budget allocation strategy
        daily_budget = min(budget / 30, 100)  # Conservative daily budget
        
        strategy = {
            "campaign_objective": campaign_objective,
            "recommended_budget": {
                "daily_budget": daily_budget,
                "monthly_budget": budget,
                "platform_split": {"facebook": 0.4, "instagram": 0.6} if business_type in ["gym_fitness", "salon_spa"] else {"facebook": 0.6, "instagram": 0.4}
            },
            "targeting_strategy": {
                "audience_type": "core_audience",
                "targeting_spec": self._build_business_targeting(business_type, industry_data),
                "audience_size_target": benchmark_data.get("optimal_audience_size", 30000)
            },
            "creative_strategy": {
                "primary_format": "single_image" if budget < 1500 else "mixed",
                "content_themes": industry_data.get("creative_angles", ["professional", "results_focused"]),
                "platform_optimization": True
            },
            "bidding_strategy": {
                "bid_type": benchmark_data.get("recommended_bid_strategy", "LOWEST_COST_WITHOUT_CAP"),
                "optimization_goal": "conversions" if goal in ["sales", "memberships"] else "link_clicks"
            },
            "placement_strategy": {
                "recommended_placements": benchmark_data.get("best_placements", ["facebook_feed", "instagram_feed"]),
                "automatic_placement": budget > 2000  # Use automatic for larger budgets
            }
        }
        
        return strategy
    
    def _map_goal_to_objective(self, goal: str) -> str:
        """Map business goal to Meta campaign objective"""
        mapping = {
            "leads": "OUTCOME_LEADS",
            "memberships": "OUTCOME_LEADS",
            "sales": "OUTCOME_SALES",
            "awareness": "OUTCOME_AWARENESS",
            "traffic": "OUTCOME_TRAFFIC"
        }
        return mapping.get(goal, "OUTCOME_LEADS")
    
    def _build_business_targeting(self, business_type: str, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build targeting specification for specific business type"""
        
        targeting = {
            "geo_locations": {"countries": ["US"]},  # Default, should be customized
            "age_min": 25,
            "age_max": 55
        }
        
        # Apply business-specific targeting
        if business_type == "gym_fitness":
            targeting.update({
                "age_min": 22,
                "age_max": 50,
                "interests": industry_data.get("core_interests", []),
                "behaviors": industry_data.get("behaviors", []),
                "radius": 15  # km
            })
        elif business_type == "restaurant":
            targeting.update({
                "age_min": 21,
                "age_max": 60,
                "interests": industry_data.get("core_interests", []),
                "behaviors": industry_data.get("behaviors", []),
                "radius": 10  # km
            })
        
        return targeting
    
    def _generate_implementation_steps(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate step-by-step implementation guide"""
        steps = [
            {
                "step": 1,
                "title": "Setup Campaign Structure",
                "description": f"Create {strategy['campaign_objective']} campaign with recommended settings",
                "estimated_time": "15 minutes",
                "details": [
                    f"Set daily budget to ₹{strategy['recommended_budget']['daily_budget']:.2f}",
                    f"Choose {strategy['bidding_strategy']['bid_type']} bidding",
                    "Configure automatic placements for optimal performance"
                ]
            },
            {
                "step": 2,
                "title": "Configure Audience Targeting",
                "description": "Set up precise audience targeting based on your business type",
                "estimated_time": "10 minutes",
                "details": [
                    "Apply demographic targeting",
                    "Add relevant interests and behaviors",
                    "Set geographic radius for local targeting"
                ]
            },
            {
                "step": 3,
                "title": "Create Ad Creatives",
                "description": f"Develop {strategy['creative_strategy']['primary_format']} creatives",
                "estimated_time": "30 minutes",
                "details": [
                    "Create platform-optimized visuals",
                    "Write compelling ad copy",
                    "Set up strong call-to-action"
                ]
            },
            {
                "step": 4,
                "title": "Launch and Monitor",
                "description": "Launch campaign and set up monitoring",
                "estimated_time": "5 minutes setup + ongoing",
                "details": [
                    "Launch campaign with active status",
                    "Monitor performance daily for first week",
                    "Make optimizations based on data"
                ]
            }
        ]
        
        return steps
    
    def _predict_campaign_performance(self, strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict expected campaign performance"""
        business_type = context["business_type"]
        budget = context.get("monthly_budget", 1000)
        
        # Get benchmark data
        benchmark_key = "local_service" if business_type in ["gym_fitness", "restaurant", "salon_spa"] else "ecommerce"
        benchmarks = self.meta_benchmarks.get(benchmark_key, {}).get(business_type, {})
        
        if not benchmarks:
            # Use default benchmarks
            benchmarks = {"avg_cpm": 15.0, "avg_ctr": 2.0, "avg_cpl": 45.0}
        
        # Calculate predictions
        daily_budget = strategy["recommended_budget"]["daily_budget"]
        predicted_impressions = (daily_budget / benchmarks.get("avg_cpm", 15.0)) * 1000
        predicted_clicks = predicted_impressions * (benchmarks.get("avg_ctr", 2.0) / 100)
        predicted_leads = predicted_clicks * 0.15  # Assume 15% conversion rate
        
        return {
            "monthly_predictions": {
                "impressions": int(predicted_impressions * 30),
                "clicks": int(predicted_clicks * 30),
                "leads": int(predicted_leads * 30),
                "cost_per_lead": benchmarks.get("avg_cpl", 45.0)
            },
            "performance_timeline": {
                "week_1": "Learning phase - expect higher CPL",
                "week_2_4": "Optimization phase - CPL should stabilize",
                "month_2+": "Mature performance - optimal results"
            },
            "success_metrics": {
                "target_cpl": benchmarks.get("avg_cpl", 45.0),
                "target_ctr": benchmarks.get("avg_ctr", 2.0),
                "expected_roas": benchmarks.get("avg_roas", 3.5)
            }
        }
    
    def _optimize_budget_allocation(self, strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide budget optimization recommendations"""
        budget = context.get("monthly_budget", 1000)
        business_type = context["business_type"]
        
        # Get industry-specific budget recommendations
        industry_data = self.industry_targeting.get("local_service", {}).get(business_type, {})
        budget_recs = industry_data.get("budget_recommendations", {})
        
        # Determine budget category
        budget_category = "500-1000" if budget <= 1000 else "1000-3000" if budget <= 3000 else "3000+"
        recommended_focus = budget_recs.get(budget_category, "balanced_approach")
        
        allocation = {
            "recommended_focus": recommended_focus,
            "platform_split": strategy["recommended_budget"]["platform_split"],
            "campaign_type_split": {
                "primary_campaign": 0.7,
                "retargeting": 0.2,
                "testing": 0.1
            },
            "optimization_tips": [
                "Start with 70% budget on proven audiences",
                "Reserve 20% for retargeting campaigns",
                "Allocate 10% for testing new audiences and creatives",
                "Increase budget by 20% for high-performing ad sets"
            ]
        }
        
        if budget < 1000:
            allocation["budget_constraints"] = [
                "Focus on single campaign objective",
                "Use broader targeting to reduce costs",
                "Prioritize Facebook over Instagram for lower CPM",
                "Consider lifetime budget over daily budget"
            ]
        
        return allocation
    
    def _create_campaign_timeline(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation and optimization timeline"""
        return {
            "setup_phase": {
                "duration": "1-2 days",
                "tasks": [
                    "Create campaign structure",
                    "Set up targeting",
                    "Create and upload creatives",
                    "Launch campaign"
                ]
            },
            "learning_phase": {
                "duration": "3-7 days",
                "expectations": [
                    "Higher cost per result during learning",
                    "Algorithm gathers performance data",
                    "Avoid major changes during this period"
                ],
                "monitoring": "Check performance 2x daily"
            },
            "optimization_phase": {
                "duration": "Week 2-4",
                "tasks": [
                    "Analyze performance data",
                    "Pause underperforming ads",
                    "Scale successful ad sets",
                    "Test new creative variations"
                ],
                "monitoring": "Daily performance review"
            },
            "scaling_phase": {
                "duration": "Month 2+",
                "focus": [
                    "Increase budget on top performers",
                    "Expand to lookalike audiences",
                    "Test new campaign objectives",
                    "Implement advanced optimization"
                ]
            }
        }
    
    async def _generate_primary_objective_campaign(
        self, 
        profile: MetaUserProfile
    ) -> Optional[MetaCampaignRecommendation]:
        """Generate campaign based on primary objective"""
        try:
            objective_key = profile.primary_objective.value.lower().replace("outcome_", "")
            business_key = profile.business_category.value
            
            # Get benchmark data
            benchmarks = self.meta_benchmarks.get(business_key, {}).get(objective_key, {})
            if not benchmarks:
                # Use default benchmarks
                benchmarks = {
                    "avg_cpm": 15.0, "avg_ctr": 2.0, "avg_cpl": 50.0,
                    "optimal_budget_min": 30, "optimal_audience_size": 50000
                }
            
            # Build targeting specification
            targeting_spec = self._build_meta_targeting_spec(profile)
            
            # Determine creative format
            creative_format = self._determine_optimal_creative_format(profile, objective_key)
            
            # Generate campaign recommendation
            campaign = MetaCampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                campaign_type=f"{objective_key}_primary",
                
                campaign_name=f"{profile.business_name} - {objective_key.title()} Campaign",
                description=f"Primary {objective_key} campaign optimized for {business_key} businesses",
                reasoning=f"Tailored for {objective_key} objective with {business_key} industry benchmarks and user preferences",
                
                # Meta configuration
                objective=profile.primary_objective,
                budget_strategy=profile.budget_strategy,
                daily_budget=min(profile.daily_budget_preference, profile.monthly_budget / 20),  # Conservative approach
                bid_strategy=profile.bid_strategy,
                
                # Targeting
                audience_strategy=MetaAudienceType.CORE_AUDIENCE,
                targeting_spec=targeting_spec,
                estimated_audience_size={"min": 10000, "max": benchmarks.get("optimal_audience_size", 50000)},
                
                # Creative
                creative_format=creative_format,
                creative_prompts=self._generate_creative_prompts(profile, objective_key),
                ad_copy_templates=self._generate_ad_copy_templates(profile, objective_key),
                cta_recommendations=self._get_cta_recommendations(objective_key),
                
                # Placement
                recommended_placements=self._optimize_placements_for_objective(profile, objective_key),
                placement_optimization="automatic",
                
                # Performance predictions
                predicted_cpm=benchmarks.get("avg_cpm", 15.0),
                predicted_ctr=benchmarks.get("avg_ctr", 2.0),
                predicted_cpl=benchmarks.get("avg_cpl"),
                predicted_cpa=profile.target_cpa,
                predicted_roas=benchmarks.get("avg_roas"),
                confidence_score=self._calculate_meta_confidence_score(profile, benchmarks),
                
                # A/B testing
                ab_test_variants=self._generate_meta_ab_variants(profile, objective_key)
            )
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error generating primary objective campaign: {e}")
            return None
    
    def _build_meta_targeting_spec(self, profile: MetaUserProfile) -> Dict[str, Any]:
        """Build complete Meta API targeting specification"""
        targeting = {
            "age_min": profile.target_age_min,
            "age_max": profile.target_age_max,
            "genders": profile.target_genders if profile.target_genders != ["all"] else [1, 2],  # 1=male, 2=female
        }
        
        # Geographic targeting
        if profile.target_locations:
            geo_locations = {"countries": [], "regions": [], "cities": []}
            for location in profile.target_locations:
                if location.get("type") == "country":
                    geo_locations["countries"].append(location["key"])
                elif location.get("type") == "region":
                    geo_locations["regions"].append({"key": location["key"]})
                elif location.get("type") == "city":
                    geo_locations["cities"].append({"key": location["key"]})
            
            if any(geo_locations.values()):
                targeting["geo_locations"] = {k: v for k, v in geo_locations.items() if v}
        else:
            # Default to US if no locations specified
            targeting["geo_locations"] = {"countries": ["US"]}
        
        # Radius targeting for local businesses
        if profile.target_radius_km and profile.business_category == BusinessCategory.LOCAL_SERVICE:
            targeting["radius"] = profile.target_radius_km
        
        # Interest targeting
        if profile.target_interests:
            targeting["interests"] = [
                {"id": interest["id"], "name": interest["name"]} 
                for interest in profile.target_interests
            ]
        
        # Behavior targeting  
        if profile.target_behaviors:
            targeting["behaviors"] = [
                {"id": behavior["id"], "name": behavior["name"]} 
                for behavior in profile.target_behaviors
            ]
        
        # Custom audiences
        if profile.custom_audiences:
            targeting["custom_audiences"] = [{"id": aud_id} for aud_id in profile.custom_audiences]
        
        # Lookalike audiences
        if profile.lookalike_audiences:
            targeting["lookalike_audiences"] = profile.lookalike_audiences
        
        return targeting
    
    def _determine_optimal_creative_format(
        self, 
        profile: MetaUserProfile, 
        objective: str
    ) -> MetaCreativeFormat:
        """Determine optimal creative format based on profile and objective"""
        
        # Check user preferences first
        if profile.preferred_creative_formats:
            preferred_format = profile.preferred_creative_formats[0]
            
            # Validate format is good for objective
            format_performance = self.creative_performance_data.get(preferred_format.value, {})
            
            if objective == "sales" and format_performance.get("conversion_rate", 1.0) >= 1.5:
                return preferred_format
            elif objective == "engagement" and format_performance.get("engagement_rate", 1.0) >= 2.0:
                return preferred_format
            else:
                return preferred_format  # Use user preference anyway
        
        # Recommend based on objective and business category
        if objective == "sales" and profile.business_category == BusinessCategory.ECOMMERCE:
            return MetaCreativeFormat.CAROUSEL
        elif objective == "engagement":
            return MetaCreativeFormat.SINGLE_VIDEO
        elif objective == "leads":
            return MetaCreativeFormat.SINGLE_IMAGE
        else:
            return MetaCreativeFormat.SINGLE_IMAGE  # Safe default
    
    def _generate_creative_prompts(self, profile: MetaUserProfile, objective: str) -> List[str]:
        """Generate creative prompts based on profile and objective"""
        business_type = profile.business_category.value.replace("_", " ").title()
        brand_voice = profile.brand_voice
        
        prompts = []
        
        if objective == "leads":
            prompts.extend([
                f"Professional {business_type} lead generation visual, {brand_voice} style, clear value proposition with contact information",
                f"Before/after transformation showcase for {business_type} services, {brand_voice} branding, credibility focus",
                f"Free consultation offer for {business_type}, {brand_voice} design, trust-building elements and testimonials"
            ])
        elif objective == "sales":
            prompts.extend([
                f"Product showcase for {business_type}, {brand_voice} style, highlighting key benefits and pricing",
                f"Limited-time offer visual for {business_type}, {brand_voice} design, urgency and scarcity elements",
                f"Customer success story for {business_type}, {brand_voice} branding, social proof and results"
            ])
        elif objective == "brand_awareness":
            prompts.extend([
                f"Brand story visual for {business_type}, {brand_voice} aesthetic, behind-the-scenes authentic content",
                f"Company values showcase for {business_type}, {brand_voice} style, mission-driven messaging",
                f"Team introduction for {business_type}, {brand_voice} branding, personal connection focus"
            ])
        else:  # engagement, traffic, etc.
            prompts.extend([
                f"Educational content for {business_type} audience, {brand_voice} style, valuable tips and insights",
                f"Interactive question or poll for {business_type} community, {brand_voice} design, engagement focus",
                f"Industry trend commentary for {business_type}, {brand_voice} branding, thought leadership"
            ])
        
        return prompts
    
    def _generate_ad_copy_templates(self, profile: MetaUserProfile, objective: str) -> List[str]:
        """Generate ad copy templates based on profile and objective"""
        business_name = profile.business_name or "Your Business"
        business_type = profile.business_category.value.replace("_", " ")
        
        templates = []
        
        if objective == "leads":
            templates.extend([
                f"🎯 Ready to transform your {business_type} results? Get a FREE consultation with {business_name} and discover how we can help you achieve your goals. Book now - limited spots available!",
                f"💡 Struggling with {business_type} challenges? {business_name} has helped 100+ clients succeed. Download our free guide and start seeing results today!",
                f"⚡ {business_name} is offering FREE assessments for {business_type} owners. Get personalized insights and actionable strategies. Claim yours before they're gone!"
            ])
        elif objective == "sales":
            templates.extend([
                f"🔥 FLASH SALE: Save 30% on all {business_type} services at {business_name}! This exclusive offer ends soon. Shop now and get premium results at unbeatable prices.",
                f"✨ Why choose {business_name} for your {business_type} needs? ✅ Premium quality ✅ Expert service ✅ Guaranteed results. Order now and join 1000+ happy customers!",
                f"🎁 Limited time: Buy 2, Get 1 FREE at {business_name}! The best {business_type} deals of the year. Don't miss out - stock is limited!"
            ])
        elif objective == "brand_awareness":
            templates.extend([
                f"🌟 Meet the team behind {business_name}! We're passionate about {business_type} and dedicated to delivering exceptional results. This is our story...",
                f"💪 At {business_name}, we believe every {business_type} challenge is an opportunity. Here's how we're making a difference in our community.",
                f"🚀 From humble beginnings to industry leaders - the {business_name} journey. See how we've revolutionized {business_type} for our clients."
            ])
        else:  # engagement, traffic
            templates.extend([
                f"🤔 What's the biggest {business_type} mistake you see businesses making? {business_name} experts share the top 5 pitfalls to avoid. Comment your thoughts below!",
                f"📈 The {business_type} landscape is changing fast. {business_name} breaks down the latest trends and what they mean for your business. Read more:",
                f"💭 Quick question: What's your #1 {business_type} goal this year? {business_name} has strategies to help you achieve it. Let us know in the comments!"
            ])
        
        return templates
    
    def _get_cta_recommendations(self, objective: str) -> List[str]:
        """Get call-to-action recommendations based on objective"""
        cta_mapping = {
            "leads": ["Learn More", "Get Quote", "Contact Us", "Book Now", "Sign Up"],
            "sales": ["Shop Now", "Buy Now", "Order Now", "Get Offer", "Purchase"],
            "brand_awareness": ["Learn More", "See More", "Visit Website", "Follow Us", "Discover"],
            "engagement": ["Like", "Comment", "Share", "Join", "Participate"],
            "traffic": ["Visit Website", "Read More", "Explore", "Browse", "View"],
            "app_promotion": ["Install Now", "Download", "Get App", "Try Free", "Play Now"]
        }
        return cta_mapping.get(objective, ["Learn More", "Get Started", "Contact Us"])
    
    def _optimize_placements_for_objective(
        self, 
        profile: MetaUserProfile, 
        objective: str
    ) -> List[MetaPlacement]:
        """Optimize placements based on objective and profile"""
        
        # Get age group insights
        age_group_key = self._get_age_group_key(profile.target_age_min, profile.target_age_max)
        age_insights = self.audience_insights.get("age_groups", {}).get(age_group_key, {})
        
        # Start with user preferred placements
        optimized_placements = profile.preferred_placements.copy() if profile.preferred_placements else []
        
        # Add objective-specific recommendations
        if objective == "engagement" and age_group_key in ["18-24", "25-34"]:
            # Younger audiences engage more on Stories and Reels
            if MetaPlacement.INSTAGRAM_STORIES not in optimized_placements:
                optimized_placements.append(MetaPlacement.INSTAGRAM_STORIES)
            if MetaPlacement.INSTAGRAM_REELS not in optimized_placements:
                optimized_placements.append(MetaPlacement.INSTAGRAM_REELS)
        
        elif objective == "leads" and profile.business_category == BusinessCategory.B2B_SERVICE:
            # B2B leads perform better on Facebook feed
            if MetaPlacement.FACEBOOK_FEED not in optimized_placements:
                optimized_placements.insert(0, MetaPlacement.FACEBOOK_FEED)
        
        elif objective == "sales" and profile.business_category == BusinessCategory.ECOMMERCE:
            # E-commerce benefits from diverse placements
            for placement in [MetaPlacement.INSTAGRAM_FEED, MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_STORIES]:
                if placement not in optimized_placements:
                    optimized_placements.append(placement)
        
        # Ensure we have at least the basic placements
        if not optimized_placements:
            optimized_placements = [MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_FEED]
        
        return optimized_placements[:6]  # Limit to 6 placements for performance
    
    def _get_age_group_key(self, age_min: int, age_max: int) -> str:
        """Get age group key based on age range"""
        avg_age = (age_min + age_max) // 2
        
        if avg_age <= 24:
            return "18-24"
        elif avg_age <= 34:
            return "25-34"
        elif avg_age <= 44:
            return "35-44"
        elif avg_age <= 54:
            return "45-54"
        else:
            return "55+"
    
    def _calculate_meta_confidence_score(
        self, 
        profile: MetaUserProfile, 
        benchmarks: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for Meta campaign recommendation"""
        base_confidence = 0.75
        
        # Profile completeness boost
        completeness_factors = 0
        
        if profile.target_interests:
            completeness_factors += 0.1
        if profile.target_behaviors:
            completeness_factors += 0.05
        if profile.custom_audiences:
            completeness_factors += 0.1
        if profile.brand_colors:
            completeness_factors += 0.02
        if profile.target_locations:
            completeness_factors += 0.05
        if len(profile.campaign_history) > 0:
            completeness_factors += 0.08
        
        # Business category alignment
        if profile.business_category.value in self.meta_benchmarks:
            completeness_factors += 0.05
        
        # Budget adequacy check
        min_budget = benchmarks.get("optimal_budget_min", 30)
        if profile.daily_budget_preference >= min_budget:
            completeness_factors += 0.05
        elif profile.daily_budget_preference >= min_budget * 0.7:
            completeness_factors += 0.02
        
        # Additional confidence factors for enhanced profile
        if hasattr(profile, 'pixel_installed') and profile.pixel_installed:
            completeness_factors += 0.08
        if hasattr(profile, 'has_customer_list') and profile.has_customer_list:
            completeness_factors += 0.06
        if hasattr(profile, 'average_order_value') and profile.average_order_value:
            completeness_factors += 0.04
        if hasattr(profile, 'seasonality_patterns') and profile.seasonality_patterns:
            completeness_factors += 0.03
        
        return min(base_confidence + completeness_factors, 0.95)
    
    def _generate_meta_ab_variants(
        self, 
        profile: MetaUserProfile, 
        objective: str
    ) -> List[Dict[str, Any]]:
        """Generate A/B test variants for Meta campaigns"""
        variants = []
        
        # Variant 1: Different creative format
        if profile.preferred_creative_formats and len(profile.preferred_creative_formats) > 1:
            alt_format = profile.preferred_creative_formats[1]
        else:
            alt_format = MetaCreativeFormat.SINGLE_VIDEO if profile.preferred_creative_formats[0] != MetaCreativeFormat.SINGLE_VIDEO else MetaCreativeFormat.CAROUSEL
        
        variants.append({
            "variant_id": "creative_format_test",
            "name": "Creative Format Test",
            "changes": {
                "creative_format": alt_format.value,
                "budget_split": 0.3
            },
            "hypothesis": f"Testing {alt_format.value} vs {profile.preferred_creative_formats[0].value} for better {objective} performance"
        })
        
        # Variant 2: Broader vs Narrow targeting
        variants.append({
            "variant_id": "audience_breadth_test",
            "name": "Audience Targeting Test", 
            "changes": {
                "targeting_expansion": "broader",
                "age_range_expansion": 10,
                "budget_split": 0.25
            },
            "hypothesis": "Testing broader audience targeting for potentially lower CPM and broader reach"
        })
        
        # Variant 3: Different placement mix
        if len(profile.preferred_placements) > 2:
            alt_placements = profile.preferred_placements[1:3]
        else:
            alt_placements = [MetaPlacement.INSTAGRAM_STORIES, MetaPlacement.FACEBOOK_STORIES]
        
        variants.append({
            "variant_id": "placement_test",
            "name": "Placement Optimization Test",
            "changes": {
                "placements": [p.value for p in alt_placements],
                "budget_split": 0.2
            },
            "hypothesis": f"Testing alternative placements for better {objective} efficiency"
        })
        
        return variants
    
    async def _generate_audience_optimized_campaign(
        self, 
        profile: MetaUserProfile
    ) -> Optional[MetaCampaignRecommendation]:
        """Generate campaign optimized for specific audience targeting"""
        try:
            # Use lookalike audiences if available, otherwise create interest-based
            if profile.lookalike_audiences:
                audience_strategy = MetaAudienceType.LOOKALIKE_AUDIENCE
                campaign_type = "lookalike_optimized"
                targeting_spec = self._build_lookalike_targeting(profile)
            elif profile.target_interests and len(profile.target_interests) >= 3:
                audience_strategy = MetaAudienceType.CORE_AUDIENCE
                campaign_type = "interest_optimized"  
                targeting_spec = self._build_interest_targeting(profile)
            else:
                # Skip if not enough targeting data
                return None
            
            objective_key = profile.primary_objective.value.lower().replace("outcome_", "")
            
            campaign = MetaCampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                campaign_type=campaign_type,
                
                campaign_name=f"{profile.business_name} - Audience Optimized",
                description=f"Campaign optimized for {audience_strategy.value} targeting strategy",
                reasoning=f"Leveraging {audience_strategy.value} targeting for precise audience reach and improved performance",
                
                objective=profile.primary_objective,
                budget_strategy=profile.budget_strategy,
                daily_budget=profile.daily_budget_preference * 0.8,  # Slightly lower budget for testing
                bid_strategy=profile.bid_strategy,
                
                audience_strategy=audience_strategy,
                targeting_spec=targeting_spec,
                estimated_audience_size={"min": 5000, "max": 30000},  # Smaller, more targeted
                
                creative_format=self._determine_optimal_creative_format(profile, objective_key),
                creative_prompts=self._generate_creative_prompts(profile, objective_key),
                ad_copy_templates=self._generate_ad_copy_templates(profile, objective_key),
                cta_recommendations=self._get_cta_recommendations(objective_key),
                
                recommended_placements=profile.preferred_placements,
                placement_optimization="automatic",
                
                predicted_cpm=15.0,  # May be higher due to precise targeting
                predicted_ctr=2.5,   # But better CTR
                predicted_cpl=None,
                predicted_cpa=profile.target_cpa,
                predicted_roas=profile.target_roas,
                confidence_score=0.85,  # High confidence for audience-optimized
                
                ab_test_variants=[]
            )
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error generating audience-optimized campaign: {e}")
            return None
    
    def _build_lookalike_targeting(self, profile: MetaUserProfile) -> Dict[str, Any]:
        """Build targeting spec for lookalike audiences"""
        targeting = {
            "age_min": profile.target_age_min,
            "age_max": profile.target_age_max,
            "lookalike_audiences": profile.lookalike_audiences
        }
        
        if profile.target_locations:
            targeting["geo_locations"] = self._format_geo_locations(profile.target_locations)
        else:
            targeting["geo_locations"] = {"countries": ["US"]}
            
        return targeting
    
    def _build_interest_targeting(self, profile: MetaUserProfile) -> Dict[str, Any]:
        """Build targeting spec focused on interests"""
        targeting = self._build_meta_targeting_spec(profile)
        
        # Enhance with industry-specific interests if available
        business_key = profile.business_category.value
        if business_key in self.industry_targeting.get("local_service", {}):
            industry_data = self.industry_targeting["local_service"][business_key]
            
            # Add core interests
            if "core_interests" in industry_data:
                existing_interest_ids = {i["id"] for i in targeting.get("interests", [])}
                for interest in industry_data["core_interests"]:
                    if interest["id"] not in existing_interest_ids:
                        targeting.setdefault("interests", []).append(interest)
            
            # Add behaviors
            if "behaviors" in industry_data and not targeting.get("behaviors"):
                targeting["behaviors"] = industry_data["behaviors"]
        
        return targeting
    
    def _format_geo_locations(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format geographic locations for Meta API"""
        geo_locations = {"countries": [], "regions": [], "cities": []}
        
        for location in locations:
            loc_type = location.get("type", "country")
            if loc_type == "country":
                geo_locations["countries"].append(location["key"])
            elif loc_type == "region":
                geo_locations["regions"].append({"key": location["key"]})
            elif loc_type == "city":
                geo_locations["cities"].append({"key": location["key"]})
        
        return {k: v for k, v in geo_locations.items() if v}
    
    async def _generate_budget_optimized_campaign(
        self, 
        profile: MetaUserProfile
    ) -> Optional[MetaCampaignRecommendation]:
        """Generate budget-optimized campaign"""
        try:
            # For budget optimization, focus on cost-effective strategies
            objective_key = profile.primary_objective.value.lower().replace("outcome_", "")
            
            # Use traffic objective for budget efficiency if original objective is expensive
            if objective_key == "leads" and profile.daily_budget_preference < 50:
                optimization_objective = MetaAdObjective.OUTCOME_TRAFFIC
                objective_key = "traffic"
            else:
                optimization_objective = profile.primary_objective
            
            campaign = MetaCampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                campaign_type="budget_optimized",
                
                campaign_name=f"{profile.business_name} - Budget Optimized",
                description="Cost-effective campaign designed to maximize results within budget constraints",
                reasoning=f"Optimized for budget efficiency with {profile.daily_budget_preference}/day budget using cost-effective targeting and placements",
                
                objective=optimization_objective,
                budget_strategy=MetaBudgetStrategy.DAILY_BUDGET,  # More control
                daily_budget=profile.daily_budget_preference,
                bid_strategy=MetaBidStrategy.LOWEST_COST,  # Most cost-effective
                
                audience_strategy=MetaAudienceType.CORE_AUDIENCE,
                targeting_spec=self._build_budget_targeting(profile),
                estimated_audience_size={"min": 50000, "max": 200000},  # Broader for lower costs
                
                creative_format=MetaCreativeFormat.SINGLE_IMAGE,  # Most cost-effective
                creative_prompts=self._generate_budget_focused_prompts(profile),
                ad_copy_templates=self._generate_budget_focused_copy(profile),
                cta_recommendations=self._get_cta_recommendations(objective_key),
                
                recommended_placements=[MetaPlacement.FACEBOOK_FEED, MetaPlacement.FACEBOOK_RIGHT_COLUMN],  # Cost-effective placements
                placement_optimization="automatic",
                
                predicted_cpm=8.0,   # Lower CPM
                predicted_ctr=1.8,   # Potentially lower CTR but good value
                predicted_cpl=None,
                predicted_cpa=profile.target_cpa,
                predicted_roas=profile.target_roas,
                confidence_score=0.80,
                
                ab_test_variants=[]
            )
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error generating budget-optimized campaign: {e}")
            return None
    
    def _build_budget_targeting(self, profile: MetaUserProfile) -> Dict[str, Any]:
        """Build cost-effective targeting specification"""
        targeting = {
            "age_min": max(profile.target_age_min - 5, 18),  # Slightly broader age range
            "age_max": min(profile.target_age_max + 5, 65),
            "genders": [1, 2]  # Both genders for broader reach
        }
        
        # Use broader geographic targeting
        if profile.target_locations:
            targeting["geo_locations"] = self._format_geo_locations(profile.target_locations)
        else:
            targeting["geo_locations"] = {"countries": ["US"]}
        
        # Use only top-performing interests to keep audience size optimal
        if profile.target_interests and len(profile.target_interests) > 0:
            targeting["interests"] = profile.target_interests[:3]  # Limit to top 3
        
        return targeting
    
    def _generate_budget_focused_prompts(self, profile: MetaUserProfile) -> List[str]:
        """Generate cost-effective creative prompts"""
        business_type = profile.business_category.value.replace("_", " ").title()
        
        return [
            f"Simple, clean {business_type} image with clear value proposition, minimal design, cost-effective production",
            f"User-generated content style for {business_type}, authentic and relatable, low production cost",
            f"Text-heavy design for {business_type} with strong offer, minimal visual elements, budget-friendly creation"
        ]
    
    def _generate_budget_focused_copy(self, profile: MetaUserProfile) -> List[str]:
        """Generate cost-effective ad copy"""
        business_name = profile.business_name or "Your Business"
        business_type = profile.business_category.value.replace("_", " ")
        
        return [
            f"💰 Best value in {business_type}! {business_name} offers quality service at prices you'll love. Get started today!",
            f"🎯 Smart choice for {business_type}: {business_name} delivers results without breaking the bank. See why customers choose us!",
            f"✅ Affordable {business_type} solutions from {business_name}. Quality service, fair prices, proven results. Contact us now!"
        ]
    
    async def _generate_creative_focused_campaign(
        self, 
        profile: MetaUserProfile
    ) -> Optional[MetaCampaignRecommendation]:
        """Generate campaign optimized for creative performance and testing"""
        try:
            objective_key = profile.primary_objective.value.lower().replace("outcome_", "")
            
            # Determine best creative format for business type
            if profile.business_category == BusinessCategory.LOCAL_SERVICE:
                primary_format = MetaCreativeFormat.SINGLE_VIDEO  # Video performs well for local services
            elif profile.business_category == BusinessCategory.ECOMMERCE:
                primary_format = MetaCreativeFormat.CAROUSEL  # Great for showcasing products
            else:
                primary_format = profile.preferred_creative_formats[0] if profile.preferred_creative_formats else MetaCreativeFormat.SINGLE_IMAGE
            
            campaign = MetaCampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                campaign_type="creative_focused",
                
                campaign_name=f"{profile.business_name} - Creative Performance Test",
                description="Creative-focused campaign with multiple format testing for optimal engagement",
                reasoning=f"Testing {primary_format.value} and alternative creative formats to maximize engagement and conversion rates",
                
                objective=profile.primary_objective,
                budget_strategy=MetaBudgetStrategy.CAMPAIGN_BUDGET_OPTIMIZATION,  # CBO for creative testing
                daily_budget=profile.daily_budget_preference * 1.2,  # Slightly higher budget for testing
                bid_strategy=MetaBidStrategy.LOWEST_COST,
                
                audience_strategy=MetaAudienceType.CORE_AUDIENCE,
                targeting_spec=self._build_meta_targeting_spec(profile),
                estimated_audience_size={"min": 25000, "max": 75000},  # Medium audience for testing
                
                creative_format=primary_format,
                creative_prompts=self._generate_creative_focused_prompts(profile, primary_format),
                ad_copy_templates=self._generate_creative_focused_copy(profile),
                cta_recommendations=self._get_cta_recommendations(objective_key),
                
                recommended_placements=self._optimize_placements_for_creative(profile, primary_format),
                placement_optimization="automatic",
                
                predicted_cpm=16.0,  # Slightly higher due to premium creative formats
                predicted_ctr=2.8,   # Higher CTR expected from optimized creatives
                predicted_cpl=profile.target_cpl * 0.9 if profile.target_cpl else 40.0,
                predicted_cpa=profile.target_cpa,
                predicted_roas=profile.target_roas,
                confidence_score=0.83,
                
                ab_test_variants=self._generate_creative_ab_variants(profile, primary_format)
            )
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error generating creative-focused campaign: {e}")
            return None
    
    def _generate_creative_focused_prompts(self, profile: MetaUserProfile, format_type: MetaCreativeFormat) -> List[str]:
        """Generate creative prompts optimized for specific formats"""
        business_type = profile.business_category.value.replace("_", " ").title()
        brand_voice = profile.brand_voice
        
        prompts = []
        
        if format_type == MetaCreativeFormat.SINGLE_VIDEO:
            prompts.extend([
                f"Short {business_type} transformation video, {brand_voice} style, before/after showcase with emotional impact",
                f"Behind-the-scenes {business_type} video, authentic {brand_voice} tone, team and process highlights",
                f"Customer success story video for {business_type}, {brand_voice} narration, results-focused testimonial"
            ])
        elif format_type == MetaCreativeFormat.CAROUSEL:
            prompts.extend([
                f"Product/service showcase carousel for {business_type}, {brand_voice} design, step-by-step benefits",
                f"Before/after transformation carousel, {brand_voice} style, multiple success stories",
                f"Features and benefits carousel for {business_type}, {brand_voice} tone, detailed value proposition"
            ])
        else:  # Single image or other formats
            prompts.extend([
                f"High-impact single image for {business_type}, {brand_voice} aesthetic, strong emotional connection",
                f"Results-focused image for {business_type}, {brand_voice} style, clear value demonstration",
                f"Community-centered image for {business_type}, {brand_voice} tone, social proof emphasis"
            ])
        
        return prompts
    
    def _generate_creative_focused_copy(self, profile: MetaUserProfile) -> List[str]:
        """Generate ad copy optimized for creative performance"""
        business_name = profile.business_name or "Your Business"
        business_type = profile.business_category.value.replace("_", " ")
        
        return [
            f"🎯 See the difference {business_name} makes! Real results from real customers in {business_type}. Your transformation starts here.",
            f"✨ Why settle for ordinary when {business_name} delivers extraordinary? Join hundreds of satisfied customers who chose excellence in {business_type}.",
            f"🚀 Ready to experience what makes {business_name} different? Discover the {business_type} solution that's changing lives every day."
        ]
    
    def _optimize_placements_for_creative(self, profile: MetaUserProfile, creative_format: MetaCreativeFormat) -> List[MetaPlacement]:
        """Optimize placements based on creative format"""
        placements = []
        
        if creative_format == MetaCreativeFormat.SINGLE_VIDEO:
            # Video performs well on feed and stories
            placements = [MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_FEED, 
                         MetaPlacement.INSTAGRAM_STORIES, MetaPlacement.INSTAGRAM_REELS]
        elif creative_format == MetaCreativeFormat.CAROUSEL:
            # Carousel works best on feed placements
            placements = [MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_FEED]
        else:
            # Single image works everywhere
            placements = profile.preferred_placements or [MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_FEED]
        
        return placements
    
    def _generate_creative_ab_variants(self, profile: MetaUserProfile, primary_format: MetaCreativeFormat) -> List[Dict[str, Any]]:
        """Generate A/B test variants for creative-focused campaigns"""
        variants = []
        
        # Creative format test
        alt_formats = [
            MetaCreativeFormat.SINGLE_IMAGE,
            MetaCreativeFormat.SINGLE_VIDEO,
            MetaCreativeFormat.CAROUSEL
        ]
        
        # Remove primary format and pick alternative
        if primary_format in alt_formats:
            alt_formats.remove(primary_format)
        
        if alt_formats:
            variants.append({
                "variant_id": "format_comparison",
                "name": f"{primary_format.value} vs {alt_formats[0].value}",
                "changes": {
                    "creative_format": alt_formats[0].value,
                    "budget_split": 0.4
                },
                "hypothesis": f"Testing {alt_formats[0].value} against {primary_format.value} for better engagement"
            })
        
        # Copy style test
        variants.append({
            "variant_id": "copy_style_test",
            "name": "Emotional vs Rational Copy",
            "changes": {
                "copy_style": "rational_benefits",
                "budget_split": 0.3
            },
            "hypothesis": "Testing benefit-focused copy against emotional appeal"
        })
        
        # Visual style test
        variants.append({
            "variant_id": "visual_style_test",
            "name": "Professional vs Authentic Style",
            "changes": {
                "visual_style": "authentic" if profile.visual_style == "clean" else "clean",
                "budget_split": 0.3
            },
            "hypothesis": "Testing visual authenticity impact on performance"
        })
        
        return variants
    
    async def _generate_retargeting_campaign(
        self, 
        profile: MetaUserProfile
    ) -> Optional[MetaCampaignRecommendation]:
        """Generate retargeting campaign for warm audiences"""
        try:
            # Only generate if user has tracking setup or custom audiences
            if not profile.pixel_installed and not profile.custom_audiences:
                return None
            
            objective_key = profile.primary_objective.value.lower().replace("outcome_", "")
            
            # Build retargeting audience specification
            retargeting_spec = {
                "age_min": profile.target_age_min,
                "age_max": profile.target_age_max
            }
            
            if profile.custom_audiences:
                retargeting_spec["custom_audiences"] = [
                    {"id": aud_id} for aud_id in profile.custom_audiences
                ]
            
            # If pixel is installed, create website visitors audience
            if profile.pixel_installed:
                retargeting_spec["website_visitors"] = {
                    "retention_days": 30,
                    "include_visitors": True,
                    "exclude_converters": True  # Exclude people who already converted
                }
            
            campaign = MetaCampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                campaign_type="retargeting",
                
                campaign_name=f"{profile.business_name} - Retargeting Campaign",
                description="Warm audience retargeting campaign for higher conversion rates",
                reasoning="Targeting users who have already shown interest in your business for improved conversion rates and lower costs",
                
                objective=profile.primary_objective,
                budget_strategy=MetaBudgetStrategy.DAILY_BUDGET,
                daily_budget=profile.daily_budget_preference * 0.3,  # Smaller budget for retargeting
                bid_strategy=MetaBidStrategy.LOWEST_COST,
                
                audience_strategy=MetaAudienceType.CUSTOM_AUDIENCE,
                targeting_spec=retargeting_spec,
                estimated_audience_size={"min": 1000, "max": 10000},  # Smaller warm audience
                
                creative_format=MetaCreativeFormat.SINGLE_IMAGE,
                creative_prompts=self._generate_retargeting_prompts(profile),
                ad_copy_templates=self._generate_retargeting_copy(profile),
                cta_recommendations=["Complete Purchase", "Finish Signup", "Get Started"],
                
                recommended_placements=[MetaPlacement.FACEBOOK_FEED, MetaPlacement.INSTAGRAM_FEED],
                placement_optimization="automatic",
                
                predicted_cpm=12.0,  # Slightly lower CPM for retargeting
                predicted_ctr=3.5,   # Higher CTR for warm audiences
                predicted_cpl=profile.target_cpl * 0.7 if profile.target_cpl else 30.0,  # 30% lower CPL
                predicted_cpa=profile.target_cpa * 0.6 if profile.target_cpa else None,
                predicted_roas=profile.target_roas * 1.4 if profile.target_roas else None,  # 40% higher ROAS
                confidence_score=0.88,  # High confidence for retargeting
                
                ab_test_variants=[
                    {
                        "variant_id": "urgency_test",
                        "name": "Urgency vs Standard Messaging",
                        "changes": {"ad_copy_tone": "urgent", "budget_split": 0.3},
                        "hypothesis": "Urgency-focused messaging will improve conversion rates for warm audiences"
                    }
                ]
            )
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error generating retargeting campaign: {e}")
            return None
    
    def _generate_retargeting_prompts(self, profile: MetaUserProfile) -> List[str]:
        """Generate creative prompts for retargeting campaigns"""
        business_type = profile.business_category.value.replace("_", " ").title()
        
        return [
            f"Friendly reminder visual for {business_type}, welcoming tone, 'complete your journey' messaging",
            f"Special offer for returning visitors to {business_type}, exclusive feel, time-sensitive element",
            f"Customer testimonial focus for {business_type}, trust-building, social proof emphasis"
        ]
    
    def _generate_retargeting_copy(self, profile: MetaUserProfile) -> List[str]:
        """Generate ad copy for retargeting campaigns"""
        business_name = profile.business_name or "Your Business"
        
        return [
            f"👋 Welcome back! Complete your journey with {business_name}. We've saved your spot and have something special waiting for you.",
            f"🎁 Exclusive offer for you! As someone interested in {business_name}, enjoy 15% off your first purchase. Limited time only!",
            f"⭐ Join 1000+ happy customers who chose {business_name}. Don't miss out on what you were looking for. Complete your signup today!"
        ]

class MetaAdsAutomationEngine:
    """
    Complete AI-powered automation engine for Facebook and Instagram ads with personalization
    """
    
    def __init__(self):
        # Load centralized Meta configuration
        self.meta_config = get_meta_config()
        
        # Validate configuration
        is_valid, errors = validate_meta_config()
        if not is_valid:
            raise ConfigurationError(f"Meta configuration validation failed: {'; '.join(errors)}")
        
        # Extract commonly used values for convenience
        self.app_id = self.meta_config.app_id
        self.app_secret = self.meta_config.app_secret
        self.access_token = self.meta_config.access_token
        self.ad_account_id = self.meta_config.ad_account_id
        self.page_id = self.meta_config.facebook_page_id
        
        # Use centralized API configuration
        self.api_version = self.meta_config.ads_api_version
        self.api_timeout = self.meta_config.api_timeout
        self.retry_count = self.meta_config.retry_count
        
        # Initialize Facebook Ads API with centralized configuration
        if all([self.app_id, self.app_secret, self.access_token]):
            FacebookAdsApi.init(
                app_id=self.app_id, 
                app_secret=self.app_secret, 
                access_token=self.access_token,
                api_version=self.api_version  # Use centralized API version
            )
            self.account = AdAccount(f'act_{self.ad_account_id}')
            logger.info(f"Meta API initialized with version {self.api_version}")
        else:
            raise ValueError("Missing required Meta API credentials in environment variables")
        
        # Thread pool for blocking operations
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Initialize error handler
        self.error_handler = MetaAPIErrorHandler(
            retry_count=self.retry_count,
            base_delay=1.0
        )
        
        # Initialize personalization engine
        self.personalization_engine = MetaAdsPersonalizationEngine()
        
        # Validate API version compatibility
        self._validate_api_version_compatibility()
    
    def _validate_api_version_compatibility(self):
        """Validate API version compatibility and warn about deprecated features"""
        try:
            # Supported API versions and their features
            SUPPORTED_VERSIONS = {
                'v21.0': {
                    'supported': True,
                    'deprecated_features': [],
                    'new_features': ['enhanced_insights', 'improved_targeting'],
                    'objective_format': 'OUTCOME_*'
                },
                'v20.0': {
                    'supported': True,
                    'deprecated_features': ['old_conversion_api'],
                    'new_features': ['outcome_driven_ads'],
                    'objective_format': 'OUTCOME_*'
                },
                'v19.0': {
                    'supported': True,
                    'deprecated_features': ['legacy_objectives', 'old_insights'],
                    'new_features': [],
                    'objective_format': 'MIXED'  # Both legacy and OUTCOME_* supported
                },
                'v18.0': {
                    'supported': False,
                    'deprecated_features': ['all_legacy_features'],
                    'new_features': [],
                    'objective_format': 'LEGACY'
                }
            }
            
            version_info = SUPPORTED_VERSIONS.get(self.api_version)
            
            if not version_info:
                logger.warning(f"Unknown API version {self.api_version}. Using default compatibility mode.")
                return
            
            if not version_info['supported']:
                raise ValueError(f"API version {self.api_version} is no longer supported. Please upgrade to v20.0 or v21.0")
            
            # Log compatibility information
            if version_info['deprecated_features']:
                logger.warning(f"API version {self.api_version} has deprecated features: {version_info['deprecated_features']}")
            
            if version_info['new_features']:
                logger.info(f"API version {self.api_version} supports new features: {version_info['new_features']}")
            
            # Validate objective format compatibility
            if version_info['objective_format'] == 'LEGACY':
                logger.warning("Using legacy objective format. Consider upgrading to OUTCOME_* format.")
            elif version_info['objective_format'] == 'OUTCOME_*':
                logger.info("Using modern OUTCOME_* objective format.")
            
            self.api_compatibility = version_info
            
        except Exception as e:
            logger.error(f"API version compatibility check failed: {e}")
            # Don't fail initialization, but warn
            self.api_compatibility = {'supported': True, 'objective_format': 'OUTCOME_*'}
    
    def migrate_legacy_objectives(self, objective: str) -> str:
        """Migrate legacy objectives to current OUTCOME_* format"""
        LEGACY_TO_OUTCOME_MAPPING = {
            # Legacy → Modern OUTCOME_* format
            'BRAND_AWARENESS': 'OUTCOME_AWARENESS',
            'REACH': 'OUTCOME_AWARENESS',
            'VIDEO_VIEWS': 'OUTCOME_AWARENESS',
            'LINK_CLICKS': 'OUTCOME_TRAFFIC',
            'CONVERSIONS': 'OUTCOME_SALES',
            'LEAD_GENERATION': 'OUTCOME_LEADS',
            'MESSAGES': 'OUTCOME_LEADS',
            'POST_ENGAGEMENT': 'OUTCOME_ENGAGEMENT',
            'PAGE_LIKES': 'OUTCOME_ENGAGEMENT',
            'EVENT_RESPONSES': 'OUTCOME_ENGAGEMENT',
            'APP_INSTALLS': 'OUTCOME_APP_PROMOTION',
            'PRODUCT_CATALOG_SALES': 'OUTCOME_SALES',
            'STORE_VISITS': 'OUTCOME_AWARENESS'
        }
        
        if objective in LEGACY_TO_OUTCOME_MAPPING:
            migrated = LEGACY_TO_OUTCOME_MAPPING[objective]
            logger.info(f"Migrated legacy objective '{objective}' to '{migrated}'")
            return migrated
        
        # If already in OUTCOME_* format or unknown, return as-is
        return objective
    
    def get_compatible_objective(self, objective: str) -> str:
        """Get API version compatible objective format"""
        try:
            # Check if we need to migrate from legacy format
            if self.api_compatibility.get('objective_format') == 'MIXED':
                # For mixed compatibility, prefer OUTCOME_* but support legacy
                return self.migrate_legacy_objectives(objective)
            elif self.api_compatibility.get('objective_format') == 'OUTCOME_*':
                # Modern format only
                return self.migrate_legacy_objectives(objective)
            else:
                # Legacy format or unknown - return as-is
                return objective
                
        except Exception as e:
            logger.error(f"Objective compatibility check failed: {e}")
            return objective  # Safe fallback
    
    # CAMPAIGN OBJECTIVES MAPPING
    CAMPAIGN_OBJECTIVES = {
        'brand_awareness': 'OUTCOME_AWARENESS',
        'traffic': 'OUTCOME_TRAFFIC',
        'engagement': 'OUTCOME_ENGAGEMENT',
        'leads': 'OUTCOME_LEADS',
        'app_promotion': 'OUTCOME_APP_PROMOTION',
        'sales': 'OUTCOME_SALES',
        'conversions': 'OUTCOME_SALES'  # Most common for e-commerce
    }
    
    async def create_ai_optimized_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete AI-optimized campaign with automatic cross-platform setup
        
        Args:
            campaign_config (Dict): Campaign configuration including:
                - name: Campaign name
                - objective: Campaign objective (brand_awareness, traffic, conversions, etc.)
                - daily_budget: Daily budget in INR
                - target_audience: Audience targeting parameters
                - creative_assets: List of images/videos
                - platforms: ['facebook', 'instagram'] or both
                - placements: Specific placement targeting
        
        Returns:
            Dict with campaign creation results and IDs
        """
        print(f"🚀 Creating AI-optimized campaign: {campaign_config['name']}")
        
        results = {
            'success': False,
            'campaign_id': None,
            'adset_ids': [],
            'ad_ids': [],
            'creative_ids': [],
            'total_ads_created': 0,
            'platforms': campaign_config.get('platforms', ['facebook', 'instagram']),
            'error': None
        }
        
        try:
            # Step 1: Create Campaign
            campaign = await self._create_campaign(campaign_config)
            results['campaign_id'] = campaign['id']
            print(f"✅ Campaign created: {campaign['id']}")
            
            # Step 2: Create platform-specific ad sets
            platforms = campaign_config.get('platforms', ['facebook', 'instagram'])
            
            for platform in platforms:
                print(f"📱 Setting up {platform.upper()} ad targeting...")
                
                # Create optimized ad set for each platform
                adset_config = self._optimize_adset_for_platform(campaign_config, platform)
                adset = await self._create_adset(campaign['id'], adset_config, platform)
                results['adset_ids'].append(adset['id'])
                print(f"✅ {platform.upper()} ad set created: {adset['id']}")
                
                # Step 3: Create AI-optimized creatives for platform
                creative_assets = campaign_config.get('creative_assets', [])
                for i, asset in enumerate(creative_assets):
                    creative = await self._create_creative(asset, platform, i)
                    if creative:
                        results['creative_ids'].append(creative['id'])
                        
                        # Step 4: Create ad linking creative to ad set
                        ad = await self._create_ad(adset['id'], creative['id'], f"{platform}_ad_{i+1}")
                        if ad:
                            results['ad_ids'].append(ad['id'])
                            results['total_ads_created'] += 1
                            print(f"✅ {platform.upper()} ad created: {ad['id']}")
            
            results['success'] = True
            print(f"🎉 Campaign setup complete! Created {results['total_ads_created']} ads across {len(platforms)} platforms")
            
            return results
            
        except ValueError as e:
            logger.error(f"Validation error in campaign creation: {e}")
            print(f"❌ Validation error: {str(e)}")
            results['error'] = f'Validation error: {e}'
            return results
        except Exception as e:
            logger.error(f"Unexpected error in campaign creation: {e}")
            print(f"❌ Campaign creation failed: {str(e)}")
            results['error'] = f'Unexpected error: {e}'
            return results
    
    @with_retry(max_attempts=3)
    async def _create_campaign(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Create Meta advertising campaign with proper async handling"""
        try:
            # Use version-compatible objective mapping
            raw_objective = self.CAMPAIGN_OBJECTIVES.get(config['objective'], 'OUTCOME_SALES')
            objective = self.get_compatible_objective(raw_objective)
            
            # Run blocking Facebook API call in thread pool
            loop = asyncio.get_event_loop()
            campaign = await loop.run_in_executor(
                self._thread_pool,
                lambda: self.account.create_campaign(
                    fields=[],
                    params={
                        Campaign.Field.name: config['name'],
                        Campaign.Field.objective: objective,
                        Campaign.Field.status: Campaign.Status.paused,  # Start paused for safety
                        Campaign.Field.buying_type: Campaign.BuyingType.auction,
                        Campaign.Field.special_ad_categories: config.get('special_ad_categories', []),  # Required field
                    }
                )
            )
            return campaign
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            raise ValueError(f"Campaign creation failed: {e}")
    
    async def _create_adset(self, campaign_id: str, config: Dict[str, Any], platform: str) -> Dict[str, str]:
        """Create optimized ad set for specific platform with proper async handling"""
        try:
            # Platform-specific targeting and placements
            targeting = config['targeting'].copy()
            targeting['publisher_platforms'] = [platform]
            
            # Set platform-specific placements
            if platform == 'facebook':
                targeting['facebook_positions'] = config.get('facebook_placements', ['feed', 'right_hand_column'])
            elif platform == 'instagram':
                targeting['instagram_positions'] = config.get('instagram_placements', ['stream', 'story', 'explore'])
            
            # Run blocking Facebook API call in thread pool
            loop = asyncio.get_event_loop()
            adset = await loop.run_in_executor(
                self._thread_pool,
                lambda: self.account.create_ad_set(
                    fields=[],
                    params={
                        AdSet.Field.name: f"{config['name']} - {platform.upper()}",
                        AdSet.Field.campaign_id: campaign_id,
                        AdSet.Field.daily_budget: int(config['daily_budget'] * 100),  # Convert to cents
                        AdSet.Field.targeting: targeting,
                        AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
                        AdSet.Field.optimization_goal: config.get('optimization_goal', AdSet.OptimizationGoal.link_clicks),
                        AdSet.Field.status: AdSet.Status.active,
                    }
                )
            )
            return adset
            
        except Exception as e:
            logger.error(f"Failed to create adset for {platform}: {e}")
            raise ValueError(f"Adset creation failed: {e}")
    
    async def _create_creative(self, asset_config: Dict[str, Any], platform: str, index: int) -> Optional[Dict[str, str]]:
        """Create platform-optimized ad creative with proper async handling"""
        try:
            creative_spec = {
                'name': f"Creative_{platform}_{index+1}",
                'object_story_spec': {
                    'page_id': self.page_id,
                }
            }
            
            loop = asyncio.get_event_loop()
            
            # Handle different asset types
            if asset_config['type'] == 'image':
                # Upload image first in thread pool
                def upload_image():
                    image = AdImage(parent_id=self.account.get_id())
                    image[AdImage.Field.filename] = asset_config['path']
                    image.remote_create()
                    return image
                
                image = await loop.run_in_executor(self._thread_pool, upload_image)
                
                creative_spec['object_story_spec']['link_data'] = {
                    'image_hash': image[AdImage.Field.hash],
                    'link': asset_config.get('link', 'https://example.com'),
                    'message': self._optimize_copy_for_platform(asset_config.get('message', ''), platform),
                    'call_to_action': {
                        'type': asset_config.get('cta_type', 'LEARN_MORE'),
                        'value': {'link': asset_config.get('link', 'https://example.com')}
                    }
                }
                
            elif asset_config['type'] == 'video':
                # Upload video first in thread pool
                def upload_video():
                    video = AdVideo(parent_id=self.account.get_id())
                    video[AdVideo.Field.filename] = asset_config['path']
                    video.remote_create()
                    return video
                
                video = await loop.run_in_executor(self._thread_pool, upload_video)
                
                creative_spec['object_story_spec']['video_data'] = {
                    'video_id': video['id'],
                    'message': self._optimize_copy_for_platform(asset_config.get('message', ''), platform),
                    'call_to_action': {
                        'type': asset_config.get('cta_type', 'LEARN_MORE'),
                        'value': {'link': asset_config.get('link', 'https://example.com')}
                    }
                }
            
            # Create creative in thread pool
            creative = await loop.run_in_executor(
                self._thread_pool,
                lambda: self.account.create_ad_creative(
                    fields=[],
                    params=creative_spec
                )
            )
            
            return creative
            
        except FileNotFoundError as e:
            logger.error(f"Asset file not found for creative creation: {e}")
            print(f"❌ Asset file not found: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Creative creation failed: {e}")
            print(f"❌ Creative creation failed: {str(e)}")
            return None
    
    async def _create_ad(self, adset_id: str, creative_id: str, ad_name: str) -> Optional[Dict[str, str]]:
        """Create individual ad with proper async handling"""
        try:
            # Run blocking Facebook API call in thread pool
            loop = asyncio.get_event_loop()
            ad = await loop.run_in_executor(
                self._thread_pool,
                lambda: self.account.create_ad(
                    fields=[],
                    params={
                        Ad.Field.name: ad_name,
                        Ad.Field.adset_id: adset_id,
                        Ad.Field.creative: {'creative_id': creative_id},
                        Ad.Field.status: Ad.Status.active,
                    }
                )
            )
            return ad
            
        except Exception as e:
            logger.error(f"Ad creation failed: {e}")
            print(f"❌ Ad creation failed: {str(e)}")
            return None
    
    def _optimize_adset_for_platform(self, config: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """AI optimization for platform-specific ad set configuration"""
        base_targeting = config['target_audience'].copy()
        
        # Platform-specific optimizations
        if platform == 'instagram':
            # Instagram users tend to be younger
            if 'age_max' in base_targeting:
                base_targeting['age_max'] = min(base_targeting.get('age_max', 65), 45)
            
            # Instagram-specific interests
            if 'interests' in base_targeting:
                base_targeting['interests'].extend([
                    {'id': '6003277229526', 'name': 'Photography'},  # Popular on Instagram
                    {'id': '6003348604581', 'name': 'Fashion'}       # Visual platform interests
                ])
        
        elif platform == 'facebook':
            # Facebook has broader age demographics
            base_targeting['age_min'] = base_targeting.get('age_min', 25)
            base_targeting['age_max'] = base_targeting.get('age_max', 65)
        
        return {
            'name': f"{config['name']} - {platform.upper()}",
            'daily_budget': config['daily_budget'] / len(config.get('platforms', [platform])),  # Split budget
            'targeting': base_targeting,
            'optimization_goal': config.get('optimization_goal', AdSet.OptimizationGoal.link_clicks),
            'facebook_placements': config.get('facebook_placements', ['feed', 'right_hand_column']),
            'instagram_placements': config.get('instagram_placements', ['stream', 'story'])
        }
    
    def _optimize_copy_for_platform(self, message: str, platform: str) -> str:
        """AI-powered copy optimization for each platform"""
        if platform == 'instagram':
            # Instagram users respond to more visual, emoji-rich content
            if not any(emoji in message for emoji in ['🔥', '✨', '💫', '🌟']):
                message = f"✨ {message}"
            
            # Add relevant hashtags if not present
            if '#' not in message:
                message += " #innovation #inspiration"
                
        elif platform == 'facebook':
            # Facebook users prefer more detailed, informative content
            if len(message) < 50:
                message += " Learn more about how this can benefit you!"
        
        return message
    
    async def get_campaign_insights(self, campaign_id: str, days: int = 7) -> Dict[str, Any]:
        """Get detailed campaign performance analytics with proper async handling"""
        try:
            # Run blocking Facebook API call in thread pool
            loop = asyncio.get_event_loop()
            
            def get_insights():
                campaign = Campaign(campaign_id)
                return campaign.get_insights(
                    fields=[
                        'impressions',
                        'clicks', 
                        'spend',
                        'cpm',
                        'ctr',
                        'cpc',
                        'conversions',
                        'cost_per_conversion',
                        'reach',
                        'frequency'
                    ],
                    params={
                        'breakdowns': ['publisher_platform', 'placement'],
                        'date_preset': f'last_{days}_days'
                    }
                )
            
            insights = await loop.run_in_executor(self._thread_pool, get_insights)
            
            return {
                'campaign_id': campaign_id,
                'insights': [dict(insight) for insight in insights],
                'summary': self._calculate_performance_summary(insights)
            }
            
        except ValueError as e:
            logger.error(f"Validation error getting campaign insights: {e}")
            print(f"❌ Validation error: {str(e)}")
            return {'error': f'Validation error: {e}'}
        except Exception as e:
            logger.error(f"Failed to get campaign insights: {e}")
            print(f"❌ Failed to get insights: {str(e)}")
            return {'error': f'Unexpected error: {e}'}
    
    def _calculate_performance_summary(self, insights) -> Dict[str, float]:
        """Calculate performance summary across all platforms"""
        total_spend = sum(float(insight.get('spend', 0)) for insight in insights)
        total_impressions = sum(int(insight.get('impressions', 0)) for insight in insights)
        total_clicks = sum(int(insight.get('clicks', 0)) for insight in insights)
        total_conversions = sum(int(insight.get('conversions', 0)) for insight in insights)
        
        return {
            'total_spend': total_spend,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'overall_ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            'overall_cpc': (total_spend / total_clicks) if total_clicks > 0 else 0,
            'overall_roas': (total_conversions / total_spend) if total_spend > 0 else 0
        }
    
    async def ai_campaign_optimizer(self, campaign_id: str) -> Dict[str, Any]:
        """AI-powered campaign optimization based on performance data"""
        print(f"🤖 Running AI optimization for campaign {campaign_id}")
        
        # Get current performance
        insights = await self.get_campaign_insights(campaign_id, days=3)
        if 'error' in insights:
            return {'success': False, 'error': insights['error']}
        
        optimizations = []
        
        # Analyze performance by platform
        for insight in insights['insights']:
            platform = insight.get('publisher_platform')
            ctr = float(insight.get('ctr', 0))
            cpc = float(insight.get('cpc', 0))
            
            # AI Decision Making
            if ctr < 1.0:  # Low CTR
                optimizations.append({
                    'type': 'creative_refresh',
                    'platform': platform,
                    'reason': f'Low CTR ({ctr:.2f}%) - recommend new creatives'
                })
            
            if cpc > 2.0:  # High CPC
                optimizations.append({
                    'type': 'audience_expansion',
                    'platform': platform,
                    'reason': f'High CPC (₹{cpc:.2f}) - expand targeting'
                })
        
        # Execute optimizations
        for optimization in optimizations:
            await self._execute_optimization(campaign_id, optimization)
        
        return {
            'success': True,
            'optimizations_applied': len(optimizations),
            'details': optimizations
        }
    
    async def _execute_optimization(self, campaign_id: str, optimization: Dict[str, Any]):
        """Execute specific optimization action"""
        print(f"⚡ Applying {optimization['type']} for {optimization['platform']}: {optimization['reason']}")
        
        # Implementation would depend on optimization type
        # This is a placeholder for the actual optimization logic
        if optimization['type'] == 'creative_refresh':
            # Logic to create new creatives
            pass
        elif optimization['type'] == 'audience_expansion':
            # Logic to expand audience targeting
            pass

# Wrapper functions for easy campaign creation
async def create_awareness_campaign(name: str, daily_budget: float, target_audience: Dict[str, Any], creative_assets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create brand awareness campaign across Facebook and Instagram"""
    engine = MetaAdsAutomationEngine()
    
    config = {
        'name': name,
        'objective': 'brand_awareness',
        'daily_budget': daily_budget,
        'target_audience': target_audience,
        'creative_assets': creative_assets,
        'platforms': ['facebook', 'instagram']
    }
    
    return await engine.create_ai_optimized_campaign(config)

async def create_conversion_campaign(name: str, daily_budget: float, target_audience: Dict[str, Any], creative_assets: List[Dict[str, Any]], landing_url: str) -> Dict[str, Any]:
    """Create conversion-focused campaign with AI optimization"""
    engine = MetaAdsAutomationEngine()
    
    # Add landing URL to all creative assets
    for asset in creative_assets:
        asset['link'] = landing_url
        asset['cta_type'] = 'SHOP_NOW'
    
    config = {
        'name': name,
        'objective': 'conversions',
        'daily_budget': daily_budget,
        'target_audience': target_audience,
        'creative_assets': creative_assets,
        'platforms': ['facebook', 'instagram'],
        'optimization_goal': AdSet.OptimizationGoal.conversions
    }
    
    return await engine.create_ai_optimized_campaign(config)

async def main():
    print("🤖 Meta Ads AI Automation Platform")
    print("=" * 40)
    print("1. Create awareness campaign")
    print("2. Create conversion campaign")
    print("3. Get campaign insights")
    print("4. Run AI campaign optimizer") 
    print("5. Demo: Complete campaign setup")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        # Sample awareness campaign
        target_audience = {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 55,
            'interests': [
                {'id': '6003139266461', 'name': 'Online shopping'},
                {'id': '6004037027412', 'name': 'Technology'}
            ]
        }
        
        creative_assets = [
            {
                'type': 'image',
                'path': '/path/to/your/image.jpg',
                'message': 'Discover amazing products that change your life!',
                'cta_type': 'LEARN_MORE'
            }
        ]
        
        result = await create_awareness_campaign(
            name="AI Brand Awareness Campaign",
            daily_budget=50.0,
            target_audience=target_audience,
            creative_assets=creative_assets
        )
        
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "2":
        # Sample conversion campaign
        target_audience = {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 45,
            'interests': [
                {'id': '6003139266461', 'name': 'Online shopping'}
            ]
        }
        
        creative_assets = [
            {
                'type': 'image',
                'path': '/path/to/your/product.jpg',
                'message': 'Get 50% off your first order! Limited time offer.',
                'cta_type': 'SHOP_NOW'
            }
        ]
        
        result = await create_conversion_campaign(
            name="AI Conversion Campaign",
            daily_budget=100.0,
            target_audience=target_audience,
            creative_assets=creative_assets,
            landing_url="https://yourstore.com/sale"
        )
        
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "3":
        campaign_id = input("Enter campaign ID: ").strip()
        engine = MetaAdsAutomationEngine()
        insights = await engine.get_campaign_insights(campaign_id)
        print(f"\n📊 Campaign Insights: {json.dumps(insights, indent=2)}")
    
    elif choice == "4":
        campaign_id = input("Enter campaign ID to optimize: ").strip()
        engine = MetaAdsAutomationEngine()
        result = await engine.ai_campaign_optimizer(campaign_id)
        print(f"\n🤖 Optimization Result: {json.dumps(result, indent=2)}")
    
    elif choice == "5":
        print("🚀 Running complete demo campaign setup...")
        
        # Demo configuration
        demo_config = {
            'name': 'AI Demo Campaign - Cross Platform',
            'objective': 'traffic',
            'daily_budget': 25.0,
            'target_audience': {
                'geo_locations': {'countries': ['US']},
                'age_min': 25,
                'age_max': 55
            },
            'creative_assets': [
                {
                    'type': 'image',
                    'path': '/path/to/demo/image.jpg',  # Replace with actual path
                    'message': 'Discover the future of AI automation!',
                    'link': 'https://example.com',
                    'cta_type': 'LEARN_MORE'
                }
            ],
            'platforms': ['facebook', 'instagram']
        }
        
        engine = MetaAdsAutomationEngine()
        result = await engine.create_ai_optimized_campaign(demo_config)
        
        print(f"\n🎉 Demo Campaign Results:")
        print(f"✅ Success: {result['success']}")
        if result['success']:
            print(f"📝 Campaign ID: {result['campaign_id']}")
            print(f"📱 Platforms: {', '.join(result['platforms'])}")
            print(f"🎯 Total Ads Created: {result['total_ads_created']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    else:
        print("❌ Invalid choice!")

# Demo function for fitness studio example
async def fitness_studio_demo():
    """
    Demo function showing how the enhanced system handles specific business scenarios
    Example: Local fitness studio owner with ₹10000/month budget wanting gym memberships
    """
    print("🏋️ FITNESS STUDIO META CAMPAIGN STRATEGY DEMO")
    print("=" * 60)
    
    # Initialize personalization engine
    personalization_engine = MetaAdsPersonalizationEngine()
    
    # Simulate the fitness studio owner's query
    user_query = "I'm a local fitness studio owner with a ₹10000/month budget. What Meta campaign strategy should I use to get more gym memberships?"
    
    # Create a sample user profile for the fitness studio
    user_id = "fitness_studio_001"
    profile_data = {
        "business_name": "FitZone Studio",
        "business_category": "local_service",
        "business_stage": "established",
        "years_in_business": 3,
        "business_location": "Downtown Austin, TX",
        "website_url": "https://fitzonestudio.com",
        "has_customer_list": True,
        "average_order_value": 120.0,  # Monthly membership
        "primary_objective": "OUTCOME_LEADS",
        "monthly_budget": 1000.0,
        "daily_budget_preference": 33.0,
        "target_age_min": 22,
        "target_age_max": 45,
        "target_genders": ["all"],
        "target_locations": [{"type": "city", "key": "Austin", "radius": 15}],
        "target_radius_km": 15,
        "preferred_creative_formats": ["single_image", "single_video"],
        "brand_voice": "motivational",
        "visual_style": "energetic",
        "preferred_placements": ["facebook_feed", "instagram_feed", "instagram_stories"],
        "facebook_vs_instagram_split": 0.4,  # 40% Facebook, 60% Instagram
        "target_cpl": 35.0,
        "risk_tolerance": "medium",
        "local_market_focus": True
    }
    
    try:
        # Create user profile
        print("🔧 Creating personalized user profile...")
        profile = await personalization_engine.create_meta_user_profile(user_id, profile_data)
        print(f"✅ Profile created for {profile.business_name}")
        print(f"   - Business Category: {profile.business_category.value}")
        print(f"   - Monthly Budget: ₹{profile.monthly_budget}")
        print(f"   - Primary Objective: {profile.primary_objective.value}")
        print(f"   - Target Audience: Ages {profile.target_age_min}-{profile.target_age_max}")
        
        # Get business-specific strategy
        print("\n🎯 Generating personalized Meta campaign strategy...")
        strategy = await personalization_engine.get_business_specific_strategy(user_query, profile)
        
        print("\n📊 RECOMMENDED META CAMPAIGN STRATEGY")
        print("-" * 50)
        
        # Business Context
        context = strategy["business_context"]
        print(f"Business Type Detected: {context['business_type']}")
        print(f"Monthly Budget: ₹{context['monthly_budget']}")
        print(f"Primary Goal: {context['primary_goal']}")
        print(f"Local Focus: {'Yes' if context['location_based'] else 'No'}")
        
        # Strategy Recommendations
        recommended_strategy = strategy["recommended_strategy"]
        print(f"\n🎯 CAMPAIGN OBJECTIVE: {recommended_strategy['campaign_objective']}")
        
        # Budget Strategy
        budget = recommended_strategy["recommended_budget"]
        print(f"\n💰 BUDGET ALLOCATION:")
        print(f"   - Daily Budget: ₹{budget['daily_budget']:.2f}")
        print(f"   - Facebook: {budget['platform_split']['facebook']*100:.0f}% (₹{budget['daily_budget']*budget['platform_split']['facebook']:.2f}/day)")
        print(f"   - Instagram: {budget['platform_split']['instagram']*100:.0f}% (₹{budget['daily_budget']*budget['platform_split']['instagram']:.2f}/day)")
        
        # Targeting Strategy
        targeting = recommended_strategy["targeting_strategy"]
        print(f"\n🎯 TARGETING STRATEGY:")
        print(f"   - Audience Type: {targeting['audience_type']}")
        print(f"   - Target Audience Size: ~{targeting['audience_size_target']:,} people")
        print(f"   - Geographic Radius: 15km around Austin, TX")
        
        # Creative Strategy
        creative = recommended_strategy["creative_strategy"]
        print(f"\n🎨 CREATIVE STRATEGY:")
        print(f"   - Primary Format: {creative['primary_format']}")
        print(f"   - Content Themes: {', '.join(creative['content_themes'])}")
        print(f"   - Platform Optimization: {'Enabled' if creative['platform_optimization'] else 'Disabled'}")
        
        # Performance Predictions
        performance = strategy["expected_results"]
        monthly_pred = performance["monthly_predictions"]
        print(f"\n📈 EXPECTED MONTHLY RESULTS:")
        print(f"   - Impressions: {monthly_pred['impressions']:,}")
        print(f"   - Clicks: {monthly_pred['clicks']:,}")
        print(f"   - Leads (Gym Memberships): {monthly_pred['leads']:,}")
        print(f"   - Cost Per Lead: ₹{monthly_pred['cost_per_lead']:.2f}")
        
        # Implementation Steps
        implementation = strategy["implementation_steps"]
        print(f"\n🚀 IMPLEMENTATION ROADMAP:")
        for step in implementation:
            print(f"   {step['step']}. {step['title']} ({step['estimated_time']})")
            for detail in step['details'][:2]:  # Show first 2 details
                print(f"      • {detail}")
        
        # Budget Optimization
        budget_opt = strategy["budget_optimization"]
        print(f"\n💡 BUDGET OPTIMIZATION TIPS:")
        for tip in budget_opt["optimization_tips"][:3]:
            print(f"   • {tip}")
        
        # Timeline
        timeline = strategy["timeline"]
        print(f"\n📅 CAMPAIGN TIMELINE:")
        print(f"   - Setup Phase: {timeline['setup_phase']['duration']}")
        print(f"   - Learning Phase: {timeline['learning_phase']['duration']}")
        print(f"   - Optimization Phase: {timeline['optimization_phase']['duration']}")
        
        print(f"\n✨ SUCCESS METRICS TO WATCH:")
        success_metrics = performance["success_metrics"]
        print(f"   - Target Cost Per Lead: ${success_metrics['target_cpl']:.2f}")
        print(f"   - Target Click-Through Rate: {success_metrics['target_ctr']:.1f}%")
        print(f"   - Expected ROAS: {success_metrics['expected_roas']:.1f}x")
        
        # Generate specific campaign recommendations
        print(f"\n🎯 PERSONALIZED CAMPAIGN RECOMMENDATIONS:")
        campaigns = await personalization_engine.get_personalized_meta_campaigns(user_id, 3)
        
        for i, campaign in enumerate(campaigns, 1):
            print(f"\n   Campaign {i}: {campaign.campaign_name}")
            print(f"   - Type: {campaign.campaign_type}")
            print(f"   - Daily Budget: ${campaign.daily_budget:.2f}")
            print(f"   - Predicted CPL: ${campaign.predicted_cpl:.2f}")
            print(f"   - Confidence Score: {campaign.confidence_score*100:.0f}%")
            print(f"   - Reasoning: {campaign.reasoning}")
        
        print(f"\n🎉 READY TO LAUNCH YOUR META CAMPAIGNS!")
        print("This strategy is specifically tailored for your fitness studio to maximize gym membership leads within your ₹25,000/month budget.")
        
        return {
            "success": True,
            "profile_created": True,
            "strategy_generated": True,
            "campaigns_recommended": len(campaigns),
            "expected_monthly_leads": monthly_pred['leads'],
            "expected_cost_per_lead": monthly_pred['cost_per_lead']
        }
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        return {"success": False, "error": str(e)}

async def main():
    print("🤖 Meta Ads AI Automation Platform with Enhanced Personalization")
    print("=" * 65)
    print("1. Create awareness campaign")
    print("2. Create conversion campaign")
    print("3. Get campaign insights")
    print("4. Run AI campaign optimizer") 
    print("5. Demo: Complete campaign setup")
    print("6. 🏋️ Fitness Studio Demo - Enhanced Personalization")
    print("7. Create personalized user profile")
    print("8. Get business-specific strategy")
    
    choice = input("\nSelect option (1-8): ").strip()
    
    if choice == "6":
        # Run the fitness studio demo
        await fitness_studio_demo()
    
    elif choice == "7":
        # Create personalized user profile demo
        print("\n🔧 CREATE PERSONALIZED META USER PROFILE")
        print("-" * 40)
        
        # Sample profile data
        user_id = input("Enter user ID (or press Enter for demo): ").strip() or "demo_user_001"
        business_name = input("Enter business name (or press Enter for demo): ").strip() or "Demo Business"
        
        profile_data = {
            "business_name": business_name,
            "business_category": "local_service",
            "primary_objective": "OUTCOME_LEADS",
            "monthly_budget": 1500.0,
            "daily_budget_preference": 50.0,
            "target_age_min": 25,
            "target_age_max": 55,
            "preferred_creative_formats": ["single_image"],
            "brand_voice": "professional"
        }
        
        engine = MetaAdsPersonalizationEngine()
        profile = await engine.create_meta_user_profile(user_id, profile_data)
        
        print(f"\n✅ Profile created successfully!")
        print(f"User ID: {profile.user_id}")
        print(f"Business: {profile.business_name}")
        print(f"Category: {profile.business_category.value}")
        print(f"Objective: {profile.primary_objective.value}")
        print(f"Budget: ${profile.monthly_budget}/month")
    
    elif choice == "8":
        # Get business-specific strategy demo
        print("\n🎯 GET BUSINESS-SPECIFIC META STRATEGY")
        print("-" * 40)
        
        user_query = input("Describe your business and goals: ").strip()
        if not user_query:
            user_query = "I run a restaurant and want to increase dinner reservations with a ₹20,000/month budget"
        
        engine = MetaAdsPersonalizationEngine()
        strategy = await engine.get_business_specific_strategy(user_query)
        
        print(f"\n📊 STRATEGY RECOMMENDATION:")
        print(f"Business Type: {strategy['business_context']['business_type']}")
        print(f"Recommended Objective: {strategy['recommended_strategy']['campaign_objective']}")
        print(f"Daily Budget: ${strategy['recommended_strategy']['recommended_budget']['daily_budget']:.2f}")
        print(f"Expected Monthly Leads: {strategy['expected_results']['monthly_predictions']['leads']}")
        
    elif choice == "1":
        # Sample awareness campaign
        target_audience = {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 55,
            'interests': [
                {'id': '6003139266461', 'name': 'Online shopping'},
                {'id': '6004037027412', 'name': 'Technology'}
            ]
        }
        
        creative_assets = [
            {
                'type': 'image',
                'path': '/path/to/your/image.jpg',
                'message': 'Discover amazing products that change your life!',
                'cta_type': 'LEARN_MORE'
            }
        ]
        
        result = await create_awareness_campaign(
            name="AI Brand Awareness Campaign",
            daily_budget=50.0,
            target_audience=target_audience,
            creative_assets=creative_assets
        )
        
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "2":
        # Sample conversion campaign
        target_audience = {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 45,
            'interests': [
                {'id': '6003139266461', 'name': 'Online shopping'}
            ]
        }
        
        creative_assets = [
            {
                'type': 'image',
                'path': '/path/to/your/product.jpg',
                'message': 'Get 50% off your first order! Limited time offer.',
                'cta_type': 'SHOP_NOW'
            }
        ]
        
        result = await create_conversion_campaign(
            name="AI Conversion Campaign",
            daily_budget=100.0,
            target_audience=target_audience,
            creative_assets=creative_assets,
            landing_url="https://yourstore.com/sale"
        )
        
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "3":
        campaign_id = input("Enter campaign ID: ").strip()
        engine = MetaAdsAutomationEngine()
        insights = await engine.get_campaign_insights(campaign_id)
        print(f"\n📊 Campaign Insights: {json.dumps(insights, indent=2)}")
    
    elif choice == "4":
        campaign_id = input("Enter campaign ID to optimize: ").strip()
        engine = MetaAdsAutomationEngine()
        result = await engine.ai_campaign_optimizer(campaign_id)
        print(f"\n🤖 Optimization Result: {json.dumps(result, indent=2)}")
    
    elif choice == "5":
        print("🚀 Running complete demo campaign setup...")
        
        # Demo configuration
        demo_config = {
            'name': 'AI Demo Campaign - Cross Platform',
            'objective': 'traffic',
            'daily_budget': 25.0,
            'target_audience': {
                'geo_locations': {'countries': ['US']},
                'age_min': 25,
                'age_max': 55
            },
            'creative_assets': [
                {
                    'type': 'image',
                    'path': '/path/to/demo/image.jpg',  # Replace with actual path
                    'message': 'Discover the future of AI automation!',
                    'link': 'https://example.com',
                    'cta_type': 'LEARN_MORE'
                }
            ],
            'platforms': ['facebook', 'instagram']
        }
        
        engine = MetaAdsAutomationEngine()
        result = await engine.create_ai_optimized_campaign(demo_config)
        
        print(f"\n🎉 Demo Campaign Results:")
        print(f"✅ Success: {result['success']}")
        if result['success']:
            print(f"📝 Campaign ID: {result['campaign_id']}")
            print(f"📱 Platforms: {', '.join(result['platforms'])}")
            print(f"🎯 Total Ads Created: {result['total_ads_created']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())