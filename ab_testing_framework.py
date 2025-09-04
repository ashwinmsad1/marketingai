"""
A/B Testing Framework for Personalized Marketing Optimization
Manages sophisticated A/B tests with statistical significance and user-specific insights
"""

import asyncio
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TestType(Enum):
    SIMPLE_AB = "simple_ab"          # A vs B
    MULTIVARIATE = "multivariate"    # Multiple variables
    SPLIT_URL = "split_url"          # Different landing pages
    CONTENT_VARIATION = "content_variation"  # Different content versions

class StatisticalSignificance(Enum):
    NOT_SIGNIFICANT = "not_significant"
    APPROACHING = "approaching"      # 85-94% confidence
    SIGNIFICANT = "significant"      # 95%+ confidence
    HIGHLY_SIGNIFICANT = "highly_significant"  # 99%+ confidence

@dataclass
class TestVariation:
    """Individual test variation configuration"""
    variation_id: str
    name: str
    description: str
    
    # Traffic allocation
    traffic_percentage: float
    
    # Content specifications
    content_config: Dict[str, Any]
    
    # Performance tracking
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    
    # Calculated metrics
    ctr: float = 0.0
    conversion_rate: float = 0.0
    revenue_per_visitor: float = 0.0
    
    # Statistical data
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    statistical_power: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TestResult:
    """A/B test statistical results"""
    test_id: str
    
    # Overall test metrics
    total_impressions: int
    total_conversions: int
    test_duration_days: int
    
    # Winner determination
    winning_variation_id: Optional[str]
    confidence_level: float
    significance_status: StatisticalSignificance
    
    # Statistical analysis
    p_value: float
    effect_size: float
    power_analysis: Dict[str, float]
    
    # Business impact
    projected_lift: float
    estimated_revenue_impact: float
    
    # Recommendations
    recommendation: str
    next_steps: List[str]
    
    calculated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PersonalizedTest:
    """Complete A/B test configuration for personalized marketing"""
    test_id: str
    user_id: str
    
    # Test configuration
    test_name: str
    test_type: TestType
    hypothesis: str
    
    # Target metrics
    primary_metric: str
    secondary_metrics: List[str]
    
    # Test variations
    variations: List[TestVariation]
    control_variation_id: str
    
    # Test parameters
    traffic_allocation: Dict[str, float]  # variation_id -> percentage
    minimum_sample_size: int
    minimum_effect_size: float  # Minimum detectable effect
    desired_power: float = 0.80  # Statistical power
    significance_level: float = 0.05  # Alpha level
    
    # Test timeline
    start_date: datetime
    planned_end_date: datetime
    actual_end_date: Optional[datetime] = None
    
    # Status and results
    status: TestStatus = TestStatus.DRAFT
    current_result: Optional[TestResult] = None
    
    # Personalization context
    target_demographics: List[str] = field(default_factory=list)
    target_platforms: List[str] = field(default_factory=list)
    personalization_factors: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class ABTestingFramework:
    """
    Comprehensive A/B testing framework with statistical rigor and personalization
    """
    
    def __init__(self):
        """Initialize A/B testing framework"""
        self.active_tests: Dict[str, PersonalizedTest] = {}
        self.test_history: List[PersonalizedTest] = []
        self.statistical_models = self._initialize_statistical_models()
        self.significance_thresholds = {
            "approaching": 0.90,
            "significant": 0.95,
            "highly_significant": 0.99
        }
    
    def _initialize_statistical_models(self) -> Dict[str, Any]:
        """Initialize statistical analysis models"""
        return {
            "minimum_sample_sizes": {
                "conversion_rate": 1000,  # Minimum conversions for statistical power
                "ctr": 500,
                "engagement_rate": 750,
                "revenue": 200
            },
            "effect_size_benchmarks": {
                "small": 0.2,
                "medium": 0.5, 
                "large": 0.8
            },
            "test_duration_limits": {
                "minimum_days": 7,
                "maximum_days": 60,
                "recommended_days": 14
            }
        }
    
    async def create_personalized_ab_test(
        self,
        user_id: str,
        test_config: Dict[str, Any],
        variations: List[Dict[str, Any]]
    ) -> PersonalizedTest:
        """
        Create a new personalized A/B test
        
        Args:
            user_id: User identifier
            test_config: Test configuration
            variations: List of test variations
            
        Returns:
            PersonalizedTest object
        """
        try:
            test_id = str(uuid.uuid4())
            
            # Create test variations
            test_variations = []
            total_traffic = 0.0
            
            for i, var_config in enumerate(variations):
                variation = TestVariation(
                    variation_id=var_config.get("variation_id", f"variation_{i}"),
                    name=var_config.get("name", f"Variation {i+1}"),
                    description=var_config.get("description", ""),
                    traffic_percentage=var_config.get("traffic_percentage", 100.0 / len(variations)),
                    content_config=var_config.get("content_config", {})
                )
                test_variations.append(variation)
                total_traffic += variation.traffic_percentage
            
            # Validate traffic allocation
            if abs(total_traffic - 100.0) > 0.01:
                raise ValueError(f"Traffic allocation must sum to 100%, got {total_traffic}%")
            
            # Calculate minimum sample size
            primary_metric = test_config.get("primary_metric", "conversion_rate")
            min_sample_size = self._calculate_minimum_sample_size(
                metric=primary_metric,
                effect_size=test_config.get("minimum_effect_size", 0.2),
                power=test_config.get("desired_power", 0.80),
                alpha=test_config.get("significance_level", 0.05)
            )
            
            # Create test object
            test = PersonalizedTest(
                test_id=test_id,
                user_id=user_id,
                test_name=test_config.get("test_name", f"A/B Test {test_id[:8]}"),
                test_type=TestType(test_config.get("test_type", "simple_ab")),
                hypothesis=test_config.get("hypothesis", "Variation will outperform control"),
                primary_metric=primary_metric,
                secondary_metrics=test_config.get("secondary_metrics", []),
                variations=test_variations,
                control_variation_id=test_variations[0].variation_id,  # First variation as control
                traffic_allocation={v.variation_id: v.traffic_percentage for v in test_variations},
                minimum_sample_size=min_sample_size,
                minimum_effect_size=test_config.get("minimum_effect_size", 0.2),
                desired_power=test_config.get("desired_power", 0.80),
                significance_level=test_config.get("significance_level", 0.05),
                start_date=datetime.now(),
                planned_end_date=datetime.now() + timedelta(
                    days=test_config.get("duration_days", 14)
                ),
                target_demographics=test_config.get("target_demographics", []),
                target_platforms=test_config.get("target_platforms", []),
                personalization_factors=test_config.get("personalization_factors", [])
            )
            
            # Store test
            self.active_tests[test_id] = test
            
            logger.info(f"Created personalized A/B test {test_id} for user {user_id}")
            return test
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            raise
    
    def _calculate_minimum_sample_size(
        self,
        metric: str,
        effect_size: float,
        power: float = 0.80,
        alpha: float = 0.05
    ) -> int:
        """
        Calculate minimum sample size for statistical significance
        
        Args:
            metric: Primary metric being tested
            effect_size: Minimum detectable effect size
            power: Statistical power (1 - β)
            alpha: Significance level (Type I error rate)
            
        Returns:
            Minimum sample size per variation
        """
        # Z-scores for two-tailed test
        z_alpha = 1.96  # For α = 0.05
        z_beta = 0.84   # For β = 0.20 (power = 0.80)
        
        if power == 0.90:
            z_beta = 1.28
        elif power == 0.95:
            z_beta = 1.64
        
        # Base sample size calculation (for proportions)
        if metric in ["conversion_rate", "ctr"]:
            # Assume baseline conversion rate based on industry benchmarks
            p1 = 0.05  # 5% baseline conversion rate
            p2 = p1 * (1 + effect_size)  # Expected improvement
            
            p_pooled = (p1 + p2) / 2
            
            numerator = (z_alpha + z_beta) ** 2 * 2 * p_pooled * (1 - p_pooled)
            denominator = (p2 - p1) ** 2
            
            sample_size = math.ceil(numerator / denominator)
        else:
            # For continuous metrics (revenue, engagement)
            # Using Cohen's d effect size
            sample_size = math.ceil(
                2 * ((z_alpha + z_beta) / effect_size) ** 2
            )
        
        # Apply minimum thresholds
        min_threshold = self.statistical_models["minimum_sample_sizes"].get(metric, 1000)
        return max(sample_size, min_threshold)
    
    async def record_test_event(
        self,
        test_id: str,
        variation_id: str,
        event_type: str,
        value: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a test event (impression, click, conversion)
        
        Args:
            test_id: Test identifier
            variation_id: Variation that received the event
            event_type: Type of event (impression, click, conversion)
            value: Event value (for revenue events)
            metadata: Additional event data
            
        Returns:
            Success status
        """
        try:
            test = self.active_tests.get(test_id)
            if not test:
                logger.warning(f"Test {test_id} not found")
                return False
            
            if test.status != TestStatus.ACTIVE:
                logger.warning(f"Test {test_id} is not active (status: {test.status.value})")
                return False
            
            # Find the variation
            variation = None
            for var in test.variations:
                if var.variation_id == variation_id:
                    variation = var
                    break
            
            if not variation:
                logger.warning(f"Variation {variation_id} not found in test {test_id}")
                return False
            
            # Record the event
            if event_type == "impression":
                variation.impressions += 1
            elif event_type == "click":
                variation.clicks += 1
            elif event_type == "conversion":
                variation.conversions += 1
                if value > 0:
                    variation.revenue += value
            
            # Update calculated metrics
            self._update_variation_metrics(variation)
            
            # Check if test should be evaluated
            if self._should_evaluate_test(test):
                await self._evaluate_test_results(test)
            
            test.updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording test event: {e}")
            return False
    
    def _update_variation_metrics(self, variation: TestVariation) -> None:
        """Update calculated metrics for a variation"""
        
        if variation.impressions > 0:
            variation.ctr = (variation.clicks / variation.impressions) * 100
            
        if variation.clicks > 0:
            variation.conversion_rate = (variation.conversions / variation.clicks) * 100
            variation.revenue_per_visitor = variation.revenue / variation.clicks
        elif variation.impressions > 0:
            variation.conversion_rate = (variation.conversions / variation.impressions) * 100
            variation.revenue_per_visitor = variation.revenue / variation.impressions
    
    def _should_evaluate_test(self, test: PersonalizedTest) -> bool:
        """Determine if test should be evaluated for statistical significance"""
        
        # Check if test has been running for minimum duration
        if (datetime.now() - test.start_date).days < self.statistical_models["test_duration_limits"]["minimum_days"]:
            return False
        
        # Check if minimum sample size is reached
        total_conversions = sum(var.conversions for var in test.variations)
        if total_conversions < test.minimum_sample_size:
            return False
        
        # Evaluate every few hours once criteria are met
        return True
    
    async def _evaluate_test_results(self, test: PersonalizedTest) -> TestResult:
        """
        Perform statistical analysis of test results
        
        Args:
            test: PersonalizedTest object
            
        Returns:
            TestResult with statistical analysis
        """
        try:
            control_variation = next(
                var for var in test.variations 
                if var.variation_id == test.control_variation_id
            )
            
            # Calculate statistical significance for each variation vs control
            results_analysis = {}
            best_variation = control_variation
            best_metric_value = getattr(control_variation, test.primary_metric.replace("_rate", ""))
            
            for variation in test.variations:
                if variation.variation_id == test.control_variation_id:
                    continue
                
                # Perform statistical test
                stat_result = self._perform_statistical_test(
                    control_variation, variation, test.primary_metric
                )
                
                results_analysis[variation.variation_id] = stat_result
                
                # Check if this variation is performing better
                current_metric = getattr(variation, test.primary_metric.replace("_rate", ""))
                if current_metric > best_metric_value:
                    best_variation = variation
                    best_metric_value = current_metric
            
            # Determine overall test result
            winner_id = None
            confidence_level = 0.0
            significance_status = StatisticalSignificance.NOT_SIGNIFICANT
            
            if best_variation.variation_id != control_variation.variation_id:
                best_result = results_analysis[best_variation.variation_id]
                confidence_level = 1.0 - best_result["p_value"]
                
                if confidence_level >= self.significance_thresholds["highly_significant"]:
                    significance_status = StatisticalSignificance.HIGHLY_SIGNIFICANT
                    winner_id = best_variation.variation_id
                elif confidence_level >= self.significance_thresholds["significant"]:
                    significance_status = StatisticalSignificance.SIGNIFICANT
                    winner_id = best_variation.variation_id
                elif confidence_level >= self.significance_thresholds["approaching"]:
                    significance_status = StatisticalSignificance.APPROACHING
            
            # Calculate business impact
            if winner_id:
                control_metric = getattr(control_variation, test.primary_metric)
                winner_metric = getattr(best_variation, test.primary_metric)
                projected_lift = ((winner_metric - control_metric) / control_metric) * 100
                
                # Estimate revenue impact
                total_impressions = sum(var.impressions for var in test.variations)
                estimated_revenue_impact = (
                    projected_lift / 100 * 
                    sum(var.revenue for var in test.variations) * 
                    (365 / max((datetime.now() - test.start_date).days, 1))
                )
            else:
                projected_lift = 0.0
                estimated_revenue_impact = 0.0
            
            # Generate recommendations
            recommendation, next_steps = self._generate_recommendations(
                test, significance_status, projected_lift, winner_id
            )
            
            # Create test result
            test_result = TestResult(
                test_id=test.test_id,
                total_impressions=sum(var.impressions for var in test.variations),
                total_conversions=sum(var.conversions for var in test.variations),
                test_duration_days=(datetime.now() - test.start_date).days,
                winning_variation_id=winner_id,
                confidence_level=confidence_level,
                significance_status=significance_status,
                p_value=results_analysis.get(winner_id, {}).get("p_value", 1.0) if winner_id else 1.0,
                effect_size=results_analysis.get(winner_id, {}).get("effect_size", 0.0) if winner_id else 0.0,
                power_analysis=self._calculate_power_analysis(test),
                projected_lift=projected_lift,
                estimated_revenue_impact=estimated_revenue_impact,
                recommendation=recommendation,
                next_steps=next_steps
            )
            
            test.current_result = test_result
            
            # Auto-conclude test if highly significant
            if significance_status == StatisticalSignificance.HIGHLY_SIGNIFICANT:
                await self._conclude_test(test.test_id)
            
            logger.info(f"Evaluated test {test.test_id}: {significance_status.value} with {confidence_level:.2%} confidence")
            return test_result
            
        except Exception as e:
            logger.error(f"Error evaluating test results: {e}")
            raise
    
    def _perform_statistical_test(
        self,
        control: TestVariation,
        treatment: TestVariation,
        metric: str
    ) -> Dict[str, float]:
        """
        Perform statistical test between control and treatment
        
        Returns:
            Dictionary with p_value, effect_size, and confidence intervals
        """
        if metric in ["conversion_rate", "ctr"]:
            # Two-proportion z-test
            return self._two_proportion_z_test(control, treatment, metric)
        else:
            # Two-sample t-test for continuous metrics
            return self._two_sample_t_test(control, treatment, metric)
    
    def _two_proportion_z_test(
        self,
        control: TestVariation,
        treatment: TestVariation,
        metric: str
    ) -> Dict[str, float]:
        """Perform two-proportion z-test"""
        
        # Get counts based on metric
        if metric == "conversion_rate":
            n1, x1 = control.clicks, control.conversions
            n2, x2 = treatment.clicks, treatment.conversions
        else:  # ctr
            n1, x1 = control.impressions, control.clicks
            n2, x2 = treatment.impressions, treatment.clicks
        
        if n1 == 0 or n2 == 0:
            return {"p_value": 1.0, "effect_size": 0.0, "confidence_interval": (0.0, 0.0)}
        
        p1 = x1 / n1
        p2 = x2 / n2
        
        # Pooled proportion
        p_pool = (x1 + x2) / (n1 + n2)
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return {"p_value": 1.0, "effect_size": 0.0, "confidence_interval": (0.0, 0.0)}
        
        # Z-score
        z_score = (p2 - p1) / se
        
        # P-value (two-tailed)
        p_value = 2 * (1 - self._standard_normal_cdf(abs(z_score)))
        
        # Effect size (Cohen's h)
        effect_size = 2 * (math.asin(math.sqrt(p2)) - math.asin(math.sqrt(p1)))
        
        # Confidence interval for difference
        se_diff = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        margin = 1.96 * se_diff
        ci_lower = (p2 - p1) - margin
        ci_upper = (p2 - p1) + margin
        
        return {
            "p_value": p_value,
            "effect_size": abs(effect_size),
            "confidence_interval": (ci_lower, ci_upper),
            "z_score": z_score
        }
    
    def _two_sample_t_test(
        self,
        control: TestVariation,
        treatment: TestVariation,
        metric: str
    ) -> Dict[str, float]:
        """Perform two-sample t-test for continuous metrics"""
        
        # For continuous metrics, we'd need individual data points
        # For now, using approximation based on summary statistics
        
        control_mean = getattr(control, metric, 0)
        treatment_mean = getattr(treatment, metric, 0)
        
        # Approximate standard deviations (this would be better with raw data)
        control_std = control_mean * 0.5  # Rough approximation
        treatment_std = treatment_mean * 0.5
        
        n1 = control.conversions if control.conversions > 0 else control.clicks
        n2 = treatment.conversions if treatment.conversions > 0 else treatment.clicks
        
        if n1 <= 1 or n2 <= 1:
            return {"p_value": 1.0, "effect_size": 0.0, "confidence_interval": (0.0, 0.0)}
        
        # Pooled standard deviation
        sp = math.sqrt(((n1 - 1) * control_std**2 + (n2 - 1) * treatment_std**2) / (n1 + n2 - 2))
        
        if sp == 0:
            return {"p_value": 1.0, "effect_size": 0.0, "confidence_interval": (0.0, 0.0)}
        
        # T-statistic
        t_stat = (treatment_mean - control_mean) / (sp * math.sqrt(1/n1 + 1/n2))
        
        # Approximate p-value (this would use t-distribution in practice)
        p_value = 2 * (1 - self._standard_normal_cdf(abs(t_stat)))
        
        # Effect size (Cohen's d)
        effect_size = abs((treatment_mean - control_mean) / sp)
        
        return {
            "p_value": p_value,
            "effect_size": effect_size,
            "confidence_interval": (0.0, 0.0),  # Would calculate properly with t-distribution
            "t_statistic": t_stat
        }
    
    def _standard_normal_cdf(self, x: float) -> float:
        """Approximate standard normal CDF"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _calculate_power_analysis(self, test: PersonalizedTest) -> Dict[str, float]:
        """Calculate statistical power analysis"""
        
        total_sample = sum(var.conversions for var in test.variations)
        achieved_power = min(0.95, total_sample / test.minimum_sample_size)
        
        return {
            "achieved_power": achieved_power,
            "required_sample_size": test.minimum_sample_size,
            "actual_sample_size": total_sample,
            "days_to_significance": max(0, test.minimum_sample_size - total_sample) / 
                                   max(1, total_sample / max(1, (datetime.now() - test.start_date).days))
        }
    
    def _generate_recommendations(
        self,
        test: PersonalizedTest,
        significance: StatisticalSignificance,
        lift: float,
        winner_id: Optional[str]
    ) -> Tuple[str, List[str]]:
        """Generate recommendations based on test results"""
        
        if significance == StatisticalSignificance.HIGHLY_SIGNIFICANT:
            recommendation = f"IMPLEMENT WINNER: {winner_id} shows {lift:.1f}% improvement with high confidence"
            next_steps = [
                f"Roll out {winner_id} to 100% of traffic",
                "Monitor performance for 30 days",
                "Plan next optimization test",
                "Document learnings for future campaigns"
            ]
        elif significance == StatisticalSignificance.SIGNIFICANT:
            recommendation = f"LIKELY WINNER: {winner_id} shows {lift:.1f}% improvement with good confidence"
            next_steps = [
                f"Consider implementing {winner_id}",
                "Run confirmation test with larger sample",
                "Monitor closely for 14 days",
                "Prepare rollback plan if performance drops"
            ]
        elif significance == StatisticalSignificance.APPROACHING:
            recommendation = "CONTINUE TESTING: Results are promising but not yet conclusive"
            next_steps = [
                "Extend test duration by 7-14 days",
                "Ensure sufficient traffic allocation",
                "Monitor for external factors affecting results",
                "Consider increasing traffic to test variations"
            ]
        else:
            recommendation = "NO CLEAR WINNER: Variations performing similarly to control"
            next_steps = [
                "End current test",
                "Analyze test learnings and hypotheses",
                "Design new test with more significant variations",
                "Consider testing different elements or audience segments"
            ]
        
        return recommendation, next_steps
    
    async def conclude_test(self, test_id: str, reason: str = "completed") -> bool:
        """
        Conclude an A/B test
        
        Args:
            test_id: Test identifier
            reason: Reason for conclusion
            
        Returns:
            Success status
        """
        try:
            return await self._conclude_test(test_id, reason)
        except Exception as e:
            logger.error(f"Error concluding test: {e}")
            return False
    
    async def _conclude_test(self, test_id: str, reason: str = "completed") -> bool:
        """Internal method to conclude test"""
        
        test = self.active_tests.get(test_id)
        if not test:
            return False
        
        # Perform final analysis
        if not test.current_result:
            await self._evaluate_test_results(test)
        
        # Update test status
        test.status = TestStatus.COMPLETED
        test.actual_end_date = datetime.now()
        test.updated_at = datetime.now()
        
        # Move to history
        self.test_history.append(test)
        del self.active_tests[test_id]
        
        logger.info(f"Concluded test {test_id}: {reason}")
        return True
    
    async def get_test_insights(self, user_id: str, test_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get insights from A/B tests for a user
        
        Args:
            user_id: User identifier  
            test_id: Specific test ID (optional)
            
        Returns:
            Test insights and recommendations
        """
        try:
            if test_id:
                # Get specific test insights
                test = self.active_tests.get(test_id) or next(
                    (t for t in self.test_history if t.test_id == test_id), None
                )
                
                if not test or test.user_id != user_id:
                    return {"error": "Test not found"}
                
                return {
                    "test_id": test_id,
                    "test_name": test.test_name,
                    "status": test.status.value,
                    "current_result": test.current_result.__dict__ if test.current_result else None,
                    "variations_performance": [
                        {
                            "variation_id": var.variation_id,
                            "name": var.name,
                            "impressions": var.impressions,
                            "conversions": var.conversions,
                            "ctr": var.ctr,
                            "conversion_rate": var.conversion_rate
                        }
                        for var in test.variations
                    ]
                }
            else:
                # Get user's testing overview
                user_tests = [t for t in self.active_tests.values() if t.user_id == user_id]
                user_history = [t for t in self.test_history if t.user_id == user_id]
                
                # Calculate overall insights
                total_tests = len(user_tests) + len(user_history)
                significant_wins = sum(
                    1 for t in user_history 
                    if t.current_result and t.current_result.significance_status in 
                    [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]
                )
                
                avg_lift = 0.0
                if user_history:
                    lifts = [
                        t.current_result.projected_lift for t in user_history 
                        if t.current_result and t.current_result.projected_lift > 0
                    ]
                    avg_lift = statistics.mean(lifts) if lifts else 0.0
                
                return {
                    "user_id": user_id,
                    "testing_summary": {
                        "total_tests": total_tests,
                        "active_tests": len(user_tests),
                        "completed_tests": len(user_history),
                        "significant_wins": significant_wins,
                        "win_rate": (significant_wins / max(len(user_history), 1)) * 100,
                        "average_lift": avg_lift
                    },
                    "active_tests": [
                        {
                            "test_id": t.test_id,
                            "test_name": t.test_name,
                            "status": t.status.value,
                            "days_running": (datetime.now() - t.start_date).days,
                            "primary_metric": t.primary_metric
                        }
                        for t in user_tests
                    ],
                    "recent_results": [
                        {
                            "test_id": t.test_id,
                            "test_name": t.test_name,
                            "projected_lift": t.current_result.projected_lift if t.current_result else 0,
                            "significance": t.current_result.significance_status.value if t.current_result else "unknown",
                            "winner": t.current_result.winning_variation_id if t.current_result else None
                        }
                        for t in user_history[-5:]  # Last 5 tests
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting test insights: {e}")
            return {"error": str(e)}

# Example usage
async def main():
    """Test the A/B testing framework"""
    print("🧪 A/B Testing Framework Test")
    print("=" * 40)
    
    framework = ABTestingFramework()
    
    # Create sample A/B test
    test_config = {
        "test_name": "Fitness Landing Page Test",
        "test_type": "simple_ab",
        "hypothesis": "Personal testimonials will increase conversion rate by 15%",
        "primary_metric": "conversion_rate",
        "secondary_metrics": ["ctr", "engagement_rate"],
        "minimum_effect_size": 0.15,
        "duration_days": 14,
        "target_demographics": ["millennial"],
        "target_platforms": ["facebook", "instagram"]
    }
    
    variations = [
        {
            "variation_id": "control",
            "name": "Original Landing Page", 
            "description": "Current landing page with feature benefits",
            "traffic_percentage": 50.0,
            "content_config": {"page_type": "features", "testimonials": False}
        },
        {
            "variation_id": "testimonials",
            "name": "Testimonial-Heavy Page",
            "description": "Landing page emphasizing customer testimonials",
            "traffic_percentage": 50.0,
            "content_config": {"page_type": "testimonials", "testimonials": True}
        }
    ]
    
    # Create test
    test = await framework.create_personalized_ab_test(
        user_id="user_123",
        test_config=test_config,
        variations=variations
    )
    
    print(f"✅ Created A/B test: {test.test_name}")
    print(f"   Test ID: {test.test_id}")
    print(f"   Minimum sample size: {test.minimum_sample_size}")
    print(f"   Variations: {len(test.variations)}")
    
    # Simulate test events
    test.status = TestStatus.ACTIVE
    
    # Control variation events
    for _ in range(1000):  # 1000 impressions
        await framework.record_test_event(
            test.test_id, "control", "impression"
        )
    
    for _ in range(120):  # 120 clicks (12% CTR)
        await framework.record_test_event(
            test.test_id, "control", "click"
        )
    
    for _ in range(6):  # 6 conversions (5% conversion rate)
        await framework.record_test_event(
            test.test_id, "control", "conversion", value=200.0
        )
    
    # Treatment variation events (better performance)
    for _ in range(1000):  # 1000 impressions
        await framework.record_test_event(
            test.test_id, "testimonials", "impression"
        )
    
    for _ in range(140):  # 140 clicks (14% CTR)
        await framework.record_test_event(
            test.test_id, "testimonials", "click"
        )
    
    for _ in range(9):  # 9 conversions (6.4% conversion rate)
        await framework.record_test_event(
            test.test_id, "testimonials", "conversion", value=200.0
        )
    
    # Get test results
    result = await framework._evaluate_test_results(test)
    
    print(f"\n📊 Test Results:")
    print(f"   Winner: {result.winning_variation_id}")
    print(f"   Confidence: {result.confidence_level:.1%}")
    print(f"   Significance: {result.significance_status.value}")
    print(f"   Projected lift: {result.projected_lift:.1f}%")
    print(f"   P-value: {result.p_value:.4f}")
    print(f"   Recommendation: {result.recommendation}")
    
    # Get insights
    insights = await framework.get_test_insights("user_123")
    print(f"\n🎯 User Insights:")
    print(f"   Total tests: {insights['testing_summary']['total_tests']}")
    print(f"   Active tests: {insights['testing_summary']['active_tests']}")

if __name__ == "__main__":
    asyncio.run(main())