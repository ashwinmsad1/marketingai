"""
Enhanced Personalization Service
Integrates all personalization components with the existing marketing automation system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from sqlalchemy.orm import Session

from backend.engines.personalization_engine import PersonalizationEngine, UserProfile, CampaignRecommendation
from backend.ml.content_generation.dynamic_content_generator import DynamicContentGenerator, AdaptiveContentSet
from backend.ml.ab_testing.ab_testing_framework import ABTestingFramework, PersonalizedTest
from backend.ml.learning.adaptive_learning_system import AdaptiveLearningSystem, LearningInsight
from backend.ml.learning.claude_ml_predictor import ClaudeMLPredictor
from .ml_prediction_service import MLPredictionService

logger = logging.getLogger(__name__)

class EnhancedPersonalizationService:
    """
    Comprehensive service that integrates all personalization capabilities
    with the existing marketing automation system
    """
    
    def __init__(self):
        """Initialize all personalization components"""
        self.personalization_engine = PersonalizationEngine()
        self.content_generator = DynamicContentGenerator(self.personalization_engine)
        self.ab_testing_framework = ABTestingFramework()
        self.learning_system = AdaptiveLearningSystem()
        
        # Initialize ML prediction components
        self.claude_ml_predictor = ClaudeMLPredictor()
        self.ml_prediction_service = MLPredictionService()
        
        # Enable ML integration for enhanced predictions
        self.ml_integration_enabled = True
        
        # Integration mappings
        self.campaign_type_mapping = {
            "viral": "viral_content",
            "custom": "custom_campaign",
            "image": "image_generation", 
            "video": "video_generation"
        }
        
        # Video-specific configuration
        self.video_styles = {
            "marketing commercial": "Professional marketing style with clear messaging",
            "cinematic": "High-end cinematic look with dramatic lighting",
            "luxury commercial": "Premium brand aesthetic with sophisticated appeal",
            "corporate": "Clean corporate style for B2B messaging",
            "lifestyle": "Casual lifestyle approach for consumer brands",
            "product showcase": "Product-focused demonstrations and features"
        }
        
        # Minimal industry guidance (smart defaults only)
        self.industry_style_suggestions = {
            "fitness": ["lifestyle", "marketing commercial"],
            "restaurant": ["cinematic", "lifestyle"],
            "beauty": ["luxury commercial", "lifestyle"],
            "real_estate": ["cinematic", "corporate"],
            "education": ["corporate", "lifestyle"],
            "healthcare": ["corporate", "lifestyle"],
            "retail": ["lifestyle", "product showcase"],
            "technology": ["corporate", "marketing commercial"]
        }
    
    async def create_comprehensive_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive user profile for deep personalization
        
        Args:
            user_id: User identifier
            profile_data: Complete user profile data
            db: Database session (optional)
            
        Returns:
            Created profile summary
        """
        try:
            # Create personalization profile
            profile = await self.personalization_engine.create_user_profile(user_id, profile_data)
            
            # Initialize learning profile
            await self.learning_system.analyze_campaign_performance(user_id, {
                "campaign_id": "profile_init",
                "user_preferences": profile_data,
                "roi": 0,  # Placeholder for initial learning
                "setup_complete": True
            })
            
            logger.info(f"Created comprehensive profile for user {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "profile_created": True,
                "personalization_ready": True,
                "profile_summary": {
                    "business_size": profile.business_size.value,
                    "industry": profile.industry,
                    "monthly_budget": profile.monthly_budget.value,
                    "primary_objective": profile.primary_objective.value,
                    "target_demographics": [demo.value for demo in profile.target_age_groups],
                    "platform_priorities": [p.value for p in profile.platform_priorities],
                    "brand_voice": profile.brand_voice.value,
                    "content_preference": profile.content_preference.value
                },
                "recommended_next_steps": [
                    "Create your first personalized campaign",
                    "Set up A/B testing for optimization", 
                    "Review personalized benchmarks"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating comprehensive user profile: {e}")
            raise
    
    async def get_personalized_video_strategy(
        self,
        user_id: str,
        campaign_brief: str,
        business_description: str,
        target_audience_description: str,
        unique_value_proposition: str,
        preferred_style: Optional[str] = None,
        aspect_ratios: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get personalized video campaign strategy based on user input
        
        Args:
            user_id: User identifier
            campaign_brief: Brief description of video campaign goals
            business_description: User's business description and what they do
            target_audience_description: Detailed description of target audience
            unique_value_proposition: What makes this business unique
            preferred_style: Override user's preferred video style
            aspect_ratios: Override user's preferred aspect ratios
            
        Returns:
            Video-specific campaign strategy based on user context
        """
        try:
            # Get user profile
            profile = self.personalization_engine.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Get industry style suggestions (minimal guidance)
            suggested_styles = self.industry_style_suggestions.get(profile.industry, ["marketing commercial", "lifestyle"])
            
            # Determine best video style
            if preferred_style:
                video_style = preferred_style
            elif hasattr(profile, 'preferred_video_style'):
                video_style = profile.preferred_video_style
            else:
                # Use first suggested style as default
                video_style = suggested_styles[0]
            
            # Determine aspect ratios based on platform priorities
            if aspect_ratios:
                target_ratios = aspect_ratios
            elif hasattr(profile, 'preferred_aspect_ratios'):
                target_ratios = profile.preferred_aspect_ratios
            else:
                # Default based on platform priorities
                target_ratios = []
                if any(p.value in ["instagram"] for p in profile.platform_priorities):
                    target_ratios.append("9:16")  # Vertical for mobile
                if any(p.value in ["facebook"] for p in profile.platform_priorities):
                    target_ratios.append("16:9")  # Horizontal for desktop
                if any(p.value == "instagram" for p in profile.platform_priorities):
                    target_ratios.append("1:1")   # Square for Instagram feed
                
                if not target_ratios:
                    target_ratios = ["16:9"]  # Default
            
            # Generate personalized video prompts based on user input
            video_prompts = []
            
            # Primary prompt based on user's unique value proposition
            primary_prompt = f"{video_style} style video: {unique_value_proposition}. Target audience: {target_audience_description}. Business context: {business_description}"
            video_prompts.append({
                "prompt": primary_prompt,
                "style": video_style,
                "theme": "value_proposition",
                "estimated_duration": "8 seconds (fixed by Veo 3.0)",
                "focus": "highlight unique selling point"
            })
            
            # Campaign-specific prompt
            campaign_prompt = f"{video_style} style: {campaign_brief}. Showing {business_description} for {target_audience_description}"
            video_prompts.append({
                "prompt": campaign_prompt,
                "style": video_style,
                "theme": "campaign_goal",
                "estimated_duration": "8 seconds (fixed by Veo 3.0)",
                "focus": "campaign objective"
            })
            
            # Audience-focused prompt
            audience_prompt = f"{video_style} style: {target_audience_description} discovering {unique_value_proposition}. Context: {campaign_brief}"
            video_prompts.append({
                "prompt": audience_prompt,
                "style": video_style,
                "theme": "audience_focused",
                "estimated_duration": "8 seconds (fixed by Veo 3.0)",
                "focus": "audience connection"
            })
            
            # Platform-specific optimization recommendations
            platform_optimizations = {}
            for ratio in target_ratios:
                if ratio == "9:16":
                    platform_optimizations["vertical"] = {
                        "platforms": ["Instagram Stories"],
                        "best_practices": [
                            "Hook viewers within first 3 seconds",
                            "Use text overlays for mobile viewing",
                            "Vertical composition for mobile screens"
                        ]
                    }
                elif ratio == "16:9":
                    platform_optimizations["horizontal"] = {
                        "platforms": ["Facebook Feed"],
                        "best_practices": [
                            "Clear central focus for desktop viewing",
                            "Professional presentation style",
                            "Suitable for longer-form content"
                        ]
                    }
                elif ratio == "1:1":
                    platform_optimizations["square"] = {
                        "platforms": ["Instagram Feed", "Facebook Feed"],
                        "best_practices": [
                            "Centered composition",
                            "Works well in feed layouts",
                            "Good for product showcases"
                        ]
                    }
            
            # Extract themes from user input rather than templates
            content_themes = []
            if hasattr(profile, 'video_content_themes') and profile.video_content_themes:
                content_themes = profile.video_content_themes
            else:
                # Derive themes from user input
                content_themes = ["value_proposition", "audience_focused", "campaign_goal"]
            
            return {
                "success": True,
                "user_id": user_id,
                "campaign_brief": campaign_brief,
                "video_strategy": {
                    "recommended_style": video_style,
                    "style_description": self.video_styles.get(video_style, "Professional video style"),
                    "target_aspect_ratios": target_ratios,
                    "content_themes": content_themes,
                    "industry_alignment": profile.industry
                },
                "video_prompts": video_prompts,
                "platform_optimizations": platform_optimizations,
                "technical_specifications": {
                    "duration": "8 seconds (fixed by Veo 3.0 API)",
                    "quality": "HD",
                    "format": "MP4",
                    "generation_time": "30-120 seconds per video"
                },
                "a_b_testing_recommendations": {
                    "test_variables": [
                        "Video style (cinematic vs marketing commercial)",
                        "Aspect ratio performance across platforms",
                        "Content theme effectiveness",
                        "Hook timing (first 1s vs first 3s)"
                    ],
                    "recommended_variations": len(video_prompts),
                    "minimum_budget": "₹5,000 for statistical significance"
                },
                "performance_predictions": {
                    "expected_engagement_lift": "40-60% vs static images",
                    "platform_performance": {
                        "Instagram": "High engagement for vertical videos",
                        "Facebook": "Good reach for horizontal format"
                    }
                },
                "implementation_checklist": [
                    "Review and approve video prompts",
                    "Generate videos using Veo 3.0 API",
                    "Set up A/B tests for different styles/ratios",
                    "Configure platform-specific campaigns",
                    "Monitor video completion rates",
                    "Analyze engagement patterns by format"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating video strategy: {e}")
            raise
    
    async def get_personalized_image_strategy(
        self,
        user_id: str,
        campaign_brief: str,
        business_description: str,
        target_audience_description: str,
        unique_value_proposition: str,
        preferred_style: Optional[str] = None,
        image_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized image campaign strategy based on user input
        
        Args:
            user_id: User identifier
            campaign_brief: Brief description of image campaign goals
            business_description: User's business description and what they do
            target_audience_description: Detailed description of target audience
            unique_value_proposition: What makes this business unique
            preferred_style: Override user's preferred image style
            image_format: Preferred image format/dimensions
            
        Returns:
            Image-specific campaign strategy based on user context
        """
        try:
            # Get user profile
            profile = self.personalization_engine.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Get industry style suggestions (minimal guidance)
            suggested_styles = self.industry_style_suggestions.get(profile.industry, ["professional", "modern"])
            
            # Determine best image style
            if preferred_style:
                image_style = preferred_style
            elif hasattr(profile, 'preferred_image_style'):
                image_style = profile.preferred_image_style
            else:
                # Use first suggested style as default
                image_style = suggested_styles[0]
            
            # Image format suggestions based on use case
            if not image_format:
                if "social media" in campaign_brief.lower():
                    image_format = "square (1:1) for Instagram, landscape (16:9) for Facebook"
                elif "poster" in campaign_brief.lower() or "print" in campaign_brief.lower():
                    image_format = "vertical poster format (2:3 or 3:4)"
                else:
                    image_format = "versatile landscape format (16:9)"
            
            # Generate personalized image prompts based on user input
            image_prompts = []
            
            # Primary prompt based on user's unique value proposition
            primary_prompt = f"{image_style} style image: {unique_value_proposition}. Target audience: {target_audience_description}. Business: {business_description}"
            image_prompts.append({
                "prompt": primary_prompt,
                "style": image_style,
                "theme": "value_proposition",
                "focus": "highlight unique selling point",
                "recommended_format": image_format
            })
            
            # Campaign-specific prompt
            campaign_prompt = f"{image_style} style: {campaign_brief}. Showing {business_description} for {target_audience_description}"
            image_prompts.append({
                "prompt": campaign_prompt,
                "style": image_style,
                "theme": "campaign_goal",
                "focus": "campaign objective",
                "recommended_format": image_format
            })
            
            # Audience-focused prompt
            audience_prompt = f"{image_style} style: {target_audience_description} discovering {unique_value_proposition}. Context: {campaign_brief}"
            image_prompts.append({
                "prompt": audience_prompt,
                "style": image_style,
                "theme": "audience_focused",
                "focus": "audience connection",
                "recommended_format": image_format
            })
            
            # Platform-specific optimization recommendations
            platform_optimizations = {
                "instagram": {
                    "formats": ["1:1 (Square Feed)", "4:5 (Portrait Feed)", "9:16 (Stories)"],
                    "best_practices": [
                        "High contrast for mobile viewing",
                        "Minimal text (under 20% of image)",
                        "Bright, eye-catching colors",
                        "Clear focal point"
                    ]
                },
                "facebook": {
                    "formats": ["16:9 (Landscape)", "1:1 (Square)", "4:5 (Vertical)"],
                    "best_practices": [
                        "Professional appearance for feed",
                        "Text overlays work well",
                        "Brand colors and logos prominent",
                        "Call-to-action elements"
                    ]
                },
                "print": {
                    "formats": ["A4 (2:3)", "Poster (3:4)", "Banner (5:1)"],
                    "best_practices": [
                        "High resolution (300 DPI)",
                        "Print-safe color profiles",
                        "Readable text from distance",
                        "Contact information prominent"
                    ]
                }
            }
            
            # Extract themes from user input rather than templates
            content_themes = []
            if hasattr(profile, 'image_content_themes') and profile.image_content_themes:
                content_themes = profile.image_content_themes
            else:
                # Derive themes from user input
                content_themes = ["value_proposition", "audience_focused", "campaign_goal"]
            
            return {
                "success": True,
                "user_id": user_id,
                "campaign_brief": campaign_brief,
                "image_strategy": {
                    "recommended_style": image_style,
                    "style_description": f"Professional {image_style} style optimized for {profile.industry}",
                    "recommended_format": image_format,
                    "content_themes": content_themes,
                    "industry_alignment": profile.industry
                },
                "image_prompts": image_prompts,
                "platform_optimizations": platform_optimizations,
                "technical_specifications": {
                    "resolution": "High resolution (1024x1024 or higher)",
                    "format": "PNG or JPG",
                    "color_space": "sRGB for digital, CMYK for print",
                    "generation_time": "10-30 seconds per image"
                },
                "a_b_testing_recommendations": {
                    "test_variables": [
                        "Image style (professional vs creative)",
                        "Color schemes (brand colors vs high contrast)",
                        "Composition (centered vs rule of thirds)",
                        "Text overlay (minimal vs descriptive)"
                    ],
                    "recommended_variations": len(image_prompts),
                    "minimum_budget": "₹2,000 for statistical significance"
                },
                "performance_predictions": {
                    "expected_engagement_vs_stock": "60-80% higher engagement vs stock photos",
                    "platform_performance": {
                        "Instagram": "High engagement for visually appealing content",
                        "Facebook": "Good reach with clear branding"
                    }
                },
                "implementation_checklist": [
                    "Review and approve image prompts",
                    "Generate images using AI image generator",
                    "Set up A/B tests for different styles/formats",
                    "Configure platform-specific campaigns",
                    "Monitor engagement rates by format",
                    "Analyze click-through rates by image style"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating image strategy: {e}")
            raise
    
    async def get_personalized_campaign_strategy(
        self,
        user_id: str,
        campaign_brief: str,
        objective_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete personalized campaign strategy with recommendations,
        content variations, and testing plan
        
        Args:
            user_id: User identifier
            campaign_brief: Brief description of campaign goals
            objective_override: Override user's primary objective
            
        Returns:
            Complete campaign strategy
        """
        try:
            # Get campaign recommendations
            recommendations = await self.personalization_engine.get_personalized_campaign_recommendations(
                user_id, objective_override
            )
            
            if not recommendations:
                return {"error": "No recommendations available - user profile may be incomplete"}
            
            # Get the top recommendation
            top_recommendation = recommendations[0]
            
            # Generate personalized content variations
            content_set = await self.content_generator.generate_personalized_content_variations(
                user_id=user_id,
                campaign_objective=top_recommendation.primary_objective if hasattr(top_recommendation, 'primary_objective') else objective_override,
                content_brief=campaign_brief,
                num_variations=3
            )
            
            # Create A/B test plan
            ab_test_config = {
                "test_name": f"Personalized Campaign: {campaign_brief[:50]}",
                "hypothesis": content_set.test_hypothesis,
                "primary_metric": "conversion_rate",
                "secondary_metrics": ["ctr", "engagement_rate"],
                "duration_days": 14
            }
            
            ab_test_variations = []
            
            # Convert content variations to A/B test format
            for i, variation in enumerate([content_set.control_variation] + content_set.variations):
                ab_test_variations.append({
                    "variation_id": variation.variation_id,
                    "name": f"Variation {i+1}" if i > 0 else "Control",
                    "description": f"Optimized for {variation.target_demographic}",
                    "traffic_percentage": 100.0 / (len(content_set.variations) + 1),
                    "content_config": {
                        "visual_prompt": variation.visual_prompt,
                        "caption": variation.caption,
                        "hashtags": variation.hashtags,
                        "visual_style": variation.visual_style,
                        "content_type": variation.content_type
                    }
                })
            
            # Get personalized benchmarks
            benchmarks = await self.personalization_engine.get_personalized_benchmarks(user_id)
            
            # Get predictive insights if available
            predictive_insights = await self.learning_system.get_predictive_insights(
                user_id, {
                    "content_type": top_recommendation.content_type,
                    "objective": objective_override or "lead_generation",
                    "budget": top_recommendation.recommended_budget
                }
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "campaign_brief": campaign_brief,
                "strategy_overview": {
                    "recommended_campaign_type": top_recommendation.recommended_type,
                    "campaign_name": top_recommendation.campaign_name,
                    "reasoning": top_recommendation.reasoning,
                    "confidence_score": top_recommendation.confidence_score,
                    "predicted_roi": top_recommendation.predicted_roi,
                    "recommended_budget": top_recommendation.recommended_budget
                },
                "content_strategy": {
                    "primary_content_type": content_set.control_variation.content_type,
                    "visual_style": content_set.control_variation.visual_style,
                    "target_platforms": [var.platform_optimized for var in content_set.variations],
                    "content_variations_count": len(content_set.variations) + 1
                },
                "targeting_strategy": {
                    "primary_demographics": top_recommendation.target_audience,
                    "platform_allocation": top_recommendation.platform_allocation,
                    "personalization_factors": content_set.variations[0].personalization_factors if content_set.variations else []
                },
                "testing_plan": {
                    "test_config": ab_test_config,
                    "variations": ab_test_variations,
                    "expected_duration": "14 days",
                    "sample_size_required": "1000+ conversions for significance"
                },
                "performance_expectations": {
                    "predicted_metrics": {
                        "ctr": f"{top_recommendation.predicted_ctr:.2f}%",
                        "conversion_rate": f"{top_recommendation.predicted_conversion_rate:.2f}%",
                        "engagement_rate": f"{top_recommendation.predicted_engagement_rate:.2f}%",
                        "roi": f"{top_recommendation.predicted_roi:.1f}%"
                    },
                    "benchmarks": benchmarks.get("benchmarks", {}),
                    "confidence_intervals": {
                        metric: benchmarks.get("benchmarks", {}).get(f"{metric}_range", {})
                        for metric in ["avg_ctr", "avg_engagement", "avg_conversion"]
                    }
                },
                "predictive_insights": predictive_insights,
                "implementation_checklist": [
                    "Review and approve campaign strategy",
                    "Generate content assets using provided prompts",
                    "Set up A/B testing framework",
                    "Configure targeting and budget allocation",
                    "Launch campaign with performance monitoring",
                    "Analyze results and apply learnings"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized campaign strategy: {e}")
            raise
    
    async def launch_personalized_campaign(
        self,
        user_id: str,
        campaign_strategy: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Launch a personalized campaign with integrated A/B testing
        
        Args:
            user_id: User identifier
            campaign_strategy: Strategy from get_personalized_campaign_strategy
            db: Database session
            
        Returns:
            Campaign launch results
        """
        try:
            # Create A/B test
            test_config = campaign_strategy["testing_plan"]["test_config"]
            test_variations = campaign_strategy["testing_plan"]["variations"]
            
            ab_test = await self.ab_testing_framework.create_personalized_ab_test(
                user_id=user_id,
                test_config=test_config,
                variations=test_variations
            )
            
            # Start the test
            ab_test.status = ab_test.status.__class__.ACTIVE
            
            # Generate content for each variation
            generated_content = {}
            for variation in test_variations:
                content_config = variation["content_config"]
                
                # Here you would integrate with the existing content generation system
                # For now, we'll simulate the content generation
                generated_content[variation["variation_id"]] = {
                    "content_generated": True,
                    "visual_prompt": content_config["visual_prompt"],
                    "caption": content_config["caption"],
                    "content_type": content_config["content_type"],
                    "estimated_generation_time": "30-60 seconds"
                }
            
            # Record campaign launch for learning
            campaign_launch_data = {
                "campaign_id": ab_test.test_id,
                "user_id": user_id,
                "campaign_type": campaign_strategy["strategy_overview"]["recommended_campaign_type"],
                "content_type": campaign_strategy["content_strategy"]["primary_content_type"],
                "objective": test_config.get("primary_metric", "conversion_rate"),
                "budget": campaign_strategy["strategy_overview"]["recommended_budget"],
                "platforms": campaign_strategy["content_strategy"]["target_platforms"],
                "target_demographics": list(campaign_strategy["targeting_strategy"]["primary_demographics"].keys()),
                "launch_timestamp": datetime.now().isoformat(),
                "ab_test_active": True
            }
            
            await self.learning_system.analyze_campaign_performance(user_id, campaign_launch_data)
            
            logger.info(f"Launched personalized campaign for user {user_id} with A/B test {ab_test.test_id}")
            
            return {
                "success": True,
                "campaign_launched": True,
                "ab_test_id": ab_test.test_id,
                "variations_created": len(test_variations),
                "content_generation": generated_content,
                "monitoring_setup": {
                    "test_duration": f"{test_config['duration_days']} days",
                    "metrics_tracked": [test_config["primary_metric"]] + test_config.get("secondary_metrics", []),
                    "auto_optimization": True
                },
                "next_steps": [
                    "Monitor campaign performance in real-time",
                    "Review A/B test results after sufficient data",
                    "Apply winning variation to scale campaign",
                    "Analyze learnings for future campaigns"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error launching personalized campaign: {e}")
            raise
    
    async def get_personalized_dashboard(
        self,
        user_id: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get personalized dashboard with insights, recommendations, and performance
        
        Args:
            user_id: User identifier
            db: Database session
            
        Returns:
            Personalized dashboard data
        """
        try:
            # Get user profile
            profile = self.personalization_engine.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Get learning insights
            learning_profile = self.learning_system.user_learning_profiles.get(user_id)
            
            # Get A/B testing insights
            testing_insights = await self.ab_testing_framework.get_test_insights(user_id)
            
            # Get personalized benchmarks
            benchmarks = await self.personalization_engine.get_personalized_benchmarks(user_id)
            
            # Get campaign recommendations
            recommendations = await self.personalization_engine.get_personalized_campaign_recommendations(user_id)
            
            # Compile dashboard data
            dashboard = {
                "user_profile": {
                    "business_name": profile.business_name or f"{profile.industry.title()} Business",
                    "industry": profile.industry,
                    "business_size": profile.business_size.value,
                    "monthly_budget": profile.monthly_budget.value,
                    "primary_objective": profile.primary_objective.value,
                    "profile_completeness": self._calculate_profile_completeness(profile)
                },
                "personalization_status": {
                    "learning_confidence": learning_profile.learning_confidence if learning_profile else 0.0,
                    "campaigns_analyzed": learning_profile.total_campaigns_analyzed if learning_profile else 0,
                    "insights_available": len(learning_profile.performance_insights + learning_profile.audience_insights + learning_profile.content_insights) if learning_profile else 0,
                    "personalization_maturity": self._calculate_personalization_maturity(profile, learning_profile)
                },
                "performance_benchmarks": {
                    "industry": profile.industry,
                    "personalized_benchmarks": benchmarks.get("benchmarks", {}),
                    "confidence_ranges": {
                        metric: benchmarks.get("benchmarks", {}).get(f"{metric}_range", {})
                        for metric in ["avg_ctr", "avg_engagement", "avg_conversion"]
                    }
                },
                "top_recommendations": [
                    {
                        "campaign_name": rec.campaign_name,
                        "type": rec.recommended_type,
                        "confidence": rec.confidence_score,
                        "predicted_roi": rec.predicted_roi,
                        "reasoning": rec.reasoning[:100] + "..." if len(rec.reasoning) > 100 else rec.reasoning
                    }
                    for rec in recommendations[:3]
                ],
                "testing_overview": {
                    "total_tests": testing_insights.get("testing_summary", {}).get("total_tests", 0),
                    "active_tests": testing_insights.get("testing_summary", {}).get("active_tests", 0),
                    "win_rate": testing_insights.get("testing_summary", {}).get("win_rate", 0),
                    "average_lift": testing_insights.get("testing_summary", {}).get("average_lift", 0)
                },
                "learning_insights": self._format_learning_insights(learning_profile) if learning_profile else [],
                "optimization_opportunities": self._identify_optimization_opportunities(profile, learning_profile),
                "personalized_tips": self._generate_personalized_tips(profile, learning_profile)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating personalized dashboard: {e}")
            raise
    
    async def optimize_existing_campaign(
        self,
        user_id: str,
        campaign_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize existing campaign based on performance data and learnings
        
        Args:
            user_id: User identifier  
            campaign_id: Campaign to optimize
            performance_data: Current campaign performance
            
        Returns:
            Optimization recommendations and actions
        """
        try:
            # Analyze performance with learning system
            analysis = await self.learning_system.analyze_campaign_performance(user_id, {
                "campaign_id": campaign_id,
                **performance_data
            })
            
            # Get predictive insights for optimization
            current_config = {
                "content_type": performance_data.get("content_type", "image"),
                "platforms": performance_data.get("platforms", ["facebook"]),
                "objective": performance_data.get("objective", "conversion"),
                "budget": performance_data.get("budget", 1000)
            }
            
            optimization_insights = await self.learning_system.get_predictive_insights(user_id, current_config)
            
            # Generate optimization recommendations
            recommendations = []
            
            # Budget optimization
            if performance_data.get("roi", 0) > 15:
                recommendations.append({
                    "type": "budget_increase",
                    "title": "Scale High-Performing Campaign",
                    "description": "Campaign showing strong ROI - consider increasing budget by 50-100%",
                    "priority": "high",
                    "expected_impact": "25-40% revenue increase"
                })
            
            # Content optimization
            if performance_data.get("ctr", 0) < 2.0:
                recommendations.append({
                    "type": "creative_refresh",
                    "title": "Refresh Creative Assets",
                    "description": "CTR below benchmark - test new visual styles and messaging",
                    "priority": "medium", 
                    "expected_impact": "15-25% CTR improvement"
                })
            
            # Platform optimization
            if len(performance_data.get("platforms", [])) > 1:
                recommendations.append({
                    "type": "platform_reallocation",
                    "title": "Optimize Platform Allocation",
                    "description": "Analyze platform performance and reallocate budget to top performers",
                    "priority": "medium",
                    "expected_impact": "10-20% efficiency improvement"
                })
            
            # A/B test recommendations
            if not performance_data.get("ab_test_active", False):
                recommendations.append({
                    "type": "ab_test_setup",
                    "title": "Start A/B Testing",
                    "description": "Set up systematic testing to improve performance",
                    "priority": "high",
                    "expected_impact": "20-35% performance improvement over time"
                })
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "optimization_analysis": analysis,
                "predictive_insights": optimization_insights,
                "recommendations": recommendations,
                "risk_factors": optimization_insights.get("risk_factors", []),
                "implementation_priority": {
                    "immediate": [r for r in recommendations if r["priority"] == "high"],
                    "next_week": [r for r in recommendations if r["priority"] == "medium"],
                    "future": [r for r in recommendations if r["priority"] == "low"]
                },
                "expected_outcomes": {
                    "performance_lift": "15-30% improvement expected",
                    "optimization_timeline": "2-4 weeks for full impact",
                    "confidence_level": optimization_insights.get("confidence_score", 0.5)
                }
            }
            
        except Exception as e:
            logger.error(f"Error optimizing campaign: {e}")
            raise
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """Calculate how complete the user profile is"""
        
        completeness = 0.0
        total_fields = 10
        
        if profile.business_name: completeness += 1
        if profile.target_age_groups: completeness += 1
        if profile.target_locations: completeness += 1
        if profile.target_interests: completeness += 1
        if profile.platform_priorities: completeness += 1
        if profile.brand_colors: completeness += 1
        if profile.website_url: completeness += 1
        if profile.years_in_business: completeness += 1
        if profile.target_behaviors: completeness += 1
        
        return (completeness / total_fields) * 100
    
    def _calculate_personalization_maturity(self, profile: UserProfile, learning_profile = None) -> str:
        """Calculate personalization maturity level"""
        
        if not learning_profile:
            return "Getting Started"
        
        campaigns = learning_profile.total_campaigns_analyzed
        confidence = learning_profile.learning_confidence
        
        if campaigns >= 20 and confidence >= 0.8:
            return "Advanced"
        elif campaigns >= 10 and confidence >= 0.6:
            return "Intermediate"
        elif campaigns >= 5:
            return "Learning"
        else:
            return "Getting Started"
    
    def _format_learning_insights(self, learning_profile) -> List[Dict[str, Any]]:
        """Format learning insights for dashboard"""
        
        all_insights = (
            learning_profile.performance_insights +
            learning_profile.audience_insights +
            learning_profile.content_insights +
            learning_profile.platform_insights
        )
        
        # Sort by significance and take top 5
        all_insights.sort(key=lambda x: x.significance_score, reverse=True)
        
        formatted = []
        for insight in all_insights[:5]:
            formatted.append({
                "type": insight.learning_type.value,
                "title": insight.insight_title,
                "description": insight.insight_description,
                "confidence": insight.confidence_level.value,
                "impact": f"{insight.estimated_roi_lift:+.1f}% ROI impact",
                "applicable_to": insight.applicable_scenarios
            })
        
        return formatted
    
    def _identify_optimization_opportunities(self, profile: UserProfile, learning_profile = None) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        
        opportunities = []
        
        # Profile completeness opportunity
        completeness = self._calculate_profile_completeness(profile)
        if completeness < 80:
            opportunities.append({
                "type": "profile_completion",
                "title": "Complete Your Profile",
                "description": f"Profile is {completeness:.0f}% complete. Adding more details improves recommendations.",
                "priority": "medium",
                "quick_action": True
            })
        
        # Learning opportunity
        if not learning_profile or learning_profile.total_campaigns_analyzed < 10:
            opportunities.append({
                "type": "data_collection",
                "title": "Build Learning Data",
                "description": "Run more campaigns to improve personalization accuracy.",
                "priority": "high",
                "quick_action": False
            })
        
        # A/B testing opportunity
        opportunities.append({
            "type": "systematic_testing",
            "title": "Start Systematic A/B Testing",
            "description": "Implement regular testing to continuously improve performance.",
            "priority": "high",
            "quick_action": True
        })
        
        return opportunities
    
    def _generate_personalized_tips(self, profile: UserProfile, learning_profile = None) -> List[str]:
        """Generate personalized tips based on user profile"""
        
        tips = []
        
        # Industry-specific tips
        if profile.industry == "fitness":
            tips.append("💪 Fitness audiences respond well to transformation stories and before/after content")
            tips.append("📱 Video content performs 2x better than images for fitness campaigns")
        elif profile.industry == "restaurant":
            tips.append("🍽️ Food photography with steam and close-ups drives higher engagement")
            tips.append("⏰ Post during meal times (11am-1pm, 5pm-8pm) for best results")
        
        # Budget-specific tips
        if profile.monthly_budget.value in ["micro", "small"]:
            tips.append("💰 Focus on organic reach and user-generated content to maximize budget impact")
            tips.append("🎯 Use precise targeting to make every dollar count")
        
        # Demographic tips
        if any(demo.value == "gen_z" for demo in profile.target_age_groups):
            tips.append("📱 Gen Z prefers vertical video content and authentic, behind-the-scenes content")
        
        # Platform tips
        if any(p.value == "instagram" for p in profile.platform_priorities):
            tips.append("📸 Instagram success requires high-quality visuals and consistent posting")
        if any(p.value == "facebook" for p in profile.platform_priorities):
            tips.append("👥 Facebook works well for community building and longer-form content")
        
        return tips[:4]  # Limit to 4 tips
    
    async def answer_campaign_question(
        self,
        user_id: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Answer specific campaign questions using personalization data
        
        This method can answer questions like:
        "What's the best campaign type for a small fitness studio with a ₹25,000/month budget 
        targeting millennial women in urban areas for lead generation?"
        """
        try:
            # Parse question components (simplified NLP)
            question_lower = question.lower()
            
            # Extract business size
            business_size = "smb"  # default
            if "startup" in question_lower:
                business_size = "startup"
            elif "small" in question_lower or "smb" in question_lower:
                business_size = "smb"
            elif "enterprise" in question_lower or "large" in question_lower:
                business_size = "enterprise"
            
            # Extract industry
            industry = "general"
            if "fitness" in question_lower:
                industry = "fitness"
            elif "restaurant" in question_lower or "food" in question_lower:
                industry = "restaurant"
            elif "beauty" in question_lower or "salon" in question_lower:
                industry = "beauty"
            elif "real estate" in question_lower:
                industry = "real_estate"
            
            # Extract budget (Indian Rupees)
            budget = "small"
            if "₹5000" in question or "5000" in question or "₹5,000" in question:
                budget = "micro"
            elif "₹25000" in question or "25000" in question or "₹25,000" in question:
                budget = "small"
            elif "₹50000" in question or "50000" in question or "₹50,000" in question:
                budget = "medium"
            elif "₹100000" in question or "100000" in question or "₹1,00,000" in question:
                budget = "large"
            
            # Extract demographics
            demographics = []
            if "millennial" in question_lower:
                demographics.append("millennial")
            elif "gen z" in question_lower:
                demographics.append("gen_z")
            elif "gen x" in question_lower:
                demographics.append("gen_x")
            elif "boomer" in question_lower:
                demographics.append("boomer")
            
            if "women" in question_lower:
                demographics.append("female")
            if "urban" in question_lower:
                demographics.append("urban")
            
            # Extract objective
            objective = "lead_generation"
            if "lead generation" in question_lower:
                objective = "lead_generation"
            elif "brand awareness" in question_lower:
                objective = "brand_awareness"
            elif "sales" in question_lower:
                objective = "sales"
            elif "engagement" in question_lower:
                objective = "engagement"
            
            # Create temporary profile for analysis
            temp_profile_data = {
                "business_size": business_size,
                "industry": industry,
                "monthly_budget": budget,
                "primary_objective": objective,
                "target_age_groups": demographics or ["millennial"],
                "brand_voice": "professional",
                "content_preference": "mixed",
                "platform_priorities": ["facebook", "instagram"]
            }
            
            # Get personalized recommendations
            temp_user_id = f"temp_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            temp_profile = await self.personalization_engine.create_user_profile(temp_user_id, temp_profile_data)
            recommendations = await self.personalization_engine.get_personalized_campaign_recommendations(temp_user_id)
            
            if not recommendations:
                return {"error": "Unable to generate recommendations based on the question"}
            
            top_rec = recommendations[0]
            
            # Get industry benchmarks for context
            industry_benchmarks = self.personalization_engine.industry_benchmarks.get(industry, {})
            
            return {
                "success": True,
                "question": question,
                "answer": {
                    "recommended_campaign_type": top_rec.recommended_type,
                    "campaign_name": top_rec.campaign_name,
                    "reasoning": top_rec.reasoning,
                    "confidence": f"{top_rec.confidence_score:.1%}",
                    "expected_performance": {
                        "predicted_ctr": f"{top_rec.predicted_ctr:.2f}%",
                        "predicted_conversion_rate": f"{top_rec.predicted_conversion_rate:.2f}%",
                        "predicted_roi": f"{top_rec.predicted_roi:.1f}%"
                    },
                    "recommended_budget": f"${top_rec.recommended_budget:,.0f}",
                    "platform_allocation": {
                        platform: f"{percentage:.0%}"
                        for platform, percentage in top_rec.platform_allocation.items()
                    },
                    "content_strategy": {
                        "primary_content_type": top_rec.content_type,
                        "visual_style": top_rec.visual_style,
                        "sample_prompts": top_rec.content_prompts[:2]
                    },
                    "industry_context": {
                        "industry_avg_ctr": f"{industry_benchmarks.get('avg_ctr', 2.5):.2f}%",
                        "industry_avg_conversion": f"{industry_benchmarks.get('avg_conversion', 8.0):.2f}%",
                        "performance_vs_industry": "Above average" if top_rec.predicted_roi > 10 else "Average"
                    }
                },
                "additional_recommendations": [
                    {
                        "campaign_name": rec.campaign_name,
                        "type": rec.recommended_type,
                        "confidence": f"{rec.confidence_score:.1%}",
                        "predicted_roi": f"{rec.predicted_roi:.1f}%"
                    }
                    for rec in recommendations[1:3]  # Next 2 recommendations
                ],
                "next_steps": [
                    "Create user profile for ongoing personalization",
                    "Generate content using recommended prompts",
                    "Set up A/B testing for optimization",
                    "Monitor performance against benchmarks"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error answering campaign question: {e}")
            return {
                "error": "Unable to process question",
                "message": "Please try rephrasing your question or provide more specific details about your business and goals."
            }
    
    # ML Prediction Integration Methods
    
    async def get_ai_powered_campaign_predictions(
        self,
        user_id: str,
        campaign_strategy: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get AI-powered campaign predictions integrated with personalization data
        
        Combines user personalization profile with Claude ML Predictor for enhanced predictions
        """
        try:
            # Get user profile for context
            profile = await self.personalization_engine.get_user_profile(user_id)
            
            # Enhance campaign config with personalization data
            enhanced_config = self._enhance_campaign_config_with_profile(campaign_strategy, profile)
            
            # Get historical data from learning system
            historical_data = None
            try:
                learning_profile = await self.learning_system.get_user_learning_profile(user_id)
                if learning_profile:
                    historical_data = self._format_historical_data_for_prediction(learning_profile)
            except Exception as e:
                logger.warning(f"Could not get historical data for user {user_id}: {e}")
            
            # Generate AI prediction using ML prediction service
            prediction = await self.ml_prediction_service.predict_campaign_performance(
                user_id=user_id,
                campaign_config=enhanced_config,
                historical_data=historical_data,
                db=db,
                use_cache=True
            )
            
            # Enhance prediction with personalization insights
            enhanced_prediction = await self._enhance_prediction_with_personalization(
                prediction, profile, campaign_strategy
            )
            
            return {
                "success": True,
                "prediction": enhanced_prediction,
                "personalization_integration": True,
                "profile_completeness": self._calculate_profile_completeness(profile) if profile else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting AI-powered campaign predictions: {e}")
            # Fall back to personalization engine recommendations
            try:
                recommendations = await self.personalization_engine.get_personalized_campaign_recommendations(user_id)
                if recommendations:
                    fallback = self._convert_recommendation_to_prediction_format(recommendations[0])
                    return {
                        "success": True,
                        "prediction": fallback,
                        "personalization_integration": True,
                        "fallback_mode": "personalization_engine",
                        "message": "Using personalization-based predictions due to AI prediction service error"
                    }
            except Exception as fallback_error:
                logger.error(f"Fallback prediction also failed: {fallback_error}")
            
            raise
    
    async def predict_viral_content_potential(
        self,
        user_id: str,
        content_config: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Predict viral potential of content using personalization-enhanced AI analysis
        """
        try:
            # Get user profile for audience context
            profile = await self.personalization_engine.get_user_profile(user_id)
            
            # Enhance content config with audience insights
            enhanced_config = self._enhance_content_config_with_profile(content_config, profile)
            
            # Generate viral prediction
            prediction = await self.ml_prediction_service.predict_viral_potential(
                user_id=user_id,
                content_config=enhanced_config,
                db=db,
                use_cache=True
            )
            
            # Add personalization insights
            personalization_insights = await self._generate_viral_personalization_insights(
                profile, content_config
            )
            
            prediction["personalization_insights"] = personalization_insights
            
            return {
                "success": True,
                "prediction": prediction,
                "personalization_integration": True
            }
            
        except Exception as e:
            logger.error(f"Error predicting viral content potential: {e}")
            raise
    
    async def optimize_campaign_with_ai_insights(
        self,
        user_id: str,
        campaign_id: str,
        current_performance: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Optimize campaign using combined AI predictions and personalization insights
        """
        try:
            # Get current optimization recommendations from existing method
            base_optimization = await self.optimize_existing_campaign(
                user_id, campaign_id, current_performance
            )
            
            # Enhance with AI-powered predictions
            enhanced_config = {
                "campaign_id": campaign_id,
                "current_metrics": current_performance,
                "optimization_goal": "performance_improvement"
            }
            
            ai_predictions = await self.get_ai_powered_campaign_predictions(
                user_id, enhanced_config, db
            )
            
            # Combine recommendations
            combined_optimization = self._combine_optimization_recommendations(
                base_optimization, ai_predictions
            )
            
            return combined_optimization
            
        except Exception as e:
            logger.error(f"Error optimizing campaign with AI insights: {e}")
            # Fall back to base optimization
            return await self.optimize_existing_campaign(
                user_id, campaign_id, current_performance
            )
    
    def _enhance_campaign_config_with_profile(
        self,
        campaign_config: Dict[str, Any],
        profile: Optional[UserProfile]
    ) -> Dict[str, Any]:
        """Enhance campaign configuration with user profile data"""
        enhanced_config = campaign_config.copy()
        
        if profile:
            enhanced_config.update({
                "business_profile": {
                    "industry": profile.industry,
                    "business_size": profile.business_size.value if hasattr(profile.business_size, 'value') else str(profile.business_size),
                    "years_in_business": getattr(profile, 'years_in_business', None),
                    "business_name": profile.business_name
                },
                "audience_profile": {
                    "target_age_groups": [age.value if hasattr(age, 'value') else str(age) for age in (profile.target_age_groups or [])],
                    "target_locations": profile.target_locations or [],
                    "target_interests": profile.target_interests or [],
                    "target_behaviors": getattr(profile, 'target_behaviors', [])
                },
                "brand_profile": {
                    "brand_voice": profile.brand_voice.value if hasattr(profile.brand_voice, 'value') else str(profile.brand_voice),
                    "brand_colors": profile.brand_colors or [],
                    "content_preference": profile.content_preference.value if hasattr(profile.content_preference, 'value') else str(profile.content_preference)
                },
                "marketing_profile": {
                    "monthly_budget": profile.monthly_budget.value if hasattr(profile.monthly_budget, 'value') else str(profile.monthly_budget),
                    "primary_objective": profile.primary_objective.value if hasattr(profile.primary_objective, 'value') else str(profile.primary_objective),
                    "platform_priorities": [p.value if hasattr(p, 'value') else str(p) for p in (profile.platform_priorities or [])],
                    "roi_focus": getattr(profile, 'roi_focus', False)
                }
            })
        
        return enhanced_config
    
    def _enhance_content_config_with_profile(
        self,
        content_config: Dict[str, Any],
        profile: Optional[UserProfile]
    ) -> Dict[str, Any]:
        """Enhance content configuration with user profile data for viral prediction"""
        enhanced_config = content_config.copy()
        
        if profile:
            enhanced_config.update({
                "target_audience": {
                    "age_groups": [age.value if hasattr(age, 'value') else str(age) for age in (profile.target_age_groups or [])],
                    "interests": profile.target_interests or [],
                    "locations": profile.target_locations or []
                },
                "brand_context": {
                    "industry": profile.industry,
                    "brand_voice": profile.brand_voice.value if hasattr(profile.brand_voice, 'value') else str(profile.brand_voice),
                    "content_style": profile.content_preference.value if hasattr(profile.content_preference, 'value') else str(profile.content_preference)
                },
                "platform_context": {
                    "primary_platforms": [p.value if hasattr(p, 'value') else str(p) for p in (profile.platform_priorities or [])]
                }
            })
        
        return enhanced_config
    
    def _format_historical_data_for_prediction(
        self,
        learning_profile: LearningInsight
    ) -> List[Dict[str, Any]]:
        """Format learning system data for AI predictions"""
        historical_data = []
        
        # Add performance insights as historical data
        for insight in learning_profile.performance_insights[:10]:  # Last 10 insights
            historical_data.append({
                "campaign_type": insight.applicable_scenarios[0] if insight.applicable_scenarios else "general",
                "performance_metrics": {
                    "roi": insight.estimated_roi_lift,
                    "confidence": insight.confidence_level.value if hasattr(insight.confidence_level, 'value') else str(insight.confidence_level)
                },
                "insights": insight.insight_description,
                "date": insight.created_at.isoformat() if hasattr(insight, 'created_at') else None
            })
        
        return historical_data
    
    async def _enhance_prediction_with_personalization(
        self,
        prediction: Dict[str, Any],
        profile: Optional[UserProfile],
        campaign_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance AI prediction with personalization insights"""
        enhanced_prediction = prediction.copy()
        
        if profile:
            # Add personalization context
            enhanced_prediction["personalization_context"] = {
                "profile_completeness": self._calculate_profile_completeness(profile),
                "industry_benchmarks": self.personalization_engine.industry_benchmarks.get(profile.industry, {}),
                "audience_insights": {
                    "primary_demographics": [age.value if hasattr(age, 'value') else str(age) for age in (profile.target_age_groups or [])],
                    "key_interests": profile.target_interests[:3] if profile.target_interests else [],
                    "platform_preferences": [p.value if hasattr(p, 'value') else str(p) for p in (profile.platform_priorities[:2] or [])]
                }
            }
            
            # Add personalized recommendations
            enhanced_prediction["personalized_recommendations"] = await self._generate_personalized_prediction_recommendations(
                profile, prediction, campaign_strategy
            )
        
        return enhanced_prediction
    
    async def _generate_personalized_prediction_recommendations(
        self,
        profile: UserProfile,
        prediction: Dict[str, Any],
        campaign_strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on profile and prediction"""
        recommendations = []
        
        # Budget recommendations based on profile
        if hasattr(profile, 'monthly_budget') and profile.monthly_budget:
            budget_value = profile.monthly_budget.value if hasattr(profile.monthly_budget, 'value') else str(profile.monthly_budget)
            if budget_value in ["micro", "small"]:
                recommendations.append({
                    "type": "budget_optimization",
                    "title": "Maximize Limited Budget Impact",
                    "description": "Focus on high-converting audiences and organic reach amplification",
                    "priority": "high"
                })
        
        # Industry-specific recommendations
        if profile.industry:
            industry_rec = self._get_industry_specific_recommendation(profile.industry, prediction)
            if industry_rec:
                recommendations.append(industry_rec)
        
        # Platform recommendations
        if profile.platform_priorities:
            platform_rec = self._get_platform_specific_recommendation(profile.platform_priorities, prediction)
            if platform_rec:
                recommendations.append(platform_rec)
        
        return recommendations
    
    def _get_industry_specific_recommendation(
        self,
        industry: str,
        prediction: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get industry-specific recommendation based on prediction"""
        industry_recommendations = {
            "fitness": {
                "type": "content_optimization",
                "title": "Fitness Industry Best Practices",
                "description": "Use transformation stories and video content for 2x better performance",
                "priority": "medium"
            },
            "restaurant": {
                "type": "timing_optimization",
                "title": "Restaurant Marketing Timing",
                "description": "Schedule posts during meal times (11am-1pm, 5pm-8pm) for optimal engagement",
                "priority": "high"
            },
            "beauty": {
                "type": "visual_optimization",
                "title": "Beauty Industry Visuals",
                "description": "Before/after content and user-generated content drive highest conversions",
                "priority": "high"
            }
        }
        
        return industry_recommendations.get(industry)
    
    def _get_platform_specific_recommendation(
        self,
        platform_priorities: List,
        prediction: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get platform-specific recommendation"""
        if not platform_priorities:
            return None
        
        primary_platform = platform_priorities[0]
        platform_value = primary_platform.value if hasattr(primary_platform, 'value') else str(primary_platform)
        
        platform_recommendations = {
            "instagram": {
                "type": "platform_optimization",
                "title": "Instagram Content Strategy",
                "description": "Use high-quality visuals, Stories, and Reels for maximum engagement",
                "priority": "medium"
            },
            "facebook": {
                "type": "platform_optimization",
                "title": "Facebook Advertising Focus",
                "description": "Leverage detailed targeting and video content for better performance",
                "priority": "medium"
            },
        }
        
        return platform_recommendations.get(platform_value)
    
    async def _generate_viral_personalization_insights(
        self,
        profile: Optional[UserProfile],
        content_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalization insights for viral content prediction"""
        insights = {
            "audience_alignment": "medium",
            "platform_optimization": [],
            "content_recommendations": []
        }
        
        if profile:
            # Analyze audience alignment
            if profile.target_age_groups:
                primary_age = profile.target_age_groups[0]
                age_value = primary_age.value if hasattr(primary_age, 'value') else str(primary_age)
                
                if age_value == "gen_z":
                    insights["audience_alignment"] = "high"
                    insights["content_recommendations"].append("Use vertical video format and trending audio")
                elif age_value in ["millennial", "gen_x"]:
                    insights["audience_alignment"] = "medium"
                    insights["content_recommendations"].append("Focus on authentic storytelling and relatable content")
            
            # Platform optimization insights
            if profile.platform_priorities:
                for platform in profile.platform_priorities[:2]:  # Top 2 platforms
                    platform_value = platform.value if hasattr(platform, 'value') else str(platform)
                    insights["platform_optimization"].append({
                        "platform": platform_value,
                        "optimization": self._get_platform_viral_optimization(platform_value)
                    })
        
        return insights
    
    def _get_platform_viral_optimization(self, platform: str) -> str:
        """Get platform-specific viral optimization advice"""
        optimizations = {
            "instagram": "Leverage Reels, Stories polls, hashtag trends",
            "facebook": "Focus on shareability, emotional content, video format"
        }
        
        return optimizations.get(platform, "Create engaging, shareable content with clear value proposition")
    
    def _convert_recommendation_to_prediction_format(
        self,
        recommendation: CampaignRecommendation
    ) -> Dict[str, Any]:
        """Convert personalization recommendation to prediction format"""
        return {
            "prediction_id": f"rec_{recommendation.campaign_name.replace(' ', '_').lower()}",
            "prediction_type": "campaign_performance",
            "predicted_metrics": {
                "roi": recommendation.predicted_roi,
                "ctr": recommendation.predicted_ctr,
                "conversion_rate": recommendation.predicted_conversion_rate
            },
            "confidence_level": "medium",
            "confidence_score": recommendation.confidence_score,
            "prediction_reasoning": recommendation.reasoning,
            "key_factors": [
                "User profile analysis",
                "Industry benchmarks",
                "Historical patterns"
            ],
            "optimization_opportunities": [
                "Budget allocation optimization",
                "Content strategy refinement",
                "Audience targeting enhancement"
            ],
            "recommended_adjustments": {
                "budget": recommendation.recommended_budget,
                "platform_allocation": recommendation.platform_allocation,
                "content_type": recommendation.content_type
            },
            "model_version": "personalization_engine_v1.0",
            "is_fallback": True
        }
    
    def _combine_optimization_recommendations(
        self,
        base_optimization: Dict[str, Any],
        ai_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine base optimization with AI prediction insights"""
        combined = base_optimization.copy()
        
        if "prediction" in ai_predictions:
            prediction = ai_predictions["prediction"]
            
            # Add AI-specific recommendations
            ai_recommendations = []
            
            if "optimization_opportunities" in prediction:
                for opportunity in prediction["optimization_opportunities"]:
                    ai_recommendations.append({
                        "type": "ai_optimization",
                        "title": "AI-Powered Optimization",
                        "description": opportunity,
                        "priority": "high",
                        "source": "claude_ml_predictor"
                    })
            
            # Merge recommendations
            combined["recommendations"].extend(ai_recommendations)
            
            # Add AI prediction context
            combined["ai_insights"] = {
                "predicted_performance": prediction.get("predicted_metrics", {}),
                "confidence_score": prediction.get("confidence_score", 0),
                "ai_reasoning": prediction.get("prediction_reasoning", ""),
                "model_version": prediction.get("model_version", "unknown")
            }
        
        return combined
    
    async def generate_ml_enhanced_dashboard(self, user_id: str, db: Session) -> dict:
        """
        Generate a comprehensive personalized dashboard with ML predictions
        """
        try:
            # Get basic personalization data
            basic_dashboard = await self.get_personalized_campaign_insights(user_id, {})
            
            # Enhance with ML predictions if enabled
            if self.ml_integration_enabled:
                try:
                    # Get user's recent campaign performance predictions
                    performance_insights = await self.ml_prediction_service.get_prediction_insights(
                        user_id=user_id,
                        prediction_type="campaign_performance",
                        db=db
                    )
                    
                    # Get viral potential insights  
                    viral_insights = await self.ml_prediction_service.get_prediction_insights(
                        user_id=user_id,
                        prediction_type="viral_potential", 
                        db=db
                    )
                    
                    # Combine insights
                    basic_dashboard["ml_enhanced_insights"] = {
                        "performance_predictions": performance_insights.get("insights", {}),
                        "viral_opportunities": viral_insights.get("insights", {}),
                        "ml_confidence_score": (performance_insights.get("confidence", 0) + 
                                              viral_insights.get("confidence", 0)) / 2,
                        "prediction_freshness": "recent"
                    }
                    
                    # Add ML-powered recommendations
                    if performance_insights.get("recommendations"):
                        basic_dashboard.setdefault("ml_recommendations", []).extend(
                            performance_insights["recommendations"]
                        )
                        
                    if viral_insights.get("recommendations"):
                        basic_dashboard.setdefault("ml_recommendations", []).extend(
                            viral_insights["recommendations"]
                        )
                    
                except Exception as ml_error:
                    logger.warning(f"ML enhancement failed for user {user_id}: {ml_error}")
                    # Continue without ML enhancements
                    pass
            
            logger.info(f"Generated comprehensive ML-enhanced dashboard for user {user_id}")
            return basic_dashboard
            
        except Exception as e:
            logger.error(f"Error generating ML-enhanced dashboard for user {user_id}: {e}")
            # Return basic dashboard as fallback
            return await self.get_personalized_campaign_insights(user_id, {})

# Example integration with existing API
async def main():
    """Test the enhanced personalization service"""
    print("🎯 Enhanced Personalization Service Test")
    print("=" * 50)
    
    service = EnhancedPersonalizationService()
    
    # Test comprehensive user profile creation
    profile_data = {
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
        "brand_colors": ["#FF6B35", "#004E89"],
        "roi_focus": True
    }
    
    user_id = "user_123"
    
    # Create profile
    profile_result = await service.create_comprehensive_user_profile(user_id, profile_data)
    print(f"✅ Profile created: {profile_result['success']}")
    
    # Get personalized strategy
    strategy = await service.get_personalized_campaign_strategy(
        user_id, 
        "30-day fitness transformation program for busy professionals"
    )
    print(f"📋 Strategy generated: {strategy['success']}")
    print(f"   Recommended type: {strategy['strategy_overview']['recommended_campaign_type']}")
    print(f"   Confidence: {strategy['strategy_overview']['confidence_score']:.2f}")
    
    # Test campaign question answering
    question = "What's the best campaign type for a small fitness studio with a ₹25,000/month budget targeting millennial women in urban areas for lead generation?"
    answer = await service.answer_campaign_question(user_id, question)
    
    print(f"\n❓ Question: {question}")
    print(f"✅ Answer: {answer['answer']['recommended_campaign_type']}")
    print(f"   Reasoning: {answer['answer']['reasoning'][:100]}...")
    print(f"   Expected ROI: {answer['answer']['expected_performance']['predicted_roi']}")

if __name__ == "__main__":
    asyncio.run(main())