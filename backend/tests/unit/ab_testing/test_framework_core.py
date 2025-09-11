"""
Unit tests for A/B Testing Framework Core Functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from ml.ab_testing.ab_testing_framework import (
    ABTestingFramework, 
    TestStatus, 
    TestType, 
    StatisticalSignificance,
    PersonalizedTest,
    TestVariation,
    TestResult
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestABTestingFrameworkCore:
    """Test core A/B testing framework functionality."""
    
    async def test_framework_initialization(self):
        """Test framework initializes correctly."""
        framework = ABTestingFramework()
        
        assert framework is not None
        assert len(framework.active_tests) == 0
        assert len(framework.test_history) == 0
        assert len(framework.statistical_models) == 3
        assert "minimum_sample_sizes" in framework.statistical_models
        assert "effect_size_benchmarks" in framework.statistical_models
        assert "test_duration_limits" in framework.statistical_models
    
    async def test_create_simple_ab_test(self, ab_framework, sample_test_config, sample_variations):
        """Test creating a simple A/B test."""
        test = await ab_framework.create_personalized_ab_test(
            "test_user", sample_test_config, sample_variations
        )
        
        assert test is not None
        assert test.test_name == sample_test_config["test_name"]
        assert test.test_type == TestType.SIMPLE_AB
        assert test.status == TestStatus.DRAFT
        assert len(test.variations) == 2
        assert test.user_id == "test_user"
        assert test.test_id in ab_framework.active_tests
    
    async def test_invalid_traffic_allocation(self, ab_framework, sample_test_config):
        """Test validation of traffic allocation."""
        invalid_variations = [
            {"variation_id": "a", "name": "A", "description": "Test A", "traffic_percentage": 60.0, "content_config": {}},
            {"variation_id": "b", "name": "B", "description": "Test B", "traffic_percentage": 50.0, "content_config": {}}
        ]
        
        with pytest.raises(ValueError, match="Traffic allocation must sum to 100%"):
            await ab_framework.create_personalized_ab_test(
                "test_user", sample_test_config, invalid_variations
            )
    
    async def test_minimum_sample_size_calculation(self, ab_framework):
        """Test minimum sample size calculation."""
        # Test conversion rate metric
        sample_size_cr = ab_framework._calculate_minimum_sample_size(
            "conversion_rate", 0.2, 0.80, 0.05
        )
        assert sample_size_cr >= 1000
        
        # Test CTR metric
        sample_size_ctr = ab_framework._calculate_minimum_sample_size(
            "ctr", 0.2, 0.80, 0.05
        )
        assert sample_size_ctr >= 500
        
        # Test continuous metric
        sample_size_cont = ab_framework._calculate_minimum_sample_size(
            "revenue", 0.5, 0.90, 0.05
        )
        assert sample_size_cont >= 200
    
    async def test_record_test_event_impression(self, ab_framework, active_test):
        """Test recording impression events."""
        initial_impressions = active_test.variations[0].impressions
        
        success = await ab_framework.record_test_event(
            active_test.test_id, "control", "impression"
        )
        
        assert success is True
        assert active_test.variations[0].impressions == initial_impressions + 1
    
    async def test_record_test_event_click(self, ab_framework, active_test):
        """Test recording click events."""
        # First add an impression
        await ab_framework.record_test_event(active_test.test_id, "control", "impression")
        
        initial_clicks = active_test.variations[0].clicks
        success = await ab_framework.record_test_event(
            active_test.test_id, "control", "click"
        )
        
        assert success is True
        assert active_test.variations[0].clicks == initial_clicks + 1
        assert active_test.variations[0].ctr > 0
    
    async def test_record_test_event_conversion(self, ab_framework, active_test):
        """Test recording conversion events."""
        # Add impression and click first
        await ab_framework.record_test_event(active_test.test_id, "control", "impression")
        await ab_framework.record_test_event(active_test.test_id, "control", "click")
        
        initial_conversions = active_test.variations[0].conversions
        initial_revenue = active_test.variations[0].revenue
        
        success = await ab_framework.record_test_event(
            active_test.test_id, "control", "conversion", value=100.0
        )
        
        assert success is True
        assert active_test.variations[0].conversions == initial_conversions + 1
        assert active_test.variations[0].revenue == initial_revenue + 100.0
        assert active_test.variations[0].conversion_rate > 0
    
    async def test_record_event_invalid_test(self, ab_framework):
        """Test recording event with invalid test ID."""
        success = await ab_framework.record_test_event(
            "invalid_test_id", "control", "impression"
        )
        assert success is False
    
    async def test_record_event_invalid_variation(self, ab_framework, active_test):
        """Test recording event with invalid variation ID."""
        success = await ab_framework.record_test_event(
            active_test.test_id, "invalid_variation", "impression"
        )
        assert success is False
    
    async def test_record_event_inactive_test(self, ab_framework, sample_test_config, sample_variations):
        """Test recording event on inactive test."""
        test = await ab_framework.create_personalized_ab_test(
            "test_user", sample_test_config, sample_variations
        )
        # Test is in DRAFT status (inactive)
        
        success = await ab_framework.record_test_event(
            test.test_id, "control", "impression"
        )
        assert success is False
    
    async def test_update_variation_metrics(self, ab_framework):
        """Test variation metrics calculation."""
        variation = TestVariation(
            variation_id="test_var",
            name="Test Variation",
            description="Test",
            traffic_percentage=50.0,
            content_config={}
        )
        
        # Add some data
        variation.impressions = 100
        variation.clicks = 10
        variation.conversions = 2
        variation.revenue = 200.0
        
        ab_framework._update_variation_metrics(variation)
        
        assert variation.ctr == 10.0  # 10/100 * 100
        assert variation.conversion_rate == 20.0  # 2/10 * 100
        assert variation.revenue_per_visitor == 20.0  # 200/10
    
    async def test_should_evaluate_test(self, ab_framework, active_test):
        """Test test evaluation conditions."""
        # New test should not be evaluated
        assert ab_framework._should_evaluate_test(active_test) is False
        
        # Add minimum duration
        active_test.start_date = datetime.now() - timedelta(days=8)
        
        # Still no data, should not evaluate
        assert ab_framework._should_evaluate_test(active_test) is False
        
        # Add sufficient conversions
        for var in active_test.variations:
            var.conversions = 500
        
        assert ab_framework._should_evaluate_test(active_test) is True
    
    async def test_find_best_variation(self, ab_framework):
        """Test finding best performing variation."""
        variations = []
        
        # Control variation
        control = TestVariation(
            variation_id="control",
            name="Control",
            description="Control",
            traffic_percentage=50.0,
            content_config={}
        )
        control.conversion_rate = 5.0
        variations.append(control)
        
        # Test variation (better performance)
        test_var = TestVariation(
            variation_id="test",
            name="Test",
            description="Test",
            traffic_percentage=50.0,
            content_config={}
        )
        test_var.conversion_rate = 7.5
        variations.append(test_var)
        
        best_var, best_value = ab_framework._find_best_variation(
            variations, control, "conversion_rate"
        )
        
        assert best_var.variation_id == "test"
        assert best_value == 7.5
    
    async def test_statistical_test_two_proportions(self, ab_framework):
        """Test two-proportion statistical test."""
        # Create variations with different performance
        control = TestVariation(
            variation_id="control",
            name="Control",
            description="Control",
            traffic_percentage=50.0,
            content_config={}
        )
        control.impressions = 1000
        control.clicks = 50
        control.conversions = 5
        
        treatment = TestVariation(
            variation_id="treatment",
            name="Treatment",
            description="Treatment",
            traffic_percentage=50.0,
            content_config={}
        )
        treatment.impressions = 1000
        treatment.clicks = 60
        treatment.conversions = 8
        
        result = ab_framework._two_proportion_z_test(control, treatment, "conversion_rate")
        
        assert "p_value" in result
        assert "effect_size" in result
        assert "confidence_interval" in result
        assert 0 <= result["p_value"] <= 1
        assert result["effect_size"] >= 0
    
    async def test_conclude_test(self, ab_framework, active_test):
        """Test test conclusion."""
        test_id = active_test.test_id
        assert test_id in ab_framework.active_tests
        
        success = await ab_framework.conclude_test(test_id, "test_completed")
        
        assert success is True
        assert test_id not in ab_framework.active_tests
        assert len(ab_framework.test_history) == 1
        assert ab_framework.test_history[0].status == TestStatus.COMPLETED
    
    async def test_get_test_insights(self, ab_framework, active_test):
        """Test getting test insights."""
        insights = await ab_framework.get_test_insights(active_test.user_id)
        
        assert "user_id" in insights
        assert "testing_summary" in insights
        assert "active_tests" in insights
        assert insights["testing_summary"]["active_tests"] == 1
        assert insights["testing_summary"]["total_tests"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestDataClasses:
    """Test A/B testing data classes."""
    
    def test_test_variation_creation(self):
        """Test TestVariation data class."""
        variation = TestVariation(
            variation_id="test_var",
            name="Test Variation",
            description="A test variation",
            traffic_percentage=50.0,
            content_config={"headline": "Test Headline"}
        )
        
        assert variation.variation_id == "test_var"
        assert variation.name == "Test Variation"
        assert variation.traffic_percentage == 50.0
        assert variation.impressions == 0
        assert variation.clicks == 0
        assert variation.conversions == 0
        assert variation.revenue == 0.0
        assert variation.ctr == 0.0
        assert variation.conversion_rate == 0.0
    
    def test_test_result_creation(self):
        """Test TestResult data class."""
        result = TestResult(
            test_id="test_123",
            total_impressions=2000,
            total_conversions=20,
            test_duration_days=14,
            winning_variation_id="test_var",
            confidence_level=0.95,
            significance_status=StatisticalSignificance.SIGNIFICANT,
            p_value=0.01,
            effect_size=0.5,
            power_analysis={"achieved_power": 0.8},
            projected_lift=25.0,
            estimated_revenue_impact=1000.0,
            recommendation="Implement the test variation",
            next_steps=["Deploy to production", "Monitor results"]
        )
        
        assert result.test_id == "test_123"
        assert result.winning_variation_id == "test_var"
        assert result.confidence_level == 0.95
        assert result.significance_status == StatisticalSignificance.SIGNIFICANT
        assert result.projected_lift == 25.0