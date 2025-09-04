"""
Adaptive Learning System for Marketing Automation
Learns from campaign performance to continuously improve recommendations and predictions
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
from collections import defaultdict

logger = logging.getLogger(__name__)

class LearningType(Enum):
    PERFORMANCE_PATTERN = "performance_pattern"
    AUDIENCE_RESPONSE = "audience_response"
    CONTENT_EFFECTIVENESS = "content_effectiveness"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    TIMING_ANALYSIS = "timing_analysis"

class ConfidenceLevel(Enum):
    LOW = "low"          # < 50 data points
    MEDIUM = "medium"    # 50-200 data points
    HIGH = "high"        # > 200 data points

@dataclass
class LearningInsight:
    """Individual learning insight extracted from campaign data"""
    insight_id: str
    user_id: str
    learning_type: LearningType
    
    # Insight content
    insight_title: str
    insight_description: str
    supporting_data: Dict[str, Any]
    
    # Statistical confidence
    confidence_level: ConfidenceLevel
    significance_score: float  # 0-1
    sample_size: int
    
    # Application context
    applicable_scenarios: List[str]
    recommended_actions: List[str]
    
    # Performance impact
    performance_impact: Dict[str, float]  # metric -> improvement
    estimated_roi_lift: float
    
    # Learning metadata
    campaigns_analyzed: List[str]
    discovery_date: datetime = field(default_factory=datetime.now)
    last_validated: datetime = field(default_factory=datetime.now)
    validation_count: int = 0

@dataclass
class UserLearningProfile:
    """Comprehensive learning profile for a user"""
    user_id: str
    
    # Learning insights by category
    performance_insights: List[LearningInsight] = field(default_factory=list)
    audience_insights: List[LearningInsight] = field(default_factory=list)
    content_insights: List[LearningInsight] = field(default_factory=list)
    platform_insights: List[LearningInsight] = field(default_factory=list)
    timing_insights: List[LearningInsight] = field(default_factory=list)
    
    # Aggregated learning patterns
    top_performing_elements: Dict[str, Any] = field(default_factory=dict)
    underperforming_elements: Dict[str, Any] = field(default_factory=dict)
    
    # Prediction models (simplified ML-like models)
    performance_predictors: Dict[str, Dict[str, float]] = field(default_factory=dict)
    audience_response_models: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Learning metadata
    total_campaigns_analyzed: int = 0
    last_learning_update: datetime = field(default_factory=datetime.now)
    learning_confidence: float = 0.0  # Overall confidence in learnings

@dataclass
class PredictionModel:
    """Simple prediction model based on historical patterns"""
    model_id: str
    model_type: str  # performance, audience, content, etc.
    
    # Model parameters (simplified weights)
    feature_weights: Dict[str, float]
    baseline_metrics: Dict[str, float]
    
    # Model performance
    accuracy_score: float
    prediction_count: int
    validation_score: float
    
    # Training data
    training_sample_size: int
    last_trained: datetime = field(default_factory=datetime.now)

class AdaptiveLearningSystem:
    """
    Machine learning-inspired system that adapts recommendations based on campaign performance
    """
    
    def __init__(self):
        """Initialize adaptive learning system"""
        self.user_learning_profiles: Dict[str, UserLearningProfile] = {}
        self.prediction_models: Dict[str, PredictionModel] = {}
        self.learning_thresholds = {
            "min_campaigns_for_insight": 5,
            "min_significance_score": 0.7,
            "confidence_threshold": 0.75
        }
        self.feature_importance_weights = self._initialize_feature_weights()
    
    def _initialize_feature_weights(self) -> Dict[str, float]:
        """Initialize feature importance weights for learning"""
        return {
            # Content features
            "visual_style": 0.25,
            "content_type": 0.20,
            "caption_length": 0.15,
            "hashtag_count": 0.10,
            
            # Audience features  
            "age_group": 0.30,
            "interests": 0.25,
            "demographics": 0.20,
            "behaviors": 0.15,
            
            # Platform features
            "platform": 0.35,
            "posting_time": 0.25,
            "frequency": 0.20,
            "format": 0.15,
            
            # Campaign features
            "objective": 0.30,
            "budget_level": 0.25,
            "duration": 0.20,
            "seasonality": 0.15
        }
    
    async def analyze_campaign_performance(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance and extract learnings
        
        Args:
            user_id: User identifier
            campaign_data: Campaign performance data
            
        Returns:
            Learning insights extracted from the campaign
        """
        try:
            # Get or create user learning profile
            if user_id not in self.user_learning_profiles:
                self.user_learning_profiles[user_id] = UserLearningProfile(user_id=user_id)
            
            profile = self.user_learning_profiles[user_id]
            profile.total_campaigns_analyzed += 1
            
            # Extract insights from campaign data
            insights = []
            
            # Analyze performance patterns
            performance_insights = await self._analyze_performance_patterns(user_id, campaign_data)
            insights.extend(performance_insights)
            profile.performance_insights.extend(performance_insights)
            
            # Analyze audience response
            audience_insights = await self._analyze_audience_response(user_id, campaign_data)
            insights.extend(audience_insights)
            profile.audience_insights.extend(audience_insights)
            
            # Analyze content effectiveness
            content_insights = await self._analyze_content_effectiveness(user_id, campaign_data)
            insights.extend(content_insights)
            profile.content_insights.extend(content_insights)
            
            # Analyze platform optimization
            platform_insights = await self._analyze_platform_optimization(user_id, campaign_data)
            insights.extend(platform_insights)
            profile.platform_insights.extend(platform_insights)
            
            # Update prediction models
            await self._update_prediction_models(user_id, campaign_data)
            
            # Update aggregated patterns
            self._update_learning_patterns(profile, campaign_data)
            
            # Calculate learning confidence
            profile.learning_confidence = self._calculate_learning_confidence(profile)
            profile.last_learning_update = datetime.now()
            
            logger.info(f"Analyzed campaign for user {user_id}, extracted {len(insights)} insights")
            
            return {
                "user_id": user_id,
                "campaign_id": campaign_data.get("campaign_id"),
                "insights_extracted": len(insights),
                "learning_confidence": profile.learning_confidence,
                "new_insights": [
                    {
                        "type": insight.learning_type.value,
                        "title": insight.insight_title,
                        "confidence": insight.confidence_level.value,
                        "impact": insight.estimated_roi_lift
                    }
                    for insight in insights
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing campaign performance: {e}")
            raise
    
    async def _analyze_performance_patterns(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> List[LearningInsight]:
        """Analyze performance patterns to extract insights"""
        
        insights = []
        
        # Get user's historical campaign data
        historical_campaigns = self._get_user_historical_campaigns(user_id)
        
        if len(historical_campaigns) < self.learning_thresholds["min_campaigns_for_insight"]:
            return insights
        
        # Analyze ROI patterns
        roi_values = [camp.get("roi", 0) for camp in historical_campaigns + [campaign_data]]
        current_roi = campaign_data.get("roi", 0)
        
        if roi_values and current_roi > 0:
            avg_roi = statistics.mean(roi_values[:-1]) if len(roi_values) > 1 else 0
            roi_improvement = ((current_roi - avg_roi) / max(avg_roi, 0.1)) * 100
            
            if abs(roi_improvement) > 20:  # Significant improvement or decline
                insight_type = "improvement" if roi_improvement > 0 else "decline"
                
                insight = LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    learning_type=LearningType.PERFORMANCE_PATTERN,
                    insight_title=f"ROI {insight_type.title()} Pattern Detected",
                    insight_description=f"Recent campaigns show {abs(roi_improvement):.1f}% {insight_type} in ROI performance",
                    supporting_data={
                        "current_roi": current_roi,
                        "historical_average": avg_roi,
                        "improvement_percentage": roi_improvement,
                        "sample_size": len(roi_values)
                    },
                    confidence_level=self._determine_confidence_level(len(roi_values)),
                    significance_score=min(abs(roi_improvement) / 50, 1.0),
                    sample_size=len(roi_values),
                    applicable_scenarios=["similar_campaigns", "same_industry", "similar_budget"],
                    recommended_actions=self._generate_roi_recommendations(roi_improvement, campaign_data),
                    performance_impact={"roi": roi_improvement},
                    estimated_roi_lift=roi_improvement,
                    campaigns_analyzed=[camp.get("campaign_id", "") for camp in historical_campaigns[-5:]]
                )
                
                insights.append(insight)
        
        # Analyze CTR patterns
        ctr_values = [camp.get("ctr", 0) for camp in historical_campaigns + [campaign_data]]
        current_ctr = campaign_data.get("ctr", 0)
        
        if ctr_values and current_ctr > 0:
            avg_ctr = statistics.mean(ctr_values[:-1]) if len(ctr_values) > 1 else 0
            ctr_improvement = ((current_ctr - avg_ctr) / max(avg_ctr, 0.1)) * 100
            
            if abs(ctr_improvement) > 15:  # Significant CTR change
                insight = LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    learning_type=LearningType.PERFORMANCE_PATTERN,
                    insight_title=f"Click-Through Rate Pattern Change",
                    insight_description=f"CTR performance shows {abs(ctr_improvement):.1f}% change from historical average",
                    supporting_data={
                        "current_ctr": current_ctr,
                        "historical_average": avg_ctr,
                        "change_percentage": ctr_improvement
                    },
                    confidence_level=self._determine_confidence_level(len(ctr_values)),
                    significance_score=min(abs(ctr_improvement) / 30, 1.0),
                    sample_size=len(ctr_values),
                    applicable_scenarios=["content_optimization", "audience_targeting"],
                    recommended_actions=self._generate_ctr_recommendations(ctr_improvement, campaign_data),
                    performance_impact={"ctr": ctr_improvement},
                    estimated_roi_lift=ctr_improvement * 0.5,  # CTR improvements typically yield 50% ROI impact
                    campaigns_analyzed=[camp.get("campaign_id", "") for camp in historical_campaigns[-5:]]
                )
                
                insights.append(insight)
        
        return insights
    
    async def _analyze_audience_response(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> List[LearningInsight]:
        """Analyze audience response patterns"""
        
        insights = []
        
        historical_campaigns = self._get_user_historical_campaigns(user_id)
        
        # Analyze demographic performance
        current_demographics = campaign_data.get("target_demographics", [])
        current_engagement = campaign_data.get("engagement_rate", 0)
        
        if current_demographics and current_engagement > 0:
            # Find campaigns with similar demographics
            similar_campaigns = [
                camp for camp in historical_campaigns
                if self._demographics_similarity(
                    current_demographics,
                    camp.get("target_demographics", [])
                ) > 0.7
            ]
            
            if len(similar_campaigns) >= 3:
                similar_engagement = [camp.get("engagement_rate", 0) for camp in similar_campaigns]
                avg_engagement = statistics.mean(similar_engagement) if similar_engagement else 0
                
                engagement_change = ((current_engagement - avg_engagement) / max(avg_engagement, 0.1)) * 100
                
                if abs(engagement_change) > 20:
                    primary_demo = current_demographics[0] if current_demographics else "unknown"
                    
                    insight = LearningInsight(
                        insight_id=str(uuid.uuid4()),
                        user_id=user_id,
                        learning_type=LearningType.AUDIENCE_RESPONSE,
                        insight_title=f"{primary_demo.title()} Audience Response Pattern",
                        insight_description=f"Engagement with {primary_demo} audience shows {abs(engagement_change):.1f}% change",
                        supporting_data={
                            "demographics": current_demographics,
                            "current_engagement": current_engagement,
                            "historical_average": avg_engagement,
                            "change_percentage": engagement_change
                        },
                        confidence_level=self._determine_confidence_level(len(similar_campaigns)),
                        significance_score=min(abs(engagement_change) / 40, 1.0),
                        sample_size=len(similar_campaigns),
                        applicable_scenarios=[f"{primary_demo}_targeting", "audience_expansion"],
                        recommended_actions=self._generate_audience_recommendations(engagement_change, primary_demo),
                        performance_impact={"engagement_rate": engagement_change},
                        estimated_roi_lift=engagement_change * 0.3,
                        campaigns_analyzed=[camp.get("campaign_id", "") for camp in similar_campaigns]
                    )
                    
                    insights.append(insight)
        
        return insights
    
    async def _analyze_content_effectiveness(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> List[LearningInsight]:
        """Analyze content effectiveness patterns"""
        
        insights = []
        
        historical_campaigns = self._get_user_historical_campaigns(user_id)
        
        # Analyze content type performance
        current_content_type = campaign_data.get("content_type", "image")
        current_performance = campaign_data.get("conversion_rate", 0)
        
        # Group campaigns by content type
        content_performance = defaultdict(list)
        for camp in historical_campaigns + [campaign_data]:
            content_type = camp.get("content_type", "image")
            performance = camp.get("conversion_rate", 0)
            if performance > 0:
                content_performance[content_type].append(performance)
        
        if len(content_performance) > 1:  # Multiple content types to compare
            content_averages = {
                content_type: statistics.mean(performances)
                for content_type, performances in content_performance.items()
                if len(performances) >= 2
            }
            
            if current_content_type in content_averages:
                best_content_type = max(content_averages.items(), key=lambda x: x[1])
                worst_content_type = min(content_averages.items(), key=lambda x: x[1])
                
                performance_gap = ((best_content_type[1] - worst_content_type[1]) / worst_content_type[1]) * 100
                
                if performance_gap > 25:  # Significant difference between content types
                    insight = LearningInsight(
                        insight_id=str(uuid.uuid4()),
                        user_id=user_id,
                        learning_type=LearningType.CONTENT_EFFECTIVENESS,
                        insight_title=f"Content Type Performance Gap Identified",
                        insight_description=f"{best_content_type[0].title()} content outperforms {worst_content_type[0]} by {performance_gap:.1f}%",
                        supporting_data={
                            "best_content_type": best_content_type[0],
                            "best_performance": best_content_type[1],
                            "worst_content_type": worst_content_type[0],
                            "worst_performance": worst_content_type[1],
                            "performance_gap": performance_gap,
                            "content_averages": content_averages
                        },
                        confidence_level=self._determine_confidence_level(sum(len(perfs) for perfs in content_performance.values())),
                        significance_score=min(performance_gap / 50, 1.0),
                        sample_size=sum(len(perfs) for perfs in content_performance.values()),
                        applicable_scenarios=["content_planning", "creative_optimization"],
                        recommended_actions=[
                            f"Prioritize {best_content_type[0]} content in future campaigns",
                            f"Test variations of {best_content_type[0]} format",
                            f"Reduce allocation to {worst_content_type[0]} content",
                            "A/B test hybrid approaches combining best elements"
                        ],
                        performance_impact={"conversion_rate": performance_gap},
                        estimated_roi_lift=performance_gap * 0.8,
                        campaigns_analyzed=[camp.get("campaign_id", "") for camp in historical_campaigns[-10:]]
                    )
                    
                    insights.append(insight)
        
        return insights
    
    async def _analyze_platform_optimization(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> List[LearningInsight]:
        """Analyze platform-specific optimization patterns"""
        
        insights = []
        
        historical_campaigns = self._get_user_historical_campaigns(user_id)
        
        # Analyze platform performance
        current_platforms = campaign_data.get("platforms", [])
        current_cpc = campaign_data.get("cost_per_click", 0)
        
        if current_platforms and current_cpc > 0:
            platform_costs = defaultdict(list)
            
            for camp in historical_campaigns + [campaign_data]:
                platforms = camp.get("platforms", [])
                cpc = camp.get("cost_per_click", 0)
                if platforms and cpc > 0:
                    for platform in platforms:
                        platform_costs[platform].append(cpc)
            
            if len(platform_costs) > 1:
                platform_avg_costs = {
                    platform: statistics.mean(costs)
                    for platform, costs in platform_costs.items()
                    if len(costs) >= 2
                }
                
                if len(platform_avg_costs) > 1:
                    cheapest_platform = min(platform_avg_costs.items(), key=lambda x: x[1])
                    most_expensive_platform = max(platform_avg_costs.items(), key=lambda x: x[1])
                    
                    cost_difference = ((most_expensive_platform[1] - cheapest_platform[1]) / cheapest_platform[1]) * 100
                    
                    if cost_difference > 30:  # Significant cost difference
                        insight = LearningInsight(
                            insight_id=str(uuid.uuid4()),
                            user_id=user_id,
                            learning_type=LearningType.PLATFORM_OPTIMIZATION,
                            insight_title=f"Platform Cost Efficiency Gap",
                            insight_description=f"{cheapest_platform[0].title()} costs {cost_difference:.1f}% less than {most_expensive_platform[0]}",
                            supporting_data={
                                "cheapest_platform": cheapest_platform[0],
                                "cheapest_cpc": cheapest_platform[1],
                                "most_expensive_platform": most_expensive_platform[0],
                                "most_expensive_cpc": most_expensive_platform[1],
                                "cost_difference": cost_difference,
                                "platform_costs": platform_avg_costs
                            },
                            confidence_level=self._determine_confidence_level(sum(len(costs) for costs in platform_costs.values())),
                            significance_score=min(cost_difference / 60, 1.0),
                            sample_size=sum(len(costs) for costs in platform_costs.values()),
                            applicable_scenarios=["budget_allocation", "platform_strategy"],
                            recommended_actions=[
                                f"Increase budget allocation to {cheapest_platform[0]}",
                                f"Optimize campaigns on {most_expensive_platform[0]} or reduce spend",
                                "Test cross-platform content adaptation",
                                "Monitor platform-specific performance trends"
                            ],
                            performance_impact={"cost_efficiency": cost_difference},
                            estimated_roi_lift=cost_difference * 0.6,
                            campaigns_analyzed=[camp.get("campaign_id", "") for camp in historical_campaigns[-8:]]
                        )
                        
                        insights.append(insight)
        
        return insights
    
    async def _update_prediction_models(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> None:
        """Update prediction models with new campaign data"""
        
        try:
            # Get user's learning profile
            profile = self.user_learning_profiles.get(user_id)
            if not profile:
                return
            
            # Update performance predictor
            model_key = f"{user_id}_performance"
            
            if model_key not in self.prediction_models:
                self.prediction_models[model_key] = PredictionModel(
                    model_id=model_key,
                    model_type="performance",
                    feature_weights=self.feature_importance_weights.copy(),
                    baseline_metrics={},
                    accuracy_score=0.5,
                    prediction_count=0,
                    validation_score=0.0,
                    training_sample_size=0
                )
            
            model = self.prediction_models[model_key]
            
            # Extract features from campaign
            features = self._extract_campaign_features(campaign_data)
            actual_performance = campaign_data.get("roi", 0)
            
            # Simple weight update based on performance
            if actual_performance > 0:
                for feature, value in features.items():
                    if feature in model.feature_weights and value:
                        # Adjust weight based on performance (simplified learning)
                        performance_factor = min(actual_performance / 10, 2.0)  # Cap at 2x
                        adjustment = 0.1 * (performance_factor - 1.0)  # +/- 10% max adjustment
                        model.feature_weights[feature] = max(0.1, min(1.0, model.feature_weights[feature] + adjustment))
            
            model.training_sample_size += 1
            model.last_trained = datetime.now()
            
            logger.debug(f"Updated prediction model for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating prediction models: {e}")
    
    def _extract_campaign_features(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from campaign data for learning"""
        
        features = {}
        
        # Content features
        features["visual_style"] = campaign_data.get("visual_style")
        features["content_type"] = campaign_data.get("content_type")
        features["caption_length"] = len(campaign_data.get("caption", ""))
        features["hashtag_count"] = len(campaign_data.get("hashtags", []))
        
        # Audience features
        features["age_group"] = campaign_data.get("target_demographics", [{}])[0] if campaign_data.get("target_demographics") else None
        features["interests"] = campaign_data.get("target_interests", [])
        features["demographics"] = campaign_data.get("target_demographics", [])
        
        # Platform features
        features["platform"] = campaign_data.get("platforms", [{}])[0] if campaign_data.get("platforms") else None
        features["posting_time"] = campaign_data.get("posting_time")
        
        # Campaign features
        features["objective"] = campaign_data.get("objective")
        features["budget_level"] = self._categorize_budget(campaign_data.get("budget", 0))
        
        return features
    
    def _categorize_budget(self, budget: float) -> str:
        """Categorize budget into levels"""
        if budget < 1000:
            return "low"
        elif budget < 5000:
            return "medium"
        elif budget < 20000:
            return "high"
        else:
            return "very_high"
    
    def _get_user_historical_campaigns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get historical campaign data for user (mock implementation)"""
        
        profile = self.user_learning_profiles.get(user_id)
        if not profile:
            return []
        
        # In a real implementation, this would query the database
        # For now, return empty list - this would be populated from actual campaign data
        return []
    
    def _demographics_similarity(self, demo1: List[str], demo2: List[str]) -> float:
        """Calculate similarity between two demographic sets"""
        
        if not demo1 or not demo2:
            return 0.0
        
        set1 = set(demo1)
        set2 = set(demo2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _determine_confidence_level(self, sample_size: int) -> ConfidenceLevel:
        """Determine confidence level based on sample size"""
        
        if sample_size < 50:
            return ConfidenceLevel.LOW
        elif sample_size < 200:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.HIGH
    
    def _calculate_learning_confidence(self, profile: UserLearningProfile) -> float:
        """Calculate overall learning confidence for user profile"""
        
        total_insights = (
            len(profile.performance_insights) +
            len(profile.audience_insights) +
            len(profile.content_insights) +
            len(profile.platform_insights) +
            len(profile.timing_insights)
        )
        
        if total_insights == 0:
            return 0.0
        
        # Calculate weighted confidence based on insight quality
        confidence_sum = 0.0
        for insights_list in [
            profile.performance_insights,
            profile.audience_insights,
            profile.content_insights,
            profile.platform_insights,
            profile.timing_insights
        ]:
            for insight in insights_list:
                confidence_sum += insight.significance_score
        
        avg_confidence = confidence_sum / total_insights
        
        # Adjust based on sample size
        sample_factor = min(profile.total_campaigns_analyzed / 20, 1.0)
        
        return avg_confidence * sample_factor
    
    def _update_learning_patterns(self, profile: UserLearningProfile, campaign_data: Dict[str, Any]) -> None:
        """Update aggregated learning patterns"""
        
        performance = campaign_data.get("roi", 0)
        
        # Update top performing elements
        if performance > 10:  # Good performance threshold
            content_type = campaign_data.get("content_type", "unknown")
            platform = campaign_data.get("platforms", ["unknown"])[0] if campaign_data.get("platforms") else "unknown"
            
            if "top_content_types" not in profile.top_performing_elements:
                profile.top_performing_elements["top_content_types"] = defaultdict(list)
            if "top_platforms" not in profile.top_performing_elements:
                profile.top_performing_elements["top_platforms"] = defaultdict(list)
            
            profile.top_performing_elements["top_content_types"][content_type].append(performance)
            profile.top_performing_elements["top_platforms"][platform].append(performance)
        
        # Update underperforming elements  
        elif performance < 5:  # Poor performance threshold
            content_type = campaign_data.get("content_type", "unknown")
            platform = campaign_data.get("platforms", ["unknown"])[0] if campaign_data.get("platforms") else "unknown"
            
            if "poor_content_types" not in profile.underperforming_elements:
                profile.underperforming_elements["poor_content_types"] = defaultdict(list)
            if "poor_platforms" not in profile.underperforming_elements:
                profile.underperforming_elements["poor_platforms"] = defaultdict(list)
            
            profile.underperforming_elements["poor_content_types"][content_type].append(performance)
            profile.underperforming_elements["poor_platforms"][platform].append(performance)
    
    # Recommendation generators
    def _generate_roi_recommendations(self, roi_change: float, campaign_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on ROI patterns"""
        
        recommendations = []
        
        if roi_change > 0:  # Improvement
            recommendations.extend([
                "Scale successful campaign elements to larger budget",
                "Replicate winning creative approach in similar campaigns",
                "Expand targeting to similar audience segments",
                "Test higher budget levels with current approach"
            ])
        else:  # Decline
            recommendations.extend([
                "Pause underperforming campaigns and analyze factors",
                "A/B test alternative creative approaches",
                "Review targeting parameters for audience fatigue",
                "Consider budget reallocation to better-performing campaigns"
            ])
        
        return recommendations
    
    def _generate_ctr_recommendations(self, ctr_change: float, campaign_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on CTR patterns"""
        
        recommendations = []
        
        if ctr_change > 0:
            recommendations.extend([
                "Apply successful creative elements to other campaigns",
                "Test similar visual styles and messaging",
                "Increase impression share for high-CTR campaigns",
                "Expand reach while maintaining creative quality"
            ])
        else:
            recommendations.extend([
                "Refresh creative assets to combat ad fatigue",
                "Test new visual styles and messaging approaches",
                "Review audience targeting for relevance",
                "Optimize ad placement and timing"
            ])
        
        return recommendations
    
    def _generate_audience_recommendations(self, engagement_change: float, demographic: str) -> List[str]:
        """Generate audience-specific recommendations"""
        
        recommendations = []
        
        if engagement_change > 0:
            recommendations.extend([
                f"Increase budget allocation to {demographic} audience",
                f"Create more content specifically for {demographic} preferences",
                f"Expand targeting to similar {demographic} segments",
                f"Test premium placements for {demographic} audience"
            ])
        else:
            recommendations.extend([
                f"Reduce {demographic} targeting or pause campaigns",
                f"Research {demographic} content preferences for better alignment",
                f"Test different messaging approaches for {demographic}",
                f"Consider alternative demographics with similar characteristics"
            ])
        
        return recommendations
    
    async def get_predictive_insights(
        self,
        user_id: str,
        proposed_campaign: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get predictive insights for a proposed campaign
        
        Args:
            user_id: User identifier
            proposed_campaign: Proposed campaign configuration
            
        Returns:
            Predictive insights and recommendations
        """
        try:
            profile = self.user_learning_profiles.get(user_id)
            if not profile:
                return {"error": "No learning profile found for user"}
            
            # Extract features from proposed campaign
            features = self._extract_campaign_features(proposed_campaign)
            
            # Get prediction model
            model_key = f"{user_id}_performance"
            model = self.prediction_models.get(model_key)
            
            if not model or model.training_sample_size < 5:
                return {
                    "predicted_performance": "insufficient_data",
                    "confidence": "low",
                    "recommendations": [
                        "Run initial campaigns to build learning data",
                        "Start with industry best practices",
                        "Focus on data collection for future optimization"
                    ]
                }
            
            # Make prediction (simplified)
            predicted_roi = self._predict_performance(features, model)
            confidence_score = min(model.training_sample_size / 50, 0.95)
            
            # Get relevant insights
            relevant_insights = self._get_relevant_insights(profile, features)
            
            # Generate recommendations
            recommendations = self._generate_predictive_recommendations(predicted_roi, relevant_insights, features)
            
            return {
                "user_id": user_id,
                "predicted_roi": predicted_roi,
                "confidence_score": confidence_score,
                "prediction_basis": f"{model.training_sample_size} historical campaigns",
                "relevant_insights": [
                    {
                        "type": insight.learning_type.value,
                        "title": insight.insight_title,
                        "impact": insight.estimated_roi_lift,
                        "applicability": self._calculate_insight_applicability(insight, features)
                    }
                    for insight in relevant_insights
                ],
                "optimization_recommendations": recommendations,
                "risk_factors": self._identify_risk_factors(features, relevant_insights),
                "confidence_factors": {
                    "learning_maturity": profile.learning_confidence,
                    "similar_campaigns": model.training_sample_size,
                    "insight_relevance": len(relevant_insights)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {e}")
            return {"error": str(e)}
    
    def _predict_performance(self, features: Dict[str, Any], model: PredictionModel) -> float:
        """Make performance prediction using simplified model"""
        
        # Simple weighted sum prediction
        prediction = 5.0  # Baseline ROI
        
        for feature, value in features.items():
            if feature in model.feature_weights and value is not None:
                weight = model.feature_weights[feature]
                
                # Simplified feature impact calculation
                if feature == "content_type" and value in ["video", "carousel"]:
                    prediction += weight * 2
                elif feature == "budget_level" and value in ["high", "very_high"]:
                    prediction += weight * 1.5
                elif feature == "platform" and value in ["instagram", "facebook"]:
                    prediction += weight * 1.2
        
        return max(0, prediction)
    
    def _get_relevant_insights(self, profile: UserLearningProfile, features: Dict[str, Any]) -> List[LearningInsight]:
        """Get insights relevant to proposed campaign features"""
        
        relevant_insights = []
        
        # Check all insights for relevance
        all_insights = (
            profile.performance_insights +
            profile.audience_insights +
            profile.content_insights +
            profile.platform_insights +
            profile.timing_insights
        )
        
        for insight in all_insights:
            applicability = self._calculate_insight_applicability(insight, features)
            if applicability > 0.6:  # 60% relevance threshold
                relevant_insights.append(insight)
        
        # Sort by relevance and significance
        relevant_insights.sort(key=lambda x: x.significance_score, reverse=True)
        
        return relevant_insights[:5]  # Top 5 most relevant
    
    def _calculate_insight_applicability(self, insight: LearningInsight, features: Dict[str, Any]) -> float:
        """Calculate how applicable an insight is to given features"""
        
        # Simple relevance scoring based on supporting data
        relevance_score = 0.0
        
        supporting_data = insight.supporting_data
        
        # Check content type relevance
        if "content_type" in supporting_data and features.get("content_type"):
            if supporting_data.get("best_content_type") == features["content_type"]:
                relevance_score += 0.3
        
        # Check demographic relevance
        if "demographics" in supporting_data and features.get("demographics"):
            overlap = self._demographics_similarity(
                supporting_data.get("demographics", []),
                features.get("demographics", [])
            )
            relevance_score += overlap * 0.4
        
        # Check platform relevance
        if "platform" in supporting_data and features.get("platform"):
            if supporting_data.get("cheapest_platform") == features["platform"]:
                relevance_score += 0.3
        
        return min(relevance_score, 1.0)
    
    def _generate_predictive_recommendations(
        self,
        predicted_roi: float,
        insights: List[LearningInsight],
        features: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on prediction and insights"""
        
        recommendations = []
        
        if predicted_roi > 15:
            recommendations.append("High ROI predicted - consider increasing budget allocation")
        elif predicted_roi < 8:
            recommendations.append("Below-average ROI predicted - review campaign elements")
        
        # Add insight-based recommendations
        for insight in insights[:3]:  # Top 3 insights
            recommendations.extend(insight.recommended_actions[:2])  # Top 2 actions per insight
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def _identify_risk_factors(self, features: Dict[str, Any], insights: List[LearningInsight]) -> List[str]:
        """Identify potential risk factors in proposed campaign"""
        
        risks = []
        
        # Check for historically poor-performing elements
        content_type = features.get("content_type")
        platform = features.get("platform")
        budget_level = features.get("budget_level")
        
        for insight in insights:
            if insight.estimated_roi_lift < 0:  # Negative impact insight
                supporting_data = insight.supporting_data
                
                if supporting_data.get("worst_content_type") == content_type:
                    risks.append(f"Content type '{content_type}' has shown poor historical performance")
                
                if supporting_data.get("most_expensive_platform") == platform:
                    risks.append(f"Platform '{platform}' has higher costs than alternatives")
        
        if budget_level == "low":
            risks.append("Low budget may limit reach and statistical significance")
        
        return risks

# Example usage
async def main():
    """Test the adaptive learning system"""
    print("🧠 Adaptive Learning System Test")
    print("=" * 40)
    
    learning_system = AdaptiveLearningSystem()
    
    # Simulate campaign performance data
    campaign_data = {
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
        "caption": "Transform your fitness journey with our proven 30-day program!",
        "hashtags": ["#fitness", "#transformation", "#health"]
    }
    
    # Analyze campaign performance
    analysis_result = await learning_system.analyze_campaign_performance("user_123", campaign_data)
    
    print(f"✅ Campaign Analysis Complete:")
    print(f"   Insights extracted: {analysis_result['insights_extracted']}")
    print(f"   Learning confidence: {analysis_result['learning_confidence']:.2f}")
    
    if analysis_result["new_insights"]:
        print(f"\n🔍 New Insights:")
        for insight in analysis_result["new_insights"]:
            print(f"   • {insight['title']} (Impact: {insight['impact']:.1f}%)")
    
    # Test predictive insights
    proposed_campaign = {
        "content_type": "image",
        "platforms": ["instagram"],
        "target_demographics": ["millennial"],
        "objective": "brand_awareness",
        "budget": 3000
    }
    
    prediction = await learning_system.get_predictive_insights("user_123", proposed_campaign)
    
    print(f"\n🔮 Predictive Insights:")
    print(f"   Predicted ROI: {prediction.get('predicted_roi', 'N/A')}")
    print(f"   Confidence: {prediction.get('confidence_score', 0):.2f}")
    
    if prediction.get("optimization_recommendations"):
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(prediction["optimization_recommendations"][:5], 1):
            print(f"   {i}. {rec}")

if __name__ == "__main__":
    asyncio.run(main())