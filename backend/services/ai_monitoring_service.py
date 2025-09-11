"""
AI Monitoring and Performance Tracking Service
Monitors AI decision quality and prevents error amplification
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

from .ai_decision_validator import AIDecision, ValidationResult, RiskLevel, PredictionType
from backend.database.models import Base

logger = logging.getLogger(__name__)

class AIDecisionLog(Base):
    """Database model for logging AI decisions and outcomes"""
    __tablename__ = "ai_decision_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    campaign_id = Column(String, index=True, nullable=True)
    prediction_type = Column(String, nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    
    # Validation results
    validation_passed = Column(Boolean, nullable=False)
    warnings_count = Column(Integer, default=0)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String, nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    
    # Outcome tracking
    actual_result = Column(Float, nullable=True)
    performance_deviation = Column(Float, nullable=True)  # % difference from prediction
    outcome_timestamp = Column(DateTime, nullable=True)
    
    # Metadata
    validation_details = Column(JSON)
    warnings = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CampaignPerformanceAlert(Base):
    """Database model for campaign performance alerts"""
    __tablename__ = "campaign_performance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    alert_type = Column(String, nullable=False)  # performance_drop, spend_velocity, anomaly
    severity = Column(String, nullable=False)  # low, medium, high, critical
    
    predicted_value = Column(Float)
    actual_value = Column(Float)
    deviation_percentage = Column(Float)
    
    alert_message = Column(Text)
    action_taken = Column(String, nullable=True)  # paused, budget_reduced, human_review
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

@dataclass
class AIPerformanceMetrics:
    """Metrics for AI decision performance tracking"""
    total_decisions: int
    successful_decisions: int
    failed_decisions: int
    accuracy_rate: float
    average_confidence: float
    high_risk_decisions: int
    human_approvals_required: int
    circuit_breaker_triggers: int
    
class AIMonitoringService:
    """
    Service for monitoring AI decision quality and preventing error amplification
    """
    
    def __init__(self):
        self.performance_thresholds = {
            "roi_accuracy_threshold": 0.8,  # 80% accuracy for ROI predictions
            "ctr_accuracy_threshold": 0.75,  # 75% accuracy for CTR predictions
            "max_deviation_percentage": 25,  # 25% max deviation from prediction
            "performance_window_hours": 24  # Monitor performance over 24 hours
        }
        
        self.alert_thresholds = {
            "performance_drop_threshold": 20,  # 20% drop triggers alert
            "spend_velocity_threshold": 150,  # 150% of expected spend rate
            "anomaly_score_threshold": 0.8  # Anomaly detection threshold
        }
    
    def log_ai_decision(self, db: Session, decision: AIDecision, validation_result: ValidationResult) -> AIDecisionLog:
        """Log an AI decision and its validation results"""
        
        try:
            decision_log = AIDecisionLog(
                user_id=decision.user_id,
                campaign_id=decision.campaign_id,
                prediction_type=decision.prediction_type.value,
                predicted_value=decision.predicted_value,
                confidence_score=decision.confidence,
                risk_level=validation_result.risk_level.value,
                validation_passed=validation_result.is_valid,
                warnings_count=len(validation_result.warnings),
                requires_approval=validation_result.requires_human_approval,
                validation_details=validation_result.validation_details,
                warnings=validation_result.warnings,
                recommendations=validation_result.recommendations
            )
            
            db.add(decision_log)
            db.commit()
            db.refresh(decision_log)
            
            logger.info(f"AI decision logged: {decision.prediction_type.value} for user {decision.user_id}")
            return decision_log
            
        except Exception as e:
            logger.error(f"Error logging AI decision: {e}")
            db.rollback()
            raise
    
    def update_decision_outcome(self, db: Session, decision_log_id: int, actual_result: float) -> None:
        """Update the actual outcome of an AI decision for performance tracking"""
        
        try:
            decision_log = db.query(AIDecisionLog).filter(AIDecisionLog.id == decision_log_id).first()
            
            if not decision_log:
                logger.warning(f"Decision log {decision_log_id} not found")
                return
            
            # Calculate performance deviation
            predicted = decision_log.predicted_value
            deviation = abs((actual_result - predicted) / predicted * 100) if predicted != 0 else 0
            
            decision_log.actual_result = actual_result
            decision_log.performance_deviation = deviation
            decision_log.outcome_timestamp = datetime.utcnow()
            
            db.commit()
            
            # Check if performance deviation triggers an alert
            if deviation > self.performance_thresholds["max_deviation_percentage"]:
                self._create_performance_alert(
                    db, 
                    decision_log, 
                    "performance_deviation", 
                    f"AI prediction deviated {deviation:.1f}% from actual result"
                )
            
            logger.info(f"Updated decision outcome: predicted {predicted}, actual {actual_result}, deviation {deviation:.1f}%")
            
        except Exception as e:
            logger.error(f"Error updating decision outcome: {e}")
            db.rollback()
    
    def monitor_campaign_performance(self, db: Session, campaign_id: str, current_metrics: Dict[str, float]) -> List[CampaignPerformanceAlert]:
        """Monitor ongoing campaign performance and detect anomalies"""
        
        alerts_created = []
        
        try:
            # Get AI predictions for this campaign
            predictions = db.query(AIDecisionLog).filter(
                AIDecisionLog.campaign_id == campaign_id,
                AIDecisionLog.created_at > datetime.utcnow() - timedelta(hours=24)
            ).all()
            
            for prediction in predictions:
                metric_key = self._get_metric_key(prediction.prediction_type)
                if metric_key not in current_metrics:
                    continue
                
                current_value = current_metrics[metric_key]
                predicted_value = prediction.predicted_value
                deviation = abs((current_value - predicted_value) / predicted_value * 100) if predicted_value != 0 else 0
                
                # Check for performance drops
                if deviation > self.alert_thresholds["performance_drop_threshold"]:
                    alert = self._create_performance_alert(
                        db,
                        prediction,
                        "performance_drop",
                        f"{prediction.prediction_type} performance dropped {deviation:.1f}% from prediction"
                    )
                    alerts_created.append(alert)
            
            return alerts_created
            
        except Exception as e:
            logger.error(f"Error monitoring campaign performance: {e}")
            return []
    
    def check_spend_velocity(self, db: Session, campaign_id: str, current_spend: float, budget: float, hours_elapsed: float) -> Optional[CampaignPerformanceAlert]:
        """Monitor campaign spend velocity and alert on unusual patterns"""
        
        try:
            expected_hourly_rate = budget / 24  # Assume 24-hour campaign duration
            actual_hourly_rate = current_spend / max(hours_elapsed, 0.1)
            velocity_ratio = (actual_hourly_rate / expected_hourly_rate) * 100
            
            if velocity_ratio > self.alert_thresholds["spend_velocity_threshold"]:
                # Get campaign info
                campaign_logs = db.query(AIDecisionLog).filter(
                    AIDecisionLog.campaign_id == campaign_id
                ).first()
                
                alert = CampaignPerformanceAlert(
                    campaign_id=campaign_id,
                    user_id=campaign_logs.user_id if campaign_logs else "unknown",
                    alert_type="spend_velocity",
                    severity="high" if velocity_ratio > 200 else "medium",
                    predicted_value=expected_hourly_rate,
                    actual_value=actual_hourly_rate,
                    deviation_percentage=velocity_ratio - 100,
                    alert_message=f"Campaign spending {velocity_ratio:.1f}% faster than expected rate",
                    action_taken="monitoring"
                )
                
                db.add(alert)
                db.commit()
                db.refresh(alert)
                
                logger.warning(f"Spend velocity alert for campaign {campaign_id}: {velocity_ratio:.1f}% of expected rate")
                return alert
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking spend velocity: {e}")
            return None
    
    def get_ai_performance_metrics(self, db: Session, user_id: Optional[str] = None, days: int = 7) -> AIPerformanceMetrics:
        """Get comprehensive AI performance metrics"""
        
        try:
            # Base query
            query = db.query(AIDecisionLog).filter(
                AIDecisionLog.created_at > datetime.utcnow() - timedelta(days=days)
            )
            
            if user_id:
                query = query.filter(AIDecisionLog.user_id == user_id)
            
            decisions = query.all()
            
            total_decisions = len(decisions)
            if total_decisions == 0:
                return AIPerformanceMetrics(0, 0, 0, 0.0, 0.0, 0, 0, 0)
            
            # Calculate metrics
            successful_decisions = len([d for d in decisions if d.validation_passed])
            failed_decisions = total_decisions - successful_decisions
            accuracy_rate = successful_decisions / total_decisions if total_decisions > 0 else 0
            average_confidence = sum(d.confidence_score for d in decisions) / total_decisions
            high_risk_decisions = len([d for d in decisions if d.risk_level in ["high", "critical"]])
            human_approvals_required = len([d for d in decisions if d.requires_approval])
            
            # Circuit breaker triggers (approximate from validation failures)
            circuit_breaker_triggers = len([d for d in decisions if not d.validation_passed and "circuit" in str(d.warnings).lower()])
            
            return AIPerformanceMetrics(
                total_decisions=total_decisions,
                successful_decisions=successful_decisions,
                failed_decisions=failed_decisions,
                accuracy_rate=accuracy_rate,
                average_confidence=average_confidence,
                high_risk_decisions=high_risk_decisions,
                human_approvals_required=human_approvals_required,
                circuit_breaker_triggers=circuit_breaker_triggers
            )
            
        except Exception as e:
            logger.error(f"Error calculating AI performance metrics: {e}")
            return AIPerformanceMetrics(0, 0, 0, 0.0, 0.0, 0, 0, 0)
    
    def get_performance_alerts(self, db: Session, user_id: str, resolved: Optional[bool] = None, days: int = 7) -> List[CampaignPerformanceAlert]:
        """Get performance alerts for a user"""
        
        try:
            query = db.query(CampaignPerformanceAlert).filter(
                CampaignPerformanceAlert.user_id == user_id,
                CampaignPerformanceAlert.created_at > datetime.utcnow() - timedelta(days=days)
            )
            
            if resolved is not None:
                query = query.filter(CampaignPerformanceAlert.resolved == resolved)
            
            return query.order_by(CampaignPerformanceAlert.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error fetching performance alerts: {e}")
            return []
    
    def resolve_alert(self, db: Session, alert_id: int, action_taken: str) -> bool:
        """Mark a performance alert as resolved"""
        
        try:
            alert = db.query(CampaignPerformanceAlert).filter(CampaignPerformanceAlert.id == alert_id).first()
            
            if not alert:
                logger.warning(f"Alert {alert_id} not found")
                return False
            
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.action_taken = action_taken
            
            db.commit()
            
            logger.info(f"Alert {alert_id} resolved with action: {action_taken}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            db.rollback()
            return False
    
    def _create_performance_alert(self, db: Session, decision_log: AIDecisionLog, alert_type: str, message: str) -> CampaignPerformanceAlert:
        """Create a performance alert"""
        
        # Determine severity based on deviation
        deviation = getattr(decision_log, 'performance_deviation', 0)
        if deviation > 50:
            severity = "critical"
        elif deviation > 30:
            severity = "high" 
        elif deviation > 20:
            severity = "medium"
        else:
            severity = "low"
        
        alert = CampaignPerformanceAlert(
            campaign_id=decision_log.campaign_id or "unknown",
            user_id=decision_log.user_id,
            alert_type=alert_type,
            severity=severity,
            predicted_value=decision_log.predicted_value,
            actual_value=decision_log.actual_result,
            deviation_percentage=decision_log.performance_deviation,
            alert_message=message
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        return alert
    
    def _get_metric_key(self, prediction_type: str) -> str:
        """Map prediction type to metric key"""
        mapping = {
            "roi": "roi",
            "ctr": "ctr", 
            "conversion_rate": "conversion_rate",
            "budget_allocation": "spend"
        }
        return mapping.get(prediction_type, prediction_type)


# Global monitoring service instance
ai_monitoring_service = AIMonitoringService()