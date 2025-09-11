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
import anthropic
import os

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
    Claude-powered adaptive learning system for marketing campaign optimization
    """
    
    def __init__(self):
        """Initialize adaptive learning system with Claude integration"""
        self.user_learning_profiles: Dict[str, UserLearningProfile] = {}
        self.prediction_models: Dict[str, PredictionModel] = {}
        self.learning_thresholds = {
            "min_campaigns_for_insight": 5,
            "min_significance_score": 0.7,
            "confidence_threshold": 0.75
        }
        self.feature_importance_weights = self._initialize_feature_weights()
        
        # Initialize Claude client
        self.anthropic_client = None
        self._initialize_claude_client()
    
    def _initialize_claude_client(self):
        """Initialize Claude client for AI-powered insights"""
        try:
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Claude client initialized for adaptive learning")
            else:
                logger.warning("ANTHROPIC_API_KEY not found - AI insights disabled")
        except Exception as e:
            logger.error(f"Claude client initialization failed: {e}")
    
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
                
                insight = await self._generate_performance_insight(
                    user_id, roi_improvement, campaign_data, historical_campaigns, "roi"
                )
                
                insights.append(insight)
        
        # Analyze CTR patterns
        ctr_values = [camp.get("ctr", 0) for camp in historical_campaigns + [campaign_data]]
        current_ctr = campaign_data.get("ctr", 0)
        
        if ctr_values and current_ctr > 0:
            avg_ctr = statistics.mean(ctr_values[:-1]) if len(ctr_values) > 1 else 0
            ctr_improvement = ((current_ctr - avg_ctr) / max(avg_ctr, 0.1)) * 100
            
            if abs(ctr_improvement) > 15:  # Significant CTR change
                insight = await self._generate_performance_insight(
                    user_id, ctr_improvement, campaign_data, historical_campaigns, "ctr"
                )
                
                insights.append(insight)
        
        return insights
    
    async def _generate_performance_insight(
        self,
        user_id: str,
        performance_change: float,
        campaign_data: Dict[str, Any],
        historical_campaigns: List[Dict[str, Any]],
        metric_type: str
    ) -> LearningInsight:
        """Generate Claude-powered performance insight"""
        
        try:
            if self.anthropic_client:
                # Prepare context for Claude analysis
                insight_context = {
                    "metric_type": metric_type,
                    "performance_change": performance_change,
                    "current_campaign": campaign_data,
                    "historical_data": historical_campaigns[-3:],  # Last 3 campaigns for context
                    "industry": campaign_data.get("industry", "unknown"),
                    "platforms": campaign_data.get("platforms", []),
                    "demographics": campaign_data.get("target_demographics", [])
                }
                
                prompt = f"""
                As a marketing performance analyst specializing in Indian digital marketing, analyze this campaign performance pattern:
                
                Metric: {metric_type.upper()}
                Performance Change: {performance_change:.1f}%
                Current Campaign: {json.dumps(campaign_data, indent=2)}
                Recent Historical Performance: {json.dumps(historical_campaigns[-3:], indent=2)}
                
                Provide a comprehensive analysis in JSON format:
                {{
                    "insight_title": "Clear, actionable title",
                    "insight_description": "Detailed explanation of the pattern and its implications",
                    "key_factors": ["factor1", "factor2", "factor3"],
                    "applicable_scenarios": ["scenario1", "scenario2", "scenario3"],
                    "recommended_actions": ["action1", "action2", "action3", "action4"],
                    "risk_factors": ["risk1", "risk2"],
                    "confidence_assessment": "high/medium/low",
                    "expected_impact": "percentage or description"
                }}
                
                Focus on:
                - Indian market context (UPI, mobile-first, price sensitivity)
                - Platform-specific insights for Meta/Instagram
                - Cultural and demographic considerations
                - Actionable recommendations for Indian businesses
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_insight = json.loads(json_match.group())
                    
                    # Create structured insight from Claude analysis
                    return LearningInsight(
                        insight_id=str(uuid.uuid4()),
                        user_id=user_id,
                        learning_type=LearningType.PERFORMANCE_PATTERN,
                        insight_title=claude_insight.get("insight_title", f"{metric_type.upper()} Pattern Detected"),
                        insight_description=claude_insight.get("insight_description", "Performance pattern analysis"),
                        supporting_data={
                            "current_value": campaign_data.get(metric_type, 0),
                            "change_percentage": performance_change,
                            "key_factors": claude_insight.get("key_factors", []),
                            "sample_size": len(historical_campaigns),
                            "confidence_assessment": claude_insight.get("confidence_assessment", "medium")
                        },
                        confidence_level=self._determine_confidence_level(len(historical_campaigns)),
                        significance_score=min(abs(performance_change) / 50, 1.0),
                        sample_size=len(historical_campaigns),
                        applicable_scenarios=claude_insight.get("applicable_scenarios", []),
                        recommended_actions=claude_insight.get("recommended_actions", []),
                        performance_impact={metric_type: performance_change},
                        estimated_roi_lift=performance_change,
                        campaigns_analyzed=[camp.get("campaign_id", "") for camp in historical_campaigns[-5:]]
                    )
        except Exception as e:
            logger.error(f"Claude insight generation failed: {e}")
        
        # Fallback to basic insight
        insight_type = "improvement" if performance_change > 0 else "decline"
        return LearningInsight(
            insight_id=str(uuid.uuid4()),
            user_id=user_id,
            learning_type=LearningType.PERFORMANCE_PATTERN,
            insight_title=f"{metric_type.upper()} {insight_type.title()} Pattern",
            insight_description=f"Campaign shows {abs(performance_change):.1f}% {insight_type} in {metric_type}",
            supporting_data={
                "change_percentage": performance_change,
                "sample_size": len(historical_campaigns)
            },
            confidence_level=self._determine_confidence_level(len(historical_campaigns)),
            significance_score=min(abs(performance_change) / 50, 1.0),
            sample_size=len(historical_campaigns),
            applicable_scenarios=["similar_campaigns"],
            recommended_actions=["Monitor performance trends", "Analyze contributing factors"],
            performance_impact={metric_type: performance_change},
            estimated_roi_lift=performance_change,
            campaigns_analyzed=[camp.get("campaign_id", "") for camp in historical_campaigns[-5:]]
        )
    
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
                        recommended_actions=["Analyze audience behavior patterns", "Test alternative targeting approaches"],
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
                        recommended_actions=await self._generate_content_recommendations(
                            best_content_type, worst_content_type, performance_gap, campaign_data
                        ),
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
                            recommended_actions=await self._generate_platform_recommendations(
                                cheapest_platform, most_expensive_platform, cost_difference, campaign_data
                            ),
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
        demographics = campaign_data.get("target_demographics", [])
        if isinstance(demographics, list) and demographics:
            features["age_group"] = demographics[0]
        else:
            features["age_group"] = None
            
        features["interests"] = campaign_data.get("target_interests", []) if isinstance(campaign_data.get("target_interests", []), list) else []
        features["demographics"] = demographics if isinstance(demographics, list) else []
        
        # Platform features
        platforms = campaign_data.get("platforms", [])
        if isinstance(platforms, list) and platforms:
            features["platform"] = platforms[0]
        else:
            features["platform"] = None
        features["posting_time"] = campaign_data.get("posting_time")
        
        # Campaign features
        features["objective"] = campaign_data.get("objective")
        features["budget_level"] = self._categorize_budget(campaign_data.get("budget", 0))
        
        return features
    
    def _categorize_budget(self, budget: float) -> str:
        """Categorize budget into levels"""
        try:
            budget_value = float(budget) if budget is not None else 0.0
        except (ValueError, TypeError):
            budget_value = 0.0
            
        if budget_value < 1000:
            return "low"
        elif budget_value < 5000:
            return "medium"
        elif budget_value < 20000:
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
    
    async def _generate_audience_insight(
        self,
        user_id: str,
        engagement_change: float,
        demographics: List[str],
        campaign_data: Dict[str, Any],
        similar_campaigns: List[Dict[str, Any]]
    ) -> LearningInsight:
        """Generate Claude-powered audience insight"""
        
        try:
            if self.anthropic_client:
                # Prepare context for Claude analysis
                audience_context = {
                    "engagement_change": engagement_change,
                    "target_demographics": demographics,
                    "current_campaign": campaign_data,
                    "similar_campaigns": similar_campaigns[-3:],  # Last 3 similar campaigns
                    "industry": campaign_data.get("industry", "unknown"),
                    "platforms": campaign_data.get("platforms", []),
                    "business_type": campaign_data.get("business_type", "unknown")
                }
                
                primary_demo = demographics[0] if demographics else "unknown"
                
                prompt = f"""
                As an expert in Indian digital marketing and audience analysis, analyze this audience engagement pattern:
                
                Demographics: {', '.join(demographics)}
                Engagement Change: {engagement_change:.1f}%
                Current Campaign: {json.dumps(campaign_data, indent=2)}
                Similar Historical Campaigns: {json.dumps(similar_campaigns[-3:], indent=2)}
                
                Provide a comprehensive audience analysis in JSON format:
                {{
                    "insight_title": "Clear, actionable title about audience response",
                    "insight_description": "Detailed explanation of audience behavior patterns",
                    "audience_factors": ["factor1", "factor2", "factor3"],
                    "cultural_insights": ["insight1", "insight2"],
                    "applicable_scenarios": ["scenario1", "scenario2", "scenario3"],
                    "recommended_actions": ["action1", "action2", "action3", "action4"],
                    "targeting_adjustments": ["adjustment1", "adjustment2"],
                    "content_recommendations": ["rec1", "rec2"],
                    "confidence_assessment": "high/medium/low",
                    "expected_impact": "percentage or description"
                }}
                
                Focus on:
                - Indian demographic preferences and behaviors
                - Cultural context and local market dynamics
                - Platform-specific audience patterns (Meta/Instagram)
                - Regional and linguistic considerations
                - Mobile-first user behavior in India
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_insight = json.loads(json_match.group())
                    
                    # Create structured insight from Claude analysis
                    return LearningInsight(
                        insight_id=str(uuid.uuid4()),
                        user_id=user_id,
                        learning_type=LearningType.AUDIENCE_RESPONSE,
                        insight_title=claude_insight.get("insight_title", f"{primary_demo.title()} Audience Response Pattern"),
                        insight_description=claude_insight.get("insight_description", "Audience engagement pattern analysis"),
                        supporting_data={
                            "demographics": demographics,
                            "current_engagement": campaign_data.get("engagement_rate", 0),
                            "change_percentage": engagement_change,
                            "audience_factors": claude_insight.get("audience_factors", []),
                            "cultural_insights": claude_insight.get("cultural_insights", []),
                            "sample_size": len(similar_campaigns),
                            "confidence_assessment": claude_insight.get("confidence_assessment", "medium")
                        },
                        confidence_level=self._determine_confidence_level(len(similar_campaigns)),
                        significance_score=min(abs(engagement_change) / 40, 1.0),
                        sample_size=len(similar_campaigns),
                        applicable_scenarios=claude_insight.get("applicable_scenarios", []),
                        recommended_actions=claude_insight.get("recommended_actions", []) + 
                                           claude_insight.get("targeting_adjustments", []) +
                                           claude_insight.get("content_recommendations", []),
                        performance_impact={"engagement_rate": engagement_change},
                        estimated_roi_lift=engagement_change * 0.3,
                        campaigns_analyzed=[camp.get("campaign_id", "") for camp in similar_campaigns]
                    )
        except Exception as e:
            logger.error(f"Claude audience insight generation failed: {e}")
        
        # Fallback to basic insight
        primary_demo = demographics[0] if demographics else "unknown"
        insight_type = "improvement" if engagement_change > 0 else "decline"
        
        return LearningInsight(
            insight_id=str(uuid.uuid4()),
            user_id=user_id,
            learning_type=LearningType.AUDIENCE_RESPONSE,
            insight_title=f"{primary_demo.title()} Audience Response Pattern",
            insight_description=f"Engagement with {primary_demo} audience shows {abs(engagement_change):.1f}% {insight_type}",
            supporting_data={
                "demographics": demographics,
                "change_percentage": engagement_change,
                "sample_size": len(similar_campaigns)
            },
            confidence_level=self._determine_confidence_level(len(similar_campaigns)),
            significance_score=min(abs(engagement_change) / 40, 1.0),
            sample_size=len(similar_campaigns),
            applicable_scenarios=[f"{primary_demo}_targeting", "audience_expansion"],
            recommended_actions=["Analyze audience behavior patterns", "Test alternative targeting approaches"],
            performance_impact={"engagement_rate": engagement_change},
            estimated_roi_lift=engagement_change * 0.3,
            campaigns_analyzed=[camp.get("campaign_id", "") for camp in similar_campaigns]
        )
    
    async def _generate_platform_recommendations(
        self,
        cheapest_platform: tuple,
        most_expensive_platform: tuple,
        cost_difference: float,
        campaign_data: Dict[str, Any]
    ) -> List[str]:
        """Generate Claude-powered platform optimization recommendations"""
        
        try:
            if self.anthropic_client:
                platform_context = {
                    "cheapest_platform": cheapest_platform[0],
                    "cheapest_cpc": cheapest_platform[1],
                    "most_expensive_platform": most_expensive_platform[0],
                    "most_expensive_cpc": most_expensive_platform[1],
                    "cost_difference": cost_difference,
                    "campaign_data": campaign_data,
                    "industry": campaign_data.get("industry", "unknown"),
                    "business_type": campaign_data.get("business_type", "unknown")
                }
                
                prompt = f"""
                As a platform optimization expert for Indian digital marketing, analyze this platform cost efficiency gap:
                
                Cheapest Platform: {cheapest_platform[0]} (CPC: ₹{cheapest_platform[1]:.2f})
                Most Expensive Platform: {most_expensive_platform[0]} (CPC: ₹{most_expensive_platform[1]:.2f})
                Cost Difference: {cost_difference:.1f}%
                Campaign Context: {json.dumps(campaign_data, indent=2)}
                
                Provide platform optimization recommendations in JSON format:
                {{
                    "budget_reallocation": ["rec1", "rec2"],
                    "platform_specific_tactics": ["tactic1", "tactic2", "tactic3"],
                    "cross_platform_strategies": ["strategy1", "strategy2"],
                    "cost_optimization": ["optimization1", "optimization2"],
                    "indian_market_considerations": ["consideration1", "consideration2"],
                    "performance_monitoring": ["monitor1", "monitor2"],
                    "priority_actions": ["action1", "action2", "action3"]
                }}
                
                Focus on:
                - Indian social media user behavior across platforms
                - Cost-effective budget distribution strategies
                - Platform-specific content optimization for India
                - Leveraging platform strengths in Indian market
                - Cultural and linguistic platform preferences
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_recommendations = json.loads(json_match.group())
                    
                    # Combine all recommendation types
                    all_recommendations = []
                    all_recommendations.extend(claude_recommendations.get("budget_reallocation", []))
                    all_recommendations.extend(claude_recommendations.get("platform_specific_tactics", []))
                    all_recommendations.extend(claude_recommendations.get("cross_platform_strategies", []))
                    all_recommendations.extend(claude_recommendations.get("cost_optimization", []))
                    all_recommendations.extend(claude_recommendations.get("indian_market_considerations", []))
                    all_recommendations.extend(claude_recommendations.get("performance_monitoring", []))
                    all_recommendations.extend(claude_recommendations.get("priority_actions", []))
                    
                    return all_recommendations[:8]  # Limit to top 8 recommendations
        except Exception as e:
            logger.error(f"Claude platform recommendations generation failed: {e}")
        
        # Fallback to basic recommendations
        return [
            f"Increase budget allocation to {cheapest_platform[0]}",
            f"Optimize campaigns on {most_expensive_platform[0]} or reduce spend",
            "Test cross-platform content adaptation",
            "Monitor platform-specific performance trends"
        ]
    
    async def _generate_content_recommendations(
        self,
        best_content_type: tuple,
        worst_content_type: tuple,
        performance_gap: float,
        campaign_data: Dict[str, Any]
    ) -> List[str]:
        """Generate Claude-powered content effectiveness recommendations"""
        
        try:
            if self.anthropic_client:
                content_context = {
                    "best_content_type": best_content_type[0],
                    "best_performance": best_content_type[1],
                    "worst_content_type": worst_content_type[0],
                    "worst_performance": worst_content_type[1],
                    "performance_gap": performance_gap,
                    "campaign_data": campaign_data,
                    "industry": campaign_data.get("industry", "unknown"),
                    "platforms": campaign_data.get("platforms", [])
                }
                
                prompt = f"""
                As a content strategy expert for Indian digital marketing, analyze this content performance gap:
                
                Best Performing Content: {best_content_type[0]} (Performance: {best_content_type[1]:.2f}%)
                Worst Performing Content: {worst_content_type[0]} (Performance: {worst_content_type[1]:.2f}%)
                Performance Gap: {performance_gap:.1f}%
                Campaign Context: {json.dumps(campaign_data, indent=2)}
                
                Provide content optimization recommendations in JSON format:
                {{
                    "content_prioritization": ["priority1", "priority2"],
                    "creative_optimization": ["creative1", "creative2", "creative3"],
                    "format_strategies": ["format1", "format2"],
                    "indian_content_trends": ["trend1", "trend2"],
                    "cross_format_testing": ["test1", "test2"],
                    "performance_enhancement": ["enhancement1", "enhancement2"],
                    "resource_allocation": ["allocation1", "allocation2"]
                }}
                
                Focus on:
                - Indian audience content preferences
                - Platform-specific content formats that work in India
                - Cultural and linguistic content considerations
                - Visual storytelling preferences in Indian market
                - Cost-effective content production strategies
                - Mobile-first content optimization
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_recommendations = json.loads(json_match.group())
                    
                    # Combine all recommendation types
                    all_recommendations = []
                    all_recommendations.extend(claude_recommendations.get("content_prioritization", []))
                    all_recommendations.extend(claude_recommendations.get("creative_optimization", []))
                    all_recommendations.extend(claude_recommendations.get("format_strategies", []))
                    all_recommendations.extend(claude_recommendations.get("indian_content_trends", []))
                    all_recommendations.extend(claude_recommendations.get("cross_format_testing", []))
                    all_recommendations.extend(claude_recommendations.get("performance_enhancement", []))
                    all_recommendations.extend(claude_recommendations.get("resource_allocation", []))
                    
                    return all_recommendations[:8]  # Limit to top 8 recommendations
        except Exception as e:
            logger.error(f"Claude content recommendations generation failed: {e}")
        
        # Fallback to basic recommendations
        return [
            f"Prioritize {best_content_type[0]} content in future campaigns",
            f"Test variations of {best_content_type[0]} format",
            f"Reduce allocation to {worst_content_type[0]} content",
            "A/B test hybrid approaches combining best elements"
        ]
    
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
            
            # Generate Claude-powered recommendations
            recommendations = await self._generate_predictive_recommendations(predicted_roi, relevant_insights, features, user_id)
            
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
    
    async def _generate_predictive_recommendations(
        self,
        predicted_roi: float,
        insights: List[LearningInsight],
        features: Dict[str, Any],
        user_id: str
    ) -> List[str]:
        """Generate Claude-powered predictive recommendations"""
        
        try:
            if self.anthropic_client and insights:
                # Prepare context for Claude analysis
                prediction_context = {
                    "predicted_roi": predicted_roi,
                    "campaign_features": features,
                    "relevant_insights": [
                        {
                            "type": insight.learning_type.value,
                            "title": insight.insight_title,
                            "impact": insight.estimated_roi_lift,
                            "recommendations": insight.recommended_actions[:3]
                        }
                        for insight in insights[:3]
                    ],
                    "user_profile": self.user_learning_profiles.get(user_id, {})
                }
                
                prompt = f"""
                As an expert in Indian digital marketing optimization, provide strategic recommendations based on this campaign prediction:
                
                Predicted ROI: {predicted_roi:.1f}%
                Campaign Features: {json.dumps(features, indent=2)}
                Relevant Learning Insights: {json.dumps(prediction_context['relevant_insights'], indent=2)}
                
                Generate strategic optimization recommendations in JSON format:
                {{
                    "strategic_recommendations": ["rec1", "rec2", "rec3"],
                    "tactical_actions": ["action1", "action2", "action3"],
                    "budget_optimization": ["budget1", "budget2"],
                    "targeting_refinements": ["target1", "target2"],
                    "content_improvements": ["content1", "content2"],
                    "platform_optimizations": ["platform1", "platform2"],
                    "indian_market_specific": ["india1", "india2"],
                    "priority_level": "high/medium/low",
                    "implementation_sequence": ["step1", "step2", "step3"]
                }}
                
                Focus on:
                - Indian market dynamics and consumer behavior
                - Platform-specific optimization for Meta/Instagram in India
                - Cultural and linguistic considerations
                - Mobile-first optimization strategies
                - Cost-effective approaches for Indian businesses
                - UPI and digital payment integration considerations
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse Claude response
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    claude_recommendations = json.loads(json_match.group())
                    
                    # Combine all recommendation types
                    all_recommendations = []
                    all_recommendations.extend(claude_recommendations.get("strategic_recommendations", []))
                    all_recommendations.extend(claude_recommendations.get("tactical_actions", []))
                    all_recommendations.extend(claude_recommendations.get("budget_optimization", []))
                    all_recommendations.extend(claude_recommendations.get("targeting_refinements", []))
                    all_recommendations.extend(claude_recommendations.get("content_improvements", []))
                    all_recommendations.extend(claude_recommendations.get("platform_optimizations", []))
                    all_recommendations.extend(claude_recommendations.get("indian_market_specific", []))
                    
                    return all_recommendations[:10]  # Limit to top 10 recommendations
        except Exception as e:
            logger.error(f"Claude predictive recommendations generation failed: {e}")
        
        # Fallback to basic recommendations
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