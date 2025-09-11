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
import uuid
import anthropic
import os

from engines.personalization_engine import (
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
    
    # Targeting Context
    target_demographic: str
    platform_optimized: str
    objective_focus: str
    
    # Performance Predictions
    predicted_engagement: float
    predicted_ctr: float
    predicted_conversion: float
    
    # Fields with default values (must come last)
    duration: Optional[int] = None  # For videos
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
    Claude-powered content generator for personalized marketing variations
    """
    
    def __init__(self, personalization_engine: PersonalizationEngine):
        """Initialize with personalization engine and Claude client"""
        self.personalization_engine = personalization_engine
        self.performance_learnings = {}
        
        # Initialize Claude client
        self.anthropic_client = None
        self._initialize_claude_client()
    
    def _initialize_claude_client(self):
        """Initialize Claude client for content generation"""
        try:
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Claude client initialized for content generation")
            else:
                logger.warning("ANTHROPIC_API_KEY not found - AI content generation disabled")
        except Exception as e:
            logger.error(f"Claude client initialization failed: {e}")
    
    def _get_indian_market_context(self) -> str:
        """Get Indian market context for content generation"""
        return """
        Indian Market Context:
        - Mobile-first audience (80%+ mobile usage)
        - UPI payment preference and trust factors
        - Price sensitivity and value-for-money messaging
        - Trust indicators (testimonials, social proof) are crucial
        - Regional diversity (Hindi, English mix acceptable)
        - Festival and seasonal considerations
        - Family and community influence in decision making
        - Growing middle class aspirations
        - WhatsApp and Instagram as primary social platforms
        """
    
    def _load_content_templates(self) -> Dict[str, Dict[str, Any]]:
        """Deprecated - All content generation now handled by Claude API"""
        # This method is deprecated and kept for backwards compatibility only
        # All content generation is now dynamic through Claude API calls
        return {}
    
    def _get_style_preferences(self, brand_voice: BrandVoice, platform: str) -> Dict[str, Any]:
        """Get style preferences for Claude content generation"""
        return {
            "tone": brand_voice.value,
            "platform": platform,
            "visual_style": {
                BrandVoice.PROFESSIONAL: "clean, authoritative, trustworthy, corporate",
                BrandVoice.CASUAL: "friendly, approachable, relaxed, conversational",
                BrandVoice.LUXURY: "elegant, premium, sophisticated, exclusive",
                BrandVoice.PLAYFUL: "vibrant, fun, energetic, creative",
                BrandVoice.AUTHENTIC: "genuine, honest, real, transparent",
                BrandVoice.BOLD: "striking, confident, impactful, attention-grabbing"
            }.get(brand_voice, "professional"),
            "platform_style": {
                "instagram": "Instagram-native, highly visual, story-friendly",
                "facebook": "Facebook-optimized, community-focused, shareable"
            }.get(platform, "social media optimized")
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
        """Generate Claude-powered control variation"""
        
        try:
            if self.anthropic_client:
                prompt = f"""
                As a marketing content creator for Indian businesses, create a baseline campaign variation:
                
                Business Profile:
                - Industry: {profile.industry}
                - Business Name: {profile.business_name or 'Business'}
                - Brand Voice: {profile.brand_voice.value}
                - Target Demographics: {', '.join([age.value for age in profile.target_age_groups])}
                - Primary Platform: {profile.platform_priorities[0].value if profile.platform_priorities else 'instagram'}
                
                Campaign Details:
                - Objective: {objective.value}
                - Content Brief: {content_brief}
                
                {self._get_indian_market_context()}
                
                Generate a control/baseline variation in JSON format:
                {{
                    "visual_prompt": "Detailed visual description for image generation",
                    "caption": "Engaging caption with clear CTA",
                    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
                    "visual_style": "Style description",
                    "predicted_engagement": 2.5,
                    "predicted_ctr": 2.0,
                    "predicted_conversion": 8.0
                }}
                
                Focus on:
                - Industry best practices
                - Indian market preferences
                - Clear value proposition
                - Trust-building elements
                - Mobile-optimized content
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_content = json.loads(json_match.group())
                    
                    context = {"target_demographic": "general", "platform": profile.platform_priorities[0].value if profile.platform_priorities else "instagram", "objective": objective.value}
                    
                    return ContentVariation(
                        variation_id="control",
                        content_type=self._get_optimal_content_type(profile, objective),
                        visual_prompt=claude_content.get("visual_prompt", "Professional content"),
                        caption=claude_content.get("caption", "Quality solution for your needs"),
                        hashtags=claude_content.get("hashtags") or await self._claude_generate_hashtags(profile, content_brief, context, 8),
                        visual_style=claude_content.get("visual_style", "professional"),
                        color_palette=await self._claude_generate_color_palette(profile, context),
                        aspect_ratio=self._get_optimal_aspect_ratio(profile, objective),
                        target_demographic="general",
                        platform_optimized=profile.platform_priorities[0].value if profile.platform_priorities else "instagram",
                        objective_focus=objective.value,
                        predicted_engagement=claude_content.get("predicted_engagement", 2.5),
                        predicted_ctr=claude_content.get("predicted_ctr", 2.0),
                        predicted_conversion=claude_content.get("predicted_conversion", 8.0),
                        personalization_factors=["claude_generated", "user_customized"]
                    )
        except Exception as e:
            logger.error(f"Claude control variation generation failed: {e}")
        
        # Fallback control variation
        return ContentVariation(
            variation_id="control",
            content_type=self._get_optimal_content_type(profile, objective),
            visual_prompt=f"Professional {profile.industry} content for {objective.value}, clean modern style",
            caption=f"Quality {profile.industry} solution. Contact us to learn more!",
            hashtags=[f"#{profile.industry.replace(' ', '')}", "#business", "#professional"],
            visual_style="professional",
            color_palette=["#2563EB", "#1E40AF", "#F8FAFC", "#475569"],
            aspect_ratio=self._get_optimal_aspect_ratio(profile, objective),
            target_demographic="general",
            platform_optimized="instagram",
            objective_focus=objective.value,
            predicted_engagement=2.5,
            predicted_ctr=2.0,
            predicted_conversion=8.0,
            personalization_factors=["fallback_generation"]
        )
    
    async def _generate_demographic_variation(
        self, 
        profile: UserProfile, 
        objective: CampaignObjective,
        content_brief: str
    ) -> ContentVariation:
        """Generate Claude-powered demographic variation"""
        
        primary_demo = profile.target_age_groups[0] if profile.target_age_groups else AgeGroup.MILLENNIAL
        
        try:
            if self.anthropic_client:
                prompt = f"""
                As a marketing specialist for Indian demographics, create content optimized for {primary_demo.value} audience:
                
                Business Profile:
                - Industry: {profile.industry}
                - Business Name: {profile.business_name or 'Business'}
                - Brand Voice: {profile.brand_voice.value}
                - Target Demographic: {primary_demo.value}
                - Primary Platform: {profile.platform_priorities[0].value if profile.platform_priorities else 'instagram'}
                
                Campaign Details:
                - Objective: {objective.value}
                - Content Brief: {content_brief}
                
                {primary_demo.value.title()} Characteristics in India:
                - Gen Z: Mobile-native, authenticity-focused, trend-driven, social-cause aware
                - Millennial: Career-focused, aspiration-driven, value-conscious, family-oriented
                - Gen X: Stability-seeking, quality-focused, family-first, trust-based decisions
                - Boomer: Traditional values, personal relationships, proven solutions, straightforward communication
                
                {self._get_indian_market_context()}
                
                Generate demographic-optimized content in JSON format:
                {{
                    "visual_prompt": "Visual description tailored to {primary_demo.value} preferences",
                    "caption": "Caption that resonates with {primary_demo.value} values and language",
                    "hashtags": ["demographic-relevant hashtags"],
                    "visual_style": "Style appealing to {primary_demo.value}",
                    "predicted_engagement": "float value",
                    "predicted_ctr": "float value",
                    "predicted_conversion": "float value"
                }}
                
                Focus on:
                - {primary_demo.value}-specific communication style
                - Relevant pain points and aspirations
                - Appropriate visual aesthetics
                - Platform behavior patterns
                - Cultural resonance for Indian {primary_demo.value}
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_content = json.loads(json_match.group())
                    
                    return ContentVariation(
                        variation_id=f"demographic_{primary_demo.value}",
                        content_type=self._get_demographic_optimal_content_type(primary_demo),
                        visual_prompt=claude_content.get("visual_prompt", "Demographic-optimized content"),
                        caption=claude_content.get("caption", "Content for your demographic"),
                        hashtags=claude_content.get("hashtags") or await self._claude_generate_hashtags(profile, content_brief, {"target_demographic": primary_demo.value, "platform": profile.platform_priorities[0].value if profile.platform_priorities else "instagram", "objective": objective.value}, 10),
                        visual_style=claude_content.get("visual_style", "demographic_optimized"),
                        color_palette=await self._claude_generate_color_palette(profile, {"target_demographic": primary_demo.value, "platform": profile.platform_priorities[0].value if profile.platform_priorities else "instagram", "objective": objective.value}),
                        aspect_ratio=self._get_demographic_aspect_ratio(primary_demo),
                        target_demographic=primary_demo.value,
                        platform_optimized=self._get_demographic_preferred_platform(primary_demo),
                        objective_focus=objective.value,
                        predicted_engagement=float(claude_content.get("predicted_engagement", 3.0)),
                        predicted_ctr=float(claude_content.get("predicted_ctr", 2.3)),
                        predicted_conversion=float(claude_content.get("predicted_conversion", 8.5)),
                        personalization_factors=["claude_demographic_optimization", primary_demo.value]
                    )
        except Exception as e:
            logger.error(f"Claude demographic variation generation failed: {e}")
        
        # Fallback demographic variation
        return ContentVariation(
            variation_id=f"demographic_{primary_demo.value}",
            content_type=self._get_demographic_optimal_content_type(primary_demo),
            visual_prompt=f"{primary_demo.value}-optimized {profile.industry} content",
            caption=f"Content tailored for {primary_demo.value} audience",
            hashtags=[f"#{primary_demo.value}", f"#{profile.industry.replace(' ', '')}"],
            visual_style="demographic_optimized",
            color_palette=await self._claude_generate_color_palette(profile, {"target_demographic": primary_demo.value, "platform": self._get_demographic_preferred_platform(primary_demo), "objective": objective.value}),
            aspect_ratio=self._get_demographic_aspect_ratio(primary_demo),
            target_demographic=primary_demo.value,
            platform_optimized=self._get_demographic_preferred_platform(primary_demo),
            objective_focus=objective.value,
            predicted_engagement=3.0,
            predicted_ctr=2.3,
            predicted_conversion=8.5,
            personalization_factors=["fallback_demographic"]
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
        
        context = {
            "target_demographic": "platform_audience",
            "platform": primary_platform.value,
            "objective": objective.value
        }
        
        visual_prompt = await self._claude_generate_prompt(profile, content_brief, context)
        caption = await self._claude_generate_caption(profile, content_brief, context)
        hashtags = await self._claude_generate_hashtags(profile, content_brief, context, platform_chars.get("hashtag_limit", 10))
        
        return ContentVariation(
            variation_id=f"platform_{primary_platform.value}",
            content_type=optimal_format,
            visual_prompt=visual_prompt,
            caption=caption,
            hashtags=hashtags,
            visual_style=f"{primary_platform.value}_native",
            color_palette=await self._claude_generate_color_palette(profile, context),
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
        
        context = {
            "target_demographic": "learned_audience",
            "platform": "best_performing",
            "objective": objective.value
        }
        
        visual_prompt = await self._claude_generate_prompt(profile, content_brief, context)
        caption = await self._claude_generate_caption(profile, content_brief, context)
        hashtags = await self._claude_generate_hashtags(profile, content_brief, context, 8)
        
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
    
    async def _claude_generate_prompt(self, profile: UserProfile, content_brief: str, context: Dict[str, Any]) -> str:
        """Generate visual prompt using Claude AI with Indian market context"""
        
        try:
            if not self.anthropic_client:
                return self._fallback_prompt_generation(profile, content_brief, context)
            
            prompt = f"""
            As a visual content creator specializing in Indian market campaigns, generate a detailed visual prompt for image/video generation:
            
            Business Profile:
            - Industry: {profile.industry}
            - Business Name: {profile.business_name or 'Business'}
            - Brand Voice: {profile.brand_voice.value}
            - Campaign Brief: {content_brief}
            
            Target Context:
            - Demographics: {context.get('target_demographic', 'general')}
            - Platform: {context.get('platform', 'instagram')}
            - Objective: {context.get('objective', 'engagement')}
            
            {self._get_indian_market_context()}
            
            Generate a comprehensive visual prompt that includes:
            - Visual style and aesthetic
            - Color scheme considerations
            - Composition and layout
            - Cultural elements for Indian audience
            - Brand voice alignment
            - Platform-specific optimizations
            
            Return only the visual prompt description (no JSON, no explanation):
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Claude prompt generation failed: {e}")
            return self._fallback_prompt_generation(profile, content_brief, context)
    
    def _fallback_prompt_generation(self, profile: UserProfile, content_brief: str, context: Dict[str, Any]) -> str:
        """Fallback prompt generation when Claude is unavailable"""
        voice_styles = {
            BrandVoice.LUXURY: "elegant, premium, sophisticated",
            BrandVoice.CASUAL: "relaxed, friendly, approachable", 
            BrandVoice.PROFESSIONAL: "clean, authoritative, trustworthy",
            BrandVoice.PLAYFUL: "vibrant, fun, energetic",
            BrandVoice.AUTHENTIC: "genuine, real, honest",
            BrandVoice.BOLD: "striking, confident, impactful"
        }
        
        style = voice_styles.get(profile.brand_voice, "professional")
        return f"Professional {profile.industry} content showcasing {content_brief}, {style} aesthetic, Indian market optimized, mobile-first design"
    
    async def _claude_generate_caption(self, profile: UserProfile, content_brief: str, context: Dict[str, Any]) -> str:
        """Generate caption using Claude AI with Indian market context"""
        
        try:
            if not self.anthropic_client:
                return self._fallback_caption_generation(profile, content_brief, context)
            
            prompt = f"""
            As a social media copywriter specializing in the Indian market, create an engaging caption:
            
            Business Profile:
            - Industry: {profile.industry}
            - Business Name: {profile.business_name or 'Business'}
            - Brand Voice: {profile.brand_voice.value}
            - Campaign Brief: {content_brief}
            
            Target Context:
            - Demographics: {context.get('target_demographic', 'general')}
            - Platform: {context.get('platform', 'instagram')}
            - Objective: {context.get('objective', 'engagement')}
            
            {self._get_indian_market_context()}
            
            Create a caption that:
            - Resonates with Indian audience values and culture
            - Includes appropriate emojis and formatting
            - Has a clear call-to-action
            - Builds trust and credibility
            - Matches the brand voice
            - Optimized for the target platform
            - Includes relevant pain points and solutions
            
            Return only the caption text (no JSON, no explanation):
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Claude caption generation failed: {e}")
            return self._fallback_caption_generation(profile, content_brief, context)
    
    def _fallback_caption_generation(self, profile: UserProfile, content_brief: str, context: Dict[str, Any]) -> str:
        """Fallback caption generation when Claude is unavailable"""
        business_name = profile.business_name or f"your {profile.industry} needs"
        return f"Quality {profile.industry} solution: {content_brief}. Contact us to learn more about {business_name}! 🚀 #business #{profile.industry.replace(' ', '')}"
    
    async def _claude_generate_color_palette(self, profile: UserProfile, context: Dict[str, Any]) -> List[str]:
        """Generate color palette using Claude AI with Indian market context"""
        
        try:
            if not self.anthropic_client:
                return self._fallback_color_palette(profile, context)
            
            prompt = f"""
            As a visual brand designer specializing in the Indian market, generate a color palette:
            
            Business Profile:
            - Industry: {profile.industry}
            - Brand Voice: {profile.brand_voice.value}
            
            Context:
            - Target Demographic: {context.get('target_demographic', 'general')}
            - Platform: {context.get('platform', 'instagram')}
            - Objective: {context.get('objective', 'engagement')}
            
            {self._get_indian_market_context()}
            
            Generate a 4-color palette that:
            - Resonates with Indian cultural aesthetics
            - Appeals to the target demographic
            - Optimized for the platform
            - Matches the brand voice
            - Performs well in mobile environments
            - Considers accessibility and contrast
            
            Return only 4 hex color codes separated by commas (no explanations):
            Example format: #FF5733, #33AFFF, #FFFFFF, #1E1E1E
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse colors from response
            colors_text = response.content[0].text.strip()
            colors = [color.strip() for color in colors_text.split(',')]
            
            # Validate hex colors and return
            valid_colors = []
            for color in colors[:4]:  # Limit to 4 colors
                if color.startswith('#') and len(color) == 7:
                    valid_colors.append(color)
            
            return valid_colors if len(valid_colors) == 4 else self._fallback_color_palette(profile, context)
            
        except Exception as e:
            logger.error(f"Claude color palette generation failed: {e}")
            return self._fallback_color_palette(profile, context)
    
    def _fallback_color_palette(self, profile: UserProfile, context: Dict[str, Any]) -> List[str]:
        """Fallback color palette when Claude is unavailable"""
        demographic = context.get('target_demographic', 'general')
        platform = context.get('platform', 'instagram')
        
        # Demographic-based fallback colors
        if demographic == 'gen_z':
            return ["#8B5CF6", "#06B6D4", "#F59E0B", "#EF4444"]  # Vibrant, diverse
        elif demographic == 'millennial':
            return ["#059669", "#2563EB", "#F97316", "#FFFFFF"]  # Modern, aspirational
        elif demographic == 'gen_x':
            return ["#374151", "#059669", "#D97706", "#F9FAFB"]  # Professional, trustworthy
        elif demographic == 'boomer':
            return ["#1F2937", "#059669", "#FFFFFF", "#6B7280"]  # Simple, high contrast
        
        # Platform-based fallback colors
        if platform == 'instagram':
            return ["#E1306C", "#405DE6", "#FFDC80", "#FFFFFF"]
        elif platform == 'facebook':
            return ["#1877F2", "#42B883", "#FF6B35", "#FFFFFF"]
        
        # Default colors
        return ["#2563EB", "#059669", "#F97316", "#FFFFFF"]
    
    # Platform-optimized methods removed - now using Claude generation
    
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
    
    # Industry-standard methods removed - now using Claude generation
    
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
        if profile.platform_priorities and profile.platform_priorities[0] == PlatformPriority.FACEBOOK:
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
    
    async def _claude_generate_hashtags(self, profile: UserProfile, content_brief: str, context: Dict[str, Any], limit: int = 10) -> List[str]:
        """Generate hashtags using Claude AI with Indian market context"""
        
        try:
            if not self.anthropic_client:
                return self._fallback_hashtag_generation(profile, content_brief, context, limit)
            
            prompt = f"""
            As a social media strategist specializing in the Indian market, generate relevant hashtags:
            
            Business Profile:
            - Industry: {profile.industry}
            - Business Name: {profile.business_name or 'Business'}
            - Brand Voice: {profile.brand_voice.value}
            - Campaign Brief: {content_brief}
            
            Context:
            - Target Demographic: {context.get('target_demographic', 'general')}
            - Platform: {context.get('platform', 'instagram')}
            - Objective: {context.get('objective', 'engagement')}
            
            {self._get_indian_market_context()}
            
            Generate {limit} hashtags that:
            - Are relevant to the Indian market
            - Appeal to the target demographic
            - Are platform-appropriate
            - Include industry-specific terms
            - Mix popular and niche hashtags
            - Consider trending topics in India
            - Avoid banned or problematic hashtags
            
            Return only the hashtags separated by commas (no explanations):
            Example format: #hashtag1, #hashtag2, #hashtag3
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse hashtags from response
            hashtags_text = response.content[0].text.strip()
            hashtags = [tag.strip() for tag in hashtags_text.split(',')]
            
            # Clean and validate hashtags
            valid_hashtags = []
            for tag in hashtags[:limit]:
                tag = tag.strip()
                if tag.startswith('#'):
                    # Remove spaces and special characters from hashtag
                    clean_tag = ''.join(c for c in tag if c.isalnum() or c == '#')
                    if len(clean_tag) > 1:  # Ensure hashtag has content after #
                        valid_hashtags.append(clean_tag)
            
            return valid_hashtags if valid_hashtags else self._fallback_hashtag_generation(profile, content_brief, context, limit)
            
        except Exception as e:
            logger.error(f"Claude hashtag generation failed: {e}")
            return self._fallback_hashtag_generation(profile, content_brief, context, limit)
    
    def _fallback_hashtag_generation(self, profile: UserProfile, content_brief: str, context: Dict[str, Any], limit: int) -> List[str]:
        """Fallback hashtag generation when Claude is unavailable"""
        base_tags = [f"#{profile.industry.replace(' ', '')}"]
        
        demographic = context.get('target_demographic', 'general')
        platform = context.get('platform', 'instagram')
        
        # Add demographic-specific tags
        if demographic == 'gen_z':
            base_tags.extend(["#authentic", "#real", "#trendy", "#viral", "#fyp"])
        elif demographic == 'millennial':
            base_tags.extend(["#goals", "#growth", "#success", "#lifestyle", "#inspiration"])
        elif demographic == 'gen_x':
            base_tags.extend(["#professional", "#experience", "#quality", "#trusted", "#results"])
        elif demographic == 'boomer':
            base_tags.extend(["#reliable", "#established", "#proven", "#trustworthy", "#quality"])
        
        # Add platform-specific tags
        if platform == 'instagram':
            base_tags.extend(["#instagood", "#photooftheday", "#business", "#entrepreneur"])
        else:  # Facebook and others
            base_tags.extend(["#business", "#local", "#community"])
        
        # Add Indian market specific tags
        base_tags.extend(["#india", "#indianbusiness", "#makeinindia"])
        
        return base_tags[:limit]
    
    # Performance-optimized methods removed - now using Claude generation

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