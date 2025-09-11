"""
End-to-end integration tests for A/B Testing Framework
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from ml.ab_testing.ab_testing_framework import ABTestingFramework, TestStatus


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndABTesting:
    """Test complete A/B testing workflow end-to-end."""
    
    async def test_complete_ab_test_lifecycle(self, ab_framework):
        """Test complete A/B test from creation to conclusion."""
        # 1. Create test
        test_config = {
            "test_name": "E2E Lifecycle Test",
            "test_type": "simple_ab",
            "hypothesis": "New design will increase conversions",
            "primary_metric": "conversion_rate",
            "duration_days": 14
        }
        
        variations = [
            {
                "variation_id": "control",
                "name": "Current Design",
                "description": "Current website design",
                "traffic_percentage": 50.0,
                "content_config": {"design": "current", "color": "blue"}
            },
            {
                "variation_id": "new_design",
                "name": "New Design",
                "description": "New improved website design",
                "traffic_percentage": 50.0,
                "content_config": {"design": "new", "color": "green"}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test("e2e_user", test_config, variations)
        
        assert test.status == TestStatus.DRAFT
        assert len(test.variations) == 2
        
        # 2. Start test
        test.status = TestStatus.ACTIVE
        assert test.status == TestStatus.ACTIVE
        
        # 3. Record realistic events over time
        # Week 1: Light traffic
        await self._simulate_traffic(ab_framework, test.test_id, {
            "control": {"impressions": 500, "clicks": 25, "conversions": 2},
            "new_design": {"impressions": 500, "clicks": 30, "conversions": 4}
        })
        
        # Check metrics after week 1
        control_var = next(v for v in test.variations if v.variation_id == "control")
        new_var = next(v for v in test.variations if v.variation_id == "new_design")
        
        assert control_var.impressions == 500
        assert control_var.clicks == 25
        assert control_var.conversions == 2
        assert control_var.ctr == 5.0  # 25/500 * 100
        
        assert new_var.conversions == 4
        assert new_var.conversion_rate > control_var.conversion_rate
        
        # 4. Continue test - Week 2: More traffic
        await self._simulate_traffic(ab_framework, test.test_id, {
            "control": {"impressions": 1000, "clicks": 50, "conversions": 5},
            "new_design": {"impressions": 1000, "clicks": 70, "conversions": 10}
        })
        
        # 5. Evaluate results
        await ab_framework._evaluate_test_results(test)
        
        assert test.current_result is not None
        assert test.current_result.winning_variation_id == "new_design"
        assert test.current_result.projected_lift > 0
        
        # 6. Conclude test
        success = await ab_framework.conclude_test(test.test_id, "e2e_test_completed")
        
        assert success is True
        assert test.status == TestStatus.COMPLETED
        assert test.test_id not in ab_framework.active_tests
        assert len(ab_framework.test_history) == 1
    
    async def test_multivariate_test_integration(self, ab_framework):
        """Test multivariate A/B testing integration."""
        test_config = {
            "test_name": "Multivariate Test",
            "test_type": "multivariate",
            "hypothesis": "Different combinations will perform differently",
            "primary_metric": "conversion_rate"
        }
        
        # Test 3 variations
        variations = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Original",
                "traffic_percentage": 33.33,
                "content_config": {"headline": "Original", "cta": "Buy Now"}
            },
            {
                "variation_id": "headline_test",
                "name": "New Headline",
                "description": "New headline only",
                "traffic_percentage": 33.33,
                "content_config": {"headline": "Improved", "cta": "Buy Now"}
            },
            {
                "variation_id": "cta_test",
                "name": "New CTA",
                "description": "New CTA only",
                "traffic_percentage": 33.34,
                "content_config": {"headline": "Original", "cta": "Shop Now"}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test("mv_user", test_config, variations)
        test.status = TestStatus.ACTIVE
        
        # Simulate different performance for each variation
        performance_data = {
            "control": {"impressions": 1000, "clicks": 50, "conversions": 5},
            "headline_test": {"impressions": 1000, "clicks": 60, "conversions": 8},
            "cta_test": {"impressions": 1000, "clicks": 55, "conversions": 6}
        }
        
        await self._simulate_traffic(ab_framework, test.test_id, performance_data)
        await ab_framework._evaluate_test_results(test)
        
        assert test.current_result.winning_variation_id == "headline_test"
        assert len(test.variations) == 3
    
    async def test_concurrent_tests_isolation(self, ab_framework):
        """Test that concurrent tests don't interfere with each other."""
        # Create multiple concurrent tests
        tests = []
        for i in range(3):
            test_config = {
                "test_name": f"Concurrent Test {i+1}",
                "test_type": "simple_ab",
                "hypothesis": f"Test {i+1} hypothesis",
                "primary_metric": "conversion_rate"
            }
            
            variations = [
                {
                    "variation_id": f"control_{i}",
                    "name": f"Control {i}",
                    "description": f"Control for test {i}",
                    "traffic_percentage": 50.0,
                    "content_config": {"test_id": i, "type": "control"}
                },
                {
                    "variation_id": f"test_{i}",
                    "name": f"Test {i}",
                    "description": f"Test variation for test {i}",
                    "traffic_percentage": 50.0,
                    "content_config": {"test_id": i, "type": "test"}
                }
            ]
            
            test = await ab_framework.create_personalized_ab_test(f"user_{i}", test_config, variations)
            test.status = TestStatus.ACTIVE
            tests.append(test)
        
        # Record events for all tests concurrently
        for i, test in enumerate(tests):
            await self._simulate_traffic(ab_framework, test.test_id, {
                f"control_{i}": {"impressions": 100 * (i + 1), "clicks": 10 * (i + 1), "conversions": i + 1},
                f"test_{i}": {"impressions": 100 * (i + 1), "clicks": 12 * (i + 1), "conversions": i + 2}
            })
        
        # Verify each test has correct data
        for i, test in enumerate(tests):
            control_var = next(v for v in test.variations if v.variation_id == f"control_{i}")
            test_var = next(v for v in test.variations if v.variation_id == f"test_{i}")
            
            assert control_var.impressions == 100 * (i + 1)
            assert control_var.conversions == i + 1
            assert test_var.impressions == 100 * (i + 1)
            assert test_var.conversions == i + 2
        
        # Conclude all tests
        for test in tests:
            await ab_framework.conclude_test(test.test_id, "concurrent_test_completed")
        
        assert len(ab_framework.active_tests) == 0
        assert len(ab_framework.test_history) == 3
    
    async def test_test_insights_generation(self, ab_framework):
        """Test comprehensive test insights generation."""
        # Create multiple tests with different outcomes
        test_configs = [
            {
                "name": "Successful Test",
                "performance": {"control": (1000, 50, 5), "test": (1000, 75, 10)},
                "expected_winner": "test"
            },
            {
                "name": "Failed Test",
                "performance": {"control": (1000, 60, 8), "test": (1000, 45, 4)},
                "expected_winner": "control"
            },
            {
                "name": "Inconclusive Test",
                "performance": {"control": (500, 25, 2), "test": (500, 26, 2)},
                "expected_winner": None
            }
        ]
        
        user_id = "insights_user"
        
        for i, config in enumerate(test_configs):
            test_config = {
                "test_name": config["name"],
                "test_type": "simple_ab",
                "hypothesis": f"Hypothesis for {config['name']}",
                "primary_metric": "conversion_rate"
            }
            
            variations = [
                {
                    "variation_id": "control",
                    "name": "Control",
                    "description": "Control version",
                    "traffic_percentage": 50.0,
                    "content_config": {"type": "control"}
                },
                {
                    "variation_id": "test",
                    "name": "Test",
                    "description": "Test version",
                    "traffic_percentage": 50.0,
                    "content_config": {"type": "test"}
                }
            ]
            
            test = await ab_framework.create_personalized_ab_test(user_id, test_config, variations)
            test.status = TestStatus.ACTIVE
            
            # Add performance data
            control_data = config["performance"]["control"]
            test_data = config["performance"]["test"]
            
            await self._simulate_traffic(ab_framework, test.test_id, {
                "control": {"impressions": control_data[0], "clicks": control_data[1], "conversions": control_data[2]},
                "test": {"impressions": test_data[0], "clicks": test_data[1], "conversions": test_data[2]}
            })
            
            await ab_framework._evaluate_test_results(test)
            await ab_framework.conclude_test(test.test_id, f"insights_test_{i}_completed")
        
        # Generate comprehensive insights
        insights = await ab_framework.get_test_insights(user_id)
        
        assert insights["user_id"] == user_id
        assert insights["testing_summary"]["total_tests"] == 3
        assert insights["testing_summary"]["completed_tests"] == 3
        assert len(insights["recent_results"]) == 3
        
        # Check that insights include performance patterns
        assert "performance_trends" in insights
        
        # Verify specific test outcomes are captured
        successful_tests = [t for t in insights["recent_results"] if t["winner"] == "test"]
        failed_tests = [t for t in insights["recent_results"] if t["winner"] == "control"]
        inconclusive_tests = [t for t in insights["recent_results"] if t["winner"] is None]
        
        assert len(successful_tests) >= 1
        assert len(failed_tests) >= 1
        assert len(inconclusive_tests) >= 1
    
    async def test_error_recovery_and_resilience(self, ab_framework):
        """Test error recovery and system resilience."""
        # Create test
        test_config = {
            "test_name": "Resilience Test",
            "test_type": "simple_ab",
            "hypothesis": "System should handle errors gracefully",
            "primary_metric": "conversion_rate"
        }
        
        variations = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Control version",
                "traffic_percentage": 50.0,
                "content_config": {"type": "control"}
            },
            {
                "variation_id": "test",
                "name": "Test",
                "description": "Test version",
                "traffic_percentage": 50.0,
                "content_config": {"type": "test"}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test("resilience_user", test_config, variations)
        test.status = TestStatus.ACTIVE
        
        # Test various error conditions
        error_scenarios = [
            # Invalid test ID
            ("invalid_test_id", "control", "impression", False),
            # Invalid variation ID
            (test.test_id, "invalid_variation", "impression", False),
            # Valid event
            (test.test_id, "control", "impression", True),
            # Another valid event
            (test.test_id, "test", "conversion", True),
        ]
        
        for test_id, variation_id, event_type, expected_success in error_scenarios:
            result = await ab_framework.record_test_event(test_id, variation_id, event_type, value=100.0)
            assert result == expected_success
        
        # Verify valid events were recorded
        control_var = next(v for v in test.variations if v.variation_id == "control")
        test_var = next(v for v in test.variations if v.variation_id == "test")
        
        assert control_var.impressions == 1
        assert test_var.conversions == 1
        
        # Test should still be functional
        await ab_framework._evaluate_test_results(test)
        success = await ab_framework.conclude_test(test.test_id, "resilience_test_completed")
        assert success is True
    
    async def _simulate_traffic(self, framework: ABTestingFramework, test_id: str, traffic_data: dict):
        """Helper to simulate realistic traffic patterns."""
        for variation_id, data in traffic_data.items():
            # Record impressions
            for _ in range(data["impressions"]):
                await framework.record_test_event(test_id, variation_id, "impression")
            
            # Record clicks
            for _ in range(data["clicks"]):
                await framework.record_test_event(test_id, variation_id, "click")
            
            # Record conversions with value
            for _ in range(data["conversions"]):
                await framework.record_test_event(test_id, variation_id, "conversion", value=100.0)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPersonalizationServiceIntegration:
    """Test integration with personalization service."""
    
    async def test_personalization_service_ab_testing(self, personalization_service):
        """Test A/B testing through personalization service."""
        # Access A/B testing framework through service
        ab_framework = personalization_service.ab_testing_framework
        
        assert ab_framework is not None
        assert hasattr(ab_framework, 'create_personalized_ab_test')
        assert hasattr(ab_framework, 'record_test_event')
        
        # Create test through service
        test_config = {
            "test_name": "Service Integration Test",
            "test_type": "simple_ab",
            "hypothesis": "Service integration works",
            "primary_metric": "conversion_rate"
        }
        
        variations = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Control version",
                "traffic_percentage": 50.0,
                "content_config": {"source": "service"}
            },
            {
                "variation_id": "test",
                "name": "Test",
                "description": "Test version",
                "traffic_percentage": 50.0,
                "content_config": {"source": "service"}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test("service_user", test_config, variations)
        
        assert test.test_id in ab_framework.active_tests
        assert test.variations[0].content_config["source"] == "service"
    
    async def test_service_level_insights(self, personalization_service):
        """Test service-level insights integration."""
        ab_framework = personalization_service.ab_testing_framework
        user_id = "service_insights_user"
        
        # Create and complete a test
        test_config = {
            "test_name": "Service Insights Test",
            "test_type": "simple_ab",
            "hypothesis": "Service insights work",
            "primary_metric": "conversion_rate"
        }
        
        variations = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Control",
                "traffic_percentage": 50.0,
                "content_config": {}
            },
            {
                "variation_id": "test",
                "name": "Test",
                "description": "Test",
                "traffic_percentage": 50.0,
                "content_config": {}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test(user_id, test_config, variations)
        await ab_framework.conclude_test(test.test_id, "service_insights_completed")
        
        # Get insights through framework
        insights = await ab_framework.get_test_insights(user_id)
        
        assert insights["user_id"] == user_id
        assert insights["testing_summary"]["completed_tests"] == 1