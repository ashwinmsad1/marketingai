"""
Claude-Powered ML Prediction Engine
Advanced machine learning predictions using Claude Sonnet for marketing campaign optimization
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
import anthropic
import os

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    AUDIENCE_RESPONSE = "audience_response"
    CONTENT_EFFECTIVENESS = "content_effectiveness"
    BUDGET_OPTIMIZATION = "budget_optimization"
    VIRAL_POTENTIAL = "viral_potential"

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class MLPrediction:
    """AI-powered prediction result"""
    prediction_id: str
    user_id: str
    prediction_type: PredictionType
    
    # Prediction Results
    predicted_metrics: Dict[str, float]  # roi, ctr, conversion_rate, engagement
    confidence_level: ConfidenceLevel
    confidence_score: float  # 0-1
    
    # Explanation and Insights
    prediction_reasoning: str
    key_factors: List[str]
    risk_factors: List[str]
    optimization_opportunities: List[str]
    
    # Recommendation Actions
    recommended_adjustments: List[str]
    expected_outcomes: Dict[str, str]
    
    # Prediction Metadata
    input_features: Dict[str, Any]
    model_version: str
    created_at: datetime = field(default_factory=datetime.now)
    
@dataclass
class CampaignPrediction:
    """Comprehensive campaign performance prediction"""
    campaign_config: Dict[str, Any]
    performance_prediction: MLPrediction
    alternative_scenarios: List[MLPrediction]
    optimization_strategy: str
    expected_budget_efficiency: float
    
    created_at: datetime = field(default_factory=datetime.now)

class ClaudeMLPredictor:
    """
    Advanced ML predictor using Claude Sonnet for sophisticated campaign performance predictions
    """
    
    def __init__(self):
        """Initialize Claude ML predictor"""
        self.anthropic_client = None
        self.prediction_history: Dict[str, List[MLPrediction]] = {}
        self.model_version = "claude-3.5-sonnet-v1.0"
        self._initialize_claude_client()
    
    def _initialize_claude_client(self):
        """Initialize Claude client for ML predictions"""
        try:
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Claude ML Predictor initialized successfully")
            else:
                logger.error("ANTHROPIC_API_KEY not found - ML predictions disabled")
                
        except Exception as e:
            logger.error(f"Claude ML predictor initialization failed: {e}")
    
    async def predict_campaign_performance(
        self,
        user_id: str,
        campaign_config: Dict[str, Any],
        historical_data: List[Dict[str, Any]] = None
    ) -> CampaignPrediction:
        """
        Predict comprehensive campaign performance using Claude ML analysis
        
        Args:
            user_id: User identifier
            campaign_config: Proposed campaign configuration
            historical_data: Historical campaign performance data
            
        Returns:
            Comprehensive campaign performance prediction
        """
        try:
            if not self.anthropic_client:
                raise ValueError("Claude client not initialized")
            
            # Generate primary performance prediction
            primary_prediction = await self._generate_performance_prediction(
                user_id, campaign_config, historical_data
            )
            
            # Generate alternative scenario predictions
            alternative_scenarios = await self._generate_alternative_scenarios(
                user_id, campaign_config, historical_data
            )
            
            # Generate optimization strategy
            optimization_strategy = await self._generate_optimization_strategy(
                campaign_config, primary_prediction, alternative_scenarios
            )
            
            # Calculate budget efficiency
            budget_efficiency = self._calculate_budget_efficiency(
                campaign_config, primary_prediction
            )
            
            campaign_prediction = CampaignPrediction(
                campaign_config=campaign_config,
                performance_prediction=primary_prediction,
                alternative_scenarios=alternative_scenarios,
                optimization_strategy=optimization_strategy,
                expected_budget_efficiency=budget_efficiency
            )
            
            # Store prediction for learning
            if user_id not in self.prediction_history:
                self.prediction_history[user_id] = []
            self.prediction_history[user_id].append(primary_prediction)
            
            logger.info(f"Generated campaign prediction for user {user_id}")
            return campaign_prediction
            
        except Exception as e:
            logger.error(f"Campaign performance prediction failed: {e}")
            raise
    
    async def _generate_performance_prediction(
        self,
        user_id: str,
        campaign_config: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> MLPrediction:
        """Generate primary performance prediction using Claude"""
        
        prompt = f"""
        As an advanced AI marketing analyst specializing in Indian digital marketing and Meta advertising, analyze this campaign configuration and predict detailed performance metrics.
        
        Campaign Configuration:
        {json.dumps(campaign_config, indent=2)}
        
        Historical Performance Data (if available):
        {json.dumps(historical_data[-5:] if historical_data else [], indent=2)}
        
        Indian Market Context:
        - Mobile-first audience (85%+ mobile usage)
        - UPI payment preference and digital trust factors
        - Price sensitivity and value-for-money messaging critical
        - Social proof and testimonials drive conversions
        - Regional diversity requires inclusive messaging
        - Meta/Instagram primary platforms for discovery
        - WhatsApp for customer service and follow-up
        - Festival seasons affect spending patterns
        - Family and community influence purchase decisions
        
        Provide comprehensive ML-style prediction analysis in JSON format:
        {{
            "predicted_metrics": {{
                "roi": "predicted ROI as float",
                "ctr": "predicted click-through rate as float",
                "conversion_rate": "predicted conversion rate as float", 
                "engagement_rate": "predicted engagement rate as float",
                "cost_per_click": "predicted CPC as float",
                "cost_per_conversion": "predicted cost per conversion as float"
            }},
            "confidence_level": "low/medium/high/very_high",
            "confidence_score": "0.0 to 1.0 float",
            "prediction_reasoning": "Detailed explanation of prediction methodology and key insights",
            "key_factors": [
                "Most important factors driving the prediction",
                "Platform-specific considerations",
                "Demographic alignment factors",
                "Content effectiveness indicators",
                "Budget optimization factors"
            ],
            "risk_factors": [
                "Potential risks that could lower performance",
                "Market-specific challenges",
                "Competition concerns"
            ],
            "optimization_opportunities": [
                "Specific ways to improve predicted performance",
                "Indian market optimization tactics",
                "Platform-specific enhancements"
            ],
            "recommended_adjustments": [
                "Immediate changes to improve results",
                "Budget reallocation suggestions",
                "Creative optimization recommendations"
            ],
            "expected_outcomes": {{
                "best_case": "Best realistic outcome",
                "most_likely": "Most probable outcome", 
                "worst_case": "Conservative outcome estimate"
            }}
        }}
        
        Consider:
        - Industry benchmarks for Indian market
        - Seasonal and cultural factors
        - Platform algorithm preferences
        - Audience behavior patterns
        - Creative fatigue potential
        - Budget efficiency optimization
        - Competitor landscape impact
        - Economic factors affecting spending
        """
        
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse Claude response
            import re
            content = response.content[0].text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                claude_prediction = json.loads(json_match.group())
                
                # Convert to structured prediction
                confidence_mapping = {
                    "low": ConfidenceLevel.LOW,
                    "medium": ConfidenceLevel.MEDIUM, 
                    "high": ConfidenceLevel.HIGH,
                    "very_high": ConfidenceLevel.VERY_HIGH
                }
                
                return MLPrediction(
                    prediction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    prediction_type=PredictionType.CAMPAIGN_PERFORMANCE,
                    predicted_metrics=claude_prediction.get("predicted_metrics", {}),
                    confidence_level=confidence_mapping.get(
                        claude_prediction.get("confidence_level", "medium"), 
                        ConfidenceLevel.MEDIUM
                    ),
                    confidence_score=float(claude_prediction.get("confidence_score", 0.7)),
                    prediction_reasoning=claude_prediction.get("prediction_reasoning", ""),
                    key_factors=claude_prediction.get("key_factors", []),
                    risk_factors=claude_prediction.get("risk_factors", []),
                    optimization_opportunities=claude_prediction.get("optimization_opportunities", []),
                    recommended_adjustments=claude_prediction.get("recommended_adjustments", []),
                    expected_outcomes=claude_prediction.get("expected_outcomes", {}),
                    input_features=campaign_config,
                    model_version=self.model_version
                )
                
        except Exception as e:
            logger.error(f"Claude performance prediction failed: {e}")
        
        # Fallback prediction
        return self._generate_fallback_prediction(user_id, campaign_config)
    
    async def _generate_alternative_scenarios(
        self,
        user_id: str,
        campaign_config: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> List[MLPrediction]:
        """Generate alternative scenario predictions"""
        
        scenarios = ["budget_optimized", "reach_maximized", "conversion_focused"]
        predictions = []
        
        for scenario in scenarios:
            try:
                prompt = f"""
                Generate a {scenario} alternative scenario for this campaign:
                
                Original Campaign: {json.dumps(campaign_config, indent=2)}
                
                For {scenario} scenario, suggest modifications and predict performance in JSON:
                {{
                    "scenario_modifications": {{
                        "budget_changes": "modifications to budget allocation",
                        "targeting_changes": "audience targeting adjustments",
                        "creative_changes": "content and creative modifications",
                        "platform_changes": "platform strategy adjustments"
                    }},
                    "predicted_metrics": {{
                        "roi": "float",
                        "ctr": "float", 
                        "conversion_rate": "float",
                        "engagement_rate": "float"
                    }},
                    "confidence_score": "0.0 to 1.0 float",
                    "scenario_reasoning": "Why this scenario would work",
                    "key_benefits": ["benefit1", "benefit2"],
                    "potential_drawbacks": ["drawback1", "drawback2"]
                }}
                
                Focus on Indian market optimization for {scenario} approach.
                """
                
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse response and create prediction
                import re
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    scenario_data = json.loads(json_match.group())
                    
                    prediction = MLPrediction(
                        prediction_id=str(uuid.uuid4()),
                        user_id=user_id,
                        prediction_type=PredictionType.CAMPAIGN_PERFORMANCE,
                        predicted_metrics=scenario_data.get("predicted_metrics", {}),
                        confidence_level=ConfidenceLevel.MEDIUM,
                        confidence_score=float(scenario_data.get("confidence_score", 0.6)),
                        prediction_reasoning=scenario_data.get("scenario_reasoning", ""),
                        key_factors=scenario_data.get("key_benefits", []),
                        risk_factors=scenario_data.get("potential_drawbacks", []),
                        optimization_opportunities=[f"{scenario}_optimization"],
                        recommended_adjustments=[],
                        expected_outcomes={scenario: scenario_data.get("scenario_reasoning", "")},
                        input_features={**campaign_config, "scenario_type": scenario},
                        model_version=self.model_version
                    )
                    
                    predictions.append(prediction)
                    
            except Exception as e:
                logger.error(f"Scenario {scenario} prediction failed: {e}")
        
        return predictions
    
    async def _generate_optimization_strategy(
        self,
        campaign_config: Dict[str, Any],
        primary_prediction: MLPrediction,
        alternatives: List[MLPrediction]
    ) -> str:
        """Generate overall optimization strategy"""
        
        try:
            prompt = f"""
            As a strategic marketing consultant for Indian businesses, create a comprehensive optimization strategy:
            
            Campaign Config: {json.dumps(campaign_config, indent=2)}
            Primary Prediction: {primary_prediction.predicted_metrics}
            Primary Confidence: {primary_prediction.confidence_score}
            
            Alternative Scenarios Available: {len(alternatives)}
            
            Create a strategic optimization plan that addresses:
            1. Immediate campaign launch strategy
            2. Performance monitoring checkpoints
            3. Optimization triggers and actions
            4. Budget reallocation strategy
            5. Creative refresh timeline
            6. Audience expansion approach
            7. Platform optimization tactics
            
            Focus on Indian market realities and Meta platform best practices.
            Provide actionable, specific guidance for campaign success.
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Optimization strategy generation failed: {e}")
            return "Standard optimization approach: monitor performance daily, optimize based on key metrics, adjust budget allocation based on performance."
    
    def _calculate_budget_efficiency(
        self,
        campaign_config: Dict[str, Any],
        prediction: MLPrediction
    ) -> float:
        """Calculate predicted budget efficiency"""
        
        try:
            budget = campaign_config.get("budget", 1000)
            predicted_roi = prediction.predicted_metrics.get("roi", 0)
            confidence = prediction.confidence_score
            
            # Efficiency = (ROI * confidence) / (budget/1000)
            # Normalized to 0-100 scale
            efficiency = (predicted_roi * confidence) / (budget / 1000)
            return min(max(efficiency, 0), 100)
            
        except Exception:
            return 50.0  # Neutral efficiency
    
    def _generate_fallback_prediction(
        self,
        user_id: str,
        campaign_config: Dict[str, Any]
    ) -> MLPrediction:
        """Generate fallback prediction when Claude fails"""
        
        # Basic heuristic-based predictions
        budget = campaign_config.get("budget", 1000)
        
        # Simple budget-based estimates
        base_roi = 8.0 if budget > 5000 else 6.0
        base_ctr = 2.5 if budget > 2000 else 2.0
        base_conversion = 8.0
        
        return MLPrediction(
            prediction_id=str(uuid.uuid4()),
            user_id=user_id,
            prediction_type=PredictionType.CAMPAIGN_PERFORMANCE,
            predicted_metrics={
                "roi": base_roi,
                "ctr": base_ctr,
                "conversion_rate": base_conversion,
                "engagement_rate": 3.5,
                "cost_per_click": budget * 0.02,
                "cost_per_conversion": budget * 0.15
            },
            confidence_level=ConfidenceLevel.LOW,
            confidence_score=0.4,
            prediction_reasoning="Fallback prediction based on basic heuristics",
            key_factors=["Budget level", "Industry average"],
            risk_factors=["Limited data available"],
            optimization_opportunities=["Gather more campaign data", "Run A/B tests"],
            recommended_adjustments=["Start with conservative budget", "Monitor closely"],
            expected_outcomes={
                "fallback": "Basic performance expectations based on budget"
            },
            input_features=campaign_config,
            model_version="fallback_v1.0"
        )
    
    async def predict_viral_potential(
        self,
        user_id: str,
        content_config: Dict[str, Any]
    ) -> MLPrediction:
        """Predict viral potential of content using Claude analysis"""
        
        try:
            if not self.anthropic_client:
                raise ValueError("Claude client not initialized")
            
            prompt = f"""
            As a viral marketing expert for Indian social media, analyze this content's viral potential:
            
            Content Configuration:
            {json.dumps(content_config, indent=2)}
            
            Viral Factors for Indian Market:
            - Emotional resonance (family, success, aspiration)
            - Cultural relevance and festival timing
            - Language accessibility (Hindi-English mix)
            - Visual appeal for mobile viewing
            - Shareability quotient (WhatsApp, Instagram Stories)
            - Trend alignment and hashtag potential
            - Influencer collaboration potential
            - Community engagement likelihood
            
            Predict viral potential in JSON format:
            {{
                "viral_score": "0-100 viral potential score",
                "predicted_metrics": {{
                    "estimated_reach": "predicted organic reach",
                    "share_rate": "predicted share percentage", 
                    "engagement_rate": "predicted engagement rate",
                    "comment_rate": "predicted comment rate"
                }},
                "confidence_score": "0.0 to 1.0",
                "viral_factors": ["factors that boost viral potential"],
                "limiting_factors": ["factors that limit viral spread"],
                "optimization_suggestions": ["ways to increase viral potential"],
                "timing_recommendations": "best time/season for launch",
                "platform_strategy": "optimal platform distribution strategy"
            }}
            
            Focus on Indian social media behavior and Meta platform dynamics.
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
                viral_data = json.loads(json_match.group())
                
                return MLPrediction(
                    prediction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    prediction_type=PredictionType.VIRAL_POTENTIAL,
                    predicted_metrics=viral_data.get("predicted_metrics", {}),
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=float(viral_data.get("confidence_score", 0.7)),
                    prediction_reasoning=f"Viral score: {viral_data.get('viral_score', 50)}/100",
                    key_factors=viral_data.get("viral_factors", []),
                    risk_factors=viral_data.get("limiting_factors", []),
                    optimization_opportunities=viral_data.get("optimization_suggestions", []),
                    recommended_adjustments=[viral_data.get("timing_recommendations", "")],
                    expected_outcomes={"viral_strategy": viral_data.get("platform_strategy", "")},
                    input_features=content_config,
                    model_version=self.model_version
                )
                
        except Exception as e:
            logger.error(f"Viral potential prediction failed: {e}")
        
        # Fallback viral prediction
        return MLPrediction(
            prediction_id=str(uuid.uuid4()),
            user_id=user_id,
            prediction_type=PredictionType.VIRAL_POTENTIAL,
            predicted_metrics={
                "estimated_reach": 1000,
                "share_rate": 2.0,
                "engagement_rate": 4.0,
                "comment_rate": 1.5
            },
            confidence_level=ConfidenceLevel.LOW,
            confidence_score=0.4,
            prediction_reasoning="Basic viral potential assessment",
            key_factors=["Content quality", "Timing"],
            risk_factors=["Limited viral indicators"],
            optimization_opportunities=["Enhance emotional appeal", "Improve shareability"],
            recommended_adjustments=["Test with small audience first"],
            expected_outcomes={"basic": "Standard organic reach expected"},
            input_features=content_config,
            model_version="fallback_v1.0"
        )
    
    async def get_prediction_insights(
        self,
        user_id: str,
        prediction_type: Optional[PredictionType] = None
    ) -> Dict[str, Any]:
        """Get insights from historical predictions"""
        
        try:
            user_predictions = self.prediction_history.get(user_id, [])
            
            if prediction_type:
                user_predictions = [
                    p for p in user_predictions 
                    if p.prediction_type == prediction_type
                ]
            
            if not user_predictions:
                return {"message": "No prediction history available"}
            
            # Calculate accuracy and insights
            total_predictions = len(user_predictions)
            avg_confidence = statistics.mean([p.confidence_score for p in user_predictions])
            
            # Get most common factors and opportunities
            all_factors = []
            all_opportunities = []
            
            for prediction in user_predictions:
                all_factors.extend(prediction.key_factors)
                all_opportunities.extend(prediction.optimization_opportunities)
            
            from collections import Counter
            top_factors = Counter(all_factors).most_common(5)
            top_opportunities = Counter(all_opportunities).most_common(5)
            
            return {
                "user_id": user_id,
                "total_predictions": total_predictions,
                "average_confidence": avg_confidence,
                "confidence_trend": self._calculate_confidence_trend(user_predictions),
                "top_success_factors": [factor for factor, count in top_factors],
                "top_optimization_opportunities": [opp for opp, count in top_opportunities],
                "recent_predictions": [
                    {
                        "id": p.prediction_id,
                        "type": p.prediction_type.value,
                        "confidence": p.confidence_score,
                        "key_metric": p.predicted_metrics.get("roi", 0),
                        "date": p.created_at.isoformat()
                    }
                    for p in user_predictions[-5:]
                ],
                "model_performance": {
                    "version": self.model_version,
                    "predictions_made": total_predictions,
                    "average_confidence": avg_confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction insights: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence_trend(self, predictions: List[MLPrediction]) -> str:
        """Calculate confidence trend over time"""
        
        if len(predictions) < 3:
            return "insufficient_data"
        
        recent_confidence = statistics.mean([p.confidence_score for p in predictions[-3:]])
        older_confidence = statistics.mean([p.confidence_score for p in predictions[:-3]])
        
        if recent_confidence > older_confidence + 0.1:
            return "improving"
        elif recent_confidence < older_confidence - 0.1:
            return "declining"
        else:
            return "stable"

# Example usage
async def main():
    """Test the Claude ML predictor"""
    print("🧠 Claude ML Predictor Test")
    print("=" * 40)
    
    predictor = ClaudeMLPredictor()
    
    # Sample campaign configuration
    campaign_config = {
        "industry": "fitness",
        "business_name": "FitLife Studio",
        "campaign_objective": "lead_generation",
        "target_demographics": ["millennial", "gen_z"],
        "platforms": ["instagram", "facebook"], 
        "budget": 5000,
        "duration_days": 14,
        "content_type": "video",
        "visual_style": "modern_energetic",
        "target_interests": ["fitness", "health", "wellness"],
        "geographic_targeting": ["mumbai", "delhi", "bangalore"]
    }
    
    # Sample historical data
    historical_data = [
        {"campaign_id": "camp1", "roi": 12.5, "ctr": 3.2, "conversion_rate": 8.5},
        {"campaign_id": "camp2", "roi": 15.2, "ctr": 2.8, "conversion_rate": 9.1},
        {"campaign_id": "camp3", "roi": 9.8, "ctr": 3.5, "conversion_rate": 7.2}
    ]
    
    # Generate campaign prediction
    prediction = await predictor.predict_campaign_performance(
        user_id="user_123",
        campaign_config=campaign_config,
        historical_data=historical_data
    )
    
    print(f"✅ Campaign Prediction Generated:")
    print(f"   ROI Prediction: {prediction.performance_prediction.predicted_metrics.get('roi', 'N/A')}")
    print(f"   Confidence: {prediction.performance_prediction.confidence_level.value}")
    print(f"   Budget Efficiency: {prediction.expected_budget_efficiency:.1f}%")
    print(f"   Alternative Scenarios: {len(prediction.alternative_scenarios)}")
    
    print(f"\n🎯 Key Success Factors:")
    for factor in prediction.performance_prediction.key_factors[:3]:
        print(f"   • {factor}")
    
    print(f"\n⚠️ Risk Factors:")
    for risk in prediction.performance_prediction.risk_factors[:3]:
        print(f"   • {risk}")
    
    # Test viral potential prediction
    content_config = {
        "content_type": "video",
        "topic": "30-day fitness transformation",
        "style": "before_after_testimonial",
        "duration": 15,
        "language": "hinglish",
        "target_emotion": "inspiration"
    }
    
    viral_prediction = await predictor.predict_viral_potential("user_123", content_config)
    
    print(f"\n🚀 Viral Potential Analysis:")
    print(f"   Predicted Reach: {viral_prediction.predicted_metrics.get('estimated_reach', 'N/A')}")
    print(f"   Share Rate: {viral_prediction.predicted_metrics.get('share_rate', 'N/A')}%")
    print(f"   Confidence: {viral_prediction.confidence_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())