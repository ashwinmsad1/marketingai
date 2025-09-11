"""
AI Decision Validation Service
Prevents AI mistakes from amplifying and impacting multiple campaigns
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PredictionType(Enum):
    ROI = "roi"
    CTR = "ctr"
    CONVERSION_RATE = "conversion_rate"
    BUDGET_ALLOCATION = "budget_allocation"
    AUDIENCE_TARGETING = "audience_targeting"

@dataclass
class ValidationResult:
    is_valid: bool
    risk_level: RiskLevel
    confidence_score: float
    warnings: List[str]
    recommendations: List[str]
    requires_human_approval: bool
    validation_details: Dict[str, Any]

@dataclass
class AIDecision:
    prediction_type: PredictionType
    predicted_value: float
    confidence: float
    historical_context: Optional[Dict[str, Any]] = None
    user_id: str = None
    campaign_id: str = None
    timestamp: datetime = None

class AIDecisionValidator:
    """
    Comprehensive AI decision validation to prevent error amplification
    """
    
    def __init__(self):
        self.prediction_history = {}
        self.performance_thresholds = {
            PredictionType.ROI: {"min": -50, "max": 500, "warning_threshold": 300},
            PredictionType.CTR: {"min": 0.1, "max": 15.0, "warning_threshold": 10.0},
            PredictionType.CONVERSION_RATE: {"min": 0.1, "max": 25.0, "warning_threshold": 20.0},
            PredictionType.BUDGET_ALLOCATION: {"min": 1.0, "max": 50000, "warning_threshold": 10000}
        }
        
        self.confidence_thresholds = {
            RiskLevel.LOW: 0.85,
            RiskLevel.MEDIUM: 0.70,
            RiskLevel.HIGH: 0.60,
            RiskLevel.CRITICAL: 0.90  # Critical decisions need very high confidence
        }
        
        # Circuit breaker settings
        self.failure_threshold = 3
        self.failure_window = timedelta(hours=1)
        self.circuit_breaker_state = {}
    
    def validate_prediction(self, decision: AIDecision) -> ValidationResult:
        """
        Comprehensive validation of AI predictions with multiple safety checks
        """
        warnings = []
        recommendations = []
        validation_details = {}
        
        try:
            # 1. Sanity check for prediction values
            sanity_result = self._validate_prediction_sanity(decision)
            warnings.extend(sanity_result["warnings"])
            validation_details["sanity_check"] = sanity_result
            
            # 2. Confidence threshold validation
            confidence_result = self._validate_confidence_threshold(decision)
            validation_details["confidence_check"] = confidence_result
            
            # 3. Historical performance correlation
            historical_result = self._validate_historical_correlation(decision)
            warnings.extend(historical_result["warnings"])
            validation_details["historical_check"] = historical_result
            
            # 4. Anomaly detection
            anomaly_result = self._detect_prediction_anomalies(decision)
            warnings.extend(anomaly_result["warnings"])
            validation_details["anomaly_check"] = anomaly_result
            
            # 5. Circuit breaker check
            circuit_result = self._check_circuit_breaker(decision)
            validation_details["circuit_breaker"] = circuit_result
            
            # 6. Risk assessment
            risk_level = self._assess_risk_level(decision, sanity_result, confidence_result, historical_result)
            
            # 7. Determine if human approval is required
            requires_approval = self._requires_human_approval(decision, risk_level, warnings)
            
            # 8. Generate recommendations
            recommendations = self._generate_recommendations(decision, risk_level, warnings)
            
            # Overall validation result
            is_valid = (
                sanity_result["is_valid"] and 
                confidence_result["is_valid"] and 
                not circuit_result["circuit_open"] and
                len([w for w in warnings if "CRITICAL" in w]) == 0
            )
            
            logger.info(f"AI decision validation complete. Valid: {is_valid}, Risk: {risk_level.value}, Confidence: {decision.confidence}")
            
            return ValidationResult(
                is_valid=is_valid,
                risk_level=risk_level,
                confidence_score=decision.confidence,
                warnings=warnings,
                recommendations=recommendations,
                requires_human_approval=requires_approval,
                validation_details=validation_details
            )
            
        except Exception as e:
            logger.error(f"Error in AI decision validation: {e}")
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                confidence_score=0.0,
                warnings=[f"CRITICAL: Validation system error - {str(e)}"],
                recommendations=["Reject decision due to validation failure"],
                requires_human_approval=True,
                validation_details={"error": str(e)}
            )
    
    def _validate_prediction_sanity(self, decision: AIDecision) -> Dict[str, Any]:
        """Validate prediction values are within reasonable ranges"""
        warnings = []
        
        if decision.prediction_type in self.performance_thresholds:
            thresholds = self.performance_thresholds[decision.prediction_type]
            
            # Check if prediction is outside acceptable range
            if decision.predicted_value < thresholds["min"]:
                warnings.append(f"CRITICAL: {decision.prediction_type.value} prediction {decision.predicted_value}% is below minimum threshold {thresholds['min']}%")
            elif decision.predicted_value > thresholds["max"]:
                warnings.append(f"CRITICAL: {decision.prediction_type.value} prediction {decision.predicted_value}% exceeds maximum threshold {thresholds['max']}%")
            elif decision.predicted_value > thresholds["warning_threshold"]:
                warnings.append(f"WARNING: {decision.prediction_type.value} prediction {decision.predicted_value}% is unusually high (>{thresholds['warning_threshold']}%)")
        
        is_valid = len([w for w in warnings if "CRITICAL" in w]) == 0
        
        return {
            "is_valid": is_valid,
            "warnings": warnings,
            "predicted_value": decision.predicted_value,
            "thresholds_applied": self.performance_thresholds.get(decision.prediction_type, {})
        }
    
    def _validate_confidence_threshold(self, decision: AIDecision) -> Dict[str, Any]:
        """Validate prediction confidence meets minimum requirements"""
        
        # Determine minimum confidence based on prediction type and value
        if decision.prediction_type == PredictionType.ROI and decision.predicted_value > 200:
            min_confidence = 0.85  # High ROI predictions need high confidence
        elif decision.prediction_type == PredictionType.BUDGET_ALLOCATION and decision.predicted_value > 5000:
            min_confidence = 0.80  # Large budget changes need high confidence
        else:
            min_confidence = 0.70  # Default minimum confidence
        
        is_valid = decision.confidence >= min_confidence
        
        return {
            "is_valid": is_valid,
            "confidence": decision.confidence,
            "min_required": min_confidence,
            "confidence_gap": min_confidence - decision.confidence if not is_valid else 0
        }
    
    def _validate_historical_correlation(self, decision: AIDecision) -> Dict[str, Any]:
        """Check prediction against historical performance patterns"""
        warnings = []
        
        # Get historical predictions for this user/campaign
        history_key = f"{decision.user_id}_{decision.prediction_type.value}"
        historical_predictions = self.prediction_history.get(history_key, [])
        
        if len(historical_predictions) >= 3:
            recent_predictions = [p["predicted_value"] for p in historical_predictions[-5:]]
            avg_prediction = statistics.mean(recent_predictions)
            std_deviation = statistics.stdev(recent_predictions) if len(recent_predictions) > 1 else 0
            
            # Check if current prediction deviates significantly from historical pattern
            deviation = abs(decision.predicted_value - avg_prediction)
            if std_deviation > 0 and deviation > (2 * std_deviation):
                warnings.append(f"WARNING: Prediction deviates significantly from historical pattern (avg: {avg_prediction:.2f}%, current: {decision.predicted_value:.2f}%)")
        
        # Store current prediction in history
        if history_key not in self.prediction_history:
            self.prediction_history[history_key] = []
        
        self.prediction_history[history_key].append({
            "predicted_value": decision.predicted_value,
            "confidence": decision.confidence,
            "timestamp": decision.timestamp or datetime.now()
        })
        
        # Keep only last 10 predictions
        if len(self.prediction_history[history_key]) > 10:
            self.prediction_history[history_key] = self.prediction_history[history_key][-10:]
        
        return {
            "warnings": warnings,
            "historical_count": len(historical_predictions),
            "historical_average": avg_prediction if len(historical_predictions) >= 3 else None,
            "deviation": deviation if len(historical_predictions) >= 3 else None
        }
    
    def _detect_prediction_anomalies(self, decision: AIDecision) -> Dict[str, Any]:
        """Detect anomalous predictions that could indicate model issues"""
        warnings = []
        
        # Check for extreme values that might indicate model drift
        extreme_values = {
            PredictionType.ROI: [1000, -100],  # ROI > 1000% or < -100%
            PredictionType.CTR: [20.0, 0.01],  # CTR > 20% or < 0.01%
            PredictionType.CONVERSION_RATE: [30.0, 0.01]  # CR > 30% or < 0.01%
        }
        
        if decision.prediction_type in extreme_values:
            high_threshold, low_threshold = extreme_values[decision.prediction_type]
            if decision.predicted_value > high_threshold or decision.predicted_value < low_threshold:
                warnings.append(f"ANOMALY: {decision.prediction_type.value} prediction {decision.predicted_value}% is in extreme range - possible model issue")
        
        # Check confidence-prediction correlation
        if decision.confidence > 0.9 and decision.prediction_type == PredictionType.ROI and decision.predicted_value > 400:
            warnings.append("ANOMALY: Very high confidence with extremely high ROI prediction - review model calibration")
        
        return {
            "warnings": warnings,
            "anomaly_detected": len(warnings) > 0
        }
    
    def _check_circuit_breaker(self, decision: AIDecision) -> Dict[str, Any]:
        """Circuit breaker pattern to prevent cascade failures"""
        
        service_key = f"{decision.prediction_type.value}_service"
        current_time = datetime.now()
        
        # Check if circuit breaker exists for this service
        if service_key not in self.circuit_breaker_state:
            self.circuit_breaker_state[service_key] = {
                "failure_count": 0,
                "last_failure_time": None,
                "circuit_open": False,
                "last_success_time": current_time
            }
        
        circuit_state = self.circuit_breaker_state[service_key]
        
        # Check if circuit should be closed (reset after timeout)
        if circuit_state["circuit_open"]:
            time_since_failure = current_time - (circuit_state["last_failure_time"] or current_time)
            if time_since_failure > timedelta(minutes=15):  # Reset after 15 minutes
                circuit_state["circuit_open"] = False
                circuit_state["failure_count"] = 0
                logger.info(f"Circuit breaker reset for {service_key}")
        
        return {
            "circuit_open": circuit_state["circuit_open"],
            "failure_count": circuit_state["failure_count"],
            "last_failure": circuit_state["last_failure_time"],
            "service_key": service_key
        }
    
    def record_prediction_failure(self, decision: AIDecision, failure_reason: str):
        """Record a prediction failure for circuit breaker logic"""
        
        service_key = f"{decision.prediction_type.value}_service"
        current_time = datetime.now()
        
        if service_key not in self.circuit_breaker_state:
            self.circuit_breaker_state[service_key] = {
                "failure_count": 0,
                "last_failure_time": None,
                "circuit_open": False,
                "last_success_time": None
            }
        
        circuit_state = self.circuit_breaker_state[service_key]
        circuit_state["failure_count"] += 1
        circuit_state["last_failure_time"] = current_time
        
        # Open circuit breaker if failure threshold exceeded
        if circuit_state["failure_count"] >= self.failure_threshold:
            circuit_state["circuit_open"] = True
            logger.warning(f"Circuit breaker opened for {service_key} after {circuit_state['failure_count']} failures")
    
    def _assess_risk_level(self, decision: AIDecision, sanity_result: Dict, confidence_result: Dict, historical_result: Dict) -> RiskLevel:
        """Assess overall risk level of the AI decision"""
        
        risk_score = 0
        
        # Factor 1: Sanity check results
        if not sanity_result["is_valid"]:
            risk_score += 3
        elif any("WARNING" in w for w in sanity_result["warnings"]):
            risk_score += 1
        
        # Factor 2: Confidence level
        if not confidence_result["is_valid"]:
            risk_score += 2
        elif decision.confidence < 0.75:
            risk_score += 1
        
        # Factor 3: Historical deviation
        if any("WARNING" in w for w in historical_result["warnings"]):
            risk_score += 1
        
        # Factor 4: Prediction magnitude
        if decision.prediction_type == PredictionType.ROI and decision.predicted_value > 300:
            risk_score += 2
        elif decision.prediction_type == PredictionType.BUDGET_ALLOCATION and decision.predicted_value > 10000:
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 5:
            return RiskLevel.CRITICAL
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _requires_human_approval(self, decision: AIDecision, risk_level: RiskLevel, warnings: List[str]) -> bool:
        """Determine if human approval is required for this decision"""
        
        # Always require approval for critical risk
        if risk_level == RiskLevel.CRITICAL:
            return True
        
        # Require approval for high-risk decisions
        if risk_level == RiskLevel.HIGH:
            return True
        
        # Require approval for large budget allocations
        if decision.prediction_type == PredictionType.BUDGET_ALLOCATION and decision.predicted_value > 5000:
            return True
        
        # Require approval for extreme ROI predictions
        if decision.prediction_type == PredictionType.ROI and decision.predicted_value > 250:
            return True
        
        # Require approval if any critical warnings
        if any("CRITICAL" in w for w in warnings):
            return True
        
        return False
    
    def _generate_recommendations(self, decision: AIDecision, risk_level: RiskLevel, warnings: List[str]) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("REJECT: Do not proceed with this AI decision")
            recommendations.append("Investigate model performance and data quality")
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("REVIEW: Require human approval before implementation")
            recommendations.append("Consider starting with smaller test budget")
        
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("MONITOR: Proceed with enhanced monitoring")
            recommendations.append("Set conservative budget limits initially")
        
        else:
            recommendations.append("PROCEED: Decision appears safe to implement")
        
        # Specific recommendations based on prediction type
        if decision.prediction_type == PredictionType.ROI and decision.predicted_value > 200:
            recommendations.append("Consider gradual rollout to validate high ROI prediction")
        
        if decision.confidence < 0.8:
            recommendations.append("Gather more data to improve prediction confidence")
        
        if any("ANOMALY" in w for w in warnings):
            recommendations.append("Review model calibration and training data")
        
        return recommendations


# Global validator instance
ai_decision_validator = AIDecisionValidator()