"""
Test fixtures for A/B Testing Framework
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ml.ab_testing.ab_testing_framework import (
    PersonalizedTest,
    TestVariation,
    TestResult,
    TestStatus,
    TestType,
    StatisticalSignificance
)


class ABTestingFixtures:
    """Collection of A/B testing fixtures for testing."""
    
    @staticmethod
    def create_sample_test_variation(
        variation_id: str = "test_var",
        name: str = "Test Variation",
        description: str = "A test variation",
        traffic_percentage: float = 50.0,
        content_config: Dict[str, Any] = None
    ) -> TestVariation:
        """Create a sample test variation."""
        if content_config is None:
            content_config = {"headline": "Test Headline", "type": "test"}
        
        return TestVariation(
            variation_id=variation_id,
            name=name,
            description=description,
            traffic_percentage=traffic_percentage,
            content_config=content_config
        )
    
    @staticmethod
    def create_sample_test(
        test_id: str = "sample_test_123",
        user_id: str = "sample_user",
        test_name: str = "Sample A/B Test",
        variations: List[TestVariation] = None
    ) -> PersonalizedTest:
        """Create a sample personalized test."""
        if variations is None:
            variations = [
                ABTestingFixtures.create_sample_test_variation("control", "Control", "Control version"),
                ABTestingFixtures.create_sample_test_variation("test", "Test", "Test version")
            ]
        
        return PersonalizedTest(
            test_id=test_id,
            user_id=user_id,
            test_name=test_name,
            test_type=TestType.SIMPLE_AB,
            hypothesis="Test will outperform control",
            primary_metric="conversion_rate",
            variations=variations,
            start_date=datetime.now(),
            planned_end_date=datetime.now() + timedelta(days=14),
            minimum_sample_size=1000,
            significance_level=0.05,
            traffic_allocation={"control": 50.0, "test": 50.0},
            status=TestStatus.DRAFT
        )
    
    @staticmethod
    def create_test_with_data(
        impressions_control: int = 1000,
        clicks_control: int = 50,
        conversions_control: int = 5,
        impressions_test: int = 1000,
        clicks_test: int = 60,
        conversions_test: int = 8
    ) -> PersonalizedTest:
        """Create a test with performance data."""
        test = ABTestingFixtures.create_sample_test()
        
        # Add data to control variation
        control = test.variations[0]
        control.impressions = impressions_control
        control.clicks = clicks_control
        control.conversions = conversions_control
        control.revenue = conversions_control * 100.0
        
        # Calculate metrics
        if impressions_control > 0:
            control.ctr = (clicks_control / impressions_control) * 100
        if clicks_control > 0:
            control.conversion_rate = (conversions_control / clicks_control) * 100
            control.revenue_per_visitor = control.revenue / clicks_control
        
        # Add data to test variation
        test_var = test.variations[1]
        test_var.impressions = impressions_test
        test_var.clicks = clicks_test
        test_var.conversions = conversions_test
        test_var.revenue = conversions_test * 100.0
        
        # Calculate metrics
        if impressions_test > 0:
            test_var.ctr = (clicks_test / impressions_test) * 100
        if clicks_test > 0:
            test_var.conversion_rate = (conversions_test / clicks_test) * 100
            test_var.revenue_per_visitor = test_var.revenue / clicks_test
        
        return test
    
    @staticmethod
    def create_multivariate_test(
        num_variations: int = 4,
        test_name: str = "Multivariate Test"
    ) -> PersonalizedTest:
        """Create a multivariate test with multiple variations."""
        variations = []
        traffic_per_variation = 100.0 / num_variations
        
        for i in range(num_variations):
            variation = ABTestingFixtures.create_sample_test_variation(
                variation_id=f"variation_{i}",
                name=f"Variation {i}",
                description=f"Test variation {i}",
                traffic_percentage=traffic_per_variation,
                content_config={"headline": f"Headline {i}", "variation_num": i}
            )
            variations.append(variation)
        
        test = PersonalizedTest(
            test_id=f"multivariate_test_{num_variations}",
            user_id="multivariate_user",
            test_name=test_name,
            test_type=TestType.MULTIVARIATE,
            hypothesis=f"One of {num_variations} variations will perform best",
            primary_metric="conversion_rate",
            variations=variations,
            start_date=datetime.now(),
            planned_end_date=datetime.now() + timedelta(days=21),
            minimum_sample_size=2000,
            significance_level=0.05,
            traffic_allocation={f"variation_{i}": traffic_per_variation for i in range(num_variations)},
            status=TestStatus.DRAFT
        )
        
        return test
    
    @staticmethod
    def create_test_result(
        test_id: str = "test_123",
        winning_variation_id: str = "test_variation",
        confidence_level: float = 0.95,
        projected_lift: float = 25.0
    ) -> TestResult:
        """Create a sample test result."""
        return TestResult(
            test_id=test_id,
            total_impressions=2000,
            total_conversions=26,
            test_duration_days=14,
            winning_variation_id=winning_variation_id,
            confidence_level=confidence_level,
            significance_status=StatisticalSignificance.SIGNIFICANT,
            p_value=0.02,
            effect_size=0.4,
            power_analysis={"achieved_power": 0.85, "required_sample_size": 1800},
            projected_lift=projected_lift,
            estimated_revenue_impact=2500.0,
            recommendation="Implement the test variation",
            next_steps=[
                "Deploy test variation to production",
                "Monitor performance for 30 days",
                "Plan next optimization test"
            ]
        )
    
    @staticmethod
    def create_performance_scenarios() -> List[Dict[str, Any]]:
        """Create various performance scenarios for testing."""
        return [
            {
                "name": "Highly Significant Win",
                "control": {"impressions": 10000, "clicks": 500, "conversions": 50},
                "test": {"impressions": 10000, "clicks": 750, "conversions": 90},
                "expected_winner": "test",
                "expected_significance": "highly_significant"
            },
            {
                "name": "Marginal Win",
                "control": {"impressions": 5000, "clicks": 250, "conversions": 25},
                "test": {"impressions": 5000, "clicks": 275, "conversions": 30},
                "expected_winner": "test",
                "expected_significance": "approaching"
            },
            {
                "name": "No Difference",
                "control": {"impressions": 2000, "clicks": 100, "conversions": 10},
                "test": {"impressions": 2000, "clicks": 101, "conversions": 10},
                "expected_winner": None,
                "expected_significance": "not_significant"
            },
            {
                "name": "Control Wins",
                "control": {"impressions": 3000, "clicks": 200, "conversions": 25},
                "test": {"impressions": 3000, "clicks": 150, "conversions": 15},
                "expected_winner": "control",
                "expected_significance": "significant"
            },
            {
                "name": "Small Sample",
                "control": {"impressions": 100, "clicks": 10, "conversions": 1},
                "test": {"impressions": 100, "clicks": 15, "conversions": 3},
                "expected_winner": None,
                "expected_significance": "not_significant"
            }
        ]
    
    @staticmethod
    def create_api_test_request(
        campaign_name: str = "Fixture Test Campaign",
        test_type: str = "content"
    ) -> Dict[str, Any]:
        """Create API test request fixture."""
        return {
            "campaign_name": campaign_name,
            "test_type": test_type,
            "variant_a": {
                "name": "Control Version",
                "description": "Current design",
                "content": {
                    "headline": "Original Headline",
                    "description": "Original description",
                    "call_to_action": "Buy Now"
                }
            },
            "variant_b": {
                "name": "Test Version",
                "description": "New improved design",
                "content": {
                    "headline": "Improved Headline",
                    "description": "Better description",
                    "call_to_action": "Shop Now"
                }
            },
            "traffic_split": 50,
            "sample_size": 2000,
            "confidence_level": 95,
            "duration_days": 14
        }
    
    @staticmethod
    def create_user_test_history(
        user_id: str = "test_user",
        num_tests: int = 5
    ) -> List[PersonalizedTest]:
        """Create test history for a user."""
        tests = []
        
        for i in range(num_tests):
            test = ABTestingFixtures.create_sample_test(
                test_id=f"history_test_{i}",
                user_id=user_id,
                test_name=f"Historical Test {i+1}"
            )
            
            # Set different statuses
            if i < 2:
                test.status = TestStatus.COMPLETED
            elif i < 4:
                test.status = TestStatus.ACTIVE
            else:
                test.status = TestStatus.PAUSED
            
            # Add some performance data
            if test.status == TestStatus.COMPLETED:
                test.current_result = ABTestingFixtures.create_test_result(
                    test_id=test.test_id,
                    projected_lift=15.0 + i * 5
                )
            
            tests.append(test)
        
        return tests


# Pytest fixtures using the fixture class
@pytest.fixture
def sample_test_variation():
    """Sample test variation fixture."""
    return ABTestingFixtures.create_sample_test_variation()


@pytest.fixture
def sample_test():
    """Sample test fixture."""
    return ABTestingFixtures.create_sample_test()


@pytest.fixture
def test_with_data():
    """Test with performance data fixture."""
    return ABTestingFixtures.create_test_with_data()


@pytest.fixture
def multivariate_test():
    """Multivariate test fixture."""
    return ABTestingFixtures.create_multivariate_test()


@pytest.fixture
def sample_test_result():
    """Sample test result fixture."""
    return ABTestingFixtures.create_test_result()


@pytest.fixture
def performance_scenarios():
    """Performance scenarios fixture."""
    return ABTestingFixtures.create_performance_scenarios()


@pytest.fixture
def api_request_fixture():
    """API request fixture."""
    return ABTestingFixtures.create_api_test_request()


@pytest.fixture
def user_test_history():
    """User test history fixture."""
    return ABTestingFixtures.create_user_test_history()


@pytest.fixture
def load_test_data():
    """Load testing data fixture."""
    return {
        "num_tests": 100,
        "events_per_test": 1000,
        "concurrent_users": 50,
        "test_duration_days": 14,
        "expected_throughput": 10000  # events per second
    }