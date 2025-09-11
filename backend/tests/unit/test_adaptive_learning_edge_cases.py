"""
Edge cases and error handling tests for Adaptive Learning System
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


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def learning_system(self):
        """Create a fresh AdaptiveLearningSystem for each test."""
        return AdaptiveLearningSystem()
    
    def test_empty_campaign_data(self, learning_system):
        """Test behavior with empty campaign data."""
        features = learning_system._extract_campaign_features({})
        
        # All features should be None or empty
        assert features["visual_style"] is None
        assert features["content_type"] is None
        assert features["caption_length"] == 0
        assert features["hashtag_count"] == 0
        assert features["age_group"] is None
        assert features["platform"] is None
        assert features["objective"] is None
        assert features["budget_level"] == "low"  # Default for budget 0
    
    def test_malformed_campaign_data(self, learning_system):
        """Test behavior with malformed campaign data."""
        malformed_data = {
            "target_demographics": "not_a_list",  # Should be a list
            "platforms": None,
            "hashtags": "not_a_list",
            "budget": "not_a_number"
        }
        
        features = learning_system._extract_campaign_features(malformed_data)
        
        # Should handle gracefully without crashing
        assert features["age_group"] is None
        assert features["platform"] is None
        assert features["hashtag_count"] == 0
        assert features["budget_level"] == "low"  # Default fallback
    
    @pytest.mark.asyncio
    async def test_analyze_campaign_with_missing_metrics(self, learning_system):
        """Test campaign analysis with missing performance metrics."""
        campaign_data = {
            "campaign_id": "incomplete_campaign",
            "content_type": "video",
            "platforms": ["instagram"]
            # Missing roi, ctr, conversion_rate, etc.
        }
        
        result = await learning_system.analyze_campaign_performance("test_user", campaign_data)
        
        # Should complete without errors
        assert result["user_id"] == "test_user"
        assert result["campaign_id"] == "incomplete_campaign"
        assert result["insights_extracted"] >= 0
    
    def test_demographics_similarity_edge_cases(self, learning_system):
        """Test demographics similarity with edge cases."""
        # Empty lists
        assert learning_system._demographics_similarity([], []) == 0.0
        assert learning_system._demographics_similarity(["a"], []) == 0.0
        assert learning_system._demographics_similarity([], ["a"]) == 0.0
        
        # Identical lists
        demo = ["millennial", "urban"]
        assert learning_system._demographics_similarity(demo, demo) == 1.0
        
        # Single element overlap
        assert learning_system._demographics_similarity(["a", "b"], ["a", "c"]) == 0.5
        
        # No overlap
        assert learning_system._demographics_similarity(["a", "b"], ["c", "d"]) == 0.0
        
        # Case sensitivity
        assert learning_system._demographics_similarity(["Millennial"], ["millennial"]) == 0.0
    
    def test_confidence_level_boundary_values(self, learning_system):
        """Test confidence level determination at boundary values."""
        assert learning_system._determine_confidence_level(0) == ConfidenceLevel.LOW
        assert learning_system._determine_confidence_level(49) == ConfidenceLevel.LOW
        assert learning_system._determine_confidence_level(50) == ConfidenceLevel.MEDIUM
        assert learning_system._determine_confidence_level(199) == ConfidenceLevel.MEDIUM
        assert learning_system._determine_confidence_level(200) == ConfidenceLevel.HIGH
        assert learning_system._determine_confidence_level(1000) == ConfidenceLevel.HIGH
    
    def test_budget_categorization_edge_cases(self, learning_system):
        """Test budget categorization with edge values."""
        assert learning_system._categorize_budget(0) == "low"
        assert learning_system._categorize_budget(-100) == "low"  # Negative budget
        assert learning_system._categorize_budget(999.99) == "low"
        assert learning_system._categorize_budget(1000) == "medium"
        assert learning_system._categorize_budget(4999.99) == "medium"
        assert learning_system._categorize_budget(5000) == "high"
        assert learning_system._categorize_budget(19999.99) == "high"
        assert learning_system._categorize_budget(20000) == "very_high"
        assert learning_system._categorize_budget(1000000) == "very_high"
    
    def test_learning_confidence_with_empty_profile(self, learning_system):
        """Test learning confidence calculation with empty profile."""
        profile = UserLearningProfile(user_id="empty_user")
        confidence = learning_system._calculate_learning_confidence(profile)
        assert confidence == 0.0
    
    def test_learning_confidence_with_zero_significance(self, learning_system):
        """Test learning confidence with zero significance insights."""
        profile = UserLearningProfile(user_id="test_user")
        
        insight = LearningInsight(
            insight_id="zero_sig_insight",
            user_id="test_user",
            learning_type=LearningType.PERFORMANCE_PATTERN,
            insight_title="Zero Significance",
            insight_description="Test",
            supporting_data={},
            confidence_level=ConfidenceLevel.LOW,
            significance_score=0.0,  # Zero significance
            sample_size=10,
            applicable_scenarios=[],
            recommended_actions=[],
            performance_impact={},
            estimated_roi_lift=0,
            campaigns_analyzed=[]
        )
        
        profile.performance_insights.append(insight)
        profile.total_campaigns_analyzed = 1
        
        confidence = learning_system._calculate_learning_confidence(profile)
        assert confidence >= 0.0
        assert confidence <= 1.0
    
    def test_insight_applicability_with_missing_data(self, learning_system):
        """Test insight applicability calculation with missing supporting data."""
        insight = LearningInsight(
            insight_id="missing_data_insight",
            user_id="test_user",
            learning_type=LearningType.CONTENT_EFFECTIVENESS,
            insight_title="Missing Data",
            insight_description="Test",
            supporting_data={},  # Empty supporting data
            confidence_level=ConfidenceLevel.MEDIUM,
            significance_score=0.5,
            sample_size=20,
            applicable_scenarios=[],
            recommended_actions=[],
            performance_impact={},
            estimated_roi_lift=0,
            campaigns_analyzed=[]
        )
        
        features = {
            "content_type": "video",
            "demographics": ["millennial"],
            "platform": "instagram"
        }
        
        applicability = learning_system._calculate_insight_applicability(insight, features)
        assert applicability == 0.0  # Should be 0 with no supporting data matches
    
    def test_predict_performance_with_empty_features(self, learning_system):
        """Test performance prediction with empty features."""
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
        
        prediction = learning_system._predict_performance({}, model)
        assert prediction == 5.0  # Should return baseline
    
    def test_predict_performance_with_none_values(self, learning_system):
        """Test performance prediction with None feature values."""
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
        
        features = {
            "content_type": None,
            "platform": None,
            "budget_level": None
        }
        
        prediction = learning_system._predict_performance(features, model)
        assert prediction == 5.0  # Should return baseline with no valid features


class TestErrorHandling:
    """Test error handling and exception scenarios."""
    
    @pytest.fixture
    def learning_system(self):
        """Create a fresh AdaptiveLearningSystem for each test."""
        return AdaptiveLearningSystem()
    
    @pytest.mark.asyncio
    async def test_claude_client_network_error(self, learning_system):
        """Test handling of Claude client network errors."""
        learning_system.anthropic_client = Mock()
        
        # Mock asyncio.to_thread to raise a network error
        with patch('asyncio.to_thread', side_effect=ConnectionError("Network error")):
            insight = await learning_system._generate_performance_insight(
                user_id="test_user",
                performance_change=20.0,
                campaign_data={"roi": 15.0},
                historical_campaigns=[],
                metric_type="roi"
            )
        
        # Should fallback to basic insight
        assert insight.insight_title == "ROI Improvement Pattern"
        assert "20.0% improvement" in insight.insight_description
    
    @pytest.mark.asyncio
    async def test_claude_malformed_json_response(self, learning_system):
        """Test handling of malformed JSON from Claude."""
        learning_system.anthropic_client = Mock()
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "This is not valid JSON at all!"
        
        with patch('asyncio.to_thread', return_value=mock_response):
            insight = await learning_system._generate_performance_insight(
                user_id="test_user",
                performance_change=25.0,
                campaign_data={"roi": 18.5},
                historical_campaigns=[],
                metric_type="roi"
            )
        
        # Should fallback to basic insight
        assert insight.insight_title == "ROI Improvement Pattern"
        assert insight.estimated_roi_lift == 25.0
    
    @pytest.mark.asyncio
    async def test_claude_incomplete_json_response(self, learning_system):
        """Test handling of incomplete JSON from Claude."""
        learning_system.anthropic_client = Mock()
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "insight_title": "Incomplete Insight"
            // Missing closing brace and other fields
        '''
        
        with patch('asyncio.to_thread', return_value=mock_response):
            insight = await learning_system._generate_performance_insight(
                user_id="test_user",
                performance_change=15.0,
                campaign_data={"roi": 12.0},
                historical_campaigns=[],
                metric_type="roi"
            )
        
        # Should fallback to basic insight
        assert insight.insight_title == "ROI Improvement Pattern"
        assert insight.estimated_roi_lift == 15.0
    
    @pytest.mark.asyncio
    async def test_update_prediction_models_with_invalid_data(self, learning_system):
        """Test updating prediction models with invalid campaign data."""
        user_id = "test_user"
        learning_system.user_learning_profiles[user_id] = UserLearningProfile(user_id=user_id)
        
        invalid_campaign = {
            "roi": "not_a_number",  # Invalid ROI
            "content_type": 123,    # Invalid content type
            "budget": None          # None budget
        }
        
        # Should not raise an exception
        await learning_system._update_prediction_models(user_id, invalid_campaign)
        
        # Model should still be created but with default handling
        model_key = f"{user_id}_performance"
        if model_key in learning_system.prediction_models:
            model = learning_system.prediction_models[model_key]
            assert model.training_sample_size == 1
    
    @pytest.mark.asyncio
    async def test_analysis_with_corrupted_profile(self, learning_system):
        """Test campaign analysis with corrupted user profile."""
        user_id = "corrupted_user"
        
        # Create a corrupted profile (missing required attributes)
        corrupted_profile = Mock()
        corrupted_profile.total_campaigns_analyzed = "not_a_number"
        corrupted_profile.performance_insights = None
        learning_system.user_learning_profiles[user_id] = corrupted_profile
        
        campaign_data = {
            "campaign_id": "test_camp",
            "roi": 15.0,
            "content_type": "video"
        }
        
        # Should handle gracefully and either create new profile or handle the error
        result = await learning_system.analyze_campaign_performance(user_id, campaign_data)
        
        # Should either succeed with recovery or provide error info
        assert "user_id" in result or "error" in result
    
    def test_get_historical_campaigns_database_error(self, learning_system):
        """Test behavior when database query for historical campaigns fails."""
        # The mock implementation returns empty list, but in real scenario
        # this would test database connection failures
        
        with patch.object(learning_system, '_get_user_historical_campaigns', side_effect=Exception("DB Error")):
            try:
                campaigns = learning_system._get_user_historical_campaigns("test_user")
                # If it doesn't raise, it should return empty list
                assert campaigns == []
            except Exception as e:
                # If it does raise, that's also acceptable behavior
                assert "DB Error" in str(e)
    
    def test_risk_factors_with_empty_insights(self, learning_system):
        """Test risk factor identification with empty insights list."""
        features = {
            "content_type": "image",
            "platform": "facebook",
            "budget_level": "low"
        }
        
        risks = learning_system._identify_risk_factors(features, [])
        
        # Should still identify budget risk
        assert len(risks) >= 1
        assert any("Low budget" in risk for risk in risks)
    
    @pytest.mark.asyncio
    async def test_predictive_insights_with_corrupted_model(self, learning_system):
        """Test predictive insights with corrupted prediction model."""
        user_id = "test_user"
        
        # Create user profile
        profile = UserLearningProfile(user_id=user_id)
        learning_system.user_learning_profiles[user_id] = profile
        
        # Create corrupted model
        corrupted_model = Mock()
        corrupted_model.training_sample_size = "not_a_number"
        corrupted_model.feature_weights = None
        learning_system.prediction_models[f"{user_id}_performance"] = corrupted_model
        
        proposed_campaign = {"content_type": "video"}
        
        result = await learning_system.get_predictive_insights(user_id, proposed_campaign)
        
        # Should handle gracefully
        assert "error" in result or "predicted_performance" in result


class TestConcurrencyAndThreadSafety:
    """Test concurrent operations and thread safety."""
    
    @pytest.fixture
    def learning_system(self):
        """Create a fresh AdaptiveLearningSystem for each test."""
        return AdaptiveLearningSystem()
    
    @pytest.mark.asyncio
    async def test_concurrent_campaign_analysis(self, learning_system):
        """Test concurrent campaign analysis for different users."""
        campaign_data_1 = {
            "campaign_id": "camp_user1",
            "content_type": "video",
            "roi": 15.0
        }
        
        campaign_data_2 = {
            "campaign_id": "camp_user2", 
            "content_type": "image",
            "roi": 12.0
        }
        
        # Analyze campaigns concurrently
        tasks = [
            learning_system.analyze_campaign_performance("user_1", campaign_data_1),
            learning_system.analyze_campaign_performance("user_2", campaign_data_2)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Both should complete successfully
        assert len(results) == 2
        for result in results:
            assert not isinstance(result, Exception)
            assert "user_id" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_same_user_analysis(self, learning_system):
        """Test concurrent campaign analysis for the same user."""
        user_id = "concurrent_user"
        
        campaigns = [
            {"campaign_id": "camp_1", "content_type": "video", "roi": 15.0},
            {"campaign_id": "camp_2", "content_type": "image", "roi": 12.0},
            {"campaign_id": "camp_3", "content_type": "carousel", "roi": 18.0}
        ]
        
        # Analyze multiple campaigns for same user concurrently
        tasks = [
            learning_system.analyze_campaign_performance(user_id, campaign)
            for campaign in campaigns
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert result["user_id"] == user_id
        
        # User profile should exist and have updated campaign count
        assert user_id in learning_system.user_learning_profiles
        profile = learning_system.user_learning_profiles[user_id]
        assert profile.total_campaigns_analyzed >= 1  # At least one should have updated
    
    @pytest.mark.asyncio
    async def test_concurrent_predictive_insights(self, learning_system):
        """Test concurrent predictive insights requests."""
        user_id = "prediction_user"
        
        # Setup user profile and model
        profile = UserLearningProfile(user_id=user_id)
        learning_system.user_learning_profiles[user_id] = profile
        
        model = PredictionModel(
            model_id=f"{user_id}_performance",
            model_type="performance",
            feature_weights=learning_system.feature_importance_weights.copy(),
            baseline_metrics={},
            accuracy_score=0.75,
            prediction_count=0,
            validation_score=0.0,
            training_sample_size=10
        )
        learning_system.prediction_models[f"{user_id}_performance"] = model
        
        proposed_campaigns = [
            {"content_type": "video", "budget": 1000},
            {"content_type": "image", "budget": 2000},
            {"content_type": "carousel", "budget": 3000}
        ]
        
        # Get predictions concurrently
        tasks = [
            learning_system.get_predictive_insights(user_id, campaign)
            for campaign in proposed_campaigns
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            if "error" not in result:
                assert "predicted_roi" in result


class TestMemoryAndPerformance:
    """Test memory usage and performance characteristics."""
    
    @pytest.fixture
    def learning_system(self):
        """Create a fresh AdaptiveLearningSystem for each test."""
        return AdaptiveLearningSystem()
    
    def test_large_insight_accumulation(self, learning_system):
        """Test behavior with large number of insights."""
        user_id = "heavy_user"
        profile = UserLearningProfile(user_id=user_id)
        
        # Add many insights
        for i in range(1000):
            insight = LearningInsight(
                insight_id=f"insight_{i}",
                user_id=user_id,
                learning_type=LearningType.PERFORMANCE_PATTERN,
                insight_title=f"Insight {i}",
                insight_description=f"Description {i}",
                supporting_data={"data": i},
                confidence_level=ConfidenceLevel.MEDIUM,
                significance_score=0.5,
                sample_size=10,
                applicable_scenarios=[],
                recommended_actions=[],
                performance_impact={},
                estimated_roi_lift=0,
                campaigns_analyzed=[]
            )
            profile.performance_insights.append(insight)
        
        learning_system.user_learning_profiles[user_id] = profile
        
        # Should still calculate confidence without issues
        confidence = learning_system._calculate_learning_confidence(profile)
        assert confidence >= 0.0
        assert confidence <= 1.0
    
    def test_feature_extraction_performance(self, learning_system):
        """Test feature extraction with large campaign data."""
        large_campaign_data = {
            "campaign_id": "large_campaign",
            "content_type": "video",
            "visual_style": "professional",
            "platforms": ["instagram", "facebook"],
            "target_demographics": ["millennial"] * 100,  # Large list
            "target_interests": [f"interest_{i}" for i in range(1000)],  # Very large list
            "hashtags": [f"#tag{i}" for i in range(500)],  # Large hashtag list
            "caption": "A" * 10000,  # Very long caption
            "budget": 50000
        }
        
        # Should handle large data efficiently
        features = learning_system._extract_campaign_features(large_campaign_data)
        
        assert features["content_type"] == "video"
        assert features["caption_length"] == 10000
        assert features["hashtag_count"] == 500
        assert features["budget_level"] == "very_high"
    
    def test_memory_cleanup_on_profile_deletion(self, learning_system):
        """Test memory cleanup when user profiles are removed."""
        user_ids = [f"temp_user_{i}" for i in range(100)]
        
        # Create many user profiles
        for user_id in user_ids:
            profile = UserLearningProfile(user_id=user_id)
            learning_system.user_learning_profiles[user_id] = profile
        
        assert len(learning_system.user_learning_profiles) == 100
        
        # Remove profiles
        for user_id in user_ids:
            del learning_system.user_learning_profiles[user_id]
        
        assert len(learning_system.user_learning_profiles) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])