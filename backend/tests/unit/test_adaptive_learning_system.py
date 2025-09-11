"""
Comprehensive test suite for Adaptive Learning System
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.learning.adaptive_learning_system import (
    AdaptiveLearningSystem,
    LearningInsight,
    UserLearningProfile,
    PredictionModel,
    LearningType,
    ConfidenceLevel
)


class TestLearningInsight:
    """Test suite for LearningInsight data class."""
    
    def test_learning_insight_creation(self):
        """Test basic LearningInsight creation."""
        insight = LearningInsight(
            insight_id="test_insight_1",
            user_id="user_123",
            learning_type=LearningType.PERFORMANCE_PATTERN,
            insight_title="Test Performance Pattern",
            insight_description="ROI improvement detected",
            supporting_data={"roi_change": 15.5},
            confidence_level=ConfidenceLevel.HIGH,
            significance_score=0.85,
            sample_size=120,
            applicable_scenarios=["similar_campaigns"],
            recommended_actions=["Increase budget", "Scale campaign"],
            performance_impact={"roi": 15.5},
            estimated_roi_lift=15.5,
            campaigns_analyzed=["camp_1", "camp_2", "camp_3"]
        )
        
        assert insight.insight_id == "test_insight_1"
        assert insight.user_id == "user_123"
        assert insight.learning_type == LearningType.PERFORMANCE_PATTERN
        assert insight.confidence_level == ConfidenceLevel.HIGH
        assert insight.significance_score == 0.85
        assert insight.sample_size == 120
        assert insight.estimated_roi_lift == 15.5
        assert len(insight.campaigns_analyzed) == 3
    
    def test_learning_insight_default_dates(self):
        """Test that default dates are set correctly."""
        insight = LearningInsight(
            insight_id="test_insight_2",
            user_id="user_123",
            learning_type=LearningType.AUDIENCE_RESPONSE,
            insight_title="Test Insight",
            insight_description="Test description",
            supporting_data={},
            confidence_level=ConfidenceLevel.MEDIUM,
            significance_score=0.5,
            sample_size=50,
            applicable_scenarios=[],
            recommended_actions=[],
            performance_impact={},
            estimated_roi_lift=0.0,
            campaigns_analyzed=[]
        )
        
        assert isinstance(insight.discovery_date, datetime)
        assert isinstance(insight.last_validated, datetime)
        assert insight.validation_count == 0
        assert insight.discovery_date <= datetime.now()
        assert insight.last_validated <= datetime.now()


class TestUserLearningProfile:
    """Test suite for UserLearningProfile data class."""
    
    def test_user_learning_profile_creation(self):
        """Test basic UserLearningProfile creation."""
        profile = UserLearningProfile(user_id="user_123")
        
        assert profile.user_id == "user_123"
        assert len(profile.performance_insights) == 0
        assert len(profile.audience_insights) == 0
        assert len(profile.content_insights) == 0
        assert len(profile.platform_insights) == 0
        assert len(profile.timing_insights) == 0
        assert profile.total_campaigns_analyzed == 0
        assert profile.learning_confidence == 0.0
        assert isinstance(profile.last_learning_update, datetime)
    
    def test_user_learning_profile_default_fields(self):
        """Test default field initialization."""
        profile = UserLearningProfile(user_id="test_user")
        
        assert isinstance(profile.top_performing_elements, dict)
        assert isinstance(profile.underperforming_elements, dict)
        assert isinstance(profile.performance_predictors, dict)
        assert isinstance(profile.audience_response_models, dict)
        assert profile.last_learning_update <= datetime.now()


class TestPredictionModel:
    """Test suite for PredictionModel data class."""
    
    def test_prediction_model_creation(self):
        """Test basic PredictionModel creation."""
        model = PredictionModel(
            model_id="model_123",
            model_type="performance",
            feature_weights={"content_type": 0.3, "platform": 0.2},
            baseline_metrics={"roi": 10.0},
            accuracy_score=0.75,
            prediction_count=100,
            validation_score=0.82,
            training_sample_size=50
        )
        
        assert model.model_id == "model_123"
        assert model.model_type == "performance"
        assert model.accuracy_score == 0.75
        assert model.prediction_count == 100
        assert model.training_sample_size == 50
        assert isinstance(model.last_trained, datetime)


class TestAdaptiveLearningSystem:
    """Test suite for AdaptiveLearningSystem main class."""
    
    @pytest.fixture
    def learning_system(self):
        """Create a fresh AdaptiveLearningSystem for each test."""
        return AdaptiveLearningSystem()
    
    @pytest.fixture
    def sample_campaign_data(self):
        """Sample campaign data for testing."""
        return {
            "campaign_id": "camp_123",
            "user_id": "user_123",
            "content_type": "video",
            "visual_style": "professional",
            "platforms": ["instagram", "facebook"],
            "target_demographics": ["millennial", "urban"],
            "target_interests": ["fitness", "health"],
            "objective": "lead_generation",
            "budget": 2500,
            "roi": 18.5,
            "ctr": 3.2,
            "conversion_rate": 8.7,
            "engagement_rate": 5.4,
            "cost_per_click": 1.25,
            "posting_time": "7pm",
            "caption": "Transform your fitness journey!",
            "hashtags": ["#fitness", "#transformation"],
            "industry": "fitness",
            "business_type": "service"
        }
    
    @pytest.fixture
    def historical_campaigns(self):
        """Historical campaign data for testing."""
        return [
            {
                "campaign_id": "camp_100",
                "content_type": "image",
                "platforms": ["instagram"],
                "target_demographics": ["millennial"],
                "roi": 12.0,
                "ctr": 2.8,
                "conversion_rate": 6.5,
                "engagement_rate": 4.2,
                "cost_per_click": 1.50
            },
            {
                "campaign_id": "camp_101", 
                "content_type": "video",
                "platforms": ["facebook"],
                "target_demographics": ["millennial", "urban"],
                "roi": 16.2,
                "ctr": 3.5,
                "conversion_rate": 7.8,
                "engagement_rate": 5.1,
                "cost_per_click": 1.15
            },
            {
                "campaign_id": "camp_102",
                "content_type": "carousel",
                "platforms": ["instagram", "facebook"],
                "target_demographics": ["urban"],
                "roi": 14.8,
                "ctr": 3.1,
                "conversion_rate": 7.2,
                "engagement_rate": 4.8,
                "cost_per_click": 1.35
            }
        ]
    
    def test_initialization(self, learning_system):
        """Test AdaptiveLearningSystem initialization."""
        assert isinstance(learning_system.user_learning_profiles, dict)
        assert isinstance(learning_system.prediction_models, dict)
        assert isinstance(learning_system.learning_thresholds, dict)
        assert isinstance(learning_system.feature_importance_weights, dict)
        
        # Check learning thresholds
        assert learning_system.learning_thresholds["min_campaigns_for_insight"] == 5
        assert learning_system.learning_thresholds["min_significance_score"] == 0.7
        assert learning_system.learning_thresholds["confidence_threshold"] == 0.75
        
        # Check feature weights exist
        assert "visual_style" in learning_system.feature_importance_weights
        assert "content_type" in learning_system.feature_importance_weights
        assert "age_group" in learning_system.feature_importance_weights
        assert "platform" in learning_system.feature_importance_weights
    
    def test_feature_weights_initialization(self, learning_system):
        """Test feature importance weights initialization."""
        weights = learning_system.feature_importance_weights
        
        # Content features
        assert weights["visual_style"] == 0.25
        assert weights["content_type"] == 0.20
        assert weights["caption_length"] == 0.15
        assert weights["hashtag_count"] == 0.10
        
        # Audience features
        assert weights["age_group"] == 0.30
        assert weights["interests"] == 0.25
        assert weights["demographics"] == 0.20
        assert weights["behaviors"] == 0.15
        
        # Platform features
        assert weights["platform"] == 0.35
        assert weights["posting_time"] == 0.25
        assert weights["frequency"] == 0.20
        assert weights["format"] == 0.15
    
    @patch('os.getenv')
    def test_claude_client_initialization_with_key(self, mock_getenv, learning_system):
        """Test Claude client initialization with API key."""
        mock_getenv.return_value = "test_api_key"
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            learning_system._initialize_claude_client()
            mock_anthropic.assert_called_once_with(api_key="test_api_key")
    
    @patch('os.getenv')
    def test_claude_client_initialization_without_key(self, mock_getenv, learning_system):
        """Test Claude client initialization without API key."""
        mock_getenv.return_value = None
        
        learning_system._initialize_claude_client()
        assert learning_system.anthropic_client is None
    
    def test_extract_campaign_features(self, learning_system, sample_campaign_data):
        """Test campaign feature extraction."""
        features = learning_system._extract_campaign_features(sample_campaign_data)
        
        assert features["visual_style"] == "professional"
        assert features["content_type"] == "video"
        assert features["caption_length"] == len("Transform your fitness journey!")
        assert features["hashtag_count"] == 2
        assert features["age_group"] == "millennial"  # First demographic
        assert features["platform"] == "instagram"  # First platform
        assert features["objective"] == "lead_generation"
        assert features["budget_level"] == "medium"  # 2500 is medium
    
    def test_categorize_budget(self, learning_system):
        """Test budget categorization."""
        assert learning_system._categorize_budget(500) == "low"
        assert learning_system._categorize_budget(2500) == "medium"
        assert learning_system._categorize_budget(10000) == "high"
        assert learning_system._categorize_budget(25000) == "very_high"
    
    def test_demographics_similarity(self, learning_system):
        """Test demographics similarity calculation."""
        demo1 = ["millennial", "urban", "fitness"]
        demo2 = ["millennial", "urban", "health"]
        demo3 = ["gen_z", "rural"]
        
        # 2 out of 4 unique elements = 0.5 similarity
        similarity1 = learning_system._demographics_similarity(demo1, demo2)
        assert similarity1 == 0.5
        
        # No overlap = 0.0 similarity
        similarity2 = learning_system._demographics_similarity(demo1, demo3)
        assert similarity2 == 0.0
        
        # Empty lists = 0.0 similarity
        similarity3 = learning_system._demographics_similarity([], demo1)
        assert similarity3 == 0.0
    
    def test_determine_confidence_level(self, learning_system):
        """Test confidence level determination based on sample size."""
        assert learning_system._determine_confidence_level(25) == ConfidenceLevel.LOW
        assert learning_system._determine_confidence_level(100) == ConfidenceLevel.MEDIUM
        assert learning_system._determine_confidence_level(300) == ConfidenceLevel.HIGH
    
    @pytest.mark.asyncio
    async def test_analyze_campaign_performance_new_user(self, learning_system, sample_campaign_data):
        """Test campaign performance analysis for new user."""
        user_id = "new_user_123"
        
        # Mock historical campaigns to be empty
        with patch.object(learning_system, '_get_user_historical_campaigns', return_value=[]):
            result = await learning_system.analyze_campaign_performance(user_id, sample_campaign_data)
        
        assert result["user_id"] == user_id
        assert result["campaign_id"] == "camp_123"
        assert result["insights_extracted"] == 0  # No insights with insufficient history
        assert user_id in learning_system.user_learning_profiles
        
        profile = learning_system.user_learning_profiles[user_id]
        assert profile.total_campaigns_analyzed == 1
    
    @pytest.mark.asyncio
    async def test_analyze_campaign_performance_existing_user(self, learning_system, sample_campaign_data, historical_campaigns):
        """Test campaign performance analysis for existing user with history."""
        user_id = "existing_user_123"
        
        # Pre-create user profile
        learning_system.user_learning_profiles[user_id] = UserLearningProfile(user_id=user_id)
        
        # Mock historical campaigns
        with patch.object(learning_system, '_get_user_historical_campaigns', return_value=historical_campaigns):
            # Mock Claude-powered insight generation
            with patch.object(learning_system, '_generate_performance_insight') as mock_insight:
                mock_insight.return_value = LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    learning_type=LearningType.PERFORMANCE_PATTERN,
                    insight_title="ROI Improvement Detected",
                    insight_description="Campaign ROI shows significant improvement",
                    supporting_data={"roi_change": 20.0},
                    confidence_level=ConfidenceLevel.MEDIUM,
                    significance_score=0.8,
                    sample_size=3,
                    applicable_scenarios=["similar_campaigns"],
                    recommended_actions=["Scale budget", "Replicate success"],
                    performance_impact={"roi": 20.0},
                    estimated_roi_lift=20.0,
                    campaigns_analyzed=["camp_100", "camp_101", "camp_102"]
                )
                
                result = await learning_system.analyze_campaign_performance(user_id, sample_campaign_data)
        
        assert result["user_id"] == user_id
        assert result["insights_extracted"] > 0
        assert len(result["new_insights"]) > 0
        
        profile = learning_system.user_learning_profiles[user_id]
        assert profile.total_campaigns_analyzed == 1
        assert profile.learning_confidence > 0
    
    @pytest.mark.asyncio
    async def test_performance_patterns_analysis(self, learning_system, sample_campaign_data, historical_campaigns):
        """Test performance patterns analysis method."""
        user_id = "test_user"
        
        with patch.object(learning_system, '_get_user_historical_campaigns', return_value=historical_campaigns):
            insights = await learning_system._analyze_performance_patterns(user_id, sample_campaign_data)
        
        # Should detect ROI improvement (18.5 vs historical averages)
        assert len(insights) > 0
        
        # Check if any ROI insights were generated
        roi_insights = [insight for insight in insights if "roi" in insight.performance_impact]
        assert len(roi_insights) > 0
    
    @pytest.mark.asyncio
    async def test_audience_response_analysis(self, learning_system, sample_campaign_data, historical_campaigns):
        """Test audience response analysis method."""
        user_id = "test_user"
        
        with patch.object(learning_system, '_get_user_historical_campaigns', return_value=historical_campaigns):
            insights = await learning_system._analyze_audience_response(user_id, sample_campaign_data)
        
        # Should analyze demographic performance
        assert isinstance(insights, list)
        
        if insights:
            audience_insight = insights[0]
            assert audience_insight.learning_type == LearningType.AUDIENCE_RESPONSE
            assert "demographics" in audience_insight.supporting_data
    
    @pytest.mark.asyncio 
    async def test_content_effectiveness_analysis(self, learning_system, sample_campaign_data, historical_campaigns):
        """Test content effectiveness analysis method."""
        user_id = "test_user"
        
        with patch.object(learning_system, '_get_user_historical_campaigns', return_value=historical_campaigns):
            insights = await learning_system._analyze_content_effectiveness(user_id, sample_campaign_data)
        
        assert isinstance(insights, list)
        
        if insights:
            content_insight = insights[0]
            assert content_insight.learning_type == LearningType.CONTENT_EFFECTIVENESS
            assert "performance_gap" in content_insight.supporting_data
    
    @pytest.mark.asyncio
    async def test_platform_optimization_analysis(self, learning_system, sample_campaign_data, historical_campaigns):
        """Test platform optimization analysis method."""
        user_id = "test_user"
        
        with patch.object(learning_system, '_get_user_historical_campaigns', return_value=historical_campaigns):
            insights = await learning_system._analyze_platform_optimization(user_id, sample_campaign_data)
        
        assert isinstance(insights, list)
        
        if insights:
            platform_insight = insights[0]
            assert platform_insight.learning_type == LearningType.PLATFORM_OPTIMIZATION
            assert "cost_difference" in platform_insight.supporting_data
    
    def test_calculate_learning_confidence(self, learning_system):
        """Test learning confidence calculation."""
        profile = UserLearningProfile(user_id="test_user")
        
        # No insights = 0 confidence
        confidence = learning_system._calculate_learning_confidence(profile)
        assert confidence == 0.0
        
        # Add some insights
        insight1 = LearningInsight(
            insight_id="insight_1",
            user_id="test_user",
            learning_type=LearningType.PERFORMANCE_PATTERN,
            insight_title="Test Insight",
            insight_description="Test",
            supporting_data={},
            confidence_level=ConfidenceLevel.HIGH,
            significance_score=0.9,
            sample_size=100,
            applicable_scenarios=[],
            recommended_actions=[],
            performance_impact={},
            estimated_roi_lift=0,
            campaigns_analyzed=[]
        )
        
        profile.performance_insights.append(insight1)
        profile.total_campaigns_analyzed = 10
        
        confidence = learning_system._calculate_learning_confidence(profile)
        assert confidence > 0
        assert confidence <= 1.0
    
    def test_update_learning_patterns_good_performance(self, learning_system):
        """Test learning pattern updates for good performance."""
        profile = UserLearningProfile(user_id="test_user")
        campaign_data = {
            "roi": 15.0,  # Good performance
            "content_type": "video",
            "platforms": ["instagram"]
        }
        
        learning_system._update_learning_patterns(profile, campaign_data)
        
        assert "top_content_types" in profile.top_performing_elements
        assert "top_platforms" in profile.top_performing_elements
        assert "video" in profile.top_performing_elements["top_content_types"]
        assert "instagram" in profile.top_performing_elements["top_platforms"]
    
    def test_update_learning_patterns_poor_performance(self, learning_system):
        """Test learning pattern updates for poor performance."""
        profile = UserLearningProfile(user_id="test_user")
        campaign_data = {
            "roi": 3.0,  # Poor performance
            "content_type": "image", 
            "platforms": ["facebook"]
        }
        
        learning_system._update_learning_patterns(profile, campaign_data)
        
        assert "poor_content_types" in profile.underperforming_elements
        assert "poor_platforms" in profile.underperforming_elements
        assert "image" in profile.underperforming_elements["poor_content_types"]
        assert "facebook" in profile.underperforming_elements["poor_platforms"]
    
    @pytest.mark.asyncio
    async def test_update_prediction_models(self, learning_system, sample_campaign_data):
        """Test prediction model updates."""
        user_id = "test_user"
        
        # Create user profile
        learning_system.user_learning_profiles[user_id] = UserLearningProfile(user_id=user_id)
        
        await learning_system._update_prediction_models(user_id, sample_campaign_data)
        
        model_key = f"{user_id}_performance"
        assert model_key in learning_system.prediction_models
        
        model = learning_system.prediction_models[model_key]
        assert model.model_type == "performance"
        assert model.training_sample_size == 1
        assert isinstance(model.feature_weights, dict)
    
    def test_predict_performance(self, learning_system):
        """Test performance prediction."""
        features = {
            "content_type": "video",
            "budget_level": "high",
            "platform": "instagram"
        }
        
        model = PredictionModel(
            model_id="test_model",
            model_type="performance",
            feature_weights=learning_system.feature_importance_weights.copy(),
            baseline_metrics={},
            accuracy_score=0.5,
            prediction_count=0,
            validation_score=0.0,
            training_sample_size=10
        )
        
        prediction = learning_system._predict_performance(features, model)
        
        assert prediction >= 0
        assert prediction > 5.0  # Should be above baseline
    
    def test_get_relevant_insights(self, learning_system):
        """Test getting relevant insights for campaign features."""
        profile = UserLearningProfile(user_id="test_user")
        
        # Add test insight
        insight = LearningInsight(
            insight_id="test_insight",
            user_id="test_user",
            learning_type=LearningType.CONTENT_EFFECTIVENESS,
            insight_title="Content Performance",
            insight_description="Video content performs better",
            supporting_data={
                "best_content_type": "video",
                "demographics": ["millennial"]
            },
            confidence_level=ConfidenceLevel.HIGH,
            significance_score=0.9,
            sample_size=50,
            applicable_scenarios=[],
            recommended_actions=[],
            performance_impact={"conversion_rate": 25.0},
            estimated_roi_lift=25.0,
            campaigns_analyzed=[]
        )
        
        profile.content_insights.append(insight)
        
        features = {
            "content_type": "video",
            "demographics": ["millennial", "urban"]
        }
        
        relevant_insights = learning_system._get_relevant_insights(profile, features)
        assert len(relevant_insights) == 1
        assert relevant_insights[0] == insight
    
    def test_calculate_insight_applicability(self, learning_system):
        """Test insight applicability calculation."""
        insight = LearningInsight(
            insight_id="test_insight",
            user_id="test_user",
            learning_type=LearningType.CONTENT_EFFECTIVENESS,
            insight_title="Test",
            insight_description="Test",
            supporting_data={
                "best_content_type": "video",
                "demographics": ["millennial", "urban"]
            },
            confidence_level=ConfidenceLevel.HIGH,
            significance_score=0.9,
            sample_size=50,
            applicable_scenarios=[],
            recommended_actions=[],
            performance_impact={},
            estimated_roi_lift=0,
            campaigns_analyzed=[]
        )
        
        features = {
            "content_type": "video",
            "demographics": ["millennial"]
        }
        
        applicability = learning_system._calculate_insight_applicability(insight, features)
        assert applicability > 0.5  # Should have good relevance
        assert applicability <= 1.0
    
    def test_identify_risk_factors(self, learning_system):
        """Test risk factor identification."""
        insights = [
            LearningInsight(
                insight_id="risk_insight",
                user_id="test_user",
                learning_type=LearningType.CONTENT_EFFECTIVENESS,
                insight_title="Poor Content Performance",
                insight_description="Image content underperforms",
                supporting_data={
                    "worst_content_type": "image",
                    "most_expensive_platform": "facebook"
                },
                confidence_level=ConfidenceLevel.MEDIUM,
                significance_score=0.7,
                sample_size=30,
                applicable_scenarios=[],
                recommended_actions=[],
                performance_impact={"conversion_rate": -15.0},
                estimated_roi_lift=-15.0,
                campaigns_analyzed=[]
            )
        ]
        
        features = {
            "content_type": "image",
            "platform": "facebook",
            "budget_level": "low"
        }
        
        risks = learning_system._identify_risk_factors(features, insights)
        
        assert len(risks) >= 2  # Should identify multiple risks
        assert any("image" in risk for risk in risks)
        assert any("facebook" in risk for risk in risks) 
        assert any("Low budget" in risk for risk in risks)


class TestClaudePoweredInsights:
    """Test suite for Claude-powered insight generation."""
    
    @pytest.fixture
    def learning_system_with_claude(self):
        """Create learning system with mocked Claude client."""
        system = AdaptiveLearningSystem()
        system.anthropic_client = Mock()
        return system
    
    @pytest.mark.asyncio
    async def test_generate_performance_insight_with_claude(self, learning_system_with_claude):
        """Test Claude-powered performance insight generation."""
        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "insight_title": "ROI Improvement Through Video Content",
            "insight_description": "Video content shows 25% better ROI compared to static images",
            "key_factors": ["engaging_visuals", "mobile_optimization", "storytelling"],
            "applicable_scenarios": ["lead_generation", "brand_awareness"],
            "recommended_actions": ["Increase video content allocation", "A/B test video formats"],
            "confidence_assessment": "high",
            "expected_impact": "20-30% ROI improvement"
        }
        '''
        
        # Mock asyncio.to_thread
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_response
            
            insight = await learning_system_with_claude._generate_performance_insight(
                user_id="test_user",
                performance_change=25.0,
                campaign_data={"roi": 18.5, "content_type": "video"},
                historical_campaigns=[{"roi": 12.0}],
                metric_type="roi"
            )
        
        assert insight.insight_title == "ROI Improvement Through Video Content"
        assert "25% better ROI" in insight.insight_description
        assert insight.estimated_roi_lift == 25.0
        assert len(insight.recommended_actions) >= 2
    
    @pytest.mark.asyncio
    async def test_generate_performance_insight_fallback(self, learning_system_with_claude):
        """Test fallback when Claude generation fails."""
        # Mock Claude client to raise an exception
        with patch('asyncio.to_thread', side_effect=Exception("Claude API error")):
            insight = await learning_system_with_claude._generate_performance_insight(
                user_id="test_user", 
                performance_change=20.0,
                campaign_data={"roi": 15.0},
                historical_campaigns=[],
                metric_type="roi"
            )
        
        # Should still return a basic insight
        assert insight.insight_title == "ROI Improvement Pattern"
        assert "20.0% improvement" in insight.insight_description
        assert insight.estimated_roi_lift == 20.0
    
    @pytest.mark.asyncio
    async def test_generate_content_recommendations(self, learning_system_with_claude):
        """Test Claude-powered content recommendations."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "content_prioritization": ["Focus on video content", "Reduce image allocation"],
            "creative_optimization": ["Use storytelling format", "Add captions for mobile"],
            "indian_content_trends": ["Local language integration", "Cultural celebrations"],
            "performance_enhancement": ["Optimize for mobile viewing", "Include clear CTAs"]
        }
        '''
        
        with patch('asyncio.to_thread', return_value=mock_response):
            recommendations = await learning_system_with_claude._generate_content_recommendations(
                best_content_type=("video", 15.0),
                worst_content_type=("image", 8.0),
                performance_gap=30.0,
                campaign_data={"industry": "fitness"}
            )
        
        assert len(recommendations) >= 4
        assert any("video content" in rec.lower() for rec in recommendations)
        assert any("mobile" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_generate_platform_recommendations(self, learning_system_with_claude):
        """Test Claude-powered platform recommendations."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "budget_reallocation": ["Shift 60% budget to Instagram", "Reduce Facebook spend"],
            "platform_specific_tactics": ["Use Stories for engagement", "Leverage Reels format"],
            "cost_optimization": ["Optimize bid strategies", "Test different audiences"],
            "indian_market_considerations": ["Peak hours 7-9 PM", "Weekend engagement higher"]
        }
        '''
        
        with patch('asyncio.to_thread', return_value=mock_response):
            recommendations = await learning_system_with_claude._generate_platform_recommendations(
                cheapest_platform=("instagram", 1.20),
                most_expensive_platform=("facebook", 1.80), 
                cost_difference=50.0,
                campaign_data={"industry": "ecommerce"}
            )
        
        assert len(recommendations) >= 4
        assert any("Instagram" in rec for rec in recommendations)
        assert any("optimize" in rec.lower() for rec in recommendations)


class TestPredictiveInsights:
    """Test suite for predictive insights functionality."""
    
    @pytest.fixture
    def learning_system_with_data(self):
        """Create learning system with sample data."""
        system = AdaptiveLearningSystem()
        
        # Create user profile with some insights
        profile = UserLearningProfile(user_id="test_user")
        profile.total_campaigns_analyzed = 10
        profile.learning_confidence = 0.75
        
        # Add sample insight
        insight = LearningInsight(
            insight_id="insight_1",
            user_id="test_user",
            learning_type=LearningType.CONTENT_EFFECTIVENESS,
            insight_title="Video Content Advantage",
            insight_description="Video content shows better performance",
            supporting_data={"best_content_type": "video"},
            confidence_level=ConfidenceLevel.HIGH,
            significance_score=0.85,
            sample_size=50,
            applicable_scenarios=["lead_generation"],
            recommended_actions=["Use more video content"],
            performance_impact={"conversion_rate": 20.0},
            estimated_roi_lift=20.0,
            campaigns_analyzed=["camp_1", "camp_2"]
        )
        
        profile.content_insights.append(insight)
        system.user_learning_profiles["test_user"] = profile
        
        # Create prediction model
        model = PredictionModel(
            model_id="test_user_performance",
            model_type="performance",
            feature_weights=system.feature_importance_weights.copy(),
            baseline_metrics={"roi": 10.0},
            accuracy_score=0.75,
            prediction_count=100,
            validation_score=0.8,
            training_sample_size=25
        )
        system.prediction_models["test_user_performance"] = model
        
        return system
    
    @pytest.mark.asyncio
    async def test_get_predictive_insights_with_data(self, learning_system_with_data):
        """Test predictive insights with sufficient data."""
        proposed_campaign = {
            "content_type": "video",
            "platforms": ["instagram"],
            "target_demographics": ["millennial"],
            "objective": "lead_generation",
            "budget": 3000
        }
        
        with patch.object(learning_system_with_data, '_generate_predictive_recommendations', return_value=[
            "Increase video content allocation",
            "Optimize for mobile viewing",
            "Test different video lengths"
        ]):
            result = await learning_system_with_data.get_predictive_insights("test_user", proposed_campaign)
        
        assert result["user_id"] == "test_user"
        assert "predicted_roi" in result
        assert result["predicted_roi"] > 0
        assert result["confidence_score"] > 0
        assert len(result["relevant_insights"]) > 0
        assert len(result["optimization_recommendations"]) >= 3
        assert "confidence_factors" in result
    
    @pytest.mark.asyncio
    async def test_get_predictive_insights_insufficient_data(self, learning_system_with_data):
        """Test predictive insights with insufficient data."""
        # Remove prediction model to simulate insufficient data
        learning_system_with_data.prediction_models = {}
        
        proposed_campaign = {
            "content_type": "image",
            "platforms": ["facebook"],
            "budget": 1000
        }
        
        result = await learning_system_with_data.get_predictive_insights("test_user", proposed_campaign)
        
        assert result["predicted_performance"] == "insufficient_data"
        assert result["confidence"] == "low"
        assert len(result["recommendations"]) >= 3
        assert "Run initial campaigns" in result["recommendations"][0]
    
    @pytest.mark.asyncio
    async def test_get_predictive_insights_no_user_profile(self, learning_system_with_data):
        """Test predictive insights for non-existent user."""
        proposed_campaign = {
            "content_type": "video",
            "budget": 2000
        }
        
        result = await learning_system_with_data.get_predictive_insights("unknown_user", proposed_campaign)
        
        assert "error" in result
        assert "No learning profile found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_generate_predictive_recommendations_with_claude(self, learning_system_with_data):
        """Test Claude-powered predictive recommendations."""
        learning_system_with_data.anthropic_client = Mock()
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "strategic_recommendations": ["Focus on video content strategy", "Expand to Stories format"],
            "tactical_actions": ["A/B test video lengths", "Optimize posting times"],
            "budget_optimization": ["Allocate 70% to video content", "Reserve 20% for testing"],
            "targeting_refinements": ["Narrow age targeting", "Test interest expansions"],
            "indian_market_specific": ["Use local language captions", "Leverage festival seasons"]
        }
        '''
        
        insights = [learning_system_with_data.user_learning_profiles["test_user"].content_insights[0]]
        features = {"content_type": "video", "platform": "instagram"}
        
        with patch('asyncio.to_thread', return_value=mock_response):
            recommendations = await learning_system_with_data._generate_predictive_recommendations(
                predicted_roi=15.0,
                insights=insights,
                features=features,
                user_id="test_user"
            )
        
        assert len(recommendations) >= 5
        assert any("video" in rec.lower() for rec in recommendations)
        assert any("local language" in rec.lower() for rec in recommendations)


class TestIntegrationWorkflow:
    """Integration tests for complete learning workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_learning_workflow(self):
        """Test complete learning workflow from analysis to prediction."""
        system = AdaptiveLearningSystem()
        user_id = "integration_test_user"
        
        # Step 1: Analyze multiple campaigns to build learning data
        campaigns = [
            {
                "campaign_id": "camp_1",
                "content_type": "video",
                "platforms": ["instagram"],
                "target_demographics": ["millennial"],
                "roi": 18.0,
                "ctr": 3.5,
                "conversion_rate": 8.0,
                "engagement_rate": 5.2,
                "cost_per_click": 1.20
            },
            {
                "campaign_id": "camp_2", 
                "content_type": "image",
                "platforms": ["facebook"],
                "target_demographics": ["millennial"],
                "roi": 12.0,
                "ctr": 2.8,
                "conversion_rate": 6.0,
                "engagement_rate": 4.1,
                "cost_per_click": 1.50
            },
            {
                "campaign_id": "camp_3",
                "content_type": "video",
                "platforms": ["instagram"],
                "target_demographics": ["gen_z"],
                "roi": 22.0,
                "ctr": 4.2,
                "conversion_rate": 9.5,
                "engagement_rate": 6.8,
                "cost_per_click": 1.10
            }
        ]
        
        # Mock historical campaigns for pattern detection
        with patch.object(system, '_get_user_historical_campaigns') as mock_historical:
            mock_historical.side_effect = lambda uid: campaigns[:len(campaigns)-1] if len(campaigns) > 1 else []
            
            # Analyze each campaign
            for i, campaign in enumerate(campaigns):
                mock_historical.side_effect = lambda uid, idx=i: campaigns[:idx] if idx > 0 else []
                result = await system.analyze_campaign_performance(user_id, campaign)
                
                assert result["user_id"] == user_id
                assert result["campaign_id"] == campaign["campaign_id"]
        
        # Step 2: Verify learning profile was created and updated
        assert user_id in system.user_learning_profiles
        profile = system.user_learning_profiles[user_id]
        assert profile.total_campaigns_analyzed == 3
        assert profile.learning_confidence > 0
        
        # Step 3: Test predictive insights
        proposed_campaign = {
            "content_type": "video",
            "platforms": ["instagram"],
            "target_demographics": ["millennial"],
            "objective": "conversion",
            "budget": 5000
        }
        
        # Mock sufficient prediction model
        model_key = f"{user_id}_performance"
        if model_key in system.prediction_models:
            system.prediction_models[model_key].training_sample_size = 10  # Ensure sufficient data
        
        prediction_result = await system.get_predictive_insights(user_id, proposed_campaign)
        
        if "error" not in prediction_result:
            assert "predicted_roi" in prediction_result
            assert "confidence_score" in prediction_result
            assert "optimization_recommendations" in prediction_result
        
        # Step 4: Verify end-to-end data flow
        assert len(campaigns) == 3
        assert profile.total_campaigns_analyzed == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])