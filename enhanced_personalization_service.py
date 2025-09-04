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

from personalization_engine import PersonalizationEngine, UserProfile, CampaignRecommendation
from dynamic_content_generator import DynamicContentGenerator, AdaptiveContentSet
from ab_testing_framework import ABTestingFramework, PersonalizedTest
from adaptive_learning_system import AdaptiveLearningSystem, LearningInsight

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
        
        # Integration mappings
        self.campaign_type_mapping = {
            "viral": "viral_content",
            "industry_optimized": "industry_template",
            "competitor_beating": "competitive_analysis",
            "image": "image_generation", 
            "video": "video_generation"
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
        if profile.competitor_urls: completeness += 1
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
        if any(p.value == "tiktok" for p in profile.platform_priorities):
            tips.append("🎵 TikTok success requires trending sounds and quick hook within first 3 seconds")
        
        return tips[:4]  # Limit to 4 tips
    
    async def answer_campaign_question(
        self,
        user_id: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Answer specific campaign questions using personalization data
        
        This method can answer questions like:
        "What's the best campaign type for a small fitness studio with a $2000/month budget 
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
            
            # Extract budget
            budget = "small"
            if "$500" in question or "500" in question:
                budget = "micro"
            elif "$2000" in question or "2000" in question or "$2,000" in question:
                budget = "small"
            elif "$10000" in question or "10000" in question or "$10,000" in question:
                budget = "medium"
            elif "$50000" in question or "50000" in question or "$50,000" in question:
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
    question = "What's the best campaign type for a small fitness studio with a $2000/month budget targeting millennial women in urban areas for lead generation?"
    answer = await service.answer_campaign_question(user_id, question)
    
    print(f"\n❓ Question: {question}")
    print(f"✅ Answer: {answer['answer']['recommended_campaign_type']}")
    print(f"   Reasoning: {answer['answer']['reasoning'][:100]}...")
    print(f"   Expected ROI: {answer['answer']['expected_performance']['predicted_roi']}")

if __name__ == "__main__":
    asyncio.run(main())