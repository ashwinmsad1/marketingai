"""
ML Prediction Service
Professional wrapper around ClaudeMLPredictor with database integration, caching, and error handling
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session

from backend.ml.learning.claude_ml_predictor import (
    ClaudeMLPredictor, CampaignPrediction, MLPrediction,
    PredictionType, ConfidenceLevel
)
from backend.database.crud import MLPredictionCRUD
from backend.database.models import (
    MLPredictionResult, CampaignPredictionScenario, MLPredictionCache,
    MLPredictionType, ConfidenceLevel as DBConfidenceLevel
)
from backend.core.config import settings
from .ai_decision_validator import AIDecision, ai_decision_validator, PredictionType as ValidatorPredictionType
from .ai_monitoring_service import ai_monitoring_service

logger = logging.getLogger(__name__)

class MLPredictionService:
    """
    Production-ready ML Prediction Service that wraps ClaudeMLPredictor
    with database integration, caching, and comprehensive error handling
    """
    
    def __init__(self):
        """Initialize ML prediction service"""
        self.claude_predictor = ClaudeMLPredictor()
        self.cache_ttl_hours = 24  # Default cache TTL
        self.max_cache_entries_per_user = 100
        
        # Mapping between predictor enums and database enums
        self.confidence_mapping = {
            ConfidenceLevel.LOW: DBConfidenceLevel.LOW,
            ConfidenceLevel.MEDIUM: DBConfidenceLevel.MEDIUM,
            ConfidenceLevel.HIGH: DBConfidenceLevel.HIGH,
            ConfidenceLevel.VERY_HIGH: DBConfidenceLevel.VERY_HIGH
        }
        
        # Validation settings
        self.enable_validation = True
        self.validation_failure_fallback = True
        
        self.prediction_type_mapping = {
            PredictionType.CAMPAIGN_PERFORMANCE: MLPredictionType.CAMPAIGN_PERFORMANCE,
            PredictionType.VIRAL_POTENTIAL: MLPredictionType.VIRAL_POTENTIAL,
            PredictionType.AUDIENCE_RESPONSE: MLPredictionType.AUDIENCE_RESPONSE,
            PredictionType.CONTENT_EFFECTIVENESS: MLPredictionType.CONTENT_EFFECTIVENESS,
            PredictionType.BUDGET_OPTIMIZATION: MLPredictionType.BUDGET_OPTIMIZATION
        }
    
    async def predict_campaign_performance(
        self,
        user_id: str,
        campaign_config: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        db: Optional[Session] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Predict campaign performance with caching and database integration
        
        Args:
            user_id: User identifier
            campaign_config: Campaign configuration for prediction
            historical_data: Optional historical campaign data
            db: Database session
            use_cache: Whether to use/store cache
            
        Returns:
            Comprehensive prediction results with scenarios
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(
                user_id, campaign_config, "campaign_performance"
            )
            
            # Check cache first
            if use_cache and db:
                cached_result = self._get_cached_prediction(db, cache_key, user_id)
                if cached_result:
                    logger.info(f"Returning cached campaign prediction for user {user_id}")
                    return self._format_cached_prediction(cached_result)
            
            # Generate new prediction using Claude
            campaign_prediction = await self.claude_predictor.predict_campaign_performance(
                user_id=user_id,
                campaign_config=campaign_config,
                historical_data=historical_data
            )
            
            # Store prediction in database if db session provided
            prediction_result = None
            if db:
                prediction_result = self._store_prediction_in_db(
                    db, campaign_prediction.performance_prediction, user_id
                )
                
                # Store alternative scenarios
                if campaign_prediction.alternative_scenarios:
                    self._store_scenarios_in_db(
                        db, prediction_result.id, campaign_prediction.alternative_scenarios, user_id
                    )
                
                # Cache the result
                if use_cache:
                    self._cache_prediction(
                        db, cache_key, user_id, campaign_prediction, MLPredictionType.CAMPAIGN_PERFORMANCE
                    )
            
            # Validate AI decision before returning
            if self.enable_validation and campaign_prediction:
                validation_result = await self._validate_ai_decision(
                    user_id, campaign_prediction, ValidatorPredictionType.ROI, db
                )
                
                # If validation fails and we have fallback enabled
                if not validation_result.is_valid and self.validation_failure_fallback:
                    logger.warning(f"AI validation failed for user {user_id}, using fallback prediction")
                    fallback = await self._generate_fallback_prediction(
                        user_id, campaign_config, "campaign_performance"
                    )
                    return {
                        "success": True,
                        "validation_failed": True,
                        "prediction": fallback,
                        "warnings": validation_result.warnings,
                        "recommendations": validation_result.recommendations
                    }
                
                # Add validation context to response
                response = self._format_campaign_prediction_response(
                    campaign_prediction, prediction_result, validation_result
                )
            else:
                # Format response without validation
                response = self._format_campaign_prediction_response(
                    campaign_prediction, prediction_result
                )
            
            logger.info(f"Generated campaign performance prediction for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in predict_campaign_performance: {e}")
            # Return fallback prediction
            fallback = await self._generate_fallback_prediction(
                user_id, campaign_config, "campaign_performance"
            )
            return {
                "success": False,
                "error": str(e),
                "fallback_prediction": fallback,
                "message": "Using fallback prediction due to ML service error"
            }
    
    async def predict_viral_potential(
        self,
        user_id: str,
        content_config: Dict[str, Any],
        db: Optional[Session] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Predict viral potential of content with caching
        
        Args:
            user_id: User identifier
            content_config: Content configuration for prediction
            db: Database session
            use_cache: Whether to use/store cache
            
        Returns:
            Viral potential prediction results
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(
                user_id, content_config, "viral_potential"
            )
            
            # Check cache first
            if use_cache and db:
                cached_result = self._get_cached_prediction(db, cache_key, user_id)
                if cached_result:
                    logger.info(f"Returning cached viral prediction for user {user_id}")
                    return self._format_cached_prediction(cached_result)
            
            # Generate new prediction using Claude
            viral_prediction = await self.claude_predictor.predict_viral_potential(
                user_id=user_id,
                content_config=content_config
            )
            
            # Store prediction in database
            prediction_result = None
            if db:
                prediction_result = self._store_prediction_in_db(
                    db, viral_prediction, user_id
                )
                
                # Cache the result
                if use_cache:
                    self._cache_prediction(
                        db, cache_key, user_id, viral_prediction, MLPredictionType.VIRAL_POTENTIAL
                    )
            
            # Format response
            response = self._format_viral_prediction_response(
                viral_prediction, prediction_result
            )
            
            logger.info(f"Generated viral potential prediction for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in predict_viral_potential: {e}")
            # Return fallback prediction
            fallback = await self._generate_fallback_prediction(
                user_id, content_config, "viral_potential"
            )
            return {
                "success": False,
                "error": str(e),
                "fallback_prediction": fallback,
                "message": "Using fallback prediction due to ML service error"
            }
    
    async def get_prediction_insights(
        self,
        user_id: str,
        prediction_type: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive prediction insights from both Claude and database
        
        Args:
            user_id: User identifier
            prediction_type: Optional filter by prediction type
            db: Database session
            
        Returns:
            Combined insights from ML predictor and database
        """
        try:
            # Get insights from Claude ML predictor
            predictor_type = None
            if prediction_type:
                type_mapping = {
                    "campaign_performance": PredictionType.CAMPAIGN_PERFORMANCE,
                    "viral_potential": PredictionType.VIRAL_POTENTIAL,
                    "audience_response": PredictionType.AUDIENCE_RESPONSE,
                    "content_effectiveness": PredictionType.CONTENT_EFFECTIVENESS,
                    "budget_optimization": PredictionType.BUDGET_OPTIMIZATION
                }
                predictor_type = type_mapping.get(prediction_type)
            
            # Get insights from Claude predictor
            claude_insights = await self.claude_predictor.get_prediction_insights(
                user_id=user_id,
                prediction_type=predictor_type
            )
            
            # Get database insights if available
            db_insights = {}
            if db:
                db_insights = self._get_database_insights(db, user_id, prediction_type)
            
            # Combine insights
            combined_insights = {
                "user_id": user_id,
                "claude_insights": claude_insights,
                "database_insights": db_insights,
                "prediction_service_info": {
                    "service_version": "v1.0",
                    "cache_enabled": True,
                    "cache_ttl_hours": self.cache_ttl_hours,
                    "fallback_enabled": True
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return combined_insights
            
        except Exception as e:
            logger.error(f"Error getting prediction insights: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "message": "Failed to retrieve prediction insights"
            }
    
    async def update_prediction_accuracy(
        self,
        prediction_id: str,
        actual_metrics: Dict[str, float],
        db: Session
    ) -> Dict[str, Any]:
        """
        Update prediction accuracy when actual results are available
        
        Args:
            prediction_id: Prediction identifier
            actual_metrics: Actual campaign results
            db: Database session
            
        Returns:
            Update result and accuracy calculation
        """
        try:
            # Calculate accuracy score
            accuracy_score = self._calculate_prediction_accuracy(
                prediction_id, actual_metrics, db
            )
            
            # Update in database
            updated_prediction = MLPredictionCRUD.update_prediction_accuracy(
                db=db,
                prediction_id=prediction_id,
                actual_metrics=actual_metrics,
                prediction_accuracy_score=accuracy_score
            )
            
            if not updated_prediction:
                return {"error": "Prediction not found"}
            
            logger.info(f"Updated prediction accuracy for {prediction_id}: {accuracy_score:.3f}")
            
            return {
                "success": True,
                "prediction_id": prediction_id,
                "accuracy_score": accuracy_score,
                "updated_at": updated_prediction.updated_at.isoformat(),
                "message": f"Prediction accuracy updated: {accuracy_score:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Error updating prediction accuracy: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_cache(
        self,
        db: Session,
        user_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Clean up expired cache entries
        
        Args:
            db: Database session
            user_id: Optional user filter
            
        Returns:
            Cleanup statistics
        """
        try:
            expired_count = MLPredictionCRUD.cleanup_expired_cache(db, user_id)
            
            logger.info(f"Cleaned up {expired_count} expired cache entries")
            
            return {
                "cleaned_up": expired_count,
                "user_filter": user_id,
                "cleanup_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return {"error": str(e), "cleaned_up": 0}
    
    def _generate_cache_key(
        self,
        user_id: str,
        config: Dict[str, Any],
        prediction_type: str
    ) -> str:
        """Generate unique cache key for prediction"""
        # Create deterministic hash of config
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        
        return f"ml_pred_{user_id}_{prediction_type}_{config_hash}"
    
    def _get_cached_prediction(
        self,
        db: Session,
        cache_key: str,
        user_id: str
    ) -> Optional[MLPredictionCache]:
        """Get cached prediction if valid"""
        try:
            cache_entry = MLPredictionCRUD.get_cache_entry(db, cache_key, user_id)
            
            if cache_entry:
                # Update hit count
                MLPredictionCRUD.update_cache_hit(db, cache_entry.id)
                return cache_entry
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
            return None
    
    def _cache_prediction(
        self,
        db: Session,
        cache_key: str,
        user_id: str,
        prediction: Union[CampaignPrediction, MLPrediction],
        prediction_type: MLPredictionType
    ) -> None:
        """Cache prediction result"""
        try:
            # Generate input hash
            if isinstance(prediction, CampaignPrediction):
                input_data = prediction.campaign_config
                pred_data = prediction.performance_prediction
            else:
                input_data = prediction.input_features
                pred_data = prediction
            
            input_hash = hashlib.md5(
                json.dumps(input_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Prepare cache data
            cache_data = {
                "prediction_id": pred_data.prediction_id,
                "predicted_metrics": pred_data.predicted_metrics,
                "confidence_level": pred_data.confidence_level.value,
                "confidence_score": pred_data.confidence_score,
                "prediction_reasoning": pred_data.prediction_reasoning,
                "key_factors": pred_data.key_factors,
                "optimization_opportunities": pred_data.optimization_opportunities,
                "model_version": pred_data.model_version
            }
            
            # Add campaign prediction specific data
            if isinstance(prediction, CampaignPrediction):
                cache_data.update({
                    "alternative_scenarios": len(prediction.alternative_scenarios),
                    "optimization_strategy": prediction.optimization_strategy,
                    "budget_efficiency": prediction.expected_budget_efficiency
                })
            
            # Set expiration time
            expires_at = datetime.utcnow() + timedelta(hours=self.cache_ttl_hours)
            
            # Create cache entry
            MLPredictionCRUD.create_cache_entry(
                db=db,
                cache_key=cache_key,
                user_id=user_id,
                prediction_type=prediction_type,
                input_hash=input_hash,
                prediction_data=cache_data,
                expires_at=expires_at,
                model_version=pred_data.model_version
            )
            
            logger.debug(f"Cached prediction {pred_data.prediction_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error caching prediction: {e}")
            # Don't fail the main operation if caching fails
    
    def _store_prediction_in_db(
        self,
        db: Session,
        prediction: MLPrediction,
        user_id: str
    ) -> MLPredictionResult:
        """Store prediction result in database"""
        try:
            # Map confidence level
            db_confidence = self.confidence_mapping.get(
                prediction.confidence_level, DBConfidenceLevel.MEDIUM
            )
            
            # Map prediction type
            db_prediction_type = self.prediction_type_mapping.get(
                prediction.prediction_type, MLPredictionType.CAMPAIGN_PERFORMANCE
            )
            
            # Create database record
            prediction_result = MLPredictionCRUD.create_prediction_result(
                db=db,
                prediction_id=prediction.prediction_id,
                user_id=user_id,
                prediction_type=db_prediction_type,
                input_features=prediction.input_features,
                predicted_metrics=prediction.predicted_metrics,
                confidence_level=db_confidence,
                confidence_score=prediction.confidence_score,
                prediction_reasoning=prediction.prediction_reasoning,
                key_factors=prediction.key_factors,
                risk_factors=prediction.risk_factors,
                optimization_opportunities=prediction.optimization_opportunities,
                recommended_adjustments=prediction.recommended_adjustments,
                expected_outcomes=prediction.expected_outcomes,
                model_version=prediction.model_version,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error storing prediction in database: {e}")
            raise
    
    def _store_scenarios_in_db(
        self,
        db: Session,
        prediction_result_id: str,
        scenarios: List[MLPrediction],
        user_id: str
    ) -> None:
        """Store alternative scenarios in database"""
        try:
            for i, scenario in enumerate(scenarios):
                scenario_name = f"scenario_{i+1}"
                if "budget_optimized" in str(scenario.input_features):
                    scenario_name = "budget_optimized"
                elif "reach_maximized" in str(scenario.input_features):
                    scenario_name = "reach_maximized"
                elif "conversion_focused" in str(scenario.input_features):
                    scenario_name = "conversion_focused"
                
                MLPredictionCRUD.create_prediction_scenario(
                    db=db,
                    prediction_result_id=prediction_result_id,
                    scenario_id=scenario.prediction_id,
                    user_id=user_id,
                    scenario_name=scenario_name,
                    scenario_description=scenario.prediction_reasoning,
                    modified_metrics=scenario.predicted_metrics,
                    scenario_reasoning=scenario.prediction_reasoning,
                    key_benefits=scenario.key_factors,
                    potential_drawbacks=scenario.risk_factors,
                    priority_ranking=i + 1
                )
                
        except Exception as e:
            logger.error(f"Error storing scenarios: {e}")
            # Don't fail main operation if scenario storage fails
    
    def _format_campaign_prediction_response(
        self,
        prediction: CampaignPrediction,
        db_result: Optional[MLPredictionResult] = None
    ) -> Dict[str, Any]:
        """Format campaign prediction for API response"""
        response = {
            "success": True,
            "prediction_id": prediction.performance_prediction.prediction_id,
            "prediction_type": "campaign_performance",
            "campaign_config": prediction.campaign_config,
            
            # Primary prediction
            "primary_prediction": {
                "predicted_metrics": prediction.performance_prediction.predicted_metrics,
                "confidence_level": prediction.performance_prediction.confidence_level.value,
                "confidence_score": prediction.performance_prediction.confidence_score,
                "prediction_reasoning": prediction.performance_prediction.prediction_reasoning,
                "key_factors": prediction.performance_prediction.key_factors,
                "risk_factors": prediction.performance_prediction.risk_factors,
                "optimization_opportunities": prediction.performance_prediction.optimization_opportunities,
                "recommended_adjustments": prediction.performance_prediction.recommended_adjustments,
                "expected_outcomes": prediction.performance_prediction.expected_outcomes
            },
            
            # Alternative scenarios
            "alternative_scenarios": [
                {
                    "scenario_id": scenario.prediction_id,
                    "predicted_metrics": scenario.predicted_metrics,
                    "confidence_score": scenario.confidence_score,
                    "reasoning": scenario.prediction_reasoning,
                    "key_factors": scenario.key_factors,
                    "risk_factors": scenario.risk_factors
                }
                for scenario in prediction.alternative_scenarios
            ],
            
            # Strategy and optimization
            "optimization_strategy": prediction.optimization_strategy,
            "expected_budget_efficiency": prediction.expected_budget_efficiency,
            
            # Metadata
            "model_version": prediction.performance_prediction.model_version,
            "created_at": prediction.created_at.isoformat(),
            "database_id": db_result.id if db_result else None,
            "cached": False
        }
        
        return response
    
    def _format_viral_prediction_response(
        self,
        prediction: MLPrediction,
        db_result: Optional[MLPredictionResult] = None
    ) -> Dict[str, Any]:
        """Format viral prediction for API response"""
        response = {
            "success": True,
            "prediction_id": prediction.prediction_id,
            "prediction_type": "viral_potential",
            
            # Prediction results
            "predicted_metrics": prediction.predicted_metrics,
            "confidence_level": prediction.confidence_level.value,
            "confidence_score": prediction.confidence_score,
            "prediction_reasoning": prediction.prediction_reasoning,
            
            # Viral-specific insights
            "viral_factors": prediction.key_factors,
            "limiting_factors": prediction.risk_factors,
            "optimization_opportunities": prediction.optimization_opportunities,
            "recommended_adjustments": prediction.recommended_adjustments,
            "expected_outcomes": prediction.expected_outcomes,
            
            # Metadata
            "input_features": prediction.input_features,
            "model_version": prediction.model_version,
            "created_at": prediction.created_at.isoformat(),
            "database_id": db_result.id if db_result else None,
            "cached": False
        }
        
        return response
    
    def _format_cached_prediction(
        self,
        cache_entry: MLPredictionCache
    ) -> Dict[str, Any]:
        """Format cached prediction for API response"""
        cached_data = cache_entry.prediction_data
        
        response = {
            "success": True,
            "prediction_id": cached_data.get("prediction_id"),
            "prediction_type": cache_entry.prediction_type.value,
            "predicted_metrics": cached_data.get("predicted_metrics", {}),
            "confidence_level": cached_data.get("confidence_level", "medium"),
            "confidence_score": cached_data.get("confidence_score", 0.5),
            "prediction_reasoning": cached_data.get("prediction_reasoning", ""),
            "key_factors": cached_data.get("key_factors", []),
            "optimization_opportunities": cached_data.get("optimization_opportunities", []),
            "model_version": cached_data.get("model_version", "cached"),
            "cached": True,
            "cache_hit_count": cache_entry.hit_count,
            "cached_at": cache_entry.created_at.isoformat(),
            "last_accessed": cache_entry.last_accessed.isoformat()
        }
        
        # Add campaign-specific cached data
        if "alternative_scenarios" in cached_data:
            response["alternative_scenarios_count"] = cached_data["alternative_scenarios"]
            response["optimization_strategy"] = cached_data.get("optimization_strategy", "")
            response["expected_budget_efficiency"] = cached_data.get("budget_efficiency", 0)
        
        return response
    
    def _get_database_insights(
        self,
        db: Session,
        user_id: str,
        prediction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get insights from database predictions"""
        try:
            # Map prediction type
            ml_prediction_type = None
            if prediction_type:
                type_mapping = {
                    "campaign_performance": MLPredictionType.CAMPAIGN_PERFORMANCE,
                    "viral_potential": MLPredictionType.VIRAL_POTENTIAL,
                    "audience_response": MLPredictionType.AUDIENCE_RESPONSE,
                    "content_effectiveness": MLPredictionType.CONTENT_EFFECTIVENESS,
                    "budget_optimization": MLPredictionType.BUDGET_OPTIMIZATION
                }
                ml_prediction_type = type_mapping.get(prediction_type)
            
            # Get accuracy trends
            accuracy_trends = MLPredictionCRUD.get_prediction_accuracy_trends(
                db=db, user_id=user_id, days=30
            )
            
            # Get feedback statistics
            feedback_stats = MLPredictionCRUD.get_prediction_feedback_stats(
                db=db, user_id=user_id, prediction_type=ml_prediction_type
            )
            
            # Get user predictions count
            user_predictions = MLPredictionCRUD.get_user_predictions(
                db=db, user_id=user_id, prediction_type=ml_prediction_type, limit=1000
            )
            
            return {
                "total_predictions": len(user_predictions),
                "accuracy_trends": accuracy_trends,
                "feedback_statistics": feedback_stats,
                "prediction_types_used": list(set(p.prediction_type.value for p in user_predictions)),
                "date_range": {
                    "earliest": min(p.created_at for p in user_predictions).isoformat() if user_predictions else None,
                    "latest": max(p.created_at for p in user_predictions).isoformat() if user_predictions else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting database insights: {e}")
            return {"error": str(e)}
    
    def _calculate_prediction_accuracy(
        self,
        prediction_id: str,
        actual_metrics: Dict[str, float],
        db: Session
    ) -> float:
        """Calculate prediction accuracy score"""
        try:
            # Get original prediction
            prediction = MLPredictionCRUD.get_prediction_by_id(db, prediction_id)
            if not prediction:
                return 0.0
            
            predicted_metrics = prediction.predicted_metrics
            
            # Calculate accuracy for each metric
            accuracies = []
            for metric, actual_value in actual_metrics.items():
                if metric in predicted_metrics:
                    predicted_value = predicted_metrics[metric]
                    if predicted_value > 0:
                        # Calculate percentage error
                        error = abs(actual_value - predicted_value) / predicted_value
                        accuracy = max(0, 1 - error)  # Accuracy between 0 and 1
                        accuracies.append(accuracy)
            
            # Return average accuracy
            return sum(accuracies) / len(accuracies) if accuracies else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating prediction accuracy: {e}")
            return 0.0
    
    async def _generate_fallback_prediction(
        self,
        user_id: str,
        config: Dict[str, Any],
        prediction_type: str
    ) -> Dict[str, Any]:
        """Generate fallback prediction when Claude ML fails"""
        try:
            if prediction_type == "campaign_performance":
                return self._generate_campaign_fallback(user_id, config)
            elif prediction_type == "viral_potential":
                return self._generate_viral_fallback(user_id, config)
            else:
                return self._generate_generic_fallback(user_id, config, prediction_type)
                
        except Exception as e:
            logger.error(f"Error generating fallback prediction: {e}")
            return {
                "prediction_id": f"fallback_{user_id}_{prediction_type}",
                "predicted_metrics": {"roi": 5.0, "ctr": 2.0, "conversion_rate": 5.0},
                "confidence_level": "low",
                "confidence_score": 0.3,
                "prediction_reasoning": "Basic fallback prediction due to service error",
                "key_factors": ["Service unavailable"],
                "optimization_opportunities": ["Retry when service is available"],
                "model_version": "fallback_v1.0",
                "is_fallback": True
            }
    
    def _generate_campaign_fallback(
        self,
        user_id: str,
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback campaign prediction"""
        budget = campaign_config.get("budget", 1000)
        industry = campaign_config.get("industry", "general")
        
        # Industry-based adjustments
        industry_multipliers = {
            "fitness": {"roi": 1.2, "ctr": 1.1, "conversion": 0.9},
            "restaurant": {"roi": 0.9, "ctr": 1.3, "conversion": 1.0},
            "beauty": {"roi": 1.1, "ctr": 1.2, "conversion": 1.1},
            "real_estate": {"roi": 1.3, "ctr": 0.8, "conversion": 0.8},
            "general": {"roi": 1.0, "ctr": 1.0, "conversion": 1.0}
        }
        
        multiplier = industry_multipliers.get(industry, industry_multipliers["general"])
        
        # Budget-based base metrics
        base_roi = 8.0 if budget > 5000 else 6.0
        base_ctr = 2.5 if budget > 2000 else 2.0
        base_conversion = 7.0
        
        return {
            "prediction_id": f"fallback_campaign_{user_id}",
            "predicted_metrics": {
                "roi": round(base_roi * multiplier["roi"], 2),
                "ctr": round(base_ctr * multiplier["ctr"], 2),
                "conversion_rate": round(base_conversion * multiplier["conversion"], 2),
                "engagement_rate": 3.5,
                "cost_per_click": round(budget * 0.02, 2),
                "cost_per_conversion": round(budget * 0.15, 2)
            },
            "confidence_level": "low",
            "confidence_score": 0.4,
            "prediction_reasoning": f"Fallback prediction for {industry} industry with ${budget} budget",
            "key_factors": [
                f"Industry: {industry}",
                f"Budget level: ${budget}",
                "Historical industry averages"
            ],
            "optimization_opportunities": [
                "Use ML predictions when service is available",
                "Gather more campaign data for better predictions",
                "Test different audience segments"
            ],
            "model_version": "fallback_v1.0",
            "is_fallback": True
        }
    
    def _generate_viral_fallback(
        self,
        user_id: str,
        content_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback viral prediction"""
        content_type = content_config.get("content_type", "image")
        
        # Content type adjustments
        type_multipliers = {
            "video": {"reach": 2.0, "share": 1.5, "engagement": 1.3},
            "image": {"reach": 1.0, "share": 1.0, "engagement": 1.0},
            "text": {"reach": 0.7, "share": 0.8, "engagement": 0.9}
        }
        
        multiplier = type_multipliers.get(content_type, type_multipliers["image"])
        
        return {
            "prediction_id": f"fallback_viral_{user_id}",
            "predicted_metrics": {
                "estimated_reach": int(1000 * multiplier["reach"]),
                "share_rate": round(2.0 * multiplier["share"], 2),
                "engagement_rate": round(4.0 * multiplier["engagement"], 2),
                "comment_rate": 1.5,
                "viral_coefficient": 0.3
            },
            "confidence_level": "low",
            "confidence_score": 0.35,
            "prediction_reasoning": f"Fallback viral prediction for {content_type} content",
            "viral_factors": [
                f"Content type: {content_type}",
                "General content quality assumptions"
            ],
            "limiting_factors": [
                "Limited analysis due to service unavailability",
                "Generic predictions without AI insights"
            ],
            "optimization_opportunities": [
                "Use full ML predictions when service is available",
                "Test content with small audience first",
                "Optimize for platform-specific features"
            ],
            "model_version": "fallback_v1.0",
            "is_fallback": True
        }
    
    def _generate_generic_fallback(
        self,
        user_id: str,
        config: Dict[str, Any],
        prediction_type: str
    ) -> Dict[str, Any]:
        """Generate generic fallback prediction"""
        return {
            "prediction_id": f"fallback_{prediction_type}_{user_id}",
            "predicted_metrics": {
                "performance_score": 60.0,
                "confidence_interval": [40.0, 80.0],
                "expected_range": "moderate"
            },
            "confidence_level": "low",
            "confidence_score": 0.3,
            "prediction_reasoning": f"Generic fallback prediction for {prediction_type}",
            "key_factors": ["Service unavailable", "Using basic heuristics"],
            "optimization_opportunities": [
                "Enable ML predictions for better insights",
                "Gather more data for analysis"
            ],
            "model_version": "fallback_v1.0",
            "is_fallback": True
        }
    
    async def _validate_ai_decision(
        self,
        user_id: str,
        prediction: Any,
        prediction_type: ValidatorPredictionType,
        db: Optional[Session] = None
    ) -> Any:
        """Validate AI decision using the AI Decision Validator"""
        try:
            # Extract predicted value based on prediction type
            if hasattr(prediction, 'performance_prediction'):
                predicted_value = prediction.performance_prediction.roi if prediction.performance_prediction else 0.0
            elif hasattr(prediction, 'viral_score'):
                predicted_value = prediction.viral_score
            else:
                predicted_value = 0.0
            
            confidence = prediction.confidence_score if hasattr(prediction, 'confidence_score') else 0.0
            
            # Create AI decision object
            ai_decision = AIDecision(
                prediction_type=prediction_type,
                predicted_value=predicted_value,
                confidence=confidence,
                user_id=user_id,
                timestamp=datetime.now()
            )
            
            # Validate the decision
            validation_result = ai_decision_validator.validate_prediction(ai_decision)
            
            # Log the decision if database is available
            if db:
                try:
                    ai_monitoring_service.log_ai_decision(db, ai_decision, validation_result)
                except Exception as log_error:
                    logger.warning(f"Failed to log AI decision: {log_error}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating AI decision: {e}")
            from .ai_decision_validator import ValidationResult, RiskLevel
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                confidence_score=0.0,
                warnings=[f"Validation error: {str(e)}"],
                recommendations=["Use fallback prediction"],
                requires_human_approval=True,
                validation_details={"error": str(e)}
            )