"""
Dynamic Content Generator
Adapts content generation to user preferences, demographics, and performance data
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import uuid

from personalization_engine import (
    PersonalizationEngine, UserProfile, AgeGroup, BrandVoice, 
    ContentPreference, PlatformPriority, CampaignObjective
)

logger = logging.getLogger(__name__)

@dataclass
class ContentVariation:
    """A content variation optimized for specific user characteristics"""
    variation_id: str
    content_type: str  # image, video, carousel
    
    # Generated Content
    visual_prompt: str
    caption: str
    hashtags: List[str]
    
    # Style Specifications
    visual_style: str
    color_palette: List[str]
    aspect_ratio: str
    duration: Optional[int] = None  # For videos
    
    # Targeting Context
    target_demographic: str
    platform_optimized: str
    objective_focus: str
    
    # Performance Predictions
    predicted_engagement: float
    predicted_ctr: float
    predicted_conversion: float
    
    # Generation Metadata
    personalization_factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AdaptiveContentSet:
    """Set of content variations for A/B testing"""
    content_set_id: str
    user_id: str
    campaign_objective: str
    
    # Content Variations
    variations: List[ContentVariation]
    control_variation: ContentVariation
    
    # Test Configuration
    test_hypothesis: str
    test_duration_days: int
    traffic_split: Dict[str, float]  # variation_id -> traffic percentage
    
    # Success Metrics
    primary_metric: str
    secondary_metrics: List[str]
    
    created_at: datetime = field(default_factory=datetime.now)

class DynamicContentGenerator:
    """
    Generates personalized content variations based on user profile and performance data
    """
    
    def __init__(self, personalization_engine: PersonalizationEngine):
        """Initialize with personalization engine"""
        self.personalization_engine = personalization_engine
        self.content_templates = self._load_content_templates()
        self.style_variations = self._load_style_variations()
        self.performance_learnings = {}
    
    def _load_content_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load content templates for different demographics and objectives"""
        return {
            "lead_generation": {
                "gen_z": {
                    "prompts": [
                        "Authentic behind-the-scenes content showing real results, casual smartphone style, bright natural lighting",
                        "Before/after transformation with genuine excitement, user-generated feel, vibrant colors",
                        "Quick tutorial or hack demonstration, trendy aesthetic, high energy visual"
                    ],
                    "captions": [
                        "ngl this actually works 💯 who else is tired of [problem]? 👀",
                        "POV: you found the solution you've been looking for ✨ try this if you're ready for change",
                        "this [industry] hack hits different 🔥 comment 'yes' if you want the free guide"
                    ],
                    "styles": ["trendy_authentic", "vibrant_casual", "smartphone_realistic"]
                },
                "millennial": {
                    "prompts": [
                        "Professional lifestyle content showing aspirational results, clean modern aesthetic, natural lighting",
                        "Educational content with clear value proposition, Instagram-worthy visuals, polished but approachable",
                        "Success story or case study presentation, modern infographic style, trustworthy design"
                    ],
                    "captions": [
                        "Finally, a [industry] solution that actually fits into my busy life 🙌 Here's what changed everything:",
                        "Invest in yourself with this game-changing [industry] strategy 💡 Save this post for later!",
                        "Real talk: This [industry] approach saved me [benefit]. Ready to level up? 📈"
                    ],
                    "styles": ["modern_aspirational", "clean_professional", "lifestyle_polished"]
                },
                "gen_x": {
                    "prompts": [
                        "Professional demonstration of expertise and results, corporate quality, trustworthy presentation",
                        "Detailed explanation with clear benefits and ROI, business-appropriate aesthetic, authoritative style",
                        "Testimonial or case study format, professional photography, credibility-focused design"
                    ],
                    "captions": [
                        "Proven [industry] strategies that deliver measurable results. Based on 20+ years of experience.",
                        "Smart [industry] investment for serious professionals. Here's the ROI breakdown:",
                        "Time-tested approach that consistently outperforms. Ready to see the difference?"
                    ],
                    "styles": ["corporate_professional", "authoritative_clean", "business_trustworthy"]
                },
                "boomer": {
                    "prompts": [
                        "Clear, straightforward presentation of benefits, traditional aesthetic, high contrast and readability",
                        "Step-by-step explanation with simple visuals, classic design, easy to understand format",
                        "Testimonial from satisfied customer, traditional photography, emphasis on trust and reliability"
                    ],
                    "captions": [
                        "Reliable [industry] service you can trust. Simple, effective, proven results.",
                        "Quality [industry] solution with old-fashioned values. Experience matters.",
                        "Straightforward approach that makes sense. No complicated steps, just results."
                    ],
                    "styles": ["traditional_trustworthy", "simple_clear", "classic_reliable"]
                }
            },
            "brand_awareness": {
                "gen_z": {
                    "prompts": [
                        "Behind-the-scenes authentic moment showing brand personality, casual documentary style",
                        "Brand values in action with real impact, social justice or sustainability angle if relevant",
                        "Community or team moment showing authentic culture, diverse and inclusive visuals"
                    ],
                    "captions": [
                        "this is why we do what we do 💜 values over profit always",
                        "meet the humans behind [brand] ✨ we're just people who care about [mission]",
                        "building something different in the [industry] space 🌟 authenticity over everything"
                    ],
                    "styles": ["documentary_authentic", "diverse_inclusive", "values_driven"]
                },
                "millennial": {
                    "prompts": [
                        "Brand story moment showing journey and growth, aspirational lifestyle integration",
                        "Mission-driven content showing impact and purpose, professional but personal approach",
                        "Innovation or progress showcase with future-focused messaging, modern aesthetic"
                    ],
                    "captions": [
                        "The story behind [brand]: Why we're passionate about changing [industry] 🚀",
                        "Building a [industry] company that aligns with your values. This is our mission:",
                        "Innovation meets purpose in everything we do. Here's what drives us: 💡"
                    ],
                    "styles": ["mission_focused", "innovation_forward", "purpose_driven"]
                }
            }
        }
    
    def _load_style_variations(self) -> Dict[str, Dict[str, Any]]:
        """Load style variations for different brand voices and platforms"""
        return {
            "professional": {
                "color_palettes": [
                    ["#2563EB", "#1E40AF", "#F8FAFC", "#475569"],  # Blue professional
                    ["#059669", "#047857", "#F0FDF4", "#374151"],  # Green professional
                    ["#7C3AED", "#5B21B6", "#FAF5FF", "#4B5563"]   # Purple professional
                ],
                "visual_elements": ["clean_lines", "minimal_text", "corporate_fonts", "professional_imagery"],
                "composition_styles": ["centered", "grid_layout", "hierarchy_clear"]
            },
            "casual": {
                "color_palettes": [
                    ["#F59E0B", "#D97706", "#FFFBEB", "#6B7280"],  # Warm casual
                    ["#EF4444", "#DC2626", "#FEF2F2", "#6B7280"],  # Red casual
                    ["#10B981", "#059669", "#ECFDF5", "#6B7280"]   # Green casual
                ],
                "visual_elements": ["rounded_corners", "friendly_fonts", "lifestyle_imagery", "approachable_design"],
                "composition_styles": ["asymmetrical", "organic_layout", "playful_hierarchy"]
            },
            "luxury": {
                "color_palettes": [
                    ["#1F2937", "#111827", "#F9FAFB", "#D4AF37"],  # Black gold luxury
                    ["#374151", "#1F2937", "#FFFFFF", "#8B5A2B"],  # Grey bronze luxury
                    ["#0F172A", "#1E293B", "#F8FAFC", "#C0392B"]   # Navy red luxury
                ],
                "visual_elements": ["elegant_typography", "premium_imagery", "gold_accents", "sophisticated_layout"],
                "composition_styles": ["symmetrical", "refined_hierarchy", "spacious_design"]
            }
        }
    
    async def generate_personalized_content_variations(
        self, 
        user_id: str, 
        campaign_objective: CampaignObjective,
        content_brief: str,
        num_variations: int = 3
    ) -> AdaptiveContentSet:
        """
        Generate personalized content variations for A/B testing
        
        Args:
            user_id: User identifier
            campaign_objective: Campaign objective
            content_brief: Brief description of desired content
            num_variations: Number of variations to generate
            
        Returns:
            Set of personalized content variations
        """
        try:
            # Get user profile
            profile = self.personalization_engine.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"User profile not found for {user_id}")
            
            variations = []
            
            # Generate control variation (baseline)
            control_variation = await self._generate_control_variation(
                profile, campaign_objective, content_brief
            )
            
            # Generate test variations
            for i in range(num_variations):
                if i == 0:
                    # Demographic-optimized variation
                    variation = await self._generate_demographic_variation(
                        profile, campaign_objective, content_brief
                    )
                elif i == 1:
                    # Platform-optimized variation
                    variation = await self._generate_platform_variation(
                        profile, campaign_objective, content_brief
                    )
                else:
                    # Performance-optimized variation (based on learning)
                    variation = await self._generate_performance_variation(
                        profile, campaign_objective, content_brief
                    )
                
                variations.append(variation)
            
            # Create adaptive content set
            content_set = AdaptiveContentSet(
                content_set_id=str(uuid.uuid4()),
                user_id=user_id,
                campaign_objective=campaign_objective.value,
                variations=variations,
                control_variation=control_variation,
                test_hypothesis=self._generate_test_hypothesis(profile, variations),
                test_duration_days=14,  # Standard 2-week test
                traffic_split=self._calculate_traffic_split(len(variations) + 1),
                primary_metric=self._get_primary_metric(campaign_objective),
                secondary_metrics=["engagement_rate", "ctr", "conversion_rate"]
            )
            
            logger.info(f"Generated {len(variations) + 1} content variations for user {user_id}")
            return content_set
            
        except Exception as e:
            logger.error(f"Error generating content variations: {e}")
            raise
    
    async def _generate_control_variation(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        content_brief: str
    ) -> ContentVariation:
        """Generate control variation (baseline)"""
        
        # Use industry best practices for control
        visual_prompt = self._create_industry_standard_prompt(profile.industry, objective, content_brief)
        caption = self._create_standard_caption(profile.industry, objective, profile.business_name)
        hashtags = self._get_industry_hashtags(profile.industry)
        
        return ContentVariation(
            variation_id="control",
            content_type=self._get_optimal_content_type(profile, objective),
            visual_prompt=visual_prompt,
            caption=caption,
            hashtags=hashtags,
            visual_style="industry_standard",
            color_palette=["#2563EB", "#1E40AF", "#F8FAFC", "#475569"],
            aspect_ratio=self._get_optimal_aspect_ratio(profile, objective),
            target_demographic="general",
            platform_optimized="facebook",
            objective_focus=objective.value,
            predicted_engagement=2.5,
            predicted_ctr=2.0,
            predicted_conversion=8.0,
            personalization_factors=["industry_standard"]
        )
    
    async def _generate_demographic_variation(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        content_brief: str
    ) -> ContentVariation:
        """Generate variation optimized for primary demographic"""
        
        primary_demo = profile.target_age_groups[0] if profile.target_age_groups else AgeGroup.MILLENNIAL
        demo_templates = self.content_templates.get(objective.value, {}).get(primary_demo.value, {})
        
        if not demo_templates:
            demo_templates = self.content_templates.get("lead_generation", {}).get("millennial", {})
        
        visual_prompt = self._personalize_prompt(
            random.choice(demo_templates.get("prompts", ["Professional content"])),
            profile, content_brief
        )
        
        caption = self._personalize_caption(
            random.choice(demo_templates.get("captions", ["Great content!"])),
            profile, content_brief
        )
        
        hashtags = self._get_demographic_hashtags(primary_demo, profile.industry)
        
        # Get demographic-specific performance predictions
        demo_insights = self.personalization_engine.demographic_insights.get(primary_demo.value, {})
        engagement_multiplier = demo_insights.get("engagement_multipliers", {}).get("image", 1.0)
        
        return ContentVariation(
            variation_id=f"demographic_{primary_demo.value}",
            content_type=self._get_demographic_optimal_content_type(primary_demo),
            visual_prompt=visual_prompt,
            caption=caption,
            hashtags=hashtags,
            visual_style=random.choice(demo_templates.get("styles", ["modern"])),
            color_palette=self._get_demographic_colors(primary_demo, profile.brand_voice),
            aspect_ratio=self._get_demographic_aspect_ratio(primary_demo),
            target_demographic=primary_demo.value,
            platform_optimized=self._get_demographic_preferred_platform(primary_demo),
            objective_focus=objective.value,
            predicted_engagement=2.5 * engagement_multiplier,
            predicted_ctr=2.0 * engagement_multiplier * 0.8,  # CTR typically lower multiplier
            predicted_conversion=8.0,
            personalization_factors=["demographic_targeting", primary_demo.value]
        )
    
    async def _generate_platform_variation(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        content_brief: str
    ) -> ContentVariation:
        """Generate variation optimized for primary platform"""
        
        primary_platform = profile.platform_priorities[0] if profile.platform_priorities else PlatformPriority.INSTAGRAM
        platform_chars = self.personalization_engine.platform_characteristics.get(primary_platform.value, {})
        
        # Create platform-optimized prompt
        optimal_format = platform_chars.get("optimal_formats", ["image"])[0]
        optimal_ratio = platform_chars.get("aspect_ratios", ["1:1"])[0]
        
        visual_prompt = self._create_platform_optimized_prompt(
            content_brief, primary_platform, optimal_format, profile
        )
        
        caption = self._create_platform_optimized_caption(
            content_brief, primary_platform, platform_chars, profile
        )
        
        hashtags = self._get_platform_optimized_hashtags(
            primary_platform, profile.industry, platform_chars.get("hashtag_limit", 10)
        )
        
        return ContentVariation(
            variation_id=f"platform_{primary_platform.value}",
            content_type=optimal_format,
            visual_prompt=visual_prompt,
            caption=caption,
            hashtags=hashtags,
            visual_style=f"{primary_platform.value}_native",
            color_palette=self._get_platform_colors(primary_platform, profile.brand_voice),
            aspect_ratio=optimal_ratio,
            duration=platform_chars.get("video_length_optimal") if optimal_format == "video" else None,
            target_demographic="platform_audience",
            platform_optimized=primary_platform.value,
            objective_focus=objective.value,
            predicted_engagement=3.0,  # Platform optimization typically improves engagement
            predicted_ctr=2.3,
            predicted_conversion=8.5,
            personalization_factors=["platform_optimization", primary_platform.value]
        )
    
    async def _generate_performance_variation(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        content_brief: str
    ) -> ContentVariation:
        """Generate variation based on historical performance data"""
        
        # Use learning from campaign history
        best_performing_elements = self._analyze_performance_history(profile)
        
        visual_prompt = self._create_performance_optimized_prompt(
            content_brief, best_performing_elements, profile
        )
        
        caption = self._create_performance_optimized_caption(
            content_brief, best_performing_elements, profile
        )
        
        hashtags = self._get_performance_hashtags(best_performing_elements, profile.industry)
        
        # Apply performance boost based on learning
        performance_boost = best_performing_elements.get("performance_multiplier", 1.1)
        
        return ContentVariation(
            variation_id="performance_optimized",
            content_type=best_performing_elements.get("best_content_type", "image"),
            visual_prompt=visual_prompt,
            caption=caption,
            hashtags=hashtags,
            visual_style=best_performing_elements.get("best_style", "modern_professional"),
            color_palette=best_performing_elements.get("best_colors", ["#2563EB", "#F8FAFC"]),
            aspect_ratio=best_performing_elements.get("best_ratio", "1:1"),
            target_demographic="learned_audience",
            platform_optimized="best_performing",
            objective_focus=objective.value,
            predicted_engagement=2.5 * performance_boost,
            predicted_ctr=2.0 * performance_boost,
            predicted_conversion=8.0 * performance_boost,
            personalization_factors=["performance_learning", "historical_optimization"]
        )
    
    def _analyze_performance_history(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user's campaign history to extract performance insights"""
        
        if not profile.campaign_history:
            return {"performance_multiplier": 1.0, "best_content_type": "image"}
        
        # Analyze campaign history for patterns
        high_performers = [
            campaign for campaign in profile.campaign_history 
            if campaign.get("performance", {}).get("roi", 0) > 10
        ]
        
        if not high_performers:
            return {"performance_multiplier": 1.0, "best_content_type": "image"}
        
        # Extract common elements from high performers
        content_types = [camp.get("type", "image") for camp in high_performers]
        most_common_type = max(set(content_types), key=content_types.count) if content_types else "image"
        
        avg_performance = sum(camp.get("performance", {}).get("roi", 0) for camp in high_performers) / len(high_performers)
        performance_multiplier = min(avg_performance / 10.0, 1.5)  # Cap at 1.5x boost
        
        return {
            "performance_multiplier": performance_multiplier,
            "best_content_type": most_common_type,
            "best_style": "performance_proven",
            "best_colors": ["#059669", "#F0FDF4"],  # Success colors
            "best_ratio": "1:1"
        }
    
    def _personalize_prompt(self, template: str, profile: UserProfile, content_brief: str) -> str:
        """Personalize visual prompt with user-specific details"""
        
        prompt = template.replace("[industry]", profile.industry)
        if profile.business_name:
            prompt = prompt.replace("[brand]", profile.business_name)
        
        # Add brand voice influence
        voice_modifiers = {
            BrandVoice.LUXURY: "elegant, premium, sophisticated",
            BrandVoice.CASUAL: "relaxed, friendly, approachable",
            BrandVoice.PROFESSIONAL: "clean, authoritative, trustworthy",
            BrandVoice.PLAYFUL: "vibrant, fun, energetic",
            BrandVoice.AUTHENTIC: "genuine, real, honest",
            BrandVoice.BOLD: "striking, confident, impactful"
        }
        
        voice_modifier = voice_modifiers.get(profile.brand_voice, "professional")
        prompt += f", {voice_modifier} aesthetic"
        
        # Include content brief elements
        prompt += f", incorporating: {content_brief}"
        
        return prompt
    
    def _personalize_caption(self, template: str, profile: UserProfile, content_brief: str) -> str:
        """Personalize caption with user-specific details"""
        
        caption = template.replace("[industry]", profile.industry)
        if profile.business_name:
            caption = caption.replace("[brand]", profile.business_name)
        
        # Add specific benefit or value prop from content brief
        if "benefit" in content_brief.lower():
            caption = caption.replace("[benefit]", content_brief)
        
        return caption
    
    def _get_demographic_colors(self, age_group: AgeGroup, brand_voice: BrandVoice) -> List[str]:
        """Get color palette optimized for demographic"""
        
        if age_group == AgeGroup.GEN_Z:
            return ["#8B5CF6", "#06B6D4", "#F59E0B", "#EF4444"]  # Vibrant, diverse
        elif age_group == AgeGroup.MILLENNIAL:
            return ["#059669", "#2563EB", "#F97316", "#FFFFFF"]  # Modern, aspirational
        elif age_group == AgeGroup.GEN_X:
            return ["#374151", "#059669", "#D97706", "#F9FAFB"]  # Professional, trustworthy
        else:  # BOOMER
            return ["#1F2937", "#059669", "#FFFFFF", "#6B7280"]  # Simple, high contrast
    
    def _get_platform_colors(self, platform: PlatformPriority, brand_voice: BrandVoice) -> List[str]:
        """Get color palette optimized for platform"""
        
        if platform == PlatformPriority.INSTAGRAM:
            return ["#E1306C", "#405DE6", "#FFDC80", "#FFFFFF"]  # Instagram brand colors
        elif platform == PlatformPriority.FACEBOOK:
            return ["#1877F2", "#42B883", "#FF6B35", "#FFFFFF"]  # Facebook optimized
        elif platform == PlatformPriority.TIKTOK:
            return ["#FF0050", "#00F2EA", "#000000", "#FFFFFF"]  # TikTok brand colors
        elif platform == PlatformPriority.LINKEDIN:
            return ["#0077B5", "#313335", "#00A0DC", "#FFFFFF"]  # LinkedIn professional
        else:
            return ["#2563EB", "#059669", "#F97316", "#FFFFFF"]  # Generic
    
    def _create_platform_optimized_prompt(
        self, 
        content_brief: str, 
        platform: PlatformPriority, 
        content_type: str,
        profile: UserProfile
    ) -> str:
        """Create prompt optimized for specific platform"""
        
        platform_styles = {
            PlatformPriority.INSTAGRAM: "Instagram-worthy, highly visual, aesthetic focus, perfect for stories and feed",
            PlatformPriority.FACEBOOK: "Facebook native, shareable, community-focused, news feed optimized",
            PlatformPriority.TIKTOK: "TikTok style, trendy, vertical format, hook within 3 seconds",
            PlatformPriority.LINKEDIN: "LinkedIn professional, business-appropriate, thought leadership focus",
            PlatformPriority.YOUTUBE: "YouTube thumbnail style, attention-grabbing, high contrast"
        }
        
        platform_style = platform_styles.get(platform, "social media optimized")
        
        return f"{content_brief} for {profile.industry}, {platform_style}, {profile.brand_voice.value} brand voice"
    
    def _create_platform_optimized_caption(
        self, 
        content_brief: str, 
        platform: PlatformPriority,
        platform_chars: Dict[str, Any],
        profile: UserProfile
    ) -> str:
        """Create caption optimized for platform"""
        
        max_length = platform_chars.get("max_caption_length", 2200)
        
        if platform == PlatformPriority.TIKTOK:
            # Short, punchy captions for TikTok
            return f"✨ {content_brief} in {profile.industry}! #trending #{profile.industry.replace(' ', '')}"
        elif platform == PlatformPriority.LINKEDIN:
            # Professional, longer-form content for LinkedIn
            return f"Insights on {content_brief} in the {profile.industry} industry. \n\nWhat's your experience? Share in the comments 👇"
        elif platform == PlatformPriority.INSTAGRAM:
            # Visual-focused with strategic hashtags
            return f"🌟 {content_brief} \n\n#{profile.industry.replace(' ', '')} #inspiration #growth"
        else:  # Facebook and others
            return f"{content_brief} - what do you think? Let us know in the comments! 💬"
    
    def _generate_test_hypothesis(self, profile: UserProfile, variations: List[ContentVariation]) -> str:
        """Generate A/B test hypothesis"""
        
        primary_demo = profile.target_age_groups[0].value if profile.target_age_groups else "general"
        primary_platform = profile.platform_priorities[0].value if profile.platform_priorities else "social"
        
        return (f"Testing {len(variations)} personalized variations against control for {primary_demo} "
                f"audience on {primary_platform}. Hypothesis: Personalized content will improve "
                f"engagement by 15-25% and conversion rate by 10-20% vs generic industry content.")
    
    def _calculate_traffic_split(self, num_variations: int) -> Dict[str, float]:
        """Calculate traffic split for A/B test"""
        
        # Give control 40% traffic, split rest among variations
        control_traffic = 0.4
        variation_traffic = (1.0 - control_traffic) / (num_variations - 1)
        
        split = {"control": control_traffic}
        for i in range(num_variations - 1):
            split[f"variation_{i+1}"] = variation_traffic
        
        return split
    
    def _get_primary_metric(self, objective: CampaignObjective) -> str:
        """Get primary success metric for objective"""
        
        metric_mapping = {
            CampaignObjective.LEAD_GENERATION: "conversion_rate",
            CampaignObjective.BRAND_AWARENESS: "engagement_rate", 
            CampaignObjective.SALES: "conversion_rate",
            CampaignObjective.ENGAGEMENT: "engagement_rate",
            CampaignObjective.TRAFFIC: "ctr"
        }
        
        return metric_mapping.get(objective, "engagement_rate")
    
    # Additional helper methods for content generation...
    
    def _create_industry_standard_prompt(self, industry: str, objective: CampaignObjective, brief: str) -> str:
        """Create industry-standard prompt"""
        return f"Professional {industry} content for {objective.value}, {brief}, clean modern style, industry best practices"
    
    def _create_standard_caption(self, industry: str, objective: CampaignObjective, business_name: Optional[str]) -> str:
        """Create standard industry caption"""
        business_ref = business_name if business_name else f"your {industry} needs"
        return f"Quality {industry} solution for {objective.value}. Contact us to learn more about {business_ref}!"
    
    def _get_industry_hashtags(self, industry: str) -> List[str]:
        """Get standard industry hashtags"""
        base_tags = [f"#{industry.replace(' ', '')}", "#business", "#professional", "#quality"]
        return base_tags[:5]  # Limit to 5 basic hashtags
    
    def _get_optimal_content_type(self, profile: UserProfile, objective: CampaignObjective) -> str:
        """Determine optimal content type"""
        if profile.content_preference == ContentPreference.VIDEO_FIRST:
            return "video"
        elif profile.content_preference == ContentPreference.IMAGE_HEAVY:
            return "image"
        else:
            return "image"  # Default to image for mixed preference
    
    def _get_optimal_aspect_ratio(self, profile: UserProfile, objective: CampaignObjective) -> str:
        """Get optimal aspect ratio"""
        if profile.platform_priorities and profile.platform_priorities[0] == PlatformPriority.TIKTOK:
            return "9:16"
        elif profile.platform_priorities and profile.platform_priorities[0] == PlatformPriority.FACEBOOK:
            return "16:9"
        else:
            return "1:1"  # Square for Instagram and general use
    
    def _get_demographic_optimal_content_type(self, age_group: AgeGroup) -> str:
        """Get content type preferred by demographic"""
        if age_group == AgeGroup.GEN_Z:
            return "video"
        elif age_group == AgeGroup.MILLENNIAL:
            return "image"
        else:
            return "image"
    
    def _get_demographic_aspect_ratio(self, age_group: AgeGroup) -> str:
        """Get aspect ratio preferred by demographic"""
        if age_group == AgeGroup.GEN_Z:
            return "9:16"  # Vertical for mobile-first generation
        else:
            return "1:1"   # Square for broader appeal
    
    def _get_demographic_preferred_platform(self, age_group: AgeGroup) -> str:
        """Get preferred platform for demographic"""
        demo_insights = self.personalization_engine.demographic_insights.get(age_group.value, {})
        preferred_platforms = demo_insights.get("preferred_platforms", ["instagram"])
        return preferred_platforms[0] if preferred_platforms else "instagram"
    
    def _get_demographic_hashtags(self, age_group: AgeGroup, industry: str) -> List[str]:
        """Get hashtags optimized for demographic"""
        
        base_tags = [f"#{industry.replace(' ', '')}"]
        
        if age_group == AgeGroup.GEN_Z:
            base_tags.extend(["#authentic", "#real", "#trendy", "#viral", "#fyp"])
        elif age_group == AgeGroup.MILLENNIAL:
            base_tags.extend(["#goals", "#growth", "#success", "#lifestyle", "#inspiration"])
        elif age_group == AgeGroup.GEN_X:
            base_tags.extend(["#professional", "#experience", "#quality", "#trusted", "#results"])
        else:  # BOOMER
            base_tags.extend(["#reliable", "#established", "#proven", "#trustworthy", "#quality"])
        
        return base_tags[:10]
    
    def _get_platform_optimized_hashtags(
        self, 
        platform: PlatformPriority, 
        industry: str,
        limit: int
    ) -> List[str]:
        """Get hashtags optimized for platform"""
        
        base_tags = [f"#{industry.replace(' ', '')}"]
        
        if platform == PlatformPriority.INSTAGRAM:
            base_tags.extend(["#instagood", "#photooftheday", "#business", "#entrepreneur"])
        elif platform == PlatformPriority.TIKTOK:
            base_tags.extend(["#fyp", "#trending", "#viral", "#foryou"])
        elif platform == PlatformPriority.LINKEDIN:
            base_tags.extend(["#business", "#professional", "#leadership"])
        else:  # Facebook
            base_tags.extend(["#business", "#local", "#community"])
        
        return base_tags[:limit]
    
    def _get_performance_hashtags(self, performance_elements: Dict[str, Any], industry: str) -> List[str]:
        """Get hashtags based on performance learning"""
        
        base_tags = [f"#{industry.replace(' ', '')}"]
        
        # Add performance-proven hashtags
        base_tags.extend(["#results", "#proven", "#success", "#growth", "#roi"])
        
        return base_tags[:8]
    
    def _create_performance_optimized_prompt(
        self, 
        content_brief: str,
        performance_elements: Dict[str, Any],
        profile: UserProfile
    ) -> str:
        """Create prompt based on performance learning"""
        
        best_style = performance_elements.get("best_style", "professional")
        return f"{content_brief} for {profile.industry}, {best_style} style that has proven high performance, ROI-focused messaging"
    
    def _create_performance_optimized_caption(
        self,
        content_brief: str,
        performance_elements: Dict[str, Any],
        profile: UserProfile
    ) -> str:
        """Create caption based on performance learning"""
        
        return f"🎯 Proven {profile.industry} solution: {content_brief}. Join our successful clients who've seen real results! 📈"

# Example usage
async def main():
    """Test the dynamic content generator"""
    print("🎨 Dynamic Content Generator Test")
    print("=" * 40)
    
    # Initialize engines
    personalization_engine = PersonalizationEngine()
    content_generator = DynamicContentGenerator(personalization_engine)
    
    # Create sample user profile
    sample_profile_data = {
        "business_size": "smb",
        "industry": "fitness",
        "business_name": "FitStudio Pro",
        "monthly_budget": "small",
        "primary_objective": "lead_generation",
        "target_age_groups": ["millennial"],
        "platform_priorities": ["instagram", "facebook"],
        "brand_voice": "authentic",
        "content_preference": "mixed"
    }
    
    user_id = "user_123"
    profile = await personalization_engine.create_user_profile(user_id, sample_profile_data)
    
    # Generate personalized content variations
    content_set = await content_generator.generate_personalized_content_variations(
        user_id=user_id,
        campaign_objective=CampaignObjective.LEAD_GENERATION,
        content_brief="30-day fitness transformation program for busy professionals",
        num_variations=3
    )
    
    print(f"Generated content set with {len(content_set.variations) + 1} variations:")
    print(f"Test hypothesis: {content_set.test_hypothesis}")
    
    # Display variations
    print(f"\n🎯 Control Variation:")
    control = content_set.control_variation
    print(f"   Prompt: {control.visual_prompt[:100]}...")
    print(f"   Caption: {control.caption[:100]}...")
    print(f"   Predicted CTR: {control.predicted_ctr:.2f}%")
    
    for i, variation in enumerate(content_set.variations, 1):
        print(f"\n✨ Variation {i} ({variation.variation_id}):")
        print(f"   Target: {variation.target_demographic}")
        print(f"   Platform: {variation.platform_optimized}")
        print(f"   Prompt: {variation.visual_prompt[:100]}...")
        print(f"   Caption: {variation.caption[:100]}...")
        print(f"   Predicted CTR: {variation.predicted_ctr:.2f}%")
        print(f"   Personalization: {', '.join(variation.personalization_factors)}")

if __name__ == "__main__":
    asyncio.run(main())