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

logger = logging.getLogger(__name__)

# User Profile Enums and Data Classes

class BusinessSize(Enum):
    STARTUP = "startup"
    SMB = "smb" 
    ENTERPRISE = "enterprise"

class BudgetRange(Enum):
    MICRO = "micro"      # $0-500/month
    SMALL = "small"      # $500-2000/month  
    MEDIUM = "medium"    # $2000-10000/month
    LARGE = "large"      # $10000-50000/month
    ENTERPRISE = "enterprise"  # $50000+/month

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

class PlatformPriority(Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"

@dataclass
class UserProfile:
    """Comprehensive user profile for personalization"""
    user_id: str
    
    # Business Information
    business_size: BusinessSize
    industry: str
    monthly_budget: BudgetRange
    primary_objective: CampaignObjective
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
    competitor_urls: List[str] = field(default_factory=list)
    
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
        """Initialize personalization engine"""
        self.user_profiles: Dict[str, UserProfile] = {}
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.demographic_insights = self._load_demographic_insights()
        self.platform_characteristics = self._load_platform_characteristics()
        self.content_performance_models = {}
        
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry-specific performance benchmarks"""
        return {
            "restaurant": {
                "avg_ctr": 2.8, "avg_engagement": 4.2, "avg_conversion": 12.5,
                "video_lift": 1.8, "image_performance": 1.2, "optimal_budget_min": 1500
            },
            "fitness": {
                "avg_ctr": 3.1, "avg_engagement": 6.2, "avg_conversion": 8.7,
                "video_lift": 2.2, "image_performance": 1.4, "optimal_budget_min": 2000
            },
            "beauty": {
                "avg_ctr": 3.8, "avg_engagement": 5.9, "avg_conversion": 11.2,
                "video_lift": 1.9, "image_performance": 1.6, "optimal_budget_min": 1800
            },
            "real_estate": {
                "avg_ctr": 2.1, "avg_engagement": 3.4, "avg_conversion": 15.8,
                "video_lift": 1.5, "image_performance": 1.8, "optimal_budget_min": 5000
            },
            "automotive": {
                "avg_ctr": 1.9, "avg_engagement": 2.8, "avg_conversion": 22.5,
                "video_lift": 2.0, "image_performance": 1.3, "optimal_budget_min": 8000
            },
            "ecommerce": {
                "avg_ctr": 2.3, "avg_engagement": 4.7, "avg_conversion": 6.8,
                "video_lift": 1.7, "image_performance": 1.1, "optimal_budget_min": 3000
            }
        }
    
    def _load_demographic_insights(self) -> Dict[str, Dict[str, Any]]:
        """Load demographic-specific insights"""
        return {
            "gen_z": {
                "preferred_platforms": ["tiktok", "instagram"],
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
                "preferred_platforms": ["facebook", "linkedin"],
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
            },
            "tiktok": {
                "optimal_formats": ["video"],
                "aspect_ratios": ["9:16"],
                "max_caption_length": 100,
                "hashtag_limit": 100,
                "video_length_optimal": 30,
                "audience_skew": "youngest"
            },
            "linkedin": {
                "optimal_formats": ["image", "video", "article"],
                "aspect_ratios": ["16:9", "1:1"],
                "max_caption_length": 3000,
                "hashtag_limit": 3,
                "video_length_optimal": 90,
                "audience_skew": "professional"
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
                competitor_urls=profile_data.get("competitor_urls", []),
                
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
            # Lead generation focused campaigns
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type="lead_generation_funnel",
                campaign_name=f"Lead Magnet Campaign - {profile.industry.title()}",
                description="Multi-stage lead generation campaign with lead magnets and retargeting",
                reasoning=f"Optimized for lead generation in {profile.industry} with {profile.business_size.value} business model",
                content_prompts=[
                    f"Professional {profile.industry} lead magnet offer, {profile.brand_voice.value} tone, premium value proposition",
                    f"Free consultation or assessment offer for {profile.industry}, trust-building elements",
                    f"Educational content showcasing expertise in {profile.industry}, credibility focus"
                ],
                caption_templates=[
                    f"🎯 FREE {profile.industry.title()} Assessment! Get personalized insights to grow your business. Limited time offer - claim yours now! 💼",
                    f"📈 Ready to transform your {profile.industry} results? Download our exclusive guide packed with insider strategies! ⬇️",
                    f"✨ Join 1000+ {profile.industry} professionals who've boosted their success with our proven system. Get started free! 🚀"
                ],
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
            # Brand awareness focused campaigns
            rec = CampaignRecommendation(
                recommendation_id=str(uuid.uuid4()),
                user_id=profile.user_id,
                recommended_type="brand_awareness_multi_touch",
                campaign_name=f"Brand Story Campaign - {profile.business_name or profile.industry.title()}",
                description="Multi-touchpoint brand awareness campaign focusing on brand story and values",
                reasoning=f"Brand awareness strategy tailored for {profile.target_age_groups[0].value if profile.target_age_groups else 'general'} audience",
                content_prompts=[
                    f"Behind-the-scenes of {profile.business_name or profile.industry} business, {profile.brand_voice.value} storytelling",
                    f"Founder story or company mission for {profile.industry}, authentic and inspiring tone",
                    f"Customer success stories and testimonials for {profile.industry}, emotional connection focus"
                ],
                caption_templates=[
                    f"🌟 Every great {profile.industry} business starts with a vision. Here's ours... What's yours? 💭",
                    f"📖 The story behind {profile.business_name or 'our company'}: Why we're passionate about {profile.industry} 💪",
                    f"👥 Meet the team making a difference in {profile.industry}. This is who we are! 🤝"
                ],
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
            BudgetRange.MICRO: {"min": 0, "max": 500},
            BudgetRange.SMALL: {"min": 500, "max": 2000},
            BudgetRange.MEDIUM: {"min": 2000, "max": 10000},
            BudgetRange.LARGE: {"min": 10000, "max": 50000},
            BudgetRange.ENTERPRISE: {"min": 50000, "max": 200000}
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
                    f"💡 Simple {profile.industry} tip that costs $0 but delivers big results! Save this post 📌",
                    f"⚡ Quick {profile.industry} solution that actually works. Who else needs this? Tag them! 👥"
                ],
                visual_style="clean_and_simple",
                content_type="image",  # More budget-friendly
                recommended_budget=min(budget_range["max"] * 0.8, 1500),  # Conservative budget
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
                caption_templates=self._generate_demographic_captions(profile, age_group),
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
                content_prompts=self._generate_platform_specific_prompts(profile, platform),
                caption_templates=self._generate_platform_specific_captions(profile, platform),
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
        """Calculate optimal budget based on profile and objective"""
        budget_mapping = {
            BudgetRange.MICRO: 300,
            BudgetRange.SMALL: 1200,
            BudgetRange.MEDIUM: 5000,
            BudgetRange.LARGE: 25000,
            BudgetRange.ENTERPRISE: 75000
        }
        
        base_budget = budget_mapping.get(profile.monthly_budget, 1200)
        
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
        min_budget = industry_benchmark.get("optimal_budget_min", 1000)
        
        recommended_budget = max(base_budget * multiplier, min_budget)
        
        return min(recommended_budget, base_budget * 1.5)  # Cap at 1.5x base budget
    
    def _build_target_audience(self, profile: UserProfile, narrow_targeting: bool = False) -> Dict[str, Any]:
        """Build target audience configuration"""
        audience = {
            "age_range": self._get_age_range_from_groups(profile.target_age_groups),
            "locations": profile.target_locations or ["United States"],
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
        if profile.competitor_urls:
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
    def _generate_demographic_captions(self, profile: UserProfile, age_group: AgeGroup) -> List[str]:
        """Generate age-group specific captions"""
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
        print(f"   Budget: ${rec.recommended_budget:,.0f}")
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