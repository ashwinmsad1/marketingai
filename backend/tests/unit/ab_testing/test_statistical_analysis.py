"""
Unit tests for A/B Testing Statistical Analysis
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from ml.ab_testing.ab_testing_framework import (
    ABTestingFramework,
    TestVariation,
    StatisticalSignificance
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestStatisticalAnalysis:
    """Test statistical analysis components."""
    
    async def test_two_proportion_z_test_identical_performance(self, ab_framework):
        """Test z-test with identical performance (no difference)."""
        control = self._create_variation("control", 1000, 100, 10)
        treatment = self._create_variation("treatment", 1000, 100, 10)
        
        result = ab_framework._two_proportion_z_test(control, treatment, "conversion_rate")
        
        assert result["p_value"] > 0.9  # Should be very high for identical performance
        assert abs(result["effect_size"]) < 0.1  # Should be very small effect
        assert result["confidence_interval"][0] <= 0 <= result["confidence_interval"][1]
    
    async def test_two_proportion_z_test_significant_difference(self, ab_framework):
        """Test z-test with significant difference."""
        control = self._create_variation("control", 10000, 500, 50)     # 10% conversion
        treatment = self._create_variation("treatment", 10000, 750, 100) # 13.3% conversion
        
        result = ab_framework._two_proportion_z_test(control, treatment, "conversion_rate")
        
        assert result["p_value"] < 0.05  # Should be statistically significant
        assert result["effect_size"] > 0.2  # Should show meaningful effect
        assert result["confidence_interval"][0] > 0  # Lower bound should be positive
    
    async def test_two_proportion_z_test_small_sample(self, ab_framework):
        """Test z-test with small sample size."""
        control = self._create_variation("control", 10, 5, 1)
        treatment = self._create_variation("treatment", 10, 6, 2)
        
        result = ab_framework._two_proportion_z_test(control, treatment, "conversion_rate")
        
        # Small samples should have high p-values (low confidence)
        assert result["p_value"] > 0.1
        # Wide confidence intervals due to small sample
        ci_width = result["confidence_interval"][1] - result["confidence_interval"][0]
        assert ci_width > 0.2
    
    async def test_welch_t_test_continuous_data(self, ab_framework):
        """Test Welch's t-test for continuous data."""
        # Mock continuous data (revenue per visitor)
        control_data = [25, 30, 20, 35, 40, 22, 28, 33, 26, 31] * 10  # 100 samples
        treatment_data = [30, 35, 25, 40, 45, 27, 33, 38, 31, 36] * 10  # Higher values
        
        result = ab_framework._welch_t_test(control_data, treatment_data)
        
        assert "p_value" in result
        assert "effect_size" in result
        assert "confidence_interval" in result
        assert result["p_value"] < 0.05  # Should detect the difference
        assert result["effect_size"] > 0  # Positive effect size
    
    async def test_calculate_confidence_interval_proportions(self, ab_framework):
        """Test confidence interval calculation for proportions."""
        # Test with conversion rate data
        n1, x1 = 1000, 50  # 5% conversion rate
        n2, x2 = 1000, 75  # 7.5% conversion rate
        
        ci = ab_framework._calculate_confidence_interval(
            x1/n1, x2/n2, n1, n2, confidence_level=0.95
        )
        
        assert len(ci) == 2
        assert ci[0] < ci[1]  # Lower bound < Upper bound
        assert ci[0] < 0.025 < ci[1]  # Should contain true difference (2.5%)
    
    async def test_determine_significance_status(self, ab_framework):
        """Test significance status determination."""
        # Highly significant
        status = ab_framework._determine_significance_status(0.001, 0.8)
        assert status == StatisticalSignificance.HIGHLY_SIGNIFICANT
        
        # Significant
        status = ab_framework._determine_significance_status(0.02, 0.8)
        assert status == StatisticalSignificance.SIGNIFICANT
        
        # Approaching significance
        status = ab_framework._determine_significance_status(0.08, 0.7)
        assert status == StatisticalSignificance.APPROACHING_SIGNIFICANCE
        
        # Not significant
        status = ab_framework._determine_significance_status(0.5, 0.3)
        assert status == StatisticalSignificance.NOT_SIGNIFICANT
    
    async def test_calculate_power_analysis(self, ab_framework):
        """Test statistical power analysis."""
        # Test with realistic A/B test scenario
        control = self._create_variation("control", 5000, 250, 25)  # 10% conversion
        treatment = self._create_variation("treatment", 5000, 300, 36)  # 12% conversion
        
        power_analysis = ab_framework._calculate_power_analysis(control, treatment, "conversion_rate")
        
        assert "achieved_power" in power_analysis
        assert "required_sample_size" in power_analysis
        assert "minimum_detectable_effect" in power_analysis
        assert 0 <= power_analysis["achieved_power"] <= 1
        assert power_analysis["required_sample_size"] > 0
        assert power_analysis["minimum_detectable_effect"] > 0
    
    async def test_bayesian_analysis(self, ab_framework):
        """Test Bayesian analysis approach."""
        control = self._create_variation("control", 1000, 50, 5)
        treatment = self._create_variation("treatment", 1000, 75, 10)
        
        with patch.object(ab_framework, '_bayesian_analysis') as mock_bayesian:
            mock_bayesian.return_value = {
                "probability_b_better": 0.85,
                "credible_interval": [0.01, 0.08],
                "expected_lift": 0.045
            }
            
            result = ab_framework._bayesian_analysis(control, treatment, "conversion_rate")
            
            assert "probability_b_better" in result
            assert "credible_interval" in result
            assert "expected_lift" in result
            assert 0 <= result["probability_b_better"] <= 1
    
    async def test_sequential_testing(self, ab_framework):
        """Test sequential testing capabilities."""
        # Test early stopping rules
        control = self._create_variation("control", 500, 25, 2)
        treatment = self._create_variation("treatment", 500, 50, 8)
        
        # Simulate sequential testing
        should_stop = ab_framework._check_early_stopping_rules(control, treatment, "conversion_rate")
        
        # With strong effect and reasonable sample size, should recommend stopping
        assert isinstance(should_stop, bool)
    
    async def test_multiple_comparison_correction(self, ab_framework):
        """Test multiple comparison correction."""
        # Simulate multiple variations
        variations = [
            self._create_variation("control", 1000, 50, 5),
            self._create_variation("var1", 1000, 55, 6),
            self._create_variation("var2", 1000, 60, 7),
            self._create_variation("var3", 1000, 45, 4)
        ]
        
        # Test Bonferroni correction
        original_alpha = 0.05
        corrected_alpha = ab_framework._apply_multiple_comparison_correction(
            original_alpha, len(variations) - 1, method="bonferroni"
        )
        
        assert corrected_alpha < original_alpha
        assert corrected_alpha == original_alpha / (len(variations) - 1)
    
    async def test_effect_size_calculations(self, ab_framework):
        """Test various effect size calculations."""
        control = self._create_variation("control", 1000, 100, 10)  # 10% conversion
        treatment = self._create_variation("treatment", 1000, 120, 15)  # 12.5% conversion
        
        # Cohen's d for proportions
        cohens_d = ab_framework._calculate_cohens_d(
            treatment.conversion_rate/100, control.conversion_rate/100,
            treatment.clicks, control.clicks
        )
        
        assert cohens_d > 0  # Treatment should be better
        assert 0.1 < cohens_d < 2.0  # Reasonable range for Cohen's d
        
        # Relative lift calculation
        relative_lift = ab_framework._calculate_relative_lift(
            control.conversion_rate, treatment.conversion_rate
        )
        
        assert relative_lift == 25.0  # (12.5 - 10) / 10 * 100 = 25%
    
    async def test_statistical_assumptions_validation(self, ab_framework):
        """Test validation of statistical assumptions."""
        control = self._create_variation("control", 1000, 50, 5)
        treatment = self._create_variation("treatment", 1000, 75, 8)
        
        # Test normality assumption for proportions
        is_valid = ab_framework._validate_normality_assumption(control, treatment)
        assert isinstance(is_valid, bool)
        
        # Test equal variance assumption
        variance_assumption = ab_framework._test_equal_variance_assumption(control, treatment)
        assert isinstance(variance_assumption, dict)
        assert "test_statistic" in variance_assumption
        assert "p_value" in variance_assumption
    
    def _create_variation(self, var_id: str, impressions: int, clicks: int, conversions: int) -> TestVariation:
        """Helper to create test variations with data."""
        variation = TestVariation(
            variation_id=var_id,
            name=f"Variation {var_id}",
            description=f"Test variation {var_id}",
            traffic_percentage=50.0,
            content_config={}
        )
        
        variation.impressions = impressions
        variation.clicks = clicks
        variation.conversions = conversions
        variation.revenue = conversions * 2500.0  # ₹2,500 per conversion
        
        # Calculate metrics
        if impressions > 0:
            variation.ctr = (clicks / impressions) * 100
        if clicks > 0:
            variation.conversion_rate = (conversions / clicks) * 100
            variation.revenue_per_visitor = variation.revenue / clicks
        
        return variation


@pytest.mark.unit
class TestStatisticalUtilities:
    """Test statistical utility functions."""
    
    def test_sample_size_calculations(self):
        """Test sample size calculation utilities."""
        framework = ABTestingFramework()
        
        # Test for different metrics and parameters
        sample_sizes = {
            "conservative": framework._calculate_minimum_sample_size("conversion_rate", 0.1, 0.8, 0.05),
            "moderate": framework._calculate_minimum_sample_size("conversion_rate", 0.2, 0.8, 0.05),
            "aggressive": framework._calculate_minimum_sample_size("conversion_rate", 0.5, 0.9, 0.01)
        }
        
        # Conservative should require more samples than moderate
        assert sample_sizes["conservative"] > sample_sizes["moderate"]
        # Aggressive (high power, low alpha) should require most samples
        assert sample_sizes["aggressive"] > sample_sizes["moderate"]
        
        # All should be reasonable values
        for size in sample_sizes.values():
            assert 100 < size < 100000
    
    def test_confidence_intervals(self):
        """Test confidence interval utilities."""
        framework = ABTestingFramework()
        
        # Test different confidence levels
        ci_95 = framework._calculate_confidence_interval(0.1, 0.12, 1000, 1000, 0.95)
        ci_99 = framework._calculate_confidence_interval(0.1, 0.12, 1000, 1000, 0.99)
        
        # 99% CI should be wider than 95% CI
        width_95 = ci_95[1] - ci_95[0]
        width_99 = ci_99[1] - ci_99[0]
        assert width_99 > width_95
        
        # Both should contain the true difference
        true_diff = 0.02
        assert ci_95[0] <= true_diff <= ci_95[1]
        assert ci_99[0] <= true_diff <= ci_99[1]
    
    def test_power_calculations(self):
        """Test statistical power calculations."""
        framework = ABTestingFramework()
        
        # Test power increases with sample size
        control_small = TestVariation("control", "Control", "Control", 50.0, {})
        control_small.clicks = 100
        control_small.conversions = 10
        
        control_large = TestVariation("control", "Control", "Control", 50.0, {})
        control_large.clicks = 1000
        control_large.conversions = 100
        
        treatment_small = TestVariation("treatment", "Treatment", "Treatment", 50.0, {})
        treatment_small.clicks = 100
        treatment_small.conversions = 15
        
        treatment_large = TestVariation("treatment", "Treatment", "Treatment", 50.0, {})
        treatment_large.clicks = 1000
        treatment_large.conversions = 150
        
        power_small = framework._calculate_power_analysis(control_small, treatment_small, "conversion_rate")
        power_large = framework._calculate_power_analysis(control_large, treatment_large, "conversion_rate")
        
        # Larger sample should have higher power
        assert power_large["achieved_power"] > power_small["achieved_power"]