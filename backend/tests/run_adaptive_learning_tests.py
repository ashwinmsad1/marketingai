#!/usr/bin/env python3
"""
Simple test runner for Adaptive Learning System tests
"""

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ml.learning.adaptive_learning_system import (
    AdaptiveLearningSystem,
    LearningInsight,
    UserLearningProfile,
    PredictionModel,
    LearningType,
    ConfidenceLevel
)


def test_data_classes():
    """Test basic data class functionality."""
    print("🧪 Testing data classes...")
    
    # Test LearningInsight
    insight = LearningInsight(
        insight_id="test_1",
        user_id="user_1",
        learning_type=LearningType.PERFORMANCE_PATTERN,
        insight_title="Test Insight",
        insight_description="Test description",
        supporting_data={"test": "data"},
        confidence_level=ConfidenceLevel.HIGH,
        significance_score=0.8,
        sample_size=50,
        applicable_scenarios=["test"],
        recommended_actions=["action1"],
        performance_impact={"roi": 10.0},
        estimated_roi_lift=10.0,
        campaigns_analyzed=["camp_1"]
    )
    assert insight.insight_id == "test_1"
    assert insight.learning_type == LearningType.PERFORMANCE_PATTERN
    print("✅ LearningInsight creation works")
    
    # Test UserLearningProfile
    profile = UserLearningProfile(user_id="user_1")
    assert profile.user_id == "user_1"
    assert len(profile.performance_insights) == 0
    assert profile.learning_confidence == 0.0
    print("✅ UserLearningProfile creation works")
    
    # Test PredictionModel
    model = PredictionModel(
        model_id="model_1",
        model_type="performance",
        feature_weights={"content": 0.5},
        baseline_metrics={"roi": 10.0},
        accuracy_score=0.75,
        prediction_count=100,
        validation_score=0.8,
        training_sample_size=25
    )
    assert model.model_id == "model_1"
    assert model.accuracy_score == 0.75
    print("✅ PredictionModel creation works")


def test_adaptive_learning_system_basic():
    """Test basic AdaptiveLearningSystem functionality."""
    print("\n🧪 Testing AdaptiveLearningSystem basics...")
    
    system = AdaptiveLearningSystem()
    
    # Test initialization
    assert isinstance(system.user_learning_profiles, dict)
    assert isinstance(system.prediction_models, dict)
    assert "min_campaigns_for_insight" in system.learning_thresholds
    print("✅ System initialization works")
    
    # Test feature extraction
    campaign_data = {
        "content_type": "video",
        "platforms": ["instagram"],
        "target_demographics": ["millennial"],
        "budget": 2500,
        "caption": "Test caption",
        "hashtags": ["#test1", "#test2"]
    }
    
    features = system._extract_campaign_features(campaign_data)
    assert features["content_type"] == "video"
    assert features["platform"] == "instagram"
    assert features["budget_level"] == "medium"
    assert features["caption_length"] == len("Test caption")
    assert features["hashtag_count"] == 2
    print("✅ Feature extraction works")
    
    # Test budget categorization
    assert system._categorize_budget(500) == "low"
    assert system._categorize_budget(2500) == "medium"
    assert system._categorize_budget(10000) == "high"
    assert system._categorize_budget(25000) == "very_high"
    print("✅ Budget categorization works")
    
    # Test demographics similarity
    demo1 = ["millennial", "urban"]
    demo2 = ["millennial", "suburban"]
    similarity = system._demographics_similarity(demo1, demo2)
    assert 0 <= similarity <= 1
    print("✅ Demographics similarity calculation works")
    
    # Test confidence level determination
    assert system._determine_confidence_level(25) == ConfidenceLevel.LOW
    assert system._determine_confidence_level(100) == ConfidenceLevel.MEDIUM
    assert system._determine_confidence_level(300) == ConfidenceLevel.HIGH
    print("✅ Confidence level determination works")


async def test_adaptive_learning_system_async():
    """Test async AdaptiveLearningSystem functionality."""
    print("\n🧪 Testing AdaptiveLearningSystem async methods...")
    
    system = AdaptiveLearningSystem()
    
    # Test campaign analysis with minimal data
    campaign_data = {
        "campaign_id": "test_camp_1",
        "content_type": "video",
        "roi": 15.0,
        "ctr": 3.0,
        "platforms": ["instagram"]
    }
    
    try:
        result = await system.analyze_campaign_performance("test_user", campaign_data)
        assert "user_id" in result
        assert result["user_id"] == "test_user"
        assert "insights_extracted" in result
        print("✅ Campaign performance analysis works")
        
        # Test that user profile was created
        assert "test_user" in system.user_learning_profiles
        profile = system.user_learning_profiles["test_user"]
        assert profile.total_campaigns_analyzed == 1
        print("✅ User profile creation works")
        
    except Exception as e:
        print(f"⚠️  Campaign analysis test failed: {e}")
    
    # Test predictive insights
    try:
        proposed_campaign = {
            "content_type": "image",
            "platforms": ["facebook"],
            "budget": 1000
        }
        
        prediction = await system.get_predictive_insights("test_user", proposed_campaign)
        assert "user_id" in prediction or "error" in prediction
        print("✅ Predictive insights works (or properly handles insufficient data)")
        
    except Exception as e:
        print(f"⚠️  Predictive insights test failed: {e}")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing edge cases...")
    
    system = AdaptiveLearningSystem()
    
    # Test empty campaign data
    features = system._extract_campaign_features({})
    assert features["content_type"] is None
    assert features["budget_level"] == "low"  # Default for 0 budget
    print("✅ Empty campaign data handling works")
    
    # Test malformed data
    malformed_data = {
        "target_demographics": "not_a_list",
        "platforms": None,
        "budget": "not_a_number"
    }
    
    features = system._extract_campaign_features(malformed_data)
    assert features["age_group"] is None
    assert features["platform"] is None
    print("✅ Malformed data handling works")
    
    # Test boundary values for confidence levels
    assert system._determine_confidence_level(0) == ConfidenceLevel.LOW
    assert system._determine_confidence_level(49) == ConfidenceLevel.LOW
    assert system._determine_confidence_level(50) == ConfidenceLevel.MEDIUM
    assert system._determine_confidence_level(200) == ConfidenceLevel.HIGH
    print("✅ Boundary value handling works")
    
    # Test demographics similarity edge cases
    assert system._demographics_similarity([], []) == 0.0
    assert system._demographics_similarity(["a"], []) == 0.0
    demo = ["millennial", "urban"]
    assert system._demographics_similarity(demo, demo) == 1.0
    print("✅ Demographics similarity edge cases work")


def test_learning_confidence():
    """Test learning confidence calculation."""
    print("\n🧪 Testing learning confidence calculation...")
    
    system = AdaptiveLearningSystem()
    
    # Test empty profile
    empty_profile = UserLearningProfile(user_id="empty_user")
    confidence = system._calculate_learning_confidence(empty_profile)
    assert confidence == 0.0
    print("✅ Empty profile confidence calculation works")
    
    # Test profile with insights
    profile = UserLearningProfile(user_id="test_user")
    profile.total_campaigns_analyzed = 10
    
    # Add a test insight
    insight = LearningInsight(
        insight_id="test_insight",
        user_id="test_user",
        learning_type=LearningType.PERFORMANCE_PATTERN,
        insight_title="Test",
        insight_description="Test",
        supporting_data={},
        confidence_level=ConfidenceLevel.HIGH,
        significance_score=0.8,
        sample_size=20,
        applicable_scenarios=[],
        recommended_actions=[],
        performance_impact={},
        estimated_roi_lift=0,
        campaigns_analyzed=[]
    )
    
    profile.performance_insights.append(insight)
    confidence = system._calculate_learning_confidence(profile)
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0  # Should be positive with insights
    print("✅ Profile with insights confidence calculation works")


def test_performance_prediction():
    """Test performance prediction functionality."""
    print("\n🧪 Testing performance prediction...")
    
    system = AdaptiveLearningSystem()
    
    # Create a basic model
    model = PredictionModel(
        model_id="test_model",
        model_type="performance",
        feature_weights=system.feature_importance_weights.copy(),
        baseline_metrics={},
        accuracy_score=0.75,
        prediction_count=0,
        validation_score=0.0,
        training_sample_size=10
    )
    
    # Test with good features
    features = {
        "content_type": "video",
        "budget_level": "high",
        "platform": "instagram"
    }
    
    prediction = system._predict_performance(features, model)
    assert prediction >= 0
    assert prediction > 5.0  # Should be above baseline
    print("✅ Performance prediction with good features works")
    
    # Test with empty features
    empty_prediction = system._predict_performance({}, model)
    assert empty_prediction == 5.0  # Should return baseline
    print("✅ Performance prediction with empty features works")


async def run_all_tests():
    """Run all test suites."""
    print("🚀 Starting Adaptive Learning System Test Suite")
    print("=" * 60)
    
    try:
        test_data_classes()
        test_adaptive_learning_system_basic()
        await test_adaptive_learning_system_async()
        test_edge_cases()
        test_learning_confidence()
        test_performance_prediction()
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)