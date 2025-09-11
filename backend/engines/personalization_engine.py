"""
Advanced Personalization Engine for Marketing Automation
Provides deep user profiling, campaign recommendations, and adaptive optimization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import random
from sqlalchemy.orm import Session
import anthropic
from backend.utils.config_manager import get_config, ConfigurationError
from backend.database.models import PlatformPriorityEnum

logger = logging.getLogger(__name__)

# User Profile Enums and Data Classes

class BusinessSize(Enum):
    STARTUP = "startup"
    SMB = "smb" 
    ENTERPRISE = "enterprise"

class BudgetRange(Enum):
    MICRO = "micro"      # ₹0-40,000/month
    SMALL = "small"      # ₹40,000-1,60,000/month  
    MEDIUM = "medium"    # ₹1,60,000-8,00,000/month
    LARGE = "large"      # ₹8,00,000-40,00,000/month
    ENTERPRISE = "enterprise"  # ₹40,00,000+/month

class AgeGroup(Enum):
    GEN_Z = "gen_z"           # 16-26
    MILLENNIAL = "millennial"  # 27-42
    GEN_X = "gen_x"           # 43-58
    BOOMER = "boomer"         # 59-77

class BrandVoice(Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"
    LUXURY = "luxury"
    AUTHENTIC = "authentic"
    BOLD = "bold"

class CampaignObjective(Enum):
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    APP_INSTALLS = "app_installs"

class ContentPreference(Enum):
    VIDEO_FIRST = "video_first"
    IMAGE_HEAVY = "image_heavy"
    TEXT_FOCUSED = "text_focused"
    MIXED = "mixed"

# Using PlatformPriorityEnum from models.py instead
PlatformPriority = PlatformPriorityEnum

@dataclass
class UserProfile:
    """Comprehensive user profile for personalization"""
    user_id: str
    
    # Business Information (required fields)
    business_size: BusinessSize
    industry: str
    monthly_budget: BudgetRange
    primary_objective: CampaignObjective
    
    # Business Information (optional fields)
    business_name: Optional[str] = None
    website_url: Optional[str] = None
    years_in_business: Optional[int] = None
    secondary_objectives: List[CampaignObjective] = field(default_factory=list)
    
    # Target Demographics
    target_age_groups: List[AgeGroup] = field(default_factory=list)
    target_locations: List[str] = field(default_factory=list)  # Geographic targeting
    target_interests: List[str] = field(default_factory=list)
    target_behaviors: List[str] = field(default_factory=list)
    
    # Brand & Content Preferences
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    content_preference: ContentPreference = ContentPreference.MIXED
    platform_priorities: List[PlatformPriority] = field(default_factory=list)
    brand_colors: List[str] = field(default_factory=list)  # Hex color codes
    
    # Video-Specific Preferences
    preferred_video_style: str = "marketing commercial"  # cinematic, luxury commercial, etc.
    preferred_aspect_ratios: List[str] = field(default_factory=lambda: ["16:9"])  # 16:9, 1:1, 9:16
    video_content_themes: List[str] = field(default_factory=list)  # product showcase, lifestyle, etc.
    
    # Performance Preferences
    roi_focus: bool = True  # ROI-focused vs engagement-focused
    risk_tolerance: str = "medium"  # conservative, medium, aggressive
    automation_level: str = "medium"  # low, medium, high
    
    # Learning Data
    campaign_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_patterns: Dict[str, Any] = field(default_factory=dict)
    learned_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_campaign: Optional[datetime] = None

@dataclass
class CampaignRecommendation:
    """Personalized campaign recommendation"""
    recommendation_id: str
    user_id: str
    
    # Campaign Details
    recommended_type: str
    campaign_name: str
    description: str
    reasoning: str
    
    # Content Specifications
    content_prompts: List[str]
    caption_templates: List[str]
    visual_style: str
    content_type: str  # image, video, carousel
    
    # Targeting & Budget
    recommended_budget: float
    target_audience: Dict[str, Any]
    platform_allocation: Dict[str, float]  # Platform -> budget percentage
    
    # Performance Predictions
    predicted_ctr: float
    predicted_engagement_rate: float
    predicted_conversion_rate: float
    predicted_roi: float
    confidence_score: float  # 0-1
    
    # A/B Testing Variants
    ab_variants: List[Dict[str, Any]] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)

class PersonalizationEngine:
    """
    Advanced personalization engine that creates deeply customized marketing campaigns
    """
    
    def __init__(self):
        """Initialize personalization engine with Claude AI integration"""
        self.user_profiles: Dict[str, UserProfile] = {}
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.demographic_insights = self._load_demographic_insights()
        self.platform_characteristics = self._load_platform_characteristics()
        self.content_performance_models = {}
        
        # Initialize Claude AI client
        try:
            api_key = get_config("ANTHROPIC_API_KEY")
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            self.ai_enabled = True
            logger.info("Claude AI integration enabled for personalization engine")
        except ConfigurationError as e:
            logger.warning(f"Claude AI not available: {e}")
            self.claude_client = None
            self.ai_enabled = False
        
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """
        Load industry-specific performance benchmarks
        
        Sources:
        - Facebook Business: Industry Benchmarks Report 2024
        - Meta Business Help Center: Ad Performance Benchmarks
        - HubSpot: Social Media Benchmarks Report 2024
        - Socialinsider: Social Media Industry Benchmarks
        - WordStream: Facebook Ad Benchmarks by Industry
        - Hootsuite: Social Media Industry Report 2024
        
        Data represents average performance across Meta platforms (Facebook/Instagram)
        Updated: December 2024
        """
        return {
            "restaurant": {
                "avg_ctr": 1.01, "avg_engagement": 0.68, "avg_conversion": 9.21,  # WordStream 2024
                "video_lift": 1.8, "image_performance": 1.2, "optimal_budget_min": 120000,  # ₹1,20,000
                "avg_cpm": 14.40, "avg_cpc": 1.85, "source": "Meta Business + WordStream 2024"
            },
            "fitness": {
                "avg_ctr": 1.90, "avg_engagement": 1.03, "avg_conversion": 14.29,  # WordStream 2024
                "video_lift": 2.2, "image_performance": 1.4, "optimal_budget_min": 160000,  # ₹1,60,000
                "avg_cpm": 8.58, "avg_cpc": 1.58, "source": "Meta Business + WordStream 2024"
            },
            "beauty": {
                "avg_ctr": 1.16, "avg_engagement": 0.72, "avg_conversion": 9.07,  # WordStream 2024
                "video_lift": 1.9, "image_performance": 1.6, "optimal_budget_min": 140000,  # ₹1,40,000
                "avg_cpm": 8.14, "avg_cpc": 2.52, "source": "Meta Business + WordStream 2024"
            },
            "real_estate": {
                "avg_ctr": 1.08, "avg_engagement": 0.99, "avg_conversion": 10.68,  # WordStream 2024
                "video_lift": 1.5, "image_performance": 1.8, "optimal_budget_min": 400000,  # ₹4,00,000
                "avg_cpm": 5.71, "avg_cpc": 1.81, "source": "Meta Business + WordStream 2024"
            },
            "automotive": {
                "avg_ctr": 0.60, "avg_engagement": 0.40, "avg_conversion": 6.03,  # WordStream 2024
                "video_lift": 2.0, "image_performance": 1.3, "optimal_budget_min": 640000,  # ₹6,40,000
                "avg_cpm": 7.64, "avg_cpc": 2.24, "source": "Meta Business + WordStream 2024"
            },
            "ecommerce": {
                "avg_ctr": 0.90, "avg_engagement": 0.60, "avg_conversion": 4.11,  # WordStream 2024
                "video_lift": 1.7, "image_performance": 1.1, "optimal_budget_min": 240000,  # ₹2,40,000
                "avg_cpm": 14.62, "avg_cpc": 1.72, "source": "Meta Business + WordStream 2024"
            },
            "technology": {
                "avg_ctr": 1.04, "avg_engagement": 0.81, "avg_conversion": 2.83,  # WordStream 2024
                "video_lift": 1.6, "image_performance": 1.2, "optimal_budget_min": 320000,  # ₹3,20,000
                "avg_cpm": 6.75, "avg_cpc": 3.33, "source": "Meta Business + WordStream 2024"
            },
            "finance": {
                "avg_ctr": 0.56, "avg_engagement": 0.35, "avg_conversion": 9.09,  # WordStream 2024
                "video_lift": 1.4, "image_performance": 1.5, "optimal_budget_min": 480000,  # ₹4,80,000
                "avg_cpm": 8.60, "avg_cpc": 3.89, "source": "Meta Business + WordStream 2024"
            }
        }
    
    def _load_demographic_insights(self) -> Dict[str, Dict[str, Any]]:
        """Load demographic-specific insights"""
        return {
            "gen_z": {
                "preferred_platforms": ["instagram", "facebook"],
                "content_preferences": ["video_first", "authentic", "fast_paced"],
                "engagement_multipliers": {"video": 2.1, "image": 1.2, "carousel": 1.4},
                "optimal_times": ["6-9 PM", "9-11 PM"],
                "attention_span": "short"
            },
            "millennial": {
                "preferred_platforms": ["instagram", "facebook"],
                "content_preferences": ["mixed", "informative", "aspirational"],
                "engagement_multipliers": {"video": 1.8, "image": 1.5, "carousel": 1.7},
                "optimal_times": ["7-9 AM", "6-8 PM"],
                "attention_span": "medium"
            },
            "gen_x": {
                "preferred_platforms": ["facebook", "instagram"],
                "content_preferences": ["informative", "value_driven", "authentic"],
                "engagement_multipliers": {"video": 1.4, "image": 1.8, "carousel": 1.3},
                "optimal_times": ["6-8 AM", "5-7 PM"],
                "attention_span": "long"
            },
            "boomer": {
                "preferred_platforms": ["facebook"],
                "content_preferences": ["simple", "clear", "trustworthy"],
                "engagement_multipliers": {"video": 1.1, "image": 1.9, "carousel": 1.2},
                "optimal_times": ["8-10 AM", "2-4 PM"],
                "attention_span": "long"
            }
        }
    
    def _load_platform_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific characteristics"""
        return {
            "instagram": {
                "optimal_formats": ["image", "video", "carousel", "reels"],
                "aspect_ratios": ["1:1", "4:5", "9:16"],
                "max_caption_length": 2200,
                "hashtag_limit": 30,
                "video_length_optimal": 15,
                "audience_skew": "younger"
            },
            "facebook": {
                "optimal_formats": ["image", "video", "link", "carousel"],
                "aspect_ratios": ["16:9", "1:1"],
                "max_caption_length": 63206,
                "hashtag_limit": 10,
                "video_length_optimal": 60,
                "audience_skew": "older"
            }
        }
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create or update comprehensive user profile
        
        Args:
            user_id: Unique user identifier
            profile_data: User profile information
            
        Returns:
            Complete UserProfile object
        """
        try:
            # Create user profile from provided data
            profile = UserProfile(
                user_id=user_id,
                business_size=BusinessSize(profile_data.get("business_size", "smb")),
                industry=profile_data.get("industry", "general"),
                business_name=profile_data.get("business_name"),
                website_url=profile_data.get("website_url"),
                years_in_business=profile_data.get("years_in_business"),
                
                monthly_budget=BudgetRange(profile_data.get("monthly_budget", "small")),
                primary_objective=CampaignObjective(profile_data.get("primary_objective", "lead_generation")),
                secondary_objectives=[CampaignObjective(obj) for obj in profile_data.get("secondary_objectives", [])],
                
                target_age_groups=[AgeGroup(age) for age in profile_data.get("target_age_groups", ["millennial"])],
                target_locations=profile_data.get("target_locations", []),
                target_interests=profile_data.get("target_interests", []),
                target_behaviors=profile_data.get("target_behaviors", []),
                
                brand_voice=BrandVoice(profile_data.get("brand_voice", "professional")),
                content_preference=ContentPreference(profile_data.get("content_preference", "mixed")),
                platform_priorities=[PlatformPriority(p) for p in profile_data.get("platform_priorities", ["facebook", "instagram"])],
                brand_colors=profile_data.get("brand_colors", []),
                
                roi_focus=profile_data.get("roi_focus", True),
                risk_tolerance=profile_data.get("risk_tolerance", "medium"),
                automation_level=profile_data.get("automation_level", "medium")
            )
            
            # Store profile
            self.user_profiles[user_id] = profile
            
            logger.info(f"Created comprehensive user profile for {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise
    
    async def get_personalized_campaign_recommendations(
        self, 
        user_id: str, 
        objective_override: Optional[str] = None
    ) -> List[CampaignRecommendation]:
        """
        Generate personalized campaign recommendations based on user profile
        
        Args:
            user_id: User identifier
            objective_override: Override primary objective for specific recommendations
            
        Returns:
            List of personalized campaign recommendations
        """
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"User profile not found for {user_id}")
            
            recommendations = []
            
            # Get primary objective (with override if provided)
            primary_obj = CampaignObjective(objective_override) if objective_override else profile.primary_objective
            
            # Generate multiple recommendations based on different strategies
            recommendations.extend(await self._generate_objective_based_recommendations(profile, primary_obj))
            recommendations.extend(await self._generate_budget_optimized_recommendations(profile))
            recommendations.extend(await self._generate_demographic_targeted_recommendations(profile))
            recommendations.extend(await self._generate_platform_specific_recommendations(profile))
            
            # Sort by confidence score and return top recommendations
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"Generated {len(recommendations)} personalized recommendations for {user_id}")
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    async def _generate_objective_based_recommendations(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective
    ) -> List[CampaignRecommendation]:
        """Generate recommendations based on campaign objective"""
        recommendations = []
        
        if objective == CampaignObjective.LEAD_GENERATION:
            # Generate AI-powered content if Claude is available
            if self.ai_enabled:
                content_prompts = await self._generate_ai_content_prompts(profile, objective)
                caption_templates = await self._generate_ai_captions(profile, objective)
                campaign_name = await self._generate_ai_campaign_name(profile, objective)
                description = await self._generate_ai_description(profile, objective)
                reasoning = await self._generate_ai_reasoning(profile, objective)
            else:
                # Fallback to static templates
                content_prompts = [
                    f"Professional {profile.industry} lead magnet offer, {profile.brand_voice.value} tone, premium value proposition",
                    f"Free consultation or assessment offer for {profile.industry}, trust-building elements",
                    f"Educational content showcasing expertise in {profile.industry}, credibility focus"
                ]
                caption_templates = [
                    f"🎯 FREE {profile.industry.title()} Assessment! Get personalized insights to grow your business. Limited time offer - claim yours now! 💼",
                    f"📈 Ready to transform your {profile.industry} results? Download our exclusive guide packed with insider strategies! ⬇️",
                    f"✨ Join 1000+ {profile.industry} professionals who've boosted their success with our proven system. Get started free! 🚀"
                ]
                campaign_name = f"Lead Magnet Campaign - {profile.industry.title()}"
                description = "Multi-stage lead generation campaign with lead magnets and retargeting"
                reasoning = f"Optimized for lead generation in {profile.industry} with {profile.business_size.value} business model"
            
            # Lead generation focused campaigns
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type="lead_generation_funnel",
                campaign_name=campaign_name,
                description=description,
                reasoning=reasoning,
                content_prompts=content_prompts,
                caption_templates=caption_templates,
                visual_style=self._get_brand_aligned_style(profile),
                content_type="image" if profile.content_preference != ContentPreference.VIDEO_FIRST else "video",
                recommended_budget=self._calculate_optimal_budget(profile, objective),
                target_audience=self._build_target_audience(profile),
                platform_allocation=self._calculate_platform_allocation(profile),
                predicted_ctr=self._predict_performance_metric(profile, "ctr", objective),
                predicted_engagement_rate=self._predict_performance_metric(profile, "engagement", objective),
                predicted_conversion_rate=self._predict_performance_metric(profile, "conversion", objective),
                predicted_roi=self._predict_performance_metric(profile, "roi", objective),
                confidence_score=self._calculate_confidence_score(profile, objective),
                ab_variants=self._generate_ab_variants(profile, objective)
            )
            recommendations.append(rec)
            
        elif objective == CampaignObjective.BRAND_AWARENESS:
            # Generate AI-powered content if Claude is available
            if self.ai_enabled:
                content_prompts = await self._generate_ai_content_prompts(profile, objective)
                caption_templates = await self._generate_ai_captions(profile, objective)
                campaign_name = await self._generate_ai_campaign_name(profile, objective)
                description = await self._generate_ai_description(profile, objective)
                reasoning = await self._generate_ai_reasoning(profile, objective)
            else:
                # Fallback to static templates
                content_prompts = [
                    f"Behind-the-scenes of {profile.business_name or profile.industry} business, {profile.brand_voice.value} storytelling",
                    f"Founder story or company mission for {profile.industry}, authentic and inspiring tone",
                    f"Customer success stories and testimonials for {profile.industry}, emotional connection focus"
                ]
                caption_templates = [
                    f"🌟 Every great {profile.industry} business starts with a vision. Here's ours... What's yours? 💭",
                    f"📖 The story behind {profile.business_name or 'our company'}: Why we're passionate about {profile.industry} 💪",
                    f"👥 Meet the team making a difference in {profile.industry}. This is who we are! 🤝"
                ]
                campaign_name = f"Brand Story Campaign - {profile.business_name or profile.industry.title()}"
                description = "Multi-touchpoint brand awareness campaign focusing on brand story and values"
                reasoning = f"Brand awareness strategy tailored for {profile.target_age_groups[0].value if profile.target_age_groups else 'general'} audience"
            
            # Brand awareness focused campaigns
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type="brand_awareness_multi_touch",
                campaign_name=campaign_name,
                description=description,
                reasoning=reasoning,
                content_prompts=content_prompts,
                caption_templates=caption_templates,
                visual_style=self._get_brand_aligned_style(profile),
                content_type="video" if profile.content_preference != ContentPreference.TEXT_FOCUSED else "image",
                recommended_budget=self._calculate_optimal_budget(profile, objective),
                target_audience=self._build_target_audience(profile),
                platform_allocation=self._calculate_platform_allocation(profile),
                predicted_ctr=self._predict_performance_metric(profile, "ctr", objective),
                predicted_engagement_rate=self._predict_performance_metric(profile, "engagement", objective),
                predicted_conversion_rate=self._predict_performance_metric(profile, "conversion", objective),
                predicted_roi=self._predict_performance_metric(profile, "roi", objective),
                confidence_score=self._calculate_confidence_score(profile, objective),
                ab_variants=self._generate_ab_variants(profile, objective)
            )
            recommendations.append(rec)
        
        # Add more objective-based recommendations...
        
        return recommendations
    
    async def _generate_budget_optimized_recommendations(self, profile: UserProfile) -> List[CampaignRecommendation]:
        """Generate budget-optimized recommendations"""
        recommendations = []
        
        budget_mapping = {
            BudgetRange.MICRO: {"min": 0, "max": 40000},           # ₹40,000
            BudgetRange.SMALL: {"min": 40000, "max": 160000},      # ₹1,60,000  
            BudgetRange.MEDIUM: {"min": 160000, "max": 800000},    # ₹8,00,000
            BudgetRange.LARGE: {"min": 800000, "max": 4000000},    # ₹40,00,000
            BudgetRange.ENTERPRISE: {"min": 4000000, "max": 16000000} # ₹1,60,00,000
        }
        
        budget_range = budget_mapping[profile.monthly_budget]
        
        if profile.monthly_budget in [BudgetRange.MICRO, BudgetRange.SMALL]:
            # Budget-conscious strategies
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type="budget_maximizer",
                campaign_name=f"Smart Budget Campaign - {profile.industry.title()}",
                description="High-impact, cost-effective campaign optimized for smaller budgets",
                reasoning=f"Budget-optimized strategy for {profile.monthly_budget.value} budget range ({budget_range['min']}-{budget_range['max']})",
                content_prompts=[
                    f"High-impact {profile.industry} content with strong emotional hook, {profile.brand_voice.value} style",
                    f"Problem-solution focused content for {profile.industry}, direct and compelling",
                    f"User-generated content style for {profile.industry}, authentic and relatable"
                ],
                caption_templates=[
                    f"🔥 This {profile.industry} hack changed everything! Try it and see the difference 👇",
                    f"💡 Simple {profile.industry} tip that costs ₹0 but delivers big results! Save this post 📌",
                    f"⚡ Quick {profile.industry} solution that actually works. Who else needs this? Tag them! 👥"
                ],
                visual_style="clean_and_simple",
                content_type="image",  # More budget-friendly
                recommended_budget=min(budget_range["max"] * 0.8, 120000),  # Conservative budget ₹1,20,000
                target_audience=self._build_target_audience(profile, narrow_targeting=True),
                platform_allocation={"facebook": 0.7, "instagram": 0.3},  # Focus on cost-effective platforms
                predicted_ctr=self._predict_performance_metric(profile, "ctr", profile.primary_objective) * 1.1,  # Budget campaigns often have higher CTR
                predicted_engagement_rate=self._predict_performance_metric(profile, "engagement", profile.primary_objective),
                predicted_conversion_rate=self._predict_performance_metric(profile, "conversion", profile.primary_objective),
                predicted_roi=self._predict_performance_metric(profile, "roi", profile.primary_objective) * 1.15,  # Higher ROI for budget campaigns
                confidence_score=0.85,
                ab_variants=self._generate_ab_variants(profile, profile.primary_objective, budget_focused=True)
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _generate_demographic_targeted_recommendations(self, profile: UserProfile) -> List[CampaignRecommendation]:
        """Generate demographic-specific recommendations"""
        recommendations = []
        
        for age_group in profile.target_age_groups:
            demo_insights = self.demographic_insights.get(age_group.value, {})
            
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type=f"demographic_targeted_{age_group.value}",
                campaign_name=f"{age_group.value.title()} Focused - {profile.industry.title()}",
                description=f"Campaign specifically designed for {age_group.value} audience preferences and behaviors",
                reasoning=f"Tailored for {age_group.value} demographics with {demo_insights.get('attention_span', 'medium')} attention span",
                content_prompts=[
                    f"{demo_insights.get('content_preferences', ['engaging'])[0].title()} {profile.industry} content for {age_group.value} audience",
                    f"{profile.industry} content with {demo_insights.get('content_preferences', ['informative'])[1] if len(demo_insights.get('content_preferences', [])) > 1 else 'relevant'} messaging for {age_group.value}",
                    f"Trending {profile.industry} content style that resonates with {age_group.value} values and interests"
                ],
                caption_templates=await self._generate_demographic_captions(profile, age_group),
                visual_style=self._get_demographic_aligned_style(profile, age_group),
                content_type=self._get_optimal_content_type_for_demographic(age_group, profile.content_preference),
                recommended_budget=self._calculate_optimal_budget(profile, profile.primary_objective),
                target_audience=self._build_demographic_specific_audience(profile, age_group),
                platform_allocation=self._get_demographic_platform_allocation(age_group, profile.platform_priorities),
                predicted_ctr=self._predict_performance_metric(profile, "ctr", profile.primary_objective) * demo_insights.get("engagement_multipliers", {}).get("image", 1.0),
                predicted_engagement_rate=self._predict_performance_metric(profile, "engagement", profile.primary_objective) * 1.2,  # Demographic targeting boost
                predicted_conversion_rate=self._predict_performance_metric(profile, "conversion", profile.primary_objective),
                predicted_roi=self._predict_performance_metric(profile, "roi", profile.primary_objective),
                confidence_score=self._calculate_confidence_score(profile, profile.primary_objective, demographic_boost=True),
                ab_variants=self._generate_demographic_ab_variants(profile, age_group)
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _generate_platform_specific_recommendations(self, profile: UserProfile) -> List[CampaignRecommendation]:
        """Generate platform-optimized recommendations"""
        recommendations = []
        
        for platform in profile.platform_priorities:
            platform_chars = self.platform_characteristics.get(platform.value, {})
            
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type=f"platform_optimized_{platform.value}",
                campaign_name=f"{platform.value.title()} Native - {profile.industry.title()}",
                description=f"Campaign optimized specifically for {platform.value} platform characteristics and audience",
                reasoning=f"Native {platform.value} strategy leveraging platform-specific features and audience behaviors",
                content_prompts=await self._generate_platform_specific_prompts(profile, platform) if self.ai_enabled else self._generate_static_platform_prompts(profile, platform),
                caption_templates=await self._generate_platform_specific_captions(profile, platform) if self.ai_enabled else self._generate_static_platform_captions(profile, platform),
                visual_style=self._get_platform_aligned_style(platform, profile.brand_voice),
                content_type=platform_chars.get("optimal_formats", ["image"])[0],
                recommended_budget=self._calculate_platform_specific_budget(profile, platform),
                target_audience=self._build_platform_specific_audience(profile, platform),
                platform_allocation={platform.value: 1.0},  # Single platform focus
                predicted_ctr=self._predict_platform_performance(profile, platform, "ctr"),
                predicted_engagement_rate=self._predict_platform_performance(profile, platform, "engagement"),
                predicted_conversion_rate=self._predict_platform_performance(profile, platform, "conversion"),
                predicted_roi=self._predict_platform_performance(profile, platform, "roi"),
                confidence_score=self._calculate_platform_confidence_score(profile, platform),
                ab_variants=self._generate_platform_ab_variants(profile, platform)
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _generate_ai_content_prompts(self, profile: UserProfile, objective: CampaignObjective) -> List[str]:
        """Generate AI-powered content prompts using Claude"""
        if not self.ai_enabled:
            return []
        
        try:
            prompt = f"""
            Create 3 professional content prompts for a {objective.value} marketing campaign with these specifications:
            
            Business Details:
            - Industry: {profile.industry}
            - Business Size: {profile.business_size.value}
            - Business Name: {profile.business_name or "Business"}
            - Brand Voice: {profile.brand_voice.value}
            - Content Preference: {profile.content_preference.value}
            
            Target Audience:
            - Age Groups: {[age.value for age in profile.target_age_groups]}
            - Interests: {profile.target_interests}
            - Locations: {profile.target_locations}
            
            Requirements:
            - Each prompt should be specific and actionable for content creators
            - Match the {profile.brand_voice.value} brand voice
            - Focus on {objective.value} as the primary goal
            - Consider {profile.content_preference.value} content preference
            - Include specific visual and messaging guidance
            
            Return 3 content prompts as a JSON array of strings.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = message.content[0].text
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            # Fallback if parsing fails
            lines = [line.strip() for line in content_text.split('\n') if line.strip() and not line.strip().startswith(('#', '-', '*'))]
            return lines[:3] if len(lines) >= 3 else lines
            
        except Exception as e:
            logger.error(f"Error generating AI content prompts: {e}")
            # Return fallback prompts
            return [
                f"High-impact {profile.industry} content with {profile.brand_voice.value} tone, {objective.value} focus",
                f"Engaging {profile.industry} visual content for {profile.target_age_groups[0].value if profile.target_age_groups else 'target'} audience",
                f"Professional {profile.industry} content showcasing expertise, {objective.value} optimized"
            ]
    
    async def _generate_ai_captions(self, profile: UserProfile, objective: CampaignObjective) -> List[str]:
        """Generate AI-powered captions using Claude"""
        if not self.ai_enabled:
            return []
        
        try:
            prompt = f"""
            Create 3 engaging social media captions for a {objective.value} campaign with these specifications:
            
            Business Details:
            - Industry: {profile.industry}
            - Business Name: {profile.business_name or "Business"}
            - Brand Voice: {profile.brand_voice.value}
            - Primary Platforms: {[p.value for p in profile.platform_priorities] if profile.platform_priorities else ["facebook", "instagram"]}
            
            Target Audience:
            - Age Groups: {[age.value for age in profile.target_age_groups]}
            - Interests: {profile.target_interests}
            
            Requirements:
            - Each caption should be 150-250 characters
            - Use appropriate emojis for social media engagement
            - Match the {profile.brand_voice.value} brand voice
            - Include clear call-to-action for {objective.value}
            - Make them platform-appropriate and engaging
            - Use industry-relevant language for {profile.industry}
            
            Return 3 captions as a JSON array of strings.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = message.content[0].text
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            # Fallback if parsing fails
            lines = [line.strip().strip('"') for line in content_text.split('\n') if line.strip() and len(line.strip()) > 50]
            return lines[:3] if len(lines) >= 3 else lines
            
        except Exception as e:
            logger.error(f"Error generating AI captions: {e}")
            # Return fallback captions
            return [
                f"🚀 Transform your {profile.industry} results! Get started today 💪",
                f"✨ Join successful {profile.industry} professionals. See the difference! 🎯",
                f"📈 Ready to elevate your {profile.industry} game? Let's do this! 🔥"
            ]
    
    async def _generate_ai_campaign_name(self, profile: UserProfile, objective: CampaignObjective) -> str:
        """Generate AI-powered campaign name using Claude"""
        if not self.ai_enabled:
            return f"{objective.value.title()} Campaign - {profile.industry.title()}"
        
        try:
            prompt = f"""
            Create a compelling campaign name for a {objective.value} marketing campaign:
            
            Business Details:
            - Industry: {profile.industry}
            - Business Name: {profile.business_name or "Business"}
            - Brand Voice: {profile.brand_voice.value}
            - Business Size: {profile.business_size.value}
            
            Requirements:
            - Make it catchy and professional
            - 3-6 words maximum
            - Reflect the {objective.value} goal
            - Match {profile.brand_voice.value} brand voice
            - Industry-relevant for {profile.industry}
            
            Return only the campaign name, no additional text.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            campaign_name = message.content[0].text.strip().strip('"')
            return campaign_name if len(campaign_name) > 0 else f"{objective.value.title()} Campaign - {profile.industry.title()}"
            
        except Exception as e:
            logger.error(f"Error generating AI campaign name: {e}")
            return f"{objective.value.title()} Campaign - {profile.industry.title()}"
    
    async def _generate_ai_description(self, profile: UserProfile, objective: CampaignObjective) -> str:
        """Generate AI-powered campaign description using Claude"""
        if not self.ai_enabled:
            return f"Professional {objective.value} campaign for {profile.industry} businesses"
        
        try:
            prompt = f"""
            Create a professional campaign description for a {objective.value} marketing campaign:
            
            Business Details:
            - Industry: {profile.industry}
            - Business Size: {profile.business_size.value}
            - Monthly Budget: {profile.monthly_budget.value}
            - Target Audience: {[age.value for age in profile.target_age_groups]}
            
            Requirements:
            - 2-3 sentences maximum
            - Professional tone
            - Explain the campaign strategy and approach
            - Focus on {objective.value} as primary goal
            - Include expected outcomes
            
            Return only the description, no additional text.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            description = message.content[0].text.strip()
            return description if len(description) > 0 else f"Professional {objective.value} campaign for {profile.industry} businesses"
            
        except Exception as e:
            logger.error(f"Error generating AI description: {e}")
            return f"Professional {objective.value} campaign for {profile.industry} businesses"
    
    async def _generate_ai_reasoning(self, profile: UserProfile, objective: CampaignObjective) -> str:
        """Generate AI-powered campaign reasoning using Claude"""
        if not self.ai_enabled:
            return f"Optimized for {objective.value} in {profile.industry} with {profile.business_size.value} business model"
        
        try:
            prompt = f"""
            Explain the strategic reasoning for a {objective.value} marketing campaign:
            
            Business Context:
            - Industry: {profile.industry}
            - Business Size: {profile.business_size.value}
            - Budget Range: {profile.monthly_budget.value}
            - Target Demographics: {[age.value for age in profile.target_age_groups]}
            - Brand Voice: {profile.brand_voice.value}
            - Platforms: {[p.value for p in profile.platform_priorities]}
            
            Requirements:
            - 1-2 sentences explaining why this campaign approach is optimal
            - Include specific benefits for this business profile
            - Mention platform and demographic alignment
            - Professional and data-informed tone
            
            Return only the reasoning, no additional text.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            reasoning = message.content[0].text.strip()
            return reasoning if len(reasoning) > 0 else f"Optimized for {objective.value} in {profile.industry} with {profile.business_size.value} business model"
            
        except Exception as e:
            logger.error(f"Error generating AI reasoning: {e}")
            return f"Optimized for {objective.value} in {profile.industry} with {profile.business_size.value} business model"
    
    async def _generate_platform_specific_prompts(self, profile: UserProfile, platform: PlatformPriority) -> List[str]:
        """Generate AI-powered platform-specific content prompts using Claude"""
        try:
            platform_info = self.platform_characteristics.get(platform.value, {})
            
            prompt = f"""
            Create 3 content prompts specifically optimized for {platform.value} platform:
            
            Platform Specifications:
            - Platform: {platform.value}
            - Optimal Formats: {platform_info.get('optimal_formats', [])}
            - Aspect Ratios: {platform_info.get('aspect_ratios', [])}
            - Video Length: {platform_info.get('video_length_optimal', 30)} seconds
            - Audience Skew: {platform_info.get('audience_skew', 'general')}
            
            Business Context:
            - Industry: {profile.industry}
            - Brand Voice: {profile.brand_voice.value}
            - Content Preference: {profile.content_preference.value}
            - Primary Objective: {profile.primary_objective.value}
            
            Requirements:
            - Each prompt must be platform-native and optimized for {platform.value}
            - Consider platform's unique features and user behavior
            - Match {profile.brand_voice.value} brand voice
            - Focus on {profile.primary_objective.value} objective
            - Include specific visual and technical guidance
            
            Return 3 platform-optimized prompts as a JSON array of strings.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = message.content[0].text
            import re, json
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            lines = [line.strip() for line in content_text.split('\n') if line.strip() and not line.strip().startswith(('#', '-', '*'))]
            return lines[:3] if len(lines) >= 3 else lines
            
        except Exception as e:
            logger.error(f"Error generating AI platform prompts: {e}")
            return self._generate_static_platform_prompts(profile, platform)
    
    async def _generate_platform_specific_captions(self, profile: UserProfile, platform: PlatformPriority) -> List[str]:
        """Generate AI-powered platform-specific captions using Claude"""
        try:
            platform_info = self.platform_characteristics.get(platform.value, {})
            
            prompt = f"""
            Create 3 social media captions optimized for {platform.value}:
            
            Platform Specifications:
            - Platform: {platform.value}
            - Max Caption Length: {platform_info.get('max_caption_length', 2200)} characters
            - Hashtag Limit: {platform_info.get('hashtag_limit', 30)}
            - Audience Skew: {platform_info.get('audience_skew', 'general')}
            
            Business Context:
            - Industry: {profile.industry}
            - Brand Voice: {profile.brand_voice.value}
            - Business Name: {profile.business_name or "Business"}
            - Primary Objective: {profile.primary_objective.value}
            
            Requirements:
            - Each caption should be native to {platform.value} culture and style
            - Use platform-appropriate length and format
            - Include relevant emojis and hashtags (within limits)
            - Match {profile.brand_voice.value} brand voice
            - Focus on {profile.primary_objective.value} objective
            - Consider platform's user engagement patterns
            
            Return 3 platform-optimized captions as a JSON array of strings.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = message.content[0].text
            import re, json
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            lines = [line.strip().strip('"') for line in content_text.split('\n') if line.strip() and len(line.strip()) > 30]
            return lines[:3] if len(lines) >= 3 else lines
            
        except Exception as e:
            logger.error(f"Error generating AI platform captions: {e}")
            return self._generate_static_platform_captions(profile, platform)
    
    def _generate_static_platform_prompts(self, profile: UserProfile, platform: PlatformPriority) -> List[str]:
        """Generate static platform-specific content prompts as fallback"""
        if platform == PlatformPriority.INSTAGRAM:
            return [
                f"Visually stunning {profile.industry} content with high-quality imagery, {profile.brand_voice.value} style",
                f"Instagram Stories-optimized {profile.industry} content with interactive elements",
                f"Aesthetic {profile.industry} post perfect for Instagram feed, lifestyle focus"
            ]
        else:  # Facebook
            return [
                f"Facebook-optimized {profile.industry} content with community engagement focus",
                f"Shareable {profile.industry} content designed for Facebook audience",
                f"Informative {profile.industry} post optimized for Facebook algorithm"
            ]
    
    def _generate_static_platform_captions(self, profile: UserProfile, platform: PlatformPriority) -> List[str]:
        """Generate static platform-specific captions as fallback"""
        if platform == PlatformPriority.INSTAGRAM:
            return [
                f"✨ {profile.industry} inspiration for your feed! Double-tap if you agree 💫 #{profile.industry.replace(' ', '')}",
                f"📸 Behind the scenes of {profile.industry} excellence! Save this post 📌 #behindthescenes",
                f"🎯 Your daily dose of {profile.industry} motivation! Follow for more 👆 #inspiration"
            ]
        else:  # Facebook
            return [
                f"🌟 {profile.industry} tips that actually work! Share with friends who need this 👥",
                f"💡 Quick {profile.industry} advice for your timeline. What do you think? 🤔",
                f"📈 {profile.industry} insights worth sharing! Tag someone who'd find this helpful 👇"
            ]
    
    def _get_brand_aligned_style(self, profile: UserProfile) -> str:
        """Get visual style aligned with brand voice"""
        style_mapping = {
            BrandVoice.PROFESSIONAL: "professional_clean",
            BrandVoice.CASUAL: "casual_friendly",
            BrandVoice.PLAYFUL: "colorful_dynamic",
            BrandVoice.LUXURY: "elegant_premium",
            BrandVoice.AUTHENTIC: "natural_authentic",
            BrandVoice.BOLD: "bold_striking"
        }
        return style_mapping.get(profile.brand_voice, "professional_clean")
    
    def _calculate_optimal_budget(self, profile: UserProfile, objective: CampaignObjective) -> float:
        """Calculate optimal budget based on profile and objective (in INR)"""
        budget_mapping = {
            BudgetRange.MICRO: 25000,      # ₹25,000
            BudgetRange.SMALL: 100000,     # ₹1,00,000  
            BudgetRange.MEDIUM: 400000,    # ₹4,00,000
            BudgetRange.LARGE: 2000000,    # ₹20,00,000
            BudgetRange.ENTERPRISE: 6000000 # ₹60,00,000
        }
        
        base_budget = budget_mapping.get(profile.monthly_budget, 100000)
        
        # Adjust based on objective
        objective_multipliers = {
            CampaignObjective.BRAND_AWARENESS: 1.2,
            CampaignObjective.LEAD_GENERATION: 1.0,
            CampaignObjective.SALES: 1.3,
            CampaignObjective.ENGAGEMENT: 0.8,
            CampaignObjective.TRAFFIC: 0.9
        }
        
        multiplier = objective_multipliers.get(objective, 1.0)
        
        # Adjust based on industry benchmarks
        industry_benchmark = self.industry_benchmarks.get(profile.industry, {})
        min_budget = industry_benchmark.get("optimal_budget_min", 80000)  # ₹80,000 minimum
        
        recommended_budget = max(base_budget * multiplier, min_budget)
        
        return min(recommended_budget, base_budget * 1.5)  # Cap at 1.5x base budget
    
    def _get_age_range_from_groups(self, age_groups: List[AgeGroup]) -> List[int]:
        """Convert age groups to age range numbers"""
        age_mapping = {
            AgeGroup.GEN_Z: [16, 26],
            AgeGroup.MILLENNIAL: [27, 42],
            AgeGroup.GEN_X: [43, 58],
            AgeGroup.BOOMER: [59, 77]
        }
        
        if not age_groups:
            return [18, 65]  # Default broad range
        
        min_age = min([age_mapping[group][0] for group in age_groups])
        max_age = max([age_mapping[group][1] for group in age_groups])
        return [min_age, max_age]
    
    def _build_target_audience(self, profile: UserProfile, narrow_targeting: bool = False) -> Dict[str, Any]:
        """Build target audience configuration"""
        audience = {
            "age_range": self._get_age_range_from_groups(profile.target_age_groups),
            "locations": profile.target_locations or ["India"],
            "interests": profile.target_interests,
            "behaviors": profile.target_behaviors,
            "business_size": profile.business_size.value
        }
        
        if narrow_targeting and profile.monthly_budget in [BudgetRange.MICRO, BudgetRange.SMALL]:
            # More specific targeting for smaller budgets
            audience["detailed_targeting"] = "narrow"
            audience["lookalike_percentage"] = 1  # 1% lookalike for precise targeting
        
        return audience
    
    def _calculate_platform_allocation(self, profile: UserProfile) -> Dict[str, float]:
        """Calculate budget allocation across platforms"""
        if not profile.platform_priorities:
            return {"facebook": 0.6, "instagram": 0.4}
        
        # Simple even distribution with slight preference for first platform
        allocation = {}
        num_platforms = len(profile.platform_priorities)
        
        for i, platform in enumerate(profile.platform_priorities):
            if i == 0:  # First platform gets slight boost
                allocation[platform.value] = 0.4 if num_platforms > 1 else 1.0
            else:
                remaining = 0.6 / (num_platforms - 1) if num_platforms > 1 else 0
                allocation[platform.value] = remaining
        
        return allocation
    
    def _predict_performance_metric(
        self, 
        profile: UserProfile, 
        metric: str, 
        objective: CampaignObjective
    ) -> float:
        """Predict performance metrics based on profile"""
        # Get industry baseline
        industry_benchmark = self.industry_benchmarks.get(profile.industry, {})
        base_value = industry_benchmark.get(f"avg_{metric}", 2.0)
        
        # Apply modifiers based on profile characteristics
        multiplier = 1.0
        
        # Business size modifier
        if profile.business_size == BusinessSize.ENTERPRISE:
            multiplier *= 1.15
        elif profile.business_size == BusinessSize.STARTUP:
            multiplier *= 0.95
        
        # Budget modifier
        if profile.monthly_budget in [BudgetRange.LARGE, BudgetRange.ENTERPRISE]:
            multiplier *= 1.1
        elif profile.monthly_budget == BudgetRange.MICRO:
            multiplier *= 0.9
        
        # Objective alignment modifier
        if metric == "conversion" and objective == CampaignObjective.SALES:
            multiplier *= 1.2
        elif metric == "engagement" and objective == CampaignObjective.ENGAGEMENT:
            multiplier *= 1.3
        
        return base_value * multiplier
    
    def _calculate_confidence_score(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        demographic_boost: bool = False
    ) -> float:
        """Calculate confidence score for recommendation"""
        base_confidence = 0.7
        
        # Boost confidence based on profile completeness
        profile_completeness = 0
        if profile.target_age_groups:
            profile_completeness += 0.15
        if profile.platform_priorities:
            profile_completeness += 0.15
        if profile.target_interests:
            profile_completeness += 0.1
        
        # Industry familiarity boost
        if profile.industry in self.industry_benchmarks:
            profile_completeness += 0.2
        
        # Campaign history boost
        if profile.campaign_history:
            profile_completeness += 0.15
        
        # Demographic targeting boost
        if demographic_boost:
            profile_completeness += 0.1
        
        return min(base_confidence + profile_completeness, 0.95)
    
    def _generate_ab_variants(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        budget_focused: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate A/B test variants"""
        variants = []
        
        # Variant 1: Different visual style
        variants.append({
            "variant_id": "style_a",
            "name": "Visual Style A",
            "changes": {
                "visual_style": "clean_minimal" if not budget_focused else "user_generated",
                "color_scheme": "brand_primary"
            },
            "test_hypothesis": "Clean minimal style will perform better for professional audience"
        })
        
        # Variant 2: Different caption approach
        variants.append({
            "variant_id": "caption_b",
            "name": "Caption Approach B",
            "changes": {
                "caption_tone": "question_focused" if objective == CampaignObjective.ENGAGEMENT else "action_focused",
                "cta_style": "soft_ask" if profile.brand_voice == BrandVoice.AUTHENTIC else "direct_ask"
            },
            "test_hypothesis": "Different caption approach will improve engagement rate"
        })
        
        # Variant 3: Different targeting
        if not budget_focused:
            variants.append({
                "variant_id": "targeting_c",
                "name": "Broader Targeting",
                "changes": {
                    "audience_size": "broader",
                    "targeting_precision": "interest_based"
                },
                "test_hypothesis": "Broader targeting will reduce cost per result"
            })
        
        return variants
    
    # Helper methods for demographic-specific content
    async def _generate_demographic_captions(self, profile: UserProfile, age_group: AgeGroup) -> List[str]:
        """Generate AI-powered age-group specific captions"""
        if self.ai_enabled:
            return await self._generate_ai_demographic_captions(profile, age_group)
        
        # Fallback to static captions
        if age_group == AgeGroup.GEN_Z:
            return [
                f"✨ {profile.industry} hack that's actually legit 💯 Who else needs this? 👀",
                f"POV: You found the perfect {profile.industry} solution 🎯 Comment if you're trying this!",
                f"This {profile.industry} trend is everything 🔥 Tag someone who needs to see this!"
            ]
        elif age_group == AgeGroup.MILLENNIAL:
            return [
                f"🌟 Game-changing {profile.industry} strategy for busy professionals. Save this for later! 📌",
                f"💡 Finally, a {profile.industry} solution that actually works. Here's what you need to know:",
                f"📈 Leveling up your {profile.industry} game with this proven approach. Who's ready to try it?"
            ]
        elif age_group == AgeGroup.GEN_X:
            return [
                f"📊 Proven {profile.industry} strategies that deliver real results. Based on 20+ years of experience.",
                f"💼 Smart {profile.industry} solutions for serious professionals. Here's what works:",
                f"🎯 Time-tested {profile.industry} approach that consistently delivers. Worth your investment."
            ]
        else:  # BOOMER
            return [
                f"📋 Reliable {profile.industry} advice you can trust. Simple, effective, proven.",
                f"✅ Straightforward {profile.industry} solution that makes sense. No complicated steps.",
                f"🏆 Quality {profile.industry} service with old-fashioned values. Experience matters."
            ]
    
    async def _generate_ai_demographic_captions(self, profile: UserProfile, age_group: AgeGroup) -> List[str]:
        """Generate AI-powered demographic-specific captions using Claude"""
        try:
            demo_characteristics = {
                AgeGroup.GEN_Z: {
                    "tone": "casual, authentic, trendy",
                    "language": "uses slang, abbreviations, trending terms",
                    "engagement": "questions, challenges, relatable content"
                },
                AgeGroup.MILLENNIAL: {
                    "tone": "aspirational, professional yet relatable",
                    "language": "goal-oriented, efficiency-focused, practical",
                    "engagement": "save-worthy content, actionable advice"
                },
                AgeGroup.GEN_X: {
                    "tone": "professional, experienced, results-focused",
                    "language": "straightforward, value-driven, proven methods",
                    "engagement": "expertise, credibility, time-tested approaches"
                },
                AgeGroup.BOOMER: {
                    "tone": "trustworthy, clear, traditional",
                    "language": "simple, direct, reliable terminology",
                    "engagement": "quality, experience, traditional values"
                }
            }
            
            demo_info = demo_characteristics.get(age_group, demo_characteristics[AgeGroup.MILLENNIAL])
            
            prompt = f"""
            Create 3 social media captions specifically for {age_group.value} demographic in the {profile.industry} industry:
            
            Demographic Profile:
            - Age Group: {age_group.value}
            - Tone: {demo_info['tone']}
            - Language Style: {demo_info['language']}
            - Engagement Style: {demo_info['engagement']}
            
            Business Context:
            - Industry: {profile.industry}
            - Brand Voice: {profile.brand_voice.value}
            - Business Name: {profile.business_name or "Business"}
            
            Requirements:
            - Each caption 150-250 characters
            - Use demographic-appropriate language and tone
            - Include relevant emojis for {age_group.value} audience
            - Focus on {profile.primary_objective.value}
            - Make them highly engaging for this specific age group
            
            Return 3 captions as a JSON array of strings.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = message.content[0].text
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            # Fallback if parsing fails
            lines = [line.strip().strip('"') for line in content_text.split('\n') if line.strip() and len(line.strip()) > 50]
            return lines[:3] if len(lines) >= 3 else lines
            
        except Exception as e:
            logger.error(f"Error generating AI demographic captions: {e}")
            # Return static fallback based on age group to avoid recursion
            if age_group == AgeGroup.GEN_Z:
                return [
                    f"✨ {profile.industry} hack that's actually legit 💯 Who else needs this? 👀",
                    f"POV: You found the perfect {profile.industry} solution 🎯 Comment if you're trying this!",
                    f"This {profile.industry} trend is everything 🔥 Tag someone who needs to see this!"
                ]
            elif age_group == AgeGroup.MILLENNIAL:
                return [
                    f"🌟 Game-changing {profile.industry} strategy for busy professionals. Save this for later! 📌",
                    f"💡 Finally, a {profile.industry} solution that actually works. Here's what you need to know:",
                    f"📈 Leveling up your {profile.industry} game with this proven approach. Who's ready to try it?"
                ]
            elif age_group == AgeGroup.GEN_X:
                return [
                    f"📊 Proven {profile.industry} strategies that deliver real results. Based on 20+ years of experience.",
                    f"💼 Smart {profile.industry} solutions for serious professionals. Here's what works:",
                    f"🎯 Time-tested {profile.industry} approach that consistently delivers. Worth your investment."
                ]
            else:  # BOOMER
                return [
                    f"📋 Reliable {profile.industry} advice you can trust. Simple, effective, proven.",
                    f"✅ Straightforward {profile.industry} solution that makes sense. No complicated steps.",
                    f"🏆 Quality {profile.industry} service with old-fashioned values. Experience matters."
                ]
    
    def _get_demographic_aligned_style(self, profile: UserProfile, age_group: AgeGroup) -> str:
        """Get visual style aligned with demographic preferences"""
        if age_group == AgeGroup.GEN_Z:
            return "trendy_vibrant"
        elif age_group == AgeGroup.MILLENNIAL:
            return "modern_aspirational"
        elif age_group == AgeGroup.GEN_X:
            return "professional_polished"
        else:  # BOOMER
            return "classic_trustworthy"
    
    def _build_demographic_specific_audience(self, profile: UserProfile, age_group: AgeGroup) -> Dict[str, Any]:
        """Build demographic-specific target audience"""
        base_audience = self._build_target_audience(profile)
        age_range = {
            AgeGroup.GEN_Z: [16, 26],
            AgeGroup.MILLENNIAL: [27, 42], 
            AgeGroup.GEN_X: [43, 58],
            AgeGroup.BOOMER: [59, 77]
        }
        base_audience["age_range"] = age_range.get(age_group, [18, 65])
        base_audience["demographic_focus"] = age_group.value
        return base_audience
    
    def _get_demographic_platform_allocation(self, age_group: AgeGroup, platform_priorities: List[PlatformPriority]) -> Dict[str, float]:
        """Get platform allocation optimized for demographic"""
        # Platform preferences by age group (Facebook and Instagram only)
        demo_platform_weights = {
            AgeGroup.GEN_Z: {"instagram": 0.7, "facebook": 0.3},
            AgeGroup.MILLENNIAL: {"instagram": 0.6, "facebook": 0.4},
            AgeGroup.GEN_X: {"facebook": 0.7, "instagram": 0.3},
            AgeGroup.BOOMER: {"facebook": 0.9, "instagram": 0.1}
        }
        
        weights = demo_platform_weights.get(age_group, demo_platform_weights[AgeGroup.MILLENNIAL])
        
        if not platform_priorities:
            return {"facebook": 0.6, "instagram": 0.4}
        
        # Adjust allocation based on user priorities and demographic weights
        allocation = {}
        total_weight = 0
        for platform in platform_priorities:
            weight = weights.get(platform.value, 0.1)
            allocation[platform.value] = weight
            total_weight += weight
        
        # Normalize to sum to 1.0
        if total_weight > 0:
            for platform in allocation:
                allocation[platform] = allocation[platform] / total_weight
        
        return allocation
    
    def _generate_demographic_ab_variants(self, profile: UserProfile, age_group: AgeGroup) -> List[Dict[str, Any]]:
        """Generate demographic-specific A/B test variants"""
        variants = []
        
        demo_insights = self.demographic_insights.get(age_group.value, {})
        
        variants.append({
            "variant_id": f"demo_style_{age_group.value}",
            "name": f"{age_group.value.title()} Optimized Style",
            "changes": {
                "visual_style": self._get_demographic_aligned_style(profile, age_group),
                "content_tone": demo_insights.get("content_preferences", ["neutral"])[0]
            },
            "test_hypothesis": f"Demographic-optimized style will resonate better with {age_group.value} audience"
        })
        
        variants.append({
            "variant_id": f"platform_native_{age_group.value}",
            "name": f"{age_group.value.title()} Platform Native",
            "changes": {
                "platform_focus": demo_insights.get("preferred_platforms", ["facebook"])[0],
                "engagement_style": demo_insights.get("engagement_multipliers", {})
            },
            "test_hypothesis": f"Platform-native approach will improve engagement for {age_group.value}"
        })
        
        return variants
    
    def _calculate_platform_specific_budget(self, profile: UserProfile, platform: PlatformPriority) -> float:
        """Calculate platform-specific budget allocation"""
        base_budget = self._calculate_optimal_budget(profile, profile.primary_objective)
        
        # Platform cost multipliers based on average CPM/CPC (Facebook and Instagram only)
        platform_multipliers = {
            PlatformPriority.INSTAGRAM: 1.0,
            PlatformPriority.FACEBOOK: 0.9
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        return base_budget * multiplier
    
    def _build_platform_specific_audience(self, profile: UserProfile, platform: PlatformPriority) -> Dict[str, Any]:
        """Build platform-specific target audience"""
        base_audience = self._build_target_audience(profile)
        
        # Platform-specific audience adjustments
        platform_adjustments = {
            PlatformPriority.INSTAGRAM: {"visual_first": True, "lifestyle_focus": True},
            PlatformPriority.FACEBOOK: {"community_focus": True, "broader_reach": True}
        }
        
        adjustments = platform_adjustments.get(platform, {})
        base_audience.update(adjustments)
        base_audience["platform_optimized"] = platform.value
        
        return base_audience
    
    def _predict_platform_performance(self, profile: UserProfile, platform: PlatformPriority, metric: str) -> float:
        """Predict platform-specific performance metrics"""
        base_metric = self._predict_performance_metric(profile, metric, profile.primary_objective)
        
        # Platform performance multipliers based on industry averages
        platform_performance = {
            PlatformPriority.INSTAGRAM: {"ctr": 1.1, "engagement": 1.3, "conversion": 0.9, "roi": 1.0},
            PlatformPriority.FACEBOOK: {"ctr": 1.0, "engagement": 1.0, "conversion": 1.0, "roi": 1.0}
        }
        
        multiplier = platform_performance.get(platform, {}).get(metric, 1.0)
        return base_metric * multiplier
    
    def _calculate_platform_confidence_score(self, profile: UserProfile, platform: PlatformPriority) -> float:
        """Calculate confidence score for platform-specific recommendation"""
        base_confidence = self._calculate_confidence_score(profile, profile.primary_objective)
        
        # Boost confidence if platform is in user priorities
        if platform in profile.platform_priorities:
            base_confidence += 0.1
        
        # Boost confidence based on demographic alignment
        if profile.target_age_groups:
            demo_platforms = self.demographic_insights.get(profile.target_age_groups[0].value, {}).get("preferred_platforms", [])
            if platform.value in demo_platforms:
                base_confidence += 0.1
        
        return min(base_confidence, 0.95)
    
    def _generate_platform_ab_variants(self, profile: UserProfile, platform: PlatformPriority) -> List[Dict[str, Any]]:
        """Generate platform-specific A/B test variants"""
        variants = []
        platform_chars = self.platform_characteristics.get(platform.value, {})
        
        # Content format variant
        optimal_formats = platform_chars.get("optimal_formats", ["image"])
        if len(optimal_formats) > 1:
            variants.append({
                "variant_id": f"format_{platform.value}",
                "name": f"Alternative {platform.value.title()} Format",
                "changes": {
                    "content_format": optimal_formats[1] if len(optimal_formats) > 1 else optimal_formats[0],
                    "aspect_ratio": platform_chars.get("aspect_ratios", ["1:1"])[0]
                },
                "test_hypothesis": f"Different content format will perform better on {platform.value}"
            })
        
        # Platform-native style variant
        variants.append({
            "variant_id": f"native_{platform.value}",
            "name": f"Native {platform.value.title()} Style",
            "changes": {
                "platform_native": True,
                "hashtag_strategy": "platform_optimized" if platform_chars.get("hashtag_limit", 0) > 0 else None
            },
            "test_hypothesis": f"Platform-native approach will improve algorithmic distribution on {platform.value}"
        })
        
        return variants
    
    def _get_platform_aligned_style(self, platform: PlatformPriority, brand_voice: BrandVoice) -> str:
        """Get visual style aligned with platform characteristics and brand voice"""
        platform_styles = {
            PlatformPriority.INSTAGRAM: "aesthetic_polished",
            PlatformPriority.FACEBOOK: "community_friendly"
        }
        
        base_style = platform_styles.get(platform, "balanced_professional")
        
        # Adjust based on brand voice
        if brand_voice == BrandVoice.LUXURY:
            base_style = f"premium_{base_style}"
        elif brand_voice == BrandVoice.PLAYFUL:
            base_style = f"vibrant_{base_style}"
        elif brand_voice == BrandVoice.AUTHENTIC:
            base_style = f"genuine_{base_style}"
        
        return base_style
    
    def _get_optimal_content_type_for_demographic(self, age_group: AgeGroup, content_pref: ContentPreference) -> str:
        """Get optimal content type for demographic"""
        demo_insights = self.demographic_insights.get(age_group.value, {})
        
        if "video_first" in demo_insights.get("content_preferences", []):
            return "video"
        elif content_pref == ContentPreference.VIDEO_FIRST:
            return "video"
        else:
            return "image"
    
    # Additional helper methods would be implemented here...
    
    async def learn_from_campaign_performance(
        self, 
        user_id: str, 
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Learn from campaign performance to improve future recommendations
        
        Args:
            user_id: User identifier
            campaign_data: Campaign performance data
            
        Returns:
            Learning insights and profile updates
        """
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Extract performance metrics
            actual_ctr = campaign_data.get("ctr", 0)
            actual_conversion = campaign_data.get("conversion_rate", 0)
            actual_roi = campaign_data.get("roi", 0)
            campaign_type = campaign_data.get("type", "unknown")
            
            # Add to campaign history
            profile.campaign_history.append({
                "campaign_id": campaign_data.get("campaign_id"),
                "type": campaign_type,
                "performance": {
                    "ctr": actual_ctr,
                    "conversion_rate": actual_conversion,
                    "roi": actual_roi
                },
                "date": datetime.now().isoformat()
            })
            
            # Update learned preferences
            if actual_roi > 10:  # Good performance
                if campaign_type not in profile.learned_preferences:
                    profile.learned_preferences[campaign_type] = {"success_count": 0, "total_count": 0}
                profile.learned_preferences[campaign_type]["success_count"] += 1
            
            if campaign_type not in profile.learned_preferences:
                profile.learned_preferences[campaign_type] = {"success_count": 0, "total_count": 0}
            profile.learned_preferences[campaign_type]["total_count"] += 1
            
            # Update performance patterns
            if "avg_performance" not in profile.performance_patterns:
                profile.performance_patterns["avg_performance"] = {}
            
            current_avg = profile.performance_patterns["avg_performance"]
            current_avg["ctr"] = (current_avg.get("ctr", 0) + actual_ctr) / 2
            current_avg["conversion"] = (current_avg.get("conversion", 0) + actual_conversion) / 2
            current_avg["roi"] = (current_avg.get("roi", 0) + actual_roi) / 2
            
            profile.updated_at = datetime.now()
            
            logger.info(f"Updated learning data for user {user_id}")
            
            return {
                "success": True,
                "insights": {
                    "best_performing_type": max(
                        profile.learned_preferences.items(),
                        key=lambda x: x[1]["success_count"] / max(x[1]["total_count"], 1),
                        default=("unknown", {"success_count": 0, "total_count": 1})
                    )[0],
                    "average_performance": profile.performance_patterns["avg_performance"],
                    "total_campaigns": len(profile.campaign_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Error learning from campaign performance: {e}")
            return {"error": str(e)}
    
    async def get_personalized_benchmarks(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized performance benchmarks for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Personalized benchmarks based on user profile and industry
        """
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Get industry baseline
            industry_benchmarks = self.industry_benchmarks.get(profile.industry, {})
            
            # Adjust benchmarks based on user characteristics
            personalized_benchmarks = {}
            
            for metric, baseline in industry_benchmarks.items():
                if metric.startswith("avg_"):
                    adjusted_value = baseline
                    
                    # Adjust for business size
                    if profile.business_size == BusinessSize.ENTERPRISE:
                        adjusted_value *= 1.15
                    elif profile.business_size == BusinessSize.STARTUP:
                        adjusted_value *= 0.95
                    
                    # Adjust for budget
                    if profile.monthly_budget in [BudgetRange.LARGE, BudgetRange.ENTERPRISE]:
                        adjusted_value *= 1.1
                    
                    # Use historical performance if available
                    if profile.performance_patterns.get("avg_performance"):
                        historical = profile.performance_patterns["avg_performance"].get(metric.replace("avg_", ""), 0)
                        if historical > 0:
                            adjusted_value = (adjusted_value * 0.7) + (historical * 0.3)  # 70% benchmark, 30% history
                    
                    personalized_benchmarks[metric] = round(adjusted_value, 2)
                else:
                    personalized_benchmarks[metric] = baseline
            
            # Add confidence intervals
            for metric in ["avg_ctr", "avg_engagement", "avg_conversion"]:
                if metric in personalized_benchmarks:
                    base = personalized_benchmarks[metric]
                    personalized_benchmarks[f"{metric}_range"] = {
                        "low": round(base * 0.8, 2),
                        "expected": base,
                        "high": round(base * 1.2, 2)
                    }
            
            return {
                "user_id": user_id,
                "industry": profile.industry,
                "business_size": profile.business_size.value,
                "benchmarks": personalized_benchmarks,
                "data_sources": {
                    "industry_baseline": True,
                    "user_history": len(profile.campaign_history) > 0,
                    "demographic_adjustments": len(profile.target_age_groups) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting personalized benchmarks: {e}")
            return {"error": str(e)}

# Example usage and testing
async def main():
    """Test the personalization engine"""
    print("🎯 Advanced Marketing Personalization Engine")
    print("=" * 50)
    
    engine = PersonalizationEngine()
    
    # Create sample user profile
    sample_profile_data = {
        "business_size": "smb",
        "industry": "fitness",
        "business_name": "FitStudio Pro",
        "monthly_budget": "small",
        "primary_objective": "lead_generation",
        "target_age_groups": ["millennial"],
        "target_locations": ["New York", "Los Angeles"],
        "target_interests": ["fitness", "health", "wellness"],
        "brand_voice": "authentic",
        "content_preference": "video_first",
        "platform_priorities": ["instagram", "facebook"],
        "roi_focus": True
    }
    
    # Create user profile
    user_id = "user_123"
    profile = await engine.create_user_profile(user_id, sample_profile_data)
    print(f"✅ Created profile for {profile.business_name}")
    
    # Get personalized recommendations
    recommendations = await engine.get_personalized_campaign_recommendations(user_id)
    print(f"\n📊 Generated {len(recommendations)} recommendations:")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.campaign_name}")
        print(f"   Type: {rec.recommended_type}")
        print(f"   Confidence: {rec.confidence_score:.2f}")
        print(f"   Budget: ₹{rec.recommended_budget:,.0f}")
        print(f"   Predicted ROI: {rec.predicted_roi:.1f}%")
        print(f"   Reasoning: {rec.reasoning}")
    
    # Get personalized benchmarks
    benchmarks = await engine.get_personalized_benchmarks(user_id)
    print(f"\n🎯 Personalized Benchmarks:")
    print(f"   Expected CTR: {benchmarks['benchmarks']['avg_ctr']:.2f}%")
    print(f"   Expected Engagement: {benchmarks['benchmarks']['avg_engagement']:.2f}%")
    print(f"   Expected Conversion: {benchmarks['benchmarks']['avg_conversion']:.2f}%")
    
    # Simulate learning from campaign
    sample_campaign_data = {
        "campaign_id": "camp_123",
        "type": "lead_generation_funnel",
        "ctr": 3.2,
        "conversion_rate": 9.8,
        "roi": 15.5
    }
    
    learning_result = await engine.learn_from_campaign_performance(user_id, sample_campaign_data)
    print(f"\n🧠 Learning Result: {learning_result}")

if __name__ == "__main__":
    asyncio.run(main())