"""
Unit tests for A/B Testing AI Recommendations
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from ml.ab_testing.ab_testing_framework import (
    ABTestingFramework,
    TestVariation,
    PersonalizedTest,
    StatisticalSignificance
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAIRecommendations:
    """Test AI-powered recommendation system."""
    
    async def test_generate_recommendations_with_claude(self, ab_framework):
        """Test recommendation generation with Claude AI."""
        # Mock Claude client
        ab_framework.anthropic_client = Mock()
        ab_framework.anthropic_client.messages = AsyncMock()
        
        mock_response = Mock()
        mock_response.content = [Mock(text="""
        Recommendation: IMPLEMENT WINNER - Test variation shows 25% improvement with high confidence.
        
        Next Steps:
        1. Deploy test variation to 100% of traffic
        2. Monitor performance for 30 days
        3. Document learnings for future campaigns
        4. Plan next optimization test
        """)]
        
        ab_framework.anthropic_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Create test data
        test = self._create_sample_test()
        
        recommendation, next_steps = await ab_framework._generate_recommendations(
            test, "highly_significant", 25.0, "test_variation"
        )
        
        assert "IMPLEMENT WINNER" in recommendation
        assert len(next_steps) == 4
        assert "Deploy test variation" in next_steps[0]
        
        # Verify Claude was called
        ab_framework.anthropic_client.messages.create.assert_called_once()
    
    async def test_generate_recommendations_fallback(self, ab_framework):
        """Test fallback recommendations when Claude is unavailable."""
        # No Claude client configured
        ab_framework.anthropic_client = None
        
        test = self._create_sample_test()
        
        recommendation, next_steps = await ab_framework._generate_recommendations(
            test, "highly_significant", 25.0, "test_variation"
        )
        
        assert "IMPLEMENT WINNER" in recommendation
        assert len(next_steps) >= 3
        assert "Roll out test_variation" in next_steps[0]
    
    async def test_claude_prompt_construction(self, ab_framework):
        """Test Claude prompt construction."""
        ab_framework.anthropic_client = Mock()
        ab_framework.anthropic_client.messages = AsyncMock()
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        ab_framework.anthropic_client.messages.create = AsyncMock(return_value=mock_response)
        
        test = self._create_sample_test()
        test.target_demographics = ["millennial", "urban"]
        test.target_platforms = ["facebook", "instagram"]
        
        await ab_framework._generate_recommendations(test, "significant", 15.0, "test_variation")
        
        # Verify the prompt includes important context
        call_args = ab_framework.anthropic_client.messages.create.call_args[1]
        prompt_content = call_args["messages"][0]["content"]
        
        assert "millennial" in prompt_content
        assert "facebook" in prompt_content
        assert "15.0%" in prompt_content
        assert "significant" in prompt_content
    
    async def test_recommendations_for_different_significance_levels(self, ab_framework):
        """Test recommendations vary by significance level."""
        ab_framework.anthropic_client = None  # Use fallback
        test = self._create_sample_test()
        
        # Highly significant
        rec_high, steps_high = await ab_framework._generate_recommendations(
            test, "highly_significant", 30.0, "test_variation"
        )
        
        # Approaching significance
        rec_approaching, steps_approaching = await ab_framework._generate_recommendations(
            test, "approaching", 10.0, "test_variation"
        )
        
        # Not significant
        rec_not, steps_not = await ab_framework._generate_recommendations(
            test, "not_significant", 2.0, None
        )
        
        assert "IMPLEMENT" in rec_high
        assert "CONTINUE TESTING" in rec_approaching
        assert "NO CLEAR WINNER" in rec_not
        
        # Different next steps
        assert "Roll out" in steps_high[0]
        assert "Extend test duration" in steps_approaching[0]
        assert "End current test" in steps_not[0]
    
    async def test_personalized_recommendations(self, ab_framework):
        """Test personalized recommendations based on user profile."""
        ab_framework.anthropic_client = Mock()
        ab_framework.anthropic_client.messages = AsyncMock()
        
        mock_response = Mock()
        mock_response.content = [Mock(text="""
        Given your e-commerce focus and millennial audience, this result suggests:
        1. Mobile-first design improvements are resonating
        2. Consider A/B testing checkout flow next
        3. Implement across all product categories
        """)]
        ab_framework.anthropic_client.messages.create = AsyncMock(return_value=mock_response)
        
        test = self._create_sample_test()
        test.industry = "e_commerce"
        test.target_demographics = ["millennial"]
        test.business_goals = ["increase_conversions", "improve_mobile_experience"]
        
        recommendation, next_steps = await ab_framework._generate_recommendations(
            test, "significant", 20.0, "mobile_optimized"
        )
        
        # Should include personalized insights
        assert "e-commerce" in recommendation or "Mobile-first" in recommendation
        assert len(next_steps) >= 2
    
    async def test_recommendation_caching(self, ab_framework):
        """Test recommendation caching to avoid redundant API calls."""
        ab_framework.anthropic_client = Mock()
        ab_framework.anthropic_client.messages = AsyncMock()
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Cached recommendation")]
        ab_framework.anthropic_client.messages.create = AsyncMock(return_value=mock_response)
        
        test = self._create_sample_test()
        
        # First call
        rec1, steps1 = await ab_framework._generate_recommendations(
            test, "significant", 15.0, "test_var"
        )
        
        # Second call with same parameters (should be cached if implemented)
        rec2, steps2 = await ab_framework._generate_recommendations(
            test, "significant", 15.0, "test_var"
        )
        
        assert rec1 == rec2
        assert steps1 == steps2
        
        # Should have called Claude at least once
        assert ab_framework.anthropic_client.messages.create.call_count >= 1
    
    async def test_error_handling_in_recommendations(self, ab_framework):
        """Test error handling when Claude API fails."""
        ab_framework.anthropic_client = Mock()
        ab_framework.anthropic_client.messages = AsyncMock()
        ab_framework.anthropic_client.messages.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        test = self._create_sample_test()
        
        # Should fall back to rule-based recommendations
        recommendation, next_steps = await ab_framework._generate_recommendations(
            test, "significant", 20.0, "test_variation"
        )
        
        # Should still provide meaningful recommendations
        assert recommendation is not None
        assert len(next_steps) > 0
        assert "LIKELY WINNER" in recommendation  # Fallback format
    
    async def test_recommendation_context_indian_market(self, ab_framework):
        """Test recommendations include Indian market context."""
        ab_framework.anthropic_client = Mock()
        ab_framework.anthropic_client.messages = AsyncMock()
        
        # Mock response with Indian market context
        mock_response = Mock()
        mock_response.content = [Mock(text="""
        For the Indian market, consider:
        1. UPI payment integration is driving higher conversions
        2. Regional language support may further improve results
        3. Mobile-first approach aligns with Indian user behavior
        4. Price-sensitive messaging tested well
        """)]
        ab_framework.anthropic_client.messages.create = AsyncMock(return_value=mock_response)
        
        test = self._create_sample_test()
        test.target_market = "india"
        test.target_platforms = ["facebook", "instagram"]
        
        recommendation, next_steps = await ab_framework._generate_recommendations(
            test, "significant", 18.0, "localized_version"
        )
        
        # Verify Claude prompt includes Indian market context
        call_args = ab_framework.anthropic_client.messages.create.call_args[1]
        prompt = call_args["messages"][0]["content"]
        
        assert "Indian market" in prompt or "India" in prompt
        assert "UPI" in recommendation
        assert "Regional language" in recommendation or "Mobile-first" in recommendation
    
    async def test_business_impact_calculations(self, ab_framework):
        """Test business impact calculations in recommendations."""
        test = self._create_sample_test()
        
        # Add business context
        test.monthly_traffic = 100000
        test.current_conversion_rate = 0.05
        test.average_order_value = 150.0
        
        # Calculate potential impact
        impact = ab_framework._calculate_business_impact(
            test, lift_percentage=25.0, confidence_level=0.95
        )
        
        assert "monthly_revenue_increase" in impact
        assert "annual_revenue_increase" in impact
        assert "conversion_increase" in impact
        
        # Verify calculations
        expected_monthly = 100000 * 0.05 * 0.25 * 150.0  # traffic * current_rate * lift * aov
        assert abs(impact["monthly_revenue_increase"] - expected_monthly) < 1.0
    
    def _create_sample_test(self) -> PersonalizedTest:
        """Helper to create a sample test for testing."""
        test = PersonalizedTest(
            test_id="test_123",
            user_id="user_456",
            test_name="Sample Test",
            test_type="simple_ab",
            hypothesis="Test will outperform control",
            primary_metric="conversion_rate",
            variations=[
                TestVariation(
                    variation_id="control",
                    name="Control",
                    description="Original version",
                    traffic_percentage=50.0,
                    content_config={"headline": "Original"}
                ),
                TestVariation(
                    variation_id="test_variation",
                    name="Test",
                    description="Improved version",
                    traffic_percentage=50.0,
                    content_config={"headline": "Improved"}
                )
            ]
        )
        
        # Add some performance data
        test.variations[0].impressions = 1000
        test.variations[0].clicks = 50
        test.variations[0].conversions = 5
        test.variations[0].conversion_rate = 10.0
        
        test.variations[1].impressions = 1000
        test.variations[1].clicks = 60
        test.variations[1].conversions = 7
        test.variations[1].conversion_rate = 11.67
        
        return test


@pytest.mark.unit
class TestFallbackRecommendations:
    """Test fallback recommendation system."""
    
    def test_rule_based_recommendations(self):
        """Test rule-based recommendation generation."""
        framework = ABTestingFramework()
        
        # Test different scenarios
        scenarios = [
            ("highly_significant", 30.0, "test_var"),
            ("significant", 15.0, "test_var"),
            ("approaching", 8.0, "test_var"),
            ("not_significant", 2.0, None)
        ]
        
        for significance, lift, winner in scenarios:
            rec, steps = framework._generate_fallback_recommendations(significance, lift, winner)
            
            assert isinstance(rec, str)
            assert isinstance(steps, list)
            assert len(steps) >= 3
            
            if significance == "highly_significant":
                assert "IMPLEMENT" in rec
            elif significance == "not_significant":
                assert "NO CLEAR WINNER" in rec
    
    def test_recommendation_templates(self):
        """Test recommendation template system."""
        framework = ABTestingFramework()
        
        # Test template selection based on context
        templates = framework._get_recommendation_templates()
        
        assert "highly_significant" in templates
        assert "significant" in templates
        assert "approaching" in templates
        assert "not_significant" in templates
        
        # Each template should have recommendation and steps
        for template in templates.values():
            assert isinstance(template[0], str)  # recommendation
            assert isinstance(template[1], list)  # steps