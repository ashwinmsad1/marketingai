"""
Additional pytest configuration and fixtures for Adaptive Learning System tests
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ml.learning.adaptive_learning_system import (
    AdaptiveLearningSystem,
    LearningInsight,
    UserLearningProfile,
    PredictionModel,
    LearningType,
    ConfidenceLevel
)


@pytest.fixture
def adaptive_learning_system():
    """Create a fresh AdaptiveLearningSystem for each test."""
    return AdaptiveLearningSystem()


@pytest.fixture
def sample_user_profile():
    """Create a sample user learning profile with some data."""
    profile = UserLearningProfile(user_id="test_user_123")
    profile.total_campaigns_analyzed = 15
    profile.learning_confidence = 0.75
    
    # Add sample performance insight
    performance_insight = LearningInsight(
        insight_id=str(uuid.uuid4()),
        user_id="test_user_123",
        learning_type=LearningType.PERFORMANCE_PATTERN,
        insight_title="ROI Improvement Pattern",
        insight_description="Video content shows consistent ROI improvements",
        supporting_data={
            "roi_change": 25.0,
            "best_content_type": "video",
            "sample_size": 12,
            "confidence_assessment": "high"
        },
        confidence_level=ConfidenceLevel.HIGH,
        significance_score=0.85,
        sample_size=12,
        applicable_scenarios=["video_campaigns", "lead_generation"],
        recommended_actions=[
            "Increase video content allocation",
            "A/B test different video lengths",
            "Optimize video thumbnails"
        ],
        performance_impact={"roi": 25.0, "ctr": 15.0},
        estimated_roi_lift=25.0,
        campaigns_analyzed=["camp_1", "camp_2", "camp_3"]
    )
    
    # Add sample audience insight
    audience_insight = LearningInsight(
        insight_id=str(uuid.uuid4()),
        user_id="test_user_123",
        learning_type=LearningType.AUDIENCE_RESPONSE,
        insight_title="Millennial Engagement Pattern",
        insight_description="Millennial audience shows higher engagement rates",
        supporting_data={
            "demographics": ["millennial", "urban"],
            "engagement_change": 18.5,
            "current_engagement": 5.2,
            "historical_average": 4.4
        },
        confidence_level=ConfidenceLevel.MEDIUM,
        significance_score=0.72,
        sample_size=8,
        applicable_scenarios=["millennial_targeting", "urban_campaigns"],
        recommended_actions=[
            "Focus on millennial demographics",
            "Use urban-centric messaging",
            "Test generational preferences"
        ],
        performance_impact={"engagement_rate": 18.5},
        estimated_roi_lift=12.3,
        campaigns_analyzed=["camp_4", "camp_5"]
    )
    
    profile.performance_insights.append(performance_insight)
    profile.audience_insights.append(audience_insight)
    
    return profile


@pytest.fixture
def sample_prediction_model():
    """Create a sample prediction model."""
    return PredictionModel(
        model_id="test_user_123_performance",
        model_type="performance",
        feature_weights={
            "content_type": 0.30,
            "platform": 0.25,
            "budget_level": 0.20,
            "demographics": 0.15,
            "objective": 0.10
        },
        baseline_metrics={
            "roi": 10.0,
            "ctr": 2.5,
            "conversion_rate": 5.0
        },
        accuracy_score=0.78,
        prediction_count=150,
        validation_score=0.82,
        training_sample_size=45
    )


@pytest.fixture
def comprehensive_campaign_dataset():
    """Create a comprehensive dataset of campaigns for testing."""
    return [
        {
            "campaign_id": "camp_001",
            "user_id": "test_user_123",
            "content_type": "video",
            "visual_style": "professional",
            "platforms": ["instagram", "facebook"],
            "target_demographics": ["millennial", "urban"],
            "target_interests": ["fitness", "health", "lifestyle"],
            "objective": "lead_generation",
            "budget": 5000,
            "roi": 22.5,
            "ctr": 3.8,
            "conversion_rate": 8.9,
            "engagement_rate": 6.2,
            "cost_per_click": 1.15,
            "posting_time": "7pm",
            "caption": "Transform your fitness journey with our proven 30-day program!",
            "hashtags": ["#fitness", "#transformation", "#health", "#lifestyle"],
            "industry": "fitness",
            "business_type": "service",
            "duration_days": 14
        },
        {
            "campaign_id": "camp_002",
            "user_id": "test_user_123",
            "content_type": "image",
            "visual_style": "minimalist",
            "platforms": ["instagram"],
            "target_demographics": ["gen_z", "urban"],
            "target_interests": ["technology", "gadgets"],
            "objective": "brand_awareness",
            "budget": 3000,
            "roi": 15.8,
            "ctr": 2.9,
            "conversion_rate": 6.4,
            "engagement_rate": 4.7,
            "cost_per_click": 1.45,
            "posting_time": "6pm",
            "caption": "Discover the future of tech with our latest innovation.",
            "hashtags": ["#tech", "#innovation", "#future"],
            "industry": "technology",
            "business_type": "product",
            "duration_days": 21
        },
        {
            "campaign_id": "camp_003",
            "user_id": "test_user_123",
            "content_type": "carousel",
            "visual_style": "colorful",
            "platforms": ["facebook", "instagram"],
            "target_demographics": ["millennial", "suburban"],
            "target_interests": ["fashion", "style", "shopping"],
            "objective": "conversion",
            "budget": 7500,
            "roi": 28.3,
            "ctr": 4.5,
            "conversion_rate": 11.2,
            "engagement_rate": 7.8,
            "cost_per_click": 0.95,
            "posting_time": "8pm",
            "caption": "Elevate your style with our exclusive fashion collection.",
            "hashtags": ["#fashion", "#style", "#exclusive", "#shopping"],
            "industry": "fashion",
            "business_type": "ecommerce",
            "duration_days": 10
        },
        {
            "campaign_id": "camp_004",
            "user_id": "test_user_123",
            "content_type": "video",
            "visual_style": "casual",
            "platforms": ["facebook", "instagram"],
            "target_demographics": ["gen_z"],
            "target_interests": ["entertainment", "music", "dance"],
            "objective": "engagement",
            "budget": 2000,
            "roi": 12.7,
            "ctr": 5.2,
            "conversion_rate": 4.8,
            "engagement_rate": 9.5,
            "cost_per_click": 0.75,
            "posting_time": "9pm",
            "caption": "Join the dance challenge that's taking over social media!",
            "hashtags": ["#dance", "#challenge", "#trending", "#viral"],
            "industry": "entertainment",
            "business_type": "content",
            "duration_days": 7
        },
        {
            "campaign_id": "camp_005",
            "user_id": "test_user_123",
            "content_type": "image",
            "visual_style": "professional",
            "platforms": ["facebook"],
            "target_demographics": ["professional", "urban"],
            "target_interests": ["business", "networking", "career"],
            "objective": "lead_generation",
            "budget": 4000,
            "roi": 19.6,
            "ctr": 2.1,
            "conversion_rate": 9.8,
            "engagement_rate": 3.4,
            "cost_per_click": 2.50,
            "posting_time": "10am",
            "caption": "Advance your career with our professional development course.",
            "hashtags": ["#career", "#professional", "#development", "#business"],
            "industry": "education",
            "business_type": "service",
            "duration_days": 28
        }
    ]


@pytest.fixture
def mock_claude_responses():
    """Mock responses from Claude for different insight types."""
    return {
        "performance_insight": {
            "insight_title": "Video Content ROI Advantage",
            "insight_description": "Video content demonstrates 25% higher ROI compared to static images, particularly effective for millennial audiences in urban markets",
            "key_factors": ["visual_engagement", "storytelling_format", "mobile_optimization"],
            "applicable_scenarios": ["lead_generation_campaigns", "brand_awareness", "social_commerce"],
            "recommended_actions": [
                "Allocate 60% of content budget to video production",
                "A/B test different video lengths (15s, 30s, 60s)",
                "Implement video-first creative strategy",
                "Optimize video thumbnails for higher click-through"
            ],
            "risk_factors": ["higher_production_costs", "platform_algorithm_changes"],
            "confidence_assessment": "high",
            "expected_impact": "20-30% ROI improvement"
        },
        "audience_insight": {
            "insight_title": "Millennial Urban Audience High Engagement",
            "insight_description": "Millennial urban demographics show 35% higher engagement rates, especially responsive to lifestyle and aspirational content",
            "audience_factors": ["disposable_income", "brand_consciousness", "social_media_activity"],
            "cultural_insights": ["value_authenticity", "prefer_video_content", "mobile_first_behavior"],
            "applicable_scenarios": ["lifestyle_brands", "premium_products", "subscription_services"],
            "recommended_actions": [
                "Increase targeting weight for millennial demographics",
                "Use urban lifestyle imagery and messaging",
                "Test premium positioning strategies",
                "Leverage user-generated content"
            ],
            "targeting_adjustments": ["narrow_age_range_25_35", "urban_metro_areas_only"],
            "content_recommendations": ["lifestyle_focused_creatives", "aspirational_messaging"],
            "confidence_assessment": "high",
            "expected_impact": "25-35% engagement improvement"
        },
        "content_insight": {
            "content_prioritization": ["prioritize_video_content", "secondary_carousel_format"],
            "creative_optimization": [
                "use_storytelling_narrative",
                "include_clear_value_proposition",
                "optimize_for_sound_off_viewing"
            ],
            "format_strategies": ["short_form_video_15_30s", "carousel_with_strong_first_slide"],
            "indian_content_trends": [
                "local_language_subtitles",
                "culturally_relevant_imagery",
                "festival_seasonal_tie_ins"
            ],
            "cross_format_testing": ["video_vs_carousel_ab_test", "static_vs_animated_comparison"],
            "performance_enhancement": ["mobile_first_optimization", "fast_loading_formats"],
            "resource_allocation": ["70_video_30_static_split", "invest_in_video_production_quality"]
        },
        "platform_insight": {
            "budget_reallocation": [
                "shift_60_percent_budget_to_instagram",
                "reduce_facebook_spend_by_30_percent"
            ],
            "platform_specific_tactics": [
                "leverage_instagram_stories_for_engagement",
                "use_facebook_for_retargeting_campaigns",
                "optimize_posting_times_per_platform"
            ],
            "cross_platform_strategies": [
                "unified_brand_messaging_across_platforms",
                "platform_specific_creative_adaptations"
            ],
            "cost_optimization": [
                "automated_bidding_strategies",
                "audience_overlap_elimination",
                "campaign_budget_optimization"
            ],
            "indian_market_considerations": [
                "peak_hours_7_to_9_pm_ist",
                "weekend_higher_engagement",
                "regional_language_targeting"
            ],
            "performance_monitoring": [
                "daily_cost_per_result_tracking",
                "platform_attribution_analysis"
            ],
            "priority_actions": [
                "immediate_budget_reallocation",
                "platform_performance_audit",
                "creative_format_optimization"
            ]
        }
    }


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing Claude interactions."""
    mock_client = Mock()
    
    # Mock message creation method
    async def mock_create_message(model, max_tokens, messages):
        mock_response = Mock()
        mock_response.content = [Mock()]
        
        # Return different responses based on message content
        user_content = messages[0]["content"].lower()
        
        if "performance" in user_content:
            mock_response.content[0].text = '''
            {
                "insight_title": "Performance Improvement Detected",
                "insight_description": "Campaign shows significant performance gains",
                "key_factors": ["content_optimization", "audience_targeting"],
                "applicable_scenarios": ["similar_campaigns"],
                "recommended_actions": ["Scale successful elements", "Test variations"],
                "confidence_assessment": "high",
                "expected_impact": "15-25% improvement"
            }
            '''
        elif "audience" in user_content:
            mock_response.content[0].text = '''
            {
                "insight_title": "Audience Response Pattern",
                "insight_description": "Target demographic shows strong engagement",
                "audience_factors": ["age_alignment", "interest_match"],
                "applicable_scenarios": ["demographic_targeting"],
                "recommended_actions": ["Expand similar audiences", "Refine targeting"],
                "confidence_assessment": "medium",
                "expected_impact": "10-20% engagement boost"
            }
            '''
        else:
            mock_response.content[0].text = '''
            {
                "insight_title": "General Marketing Insight",
                "insight_description": "Analysis complete",
                "recommended_actions": ["Continue monitoring", "Test new approaches"],
                "confidence_assessment": "medium"
            }
            '''
        
        return mock_response
    
    mock_client.messages.create = mock_create_message
    return mock_client


@pytest.fixture
def learning_system_with_mock_claude(mock_anthropic_client):
    """Create learning system with mocked Claude client."""
    system = AdaptiveLearningSystem()
    system.anthropic_client = mock_anthropic_client
    return system


# Test data generators
class AdaptiveLearningTestDataGenerator:
    """Utility class for generating adaptive learning test data."""
    
    @staticmethod
    def create_campaign_sequence(user_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """Create a sequence of campaigns showing learning progression."""
        campaigns = []
        base_roi = 10.0
        
        for i in range(count):
            campaign = {
                "campaign_id": f"sequence_camp_{i+1}",
                "user_id": user_id,
                "content_type": ["image", "video", "carousel"][i % 3],
                "platforms": [["instagram"], ["facebook"], ["instagram", "facebook"]][i % 3],
                "target_demographics": ["millennial", "gen_z", "gen_x"][i % 3],
                "objective": ["awareness", "consideration", "conversion"][i % 3],
                "budget": 1000 + (i * 500),
                "roi": base_roi + (i * 2.5),  # Improving performance
                "ctr": 2.0 + (i * 0.3),
                "conversion_rate": 5.0 + (i * 0.8),
                "engagement_rate": 3.5 + (i * 0.5),
                "cost_per_click": 1.50 - (i * 0.05),  # Decreasing cost
                "posting_time": f"{6 + i}pm",
                "industry": "test_industry",
                "business_type": "test_business"
            }
            campaigns.append(campaign)
        
        return campaigns
    
    @staticmethod
    def create_diverse_user_profiles(count: int = 3) -> List[UserLearningProfile]:
        """Create diverse user profiles for testing."""
        profiles = []
        
        for i in range(count):
            profile = UserLearningProfile(user_id=f"diverse_user_{i+1}")
            profile.total_campaigns_analyzed = 5 + (i * 3)
            profile.learning_confidence = 0.5 + (i * 0.15)
            
            # Add different types of insights based on user
            if i == 0:  # Performance-focused user
                profile.performance_insights = AdaptiveLearningTestDataGenerator._create_performance_insights(profile.user_id, 3)
            elif i == 1:  # Audience-focused user  
                profile.audience_insights = AdaptiveLearningTestDataGenerator._create_audience_insights(profile.user_id, 2)
                profile.content_insights = AdaptiveLearningTestDataGenerator._create_content_insights(profile.user_id, 1)
            else:  # Well-rounded user
                profile.performance_insights = AdaptiveLearningTestDataGenerator._create_performance_insights(profile.user_id, 1)
                profile.audience_insights = AdaptiveLearningTestDataGenerator._create_audience_insights(profile.user_id, 1)
                profile.content_insights = AdaptiveLearningTestDataGenerator._create_content_insights(profile.user_id, 1)
                profile.platform_insights = AdaptiveLearningTestDataGenerator._create_platform_insights(profile.user_id, 1)
            
            profiles.append(profile)
        
        return profiles
    
    @staticmethod
    def _create_performance_insights(user_id: str, count: int) -> List[LearningInsight]:
        """Create performance insights for testing."""
        insights = []
        for i in range(count):
            insight = LearningInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                learning_type=LearningType.PERFORMANCE_PATTERN,
                insight_title=f"Performance Insight {i+1}",
                insight_description=f"Performance pattern {i+1} detected",
                supporting_data={"roi_change": 10 + (i * 5)},
                confidence_level=[ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH][i % 3],
                significance_score=0.6 + (i * 0.1),
                sample_size=10 + (i * 5),
                applicable_scenarios=[f"scenario_{i+1}"],
                recommended_actions=[f"action_{i+1}"],
                performance_impact={"roi": 10 + (i * 5)},
                estimated_roi_lift=10 + (i * 5),
                campaigns_analyzed=[f"camp_{j}" for j in range(i+1, i+4)]
            )
            insights.append(insight)
        return insights
    
    @staticmethod
    def _create_audience_insights(user_id: str, count: int) -> List[LearningInsight]:
        """Create audience insights for testing.""" 
        insights = []
        demographics = ["millennial", "gen_z", "gen_x"]
        
        for i in range(count):
            insight = LearningInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                learning_type=LearningType.AUDIENCE_RESPONSE,
                insight_title=f"Audience Insight {i+1}",
                insight_description=f"Audience pattern {i+1} detected",
                supporting_data={"demographics": [demographics[i % 3]]},
                confidence_level=ConfidenceLevel.MEDIUM,
                significance_score=0.7,
                sample_size=15,
                applicable_scenarios=[f"audience_scenario_{i+1}"],
                recommended_actions=[f"audience_action_{i+1}"],
                performance_impact={"engagement_rate": 15 + (i * 3)},
                estimated_roi_lift=8 + (i * 2),
                campaigns_analyzed=[f"camp_{j}" for j in range(i+1, i+3)]
            )
            insights.append(insight)
        return insights
    
    @staticmethod
    def _create_content_insights(user_id: str, count: int) -> List[LearningInsight]:
        """Create content insights for testing."""
        insights = []
        content_types = ["video", "image", "carousel"]
        
        for i in range(count):
            insight = LearningInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                learning_type=LearningType.CONTENT_EFFECTIVENESS,
                insight_title=f"Content Insight {i+1}",
                insight_description=f"Content pattern {i+1} detected",
                supporting_data={"best_content_type": content_types[i % 3]},
                confidence_level=ConfidenceLevel.HIGH,
                significance_score=0.8,
                sample_size=20,
                applicable_scenarios=[f"content_scenario_{i+1}"],
                recommended_actions=[f"content_action_{i+1}"],
                performance_impact={"conversion_rate": 20 + (i * 4)},
                estimated_roi_lift=12 + (i * 3),
                campaigns_analyzed=[f"camp_{j}" for j in range(i+1, i+4)]
            )
            insights.append(insight)
        return insights
    
    @staticmethod 
    def _create_platform_insights(user_id: str, count: int) -> List[LearningInsight]:
        """Create platform insights for testing."""
        insights = []
        platforms = ["instagram", "facebook"]
        
        for i in range(count):
            insight = LearningInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                learning_type=LearningType.PLATFORM_OPTIMIZATION,
                insight_title=f"Platform Insight {i+1}",
                insight_description=f"Platform pattern {i+1} detected",
                supporting_data={"cheapest_platform": platforms[i % 3]},
                confidence_level=ConfidenceLevel.MEDIUM,
                significance_score=0.75,
                sample_size=12,
                applicable_scenarios=[f"platform_scenario_{i+1}"],
                recommended_actions=[f"platform_action_{i+1}"],
                performance_impact={"cost_efficiency": 18 + (i * 2)},
                estimated_roi_lift=10 + (i * 2),
                campaigns_analyzed=[f"camp_{j}" for j in range(i+1, i+3)]
            )
            insights.append(insight)
        return insights


@pytest.fixture
def adaptive_learning_data_generator():
    """Adaptive learning test data generator fixture."""
    return AdaptiveLearningTestDataGenerator()


# Performance test fixtures
@pytest.fixture(scope="session")
def performance_test_campaigns():
    """Large dataset of campaigns for performance testing."""
    campaigns = []
    content_types = ["video", "image", "carousel", "story"]
    platforms = ["instagram", "facebook"]
    demographics = ["millennial", "gen_z", "gen_x", "boomer"]
    objectives = ["awareness", "consideration", "conversion", "retention"]
    
    for i in range(1000):  # 1000 campaigns for performance testing
        campaign = {
            "campaign_id": f"perf_camp_{i+1:04d}",
            "user_id": f"perf_user_{(i % 50) + 1}",  # 50 different users
            "content_type": content_types[i % len(content_types)],
            "platforms": [platforms[i % len(platforms)]],
            "target_demographics": [demographics[i % len(demographics)]],
            "objective": objectives[i % len(objectives)],
            "budget": 1000 + (i * 10),
            "roi": 8.0 + (i * 0.02),
            "ctr": 1.5 + (i * 0.001),
            "conversion_rate": 4.0 + (i * 0.005),
            "engagement_rate": 3.0 + (i * 0.002),
            "cost_per_click": 2.0 - (i * 0.0005),
            "industry": "test_industry",
            "business_type": "test_business"
        }
        campaigns.append(campaign)
    
    return campaigns