"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ml.ab_testing.ab_testing_framework import ABTestingFramework, TestStatus, TestType
from services.personalization_service import EnhancedPersonalizationService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def ab_framework():
    """Create a fresh A/B testing framework for each test."""
    framework = ABTestingFramework()
    yield framework
    # Cleanup
    framework.active_tests.clear()
    framework.test_history.clear()


@pytest.fixture
async def personalization_service():
    """Create personalization service for testing."""
    service = EnhancedPersonalizationService()
    yield service
    # Cleanup
    service.ab_testing_framework.active_tests.clear()
    service.ab_testing_framework.test_history.clear()


@pytest.fixture
def sample_test_config():
    """Sample test configuration for testing."""
    return {
        "test_name": "Sample A/B Test",
        "test_type": "simple_ab",
        "hypothesis": "Variation B will outperform Variation A",
        "primary_metric": "conversion_rate",
        "secondary_metrics": ["ctr", "engagement_rate"],
        "minimum_effect_size": 0.1,
        "duration_days": 14,
        "significance_level": 0.05
    }


@pytest.fixture
def sample_variations():
    """Sample variations for testing."""
    return [
        {
            "variation_id": "control",
            "name": "Control Version",
            "description": "Original version",
            "traffic_percentage": 50.0,
            "content_config": {"headline": "Original Headline", "type": "control"}
        },
        {
            "variation_id": "test",
            "name": "Test Version",
            "description": "New improved version",
            "traffic_percentage": 50.0,
            "content_config": {"headline": "New Improved Headline", "type": "test"}
        }
    ]


@pytest.fixture
def api_test_request():
    """Sample API request for A/B test creation."""
    return {
        "campaign_name": "API Test Campaign",
        "test_type": "content",
        "variant_a": {
            "name": "Control",
            "description": "Control version",
            "content": {"headline": "Original Headline"}
        },
        "variant_b": {
            "name": "Test",
            "description": "Test version",
            "content": {"headline": "New Headline"}
        },
        "traffic_split": 50,
        "sample_size": 1000,
        "confidence_level": 95,
        "duration_days": 14
    }


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    class MockUser:
        def __init__(self):
            self.id = "test_user_123"
            self.email = "test@example.com"
            self.first_name = "Test"
            self.last_name = "User"
    
    return MockUser()


@pytest.fixture
async def active_test(ab_framework, sample_test_config, sample_variations):
    """Create an active test for testing."""
    test = await ab_framework.create_personalized_ab_test(
        "test_user", sample_test_config, sample_variations
    )
    test.status = TestStatus.ACTIVE
    return test


@pytest.fixture
def performance_test_data():
    """Generate performance test data."""
    return {
        "control": {"impressions": 1000, "clicks": 50, "conversions": 5},
        "test": {"impressions": 1000, "clicks": 75, "conversions": 8}
    }


# Test utilities
class TestDataGenerator:
    """Utility class for generating test data."""
    
    @staticmethod
    def create_test_variations(count: int = 2) -> List[Dict[str, Any]]:
        """Create multiple test variations."""
        variations = []
        traffic_split = 100.0 / count
        
        for i in range(count):
            variations.append({
                "variation_id": f"variation_{i}",
                "name": f"Variation {i}",
                "description": f"Test variation {i}",
                "traffic_percentage": traffic_split,
                "content_config": {"headline": f"Headline {i}", "type": f"type_{i}"}
            })
        
        return variations
    
    @staticmethod
    def create_event_sequence(impressions: int, clicks: int, conversions: int) -> List[Dict[str, Any]]:
        """Create a sequence of events for testing."""
        events = []
        
        for i in range(impressions):
            events.append({"type": "impression", "value": 1.0})
        
        for i in range(clicks):
            events.append({"type": "click", "value": 1.0})
        
        for i in range(conversions):
            events.append({"type": "conversion", "value": 100.0})
        
        return events


@pytest.fixture
def test_data_generator():
    """Test data generator fixture."""
    return TestDataGenerator()


# Mark async tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test to run with asyncio"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )