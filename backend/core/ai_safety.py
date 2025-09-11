"""
AI Decision Safety and Validation System
Comprehensive safety guards for AI-powered marketing decisions to prevent error amplification
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """AI decision safety levels"""
    SAFE = "safe"
    CAUTION = "caution" 
    DANGER = "danger"
    CRITICAL = "critical"

class ApprovalRequirement(Enum):
    """Approval requirement levels"""
    NONE = "none"
    AUTOMATED = "automated"
    HUMAN = "human"
    MULTI_STAKEHOLDER = "multi_stakeholder"

@dataclass
class SafetyCheck:
    """Individual safety check result"""
    check_name: str
    status: SafetyLevel
    message: str
    recommendation: str
    blocking: bool = False
    confidence: float = 1.0

@dataclass
class AIDecisionSafetyResult:
    """Comprehensive AI decision safety assessment"""
    overall_safety: SafetyLevel
    approval_required: ApprovalRequirement
    safety_score: float  # 0-1 scale
    checks: List[SafetyCheck]
    blocking_issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    monitoring_requirements: List[str]
    
class AISafetyGuard:
    """
    AI Decision Safety Guard System
    Prevents AI mistakes from scaling and impacting multiple campaigns
    """
    
    def __init__(self):
        """Initialize AI Safety Guard with configuration"""
        self.safety_config = {
            # ROI Thresholds
            "max_realistic_roi": 500.0,  # 500% ROI threshold
            "suspicious_roi": 100.0,     # 100% ROI warning threshold
            "min_confidence": 0.70,      # Minimum confidence for high-risk decisions
            
            # Budget Thresholds  
            "budget_increase_threshold": 0.20,  # 20% budget increase requires approval
            "high_budget_threshold": 50000,     # High budget campaigns need approval
            "critical_budget_threshold": 100000, # Critical budget requires multi-approval
            
            # Performance Monitoring
            "performance_deviation_threshold": 0.30,  # 30% deviation triggers alerts
            "consecutive_failure_threshold": 5,       # Circuit breaker threshold
            "accuracy_degradation_threshold": 0.60,   # Accuracy below 60% triggers review
            
            # Campaign Safety
            "max_daily_spend_increase": 0.50,  # 50% daily spend increase limit
            "min_test_period_days": 3,         # Minimum test period before scaling
            "max_audience_expansion": 2.0,     # 2x audience expansion limit
        }
        
        # Monitoring state
        self.decision_history: Dict[str, List[Dict[str, Any]]] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
        self.safety_alerts: List[Dict[str, Any]] = []
        
    async def validate_ai_decision(
        self,
        decision_type: str,
        decision_data: Dict[str, Any],
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AIDecisionSafetyResult:
        """
        Comprehensive validation of AI decision with safety checks
        
        Args:
            decision_type: Type of AI decision (campaign_prediction, budget_optimization, etc.)
            decision_data: The AI decision data to validate
            user_id: User making the decision
            context: Additional context (historical data, campaign info, etc.)
            
        Returns:
            Comprehensive safety assessment result
        """
        try:
            logger.info(f"Validating AI decision: {decision_type} for user {user_id}")
            
            # Initialize checks list
            safety_checks = []
            blocking_issues = []
            warnings = []
            recommendations = []
            monitoring_requirements = []
            
            # 1. ROI Reality Check
            roi_check = self._check_roi_realism(decision_data)
            safety_checks.append(roi_check)
            if roi_check.blocking:
                blocking_issues.append(roi_check.message)
            
            # 2. Confidence Validation
            confidence_check = self._check_confidence_levels(decision_data)
            safety_checks.append(confidence_check)
            if confidence_check.status in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
                warnings.append(confidence_check.message)
            
            # 3. Budget Impact Assessment
            budget_check = self._check_budget_impact(decision_data, context)
            safety_checks.append(budget_check)
            if budget_check.blocking:
                blocking_issues.append(budget_check.message)
            
            # 4. Historical Performance Correlation
            history_check = await self._check_historical_performance(user_id, decision_data)
            safety_checks.append(history_check)
            
            # 5. Anomaly Detection
            anomaly_check = self._check_for_anomalies(decision_data, context)
            safety_checks.append(anomaly_check)
            if anomaly_check.status == SafetyLevel.CRITICAL:
                blocking_issues.append(anomaly_check.message)
            
            # 6. Cross-Campaign Impact Assessment
            impact_check = await self._check_cross_campaign_impact(user_id, decision_data)
            safety_checks.append(impact_check)
            
            # 7. Velocity and Scale Checks
            velocity_check = self._check_decision_velocity(user_id, decision_type)
            safety_checks.append(velocity_check)
            
            # 8. Model Reliability Check
            reliability_check = self._check_model_reliability(decision_data)
            safety_checks.append(reliability_check)
            
            # Calculate overall safety assessment
            overall_safety = self._calculate_overall_safety(safety_checks)
            approval_required = self._determine_approval_requirement(safety_checks, blocking_issues)
            safety_score = self._calculate_safety_score(safety_checks)
            
            # Generate monitoring requirements
            monitoring_requirements = self._generate_monitoring_requirements(
                overall_safety, decision_type, decision_data
            )
            
            # Collect all recommendations
            for check in safety_checks:
                if check.recommendation and check.recommendation not in recommendations:
                    recommendations.append(check.recommendation)
            
            # Record decision for future analysis
            self._record_decision(user_id, decision_type, decision_data, overall_safety)
            
            # Generate safety alerts if needed
            if overall_safety in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
                await self._generate_safety_alert(user_id, decision_type, overall_safety, blocking_issues)
            
            result = AIDecisionSafetyResult(
                overall_safety=overall_safety,
                approval_required=approval_required,
                safety_score=safety_score,
                checks=safety_checks,
                blocking_issues=blocking_issues,
                warnings=warnings,
                recommendations=recommendations,
                monitoring_requirements=monitoring_requirements
            )
            
            logger.info(
                f"AI decision safety validation completed: {overall_safety.value} "
                f"(score: {safety_score:.2f}, approval: {approval_required.value})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"AI decision validation failed: {e}")
            return self._generate_critical_failure_result(str(e))
    
    def _check_roi_realism(self, decision_data: Dict[str, Any]) -> SafetyCheck:
        """Check if ROI predictions are realistic"""
        try:
            predicted_metrics = decision_data.get("predicted_metrics", {})
            roi = predicted_metrics.get("roi", 0)
            
            if roi > self.safety_config["max_realistic_roi"]:
                return SafetyCheck(
                    check_name="roi_realism",
                    status=SafetyLevel.CRITICAL,
                    message=f"Unrealistic ROI prediction: {roi}% (max realistic: {self.safety_config['max_realistic_roi']}%)",
                    recommendation="Review prediction model and validate against industry benchmarks",
                    blocking=True,
                    confidence=0.95
                )
            elif roi > self.safety_config["suspicious_roi"]:
                return SafetyCheck(
                    check_name="roi_realism",
                    status=SafetyLevel.CAUTION,
                    message=f"High ROI prediction: {roi}% - requires validation",
                    recommendation="Validate assumptions and consider conservative approach",
                    blocking=False,
                    confidence=0.80
                )
            else:
                return SafetyCheck(
                    check_name="roi_realism",
                    status=SafetyLevel.SAFE,
                    message=f"ROI prediction appears realistic: {roi}%",
                    recommendation="Monitor actual performance against prediction",
                    confidence=0.90
                )
                
        except Exception as e:
            return SafetyCheck(
                check_name="roi_realism",
                status=SafetyLevel.CRITICAL,
                message=f"ROI validation failed: {e}",
                recommendation="Manual review required",
                blocking=True,
                confidence=0.0
            )
    
    def _check_confidence_levels(self, decision_data: Dict[str, Any]) -> SafetyCheck:
        """Check AI confidence levels"""
        try:
            confidence = decision_data.get("confidence_score", 0.5)
            confidence_level = decision_data.get("confidence_level", "medium")
            
            if confidence < 0.4:
                return SafetyCheck(
                    check_name="confidence_validation",
                    status=SafetyLevel.DANGER,
                    message=f"Very low AI confidence: {confidence:.2f}",
                    recommendation="Gather more data or use conservative approach",
                    blocking=False,
                    confidence=0.95
                )
            elif confidence < self.safety_config["min_confidence"]:
                return SafetyCheck(
                    check_name="confidence_validation",
                    status=SafetyLevel.CAUTION,
                    message=f"Low AI confidence: {confidence:.2f} (minimum: {self.safety_config['min_confidence']})",
                    recommendation="Consider additional validation or reduced risk approach",
                    blocking=False,
                    confidence=0.85
                )
            else:
                return SafetyCheck(
                    check_name="confidence_validation",
                    status=SafetyLevel.SAFE,
                    message=f"Adequate AI confidence: {confidence:.2f}",
                    recommendation="Proceed with standard monitoring",
                    confidence=0.90
                )
                
        except Exception as e:
            return SafetyCheck(
                check_name="confidence_validation",
                status=SafetyLevel.CRITICAL,
                message=f"Confidence validation failed: {e}",
                recommendation="Manual review required",
                blocking=True,
                confidence=0.0
            )
    
    def _check_budget_impact(
        self, 
        decision_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> SafetyCheck:
        """Check budget impact and requirements"""
        try:
            # Extract budget information
            current_budget = 0
            proposed_budget = 0
            
            if context:
                current_budget = context.get("current_budget", 0)
                campaign_config = context.get("campaign_config", {})
                proposed_budget = campaign_config.get("budget", 0)
            
            # Check absolute budget levels
            if proposed_budget > self.safety_config["critical_budget_threshold"]:
                return SafetyCheck(
                    check_name="budget_impact",
                    status=SafetyLevel.CRITICAL,
                    message=f"Critical budget level: ₹{proposed_budget:,}",
                    recommendation="Multi-stakeholder approval and phased rollout required",
                    blocking=True,
                    confidence=1.0
                )
            elif proposed_budget > self.safety_config["high_budget_threshold"]:
                return SafetyCheck(
                    check_name="budget_impact",
                    status=SafetyLevel.DANGER,
                    message=f"High budget campaign: ₹{proposed_budget:,}",
                    recommendation="Human approval and enhanced monitoring required",
                    blocking=False,
                    confidence=0.95
                )
            
            # Check budget increase percentage
            if current_budget > 0:
                increase_ratio = (proposed_budget - current_budget) / current_budget
                if increase_ratio > self.safety_config["budget_increase_threshold"]:
                    return SafetyCheck(
                        check_name="budget_impact",
                        status=SafetyLevel.CAUTION,
                        message=f"Significant budget increase: {increase_ratio:.1%}",
                        recommendation="Gradual increase with performance validation",
                        blocking=False,
                        confidence=0.85
                    )
            
            return SafetyCheck(
                check_name="budget_impact",
                status=SafetyLevel.SAFE,
                message="Budget levels within acceptable range",
                recommendation="Standard budget monitoring protocols",
                confidence=0.90
            )
            
        except Exception as e:
            return SafetyCheck(
                check_name="budget_impact",
                status=SafetyLevel.CRITICAL,
                message=f"Budget validation failed: {e}",
                recommendation="Manual budget review required",
                blocking=True,
                confidence=0.0
            )
    
    async def _check_historical_performance(
        self, 
        user_id: str, 
        decision_data: Dict[str, Any]
    ) -> SafetyCheck:
        """Check against historical performance patterns"""
        try:
            user_history = self.decision_history.get(user_id, [])
            
            if not user_history:
                return SafetyCheck(
                    check_name="historical_performance",
                    status=SafetyLevel.CAUTION,
                    message="No historical data available for comparison",
                    recommendation="Start with conservative approach and gather baseline data",
                    confidence=0.60
                )
            
            # Analyze recent performance
            recent_decisions = user_history[-10:]  # Last 10 decisions
            performance_scores = [d.get("actual_performance", 0.5) for d in recent_decisions]
            avg_performance = statistics.mean(performance_scores) if performance_scores else 0.5
            
            if avg_performance < self.safety_config["accuracy_degradation_threshold"]:
                return SafetyCheck(
                    check_name="historical_performance",
                    status=SafetyLevel.DANGER,
                    message=f"Poor recent performance history: {avg_performance:.1%}",
                    recommendation="Review decision patterns and consider model recalibration",
                    confidence=0.90
                )
            elif avg_performance < 0.75:
                return SafetyCheck(
                    check_name="historical_performance",
                    status=SafetyLevel.CAUTION,
                    message=f"Moderate performance history: {avg_performance:.1%}",
                    recommendation="Enhanced monitoring and gradual scaling",
                    confidence=0.80
                )
            else:
                return SafetyCheck(
                    check_name="historical_performance",
                    status=SafetyLevel.SAFE,
                    message=f"Good performance history: {avg_performance:.1%}",
                    recommendation="Continue with standard monitoring",
                    confidence=0.85
                )
                
        except Exception as e:
            return SafetyCheck(
                check_name="historical_performance",
                status=SafetyLevel.CAUTION,
                message=f"Historical analysis failed: {e}",
                recommendation="Proceed with caution and manual oversight",
                confidence=0.50
            )
    
    def _check_for_anomalies(
        self, 
        decision_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> SafetyCheck:
        """Detect anomalies in AI decision patterns"""
        try:
            anomalies = []
            
            predicted_metrics = decision_data.get("predicted_metrics", {})
            
            # Check for metric inconsistencies
            roi = predicted_metrics.get("roi", 0)
            ctr = predicted_metrics.get("ctr", 0)
            conversion_rate = predicted_metrics.get("conversion_rate", 0)
            
            # Anomaly: High ROI with low engagement metrics
            if roi > 50 and (ctr < 1.0 or conversion_rate < 2.0):
                anomalies.append("High ROI predicted with suspiciously low engagement metrics")
            
            # Anomaly: Extremely high conversion rates
            if conversion_rate > 25:
                anomalies.append(f"Unrealistic conversion rate: {conversion_rate}%")
            
            # Anomaly: Very high CTR
            if ctr > 15:
                anomalies.append(f"Unrealistic click-through rate: {ctr}%")
            
            # Check against industry context if available
            if context:
                industry = context.get("campaign_config", {}).get("industry")
                if industry and self._is_prediction_anomalous_for_industry(predicted_metrics, industry):
                    anomalies.append(f"Predictions anomalous for {industry} industry")
            
            if anomalies:
                severity = SafetyLevel.CRITICAL if len(anomalies) > 2 else SafetyLevel.DANGER
                return SafetyCheck(
                    check_name="anomaly_detection",
                    status=severity,
                    message=f"Anomalies detected: {'; '.join(anomalies)}",
                    recommendation="Thorough review and validation required before proceeding",
                    blocking=(severity == SafetyLevel.CRITICAL),
                    confidence=0.85
                )
            else:
                return SafetyCheck(
                    check_name="anomaly_detection",
                    status=SafetyLevel.SAFE,
                    message="No anomalies detected in prediction patterns",
                    recommendation="Continue with standard validation processes",
                    confidence=0.80
                )
                
        except Exception as e:
            return SafetyCheck(
                check_name="anomaly_detection",
                status=SafetyLevel.CRITICAL,
                message=f"Anomaly detection failed: {e}",
                recommendation="Manual anomaly review required",
                blocking=True,
                confidence=0.0
            )
    
    async def _check_cross_campaign_impact(
        self, 
        user_id: str, 
        decision_data: Dict[str, Any]
    ) -> SafetyCheck:
        """Check potential impact across multiple campaigns"""
        try:
            # Simulate checking for cross-campaign impacts
            # In production, this would query active campaigns and assess conflicts
            
            predicted_metrics = decision_data.get("predicted_metrics", {})
            roi = predicted_metrics.get("roi", 0)
            
            # High-impact decisions could affect other campaigns
            if roi > 100:  # High ROI predictions might indicate system-wide issues
                return SafetyCheck(
                    check_name="cross_campaign_impact",
                    status=SafetyLevel.CAUTION,
                    message="High-impact prediction could affect campaign portfolio",
                    recommendation="Assess impact on other active campaigns",
                    confidence=0.70
                )
            
            return SafetyCheck(
                check_name="cross_campaign_impact",
                status=SafetyLevel.SAFE,
                message="Minimal cross-campaign impact expected",
                recommendation="Monitor for unexpected interactions",
                confidence=0.75
            )
            
        except Exception as e:
            return SafetyCheck(
                check_name="cross_campaign_impact",
                status=SafetyLevel.CAUTION,
                message=f"Cross-campaign analysis failed: {e}",
                recommendation="Manual cross-campaign review recommended",
                confidence=0.50
            )
    
    def _check_decision_velocity(self, user_id: str, decision_type: str) -> SafetyCheck:
        """Check the velocity of AI decisions to prevent rapid escalation of errors"""
        try:
            user_history = self.decision_history.get(user_id, [])
            recent_decisions = [
                d for d in user_history 
                if d.get("timestamp", datetime.min) > datetime.now() - timedelta(hours=24)
                and d.get("decision_type") == decision_type
            ]
            
            if len(recent_decisions) > 10:  # More than 10 similar decisions in 24h
                return SafetyCheck(
                    check_name="decision_velocity",
                    status=SafetyLevel.DANGER,
                    message=f"High decision velocity: {len(recent_decisions)} {decision_type} decisions in 24h",
                    recommendation="Implement cooling-off period and manual review",
                    confidence=0.95
                )
            elif len(recent_decisions) > 5:  # More than 5 similar decisions in 24h
                return SafetyCheck(
                    check_name="decision_velocity",
                    status=SafetyLevel.CAUTION,
                    message=f"Elevated decision velocity: {len(recent_decisions)} {decision_type} decisions in 24h",
                    recommendation="Monitor for pattern escalation",
                    confidence=0.80
                )
            else:
                return SafetyCheck(
                    check_name="decision_velocity",
                    status=SafetyLevel.SAFE,
                    message="Decision velocity within normal range",
                    recommendation="Continue standard monitoring",
                    confidence=0.85
                )
                
        except Exception as e:
            return SafetyCheck(
                check_name="decision_velocity",
                status=SafetyLevel.CAUTION,
                message=f"Velocity check failed: {e}",
                recommendation="Manual velocity assessment recommended",
                confidence=0.50
            )
    
    def _check_model_reliability(self, decision_data: Dict[str, Any]) -> SafetyCheck:
        """Check AI model reliability indicators"""
        try:
            model_version = decision_data.get("model_version", "unknown")
            is_fallback = decision_data.get("is_fallback", False)
            
            if is_fallback:
                return SafetyCheck(
                    check_name="model_reliability",
                    status=SafetyLevel.DANGER,
                    message="Using fallback prediction due to model failure",
                    recommendation="Investigate model issues before scaling decisions",
                    confidence=1.0
                )
            
            # Check for outdated models
            if "fallback" in model_version.lower():
                return SafetyCheck(
                    check_name="model_reliability",
                    status=SafetyLevel.CAUTION,
                    message="Using basic fallback model",
                    recommendation="Upgrade to primary model when available",
                    confidence=0.90
                )
            
            return SafetyCheck(
                check_name="model_reliability",
                status=SafetyLevel.SAFE,
                message=f"Primary model active: {model_version}",
                recommendation="Continue with standard model monitoring",
                confidence=0.85
            )
            
        except Exception as e:
            return SafetyCheck(
                check_name="model_reliability",
                status=SafetyLevel.CRITICAL,
                message=f"Model reliability check failed: {e}",
                recommendation="Manual model assessment required",
                blocking=True,
                confidence=0.0
            )
    
    def _is_prediction_anomalous_for_industry(
        self, 
        predicted_metrics: Dict[str, float], 
        industry: str
    ) -> bool:
        """Check if predictions are anomalous for specific industry"""
        
        # Industry benchmark ranges (simplified for demonstration)
        industry_benchmarks = {
            "fitness": {"roi": (5, 30), "ctr": (1.5, 5.0), "conversion": (3, 15)},
            "restaurant": {"roi": (3, 20), "ctr": (2.0, 6.0), "conversion": (2, 10)},
            "beauty": {"roi": (4, 25), "ctr": (1.8, 5.5), "conversion": (4, 12)},
            "real_estate": {"roi": (8, 40), "ctr": (1.0, 3.5), "conversion": (1, 8)},
            "general": {"roi": (3, 25), "ctr": (1.5, 5.0), "conversion": (2, 12)}
        }
        
        benchmarks = industry_benchmarks.get(industry, industry_benchmarks["general"])
        
        for metric, (min_val, max_val) in benchmarks.items():
            value = predicted_metrics.get(metric, 0)
            if value > max_val * 2 or value < min_val * 0.3:  # 2x above or 70% below
                return True
        
        return False
    
    def _calculate_overall_safety(self, checks: List[SafetyCheck]) -> SafetyLevel:
        """Calculate overall safety level from individual checks"""
        
        if not checks:
            return SafetyLevel.CRITICAL
        
        # Count checks by safety level
        critical_count = sum(1 for c in checks if c.status == SafetyLevel.CRITICAL)
        danger_count = sum(1 for c in checks if c.status == SafetyLevel.DANGER)
        caution_count = sum(1 for c in checks if c.status == SafetyLevel.CAUTION)
        
        # Determine overall level
        if critical_count > 0:
            return SafetyLevel.CRITICAL
        elif danger_count > 1:  # Multiple danger flags
            return SafetyLevel.CRITICAL
        elif danger_count > 0:
            return SafetyLevel.DANGER
        elif caution_count > 2:  # Multiple caution flags
            return SafetyLevel.DANGER
        elif caution_count > 0:
            return SafetyLevel.CAUTION
        else:
            return SafetyLevel.SAFE
    
    def _determine_approval_requirement(
        self, 
        checks: List[SafetyCheck], 
        blocking_issues: List[str]
    ) -> ApprovalRequirement:
        """Determine what level of approval is required"""
        
        if blocking_issues:
            return ApprovalRequirement.MULTI_STAKEHOLDER
        
        # Count high-risk checks
        critical_checks = [c for c in checks if c.status == SafetyLevel.CRITICAL]
        danger_checks = [c for c in checks if c.status == SafetyLevel.DANGER]
        
        if critical_checks:
            return ApprovalRequirement.MULTI_STAKEHOLDER
        elif len(danger_checks) > 1:
            return ApprovalRequirement.MULTI_STAKEHOLDER
        elif danger_checks:
            return ApprovalRequirement.HUMAN
        else:
            caution_checks = [c for c in checks if c.status == SafetyLevel.CAUTION]
            if len(caution_checks) > 2:
                return ApprovalRequirement.HUMAN
            elif caution_checks:
                return ApprovalRequirement.AUTOMATED
            else:
                return ApprovalRequirement.NONE
    
    def _calculate_safety_score(self, checks: List[SafetyCheck]) -> float:
        """Calculate numerical safety score (0-1)"""
        
        if not checks:
            return 0.0
        
        # Weight checks by confidence and status
        total_weight = 0.0
        weighted_score = 0.0
        
        status_scores = {
            SafetyLevel.SAFE: 1.0,
            SafetyLevel.CAUTION: 0.7,
            SafetyLevel.DANGER: 0.4,
            SafetyLevel.CRITICAL: 0.0
        }
        
        for check in checks:
            weight = check.confidence
            score = status_scores.get(check.status, 0.0)
            
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_monitoring_requirements(
        self, 
        safety_level: SafetyLevel, 
        decision_type: str, 
        decision_data: Dict[str, Any]
    ) -> List[str]:
        """Generate monitoring requirements based on safety assessment"""
        
        requirements = []
        
        if safety_level == SafetyLevel.CRITICAL:
            requirements.extend([
                "Real-time performance monitoring with automatic pause triggers",
                "Hourly performance reviews for first 48 hours",
                "Multi-stakeholder alert system activation",
                "Automatic rollback mechanisms on performance deviation >15%"
            ])
        elif safety_level == SafetyLevel.DANGER:
            requirements.extend([
                "Enhanced monitoring with 4-hour check intervals",
                "Daily performance reviews",
                "Automatic alerts on performance deviation >20%",
                "Rapid response team notification"
            ])
        elif safety_level == SafetyLevel.CAUTION:
            requirements.extend([
                "Standard monitoring with 8-hour check intervals", 
                "Automated alerts on performance deviation >25%",
                "Weekly performance reviews"
            ])
        else:  # SAFE
            requirements.extend([
                "Standard monitoring protocols",
                "Daily automated performance reports"
            ])
        
        # Add decision-specific monitoring
        if decision_type == "campaign_prediction":
            roi = decision_data.get("predicted_metrics", {}).get("roi", 0)
            if roi > 50:
                requirements.append("ROI tracking with industry benchmark comparison")
        
        return requirements
    
    def _record_decision(
        self, 
        user_id: str, 
        decision_type: str, 
        decision_data: Dict[str, Any], 
        safety_level: SafetyLevel
    ):
        """Record decision in history for pattern analysis"""
        
        if user_id not in self.decision_history:
            self.decision_history[user_id] = []
        
        decision_record = {
            "timestamp": datetime.now(),
            "decision_type": decision_type,
            "safety_level": safety_level.value,
            "predicted_roi": decision_data.get("predicted_metrics", {}).get("roi", 0),
            "confidence": decision_data.get("confidence_score", 0.5),
            "model_version": decision_data.get("model_version", "unknown")
        }
        
        self.decision_history[user_id].append(decision_record)
        
        # Keep last 100 decisions per user
        if len(self.decision_history[user_id]) > 100:
            self.decision_history[user_id].pop(0)
    
    async def _generate_safety_alert(
        self, 
        user_id: str, 
        decision_type: str, 
        safety_level: SafetyLevel, 
        issues: List[str]
    ):
        """Generate safety alert for high-risk decisions"""
        
        alert = {
            "timestamp": datetime.now(),
            "user_id": user_id,
            "decision_type": decision_type,
            "safety_level": safety_level.value,
            "issues": issues,
            "alert_type": "ai_safety_violation",
            "severity": "high" if safety_level == SafetyLevel.DANGER else "critical"
        }
        
        self.safety_alerts.append(alert)
        
        # Keep last 1000 alerts
        if len(self.safety_alerts) > 1000:
            self.safety_alerts.pop(0)
        
        logger.warning(
            f"AI Safety Alert: {safety_level.value} level decision for user {user_id} "
            f"({decision_type}): {'; '.join(issues[:3])}"
        )
    
    def _generate_critical_failure_result(self, error_message: str) -> AIDecisionSafetyResult:
        """Generate critical failure result when validation itself fails"""
        
        return AIDecisionSafetyResult(
            overall_safety=SafetyLevel.CRITICAL,
            approval_required=ApprovalRequirement.MULTI_STAKEHOLDER,
            safety_score=0.0,
            checks=[SafetyCheck(
                check_name="validation_failure",
                status=SafetyLevel.CRITICAL,
                message=f"Safety validation failed: {error_message}",
                recommendation="Manual review and approval required",
                blocking=True,
                confidence=1.0
            )],
            blocking_issues=[f"Safety validation system failure: {error_message}"],
            warnings=["AI safety system compromised"],
            recommendations=["Immediate manual review required", "Investigate safety system failure"],
            monitoring_requirements=["Manual monitoring until safety system restored"]
        )
    
    # Public API methods for monitoring and management
    
    async def get_safety_dashboard(
        self, 
        user_id: Optional[str] = None, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get safety monitoring dashboard data"""
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter recent alerts
            recent_alerts = [
                alert for alert in self.safety_alerts
                if alert.get("timestamp", datetime.min) > cutoff_time
            ]
            
            if user_id:
                recent_alerts = [a for a in recent_alerts if a.get("user_id") == user_id]
            
            # Calculate safety metrics
            total_decisions = sum(len(history) for history in self.decision_history.values())
            high_risk_decisions = len([
                a for a in recent_alerts 
                if a.get("safety_level") in ["danger", "critical"]
            ])
            
            safety_rate = 1.0 - (high_risk_decisions / max(total_decisions, 1))
            
            return {
                "period_hours": hours,
                "total_decisions": total_decisions,
                "high_risk_decisions": high_risk_decisions,
                "safety_rate": safety_rate,
                "recent_alerts": len(recent_alerts),
                "alert_breakdown": self._get_alert_breakdown(recent_alerts),
                "user_filter": user_id,
                "system_health": "healthy" if safety_rate > 0.95 else (
                    "degraded" if safety_rate > 0.90 else "critical"
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating safety dashboard: {e}")
            return {"error": str(e), "system_health": "unknown"}
    
    def _get_alert_breakdown(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of alerts by type and severity"""
        
        breakdown = {
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_type": {},
            "by_safety_level": {"safe": 0, "caution": 0, "danger": 0, "critical": 0}
        }
        
        for alert in alerts:
            # Count by severity
            severity = alert.get("severity", "low")
            if severity in breakdown["by_severity"]:
                breakdown["by_severity"][severity] += 1
            
            # Count by type
            alert_type = alert.get("decision_type", "unknown")
            breakdown["by_type"][alert_type] = breakdown["by_type"].get(alert_type, 0) + 1
            
            # Count by safety level
            safety_level = alert.get("safety_level", "safe")
            if safety_level in breakdown["by_safety_level"]:
                breakdown["by_safety_level"][safety_level] += 1
        
        return breakdown

# Global instance for use across the application
ai_safety_guard = AISafetyGuard()