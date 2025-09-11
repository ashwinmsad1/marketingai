"""
Automated Campaign Safety Guards
Real-time monitoring and automatic protection against campaign performance issues
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class GuardAction(Enum):
    """Types of safety guard actions"""
    MONITOR = "monitor"
    ALERT = "alert" 
    THROTTLE = "throttle"
    PAUSE = "pause"
    ROLLBACK = "rollback"
    EMERGENCY_STOP = "emergency_stop"

class GuardTrigger(Enum):
    """Safety guard trigger conditions"""
    PERFORMANCE_DROP = "performance_drop"
    SPEND_VELOCITY = "spend_velocity"
    ANOMALY_DETECTION = "anomaly_detection"
    BUDGET_EXCEEDED = "budget_exceeded"
    CONVERSION_FAILURE = "conversion_failure"
    QUALITY_DECLINE = "quality_decline"

@dataclass
class SafetyThreshold:
    """Safety threshold configuration"""
    metric: str
    operator: str  # gt, lt, gte, lte, eq
    value: float
    duration_minutes: int = 30  # How long condition must persist
    action: GuardAction = GuardAction.ALERT
    severity: str = "medium"  # low, medium, high, critical

@dataclass
class GuardViolation:
    """Safety guard violation record"""
    guard_name: str
    trigger: GuardTrigger
    campaign_id: str
    user_id: str
    metric: str
    current_value: float
    threshold_value: float
    action_taken: GuardAction
    timestamp: datetime
    message: str
    severity: str
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class CampaignSafetyGuards:
    """
    Automated Campaign Safety Guards System
    Monitors campaigns and automatically takes protective actions
    """
    
    def __init__(self):
        """Initialize safety guards with default thresholds"""
        
        # Configure default safety thresholds
        self.safety_thresholds = {
            # Performance-based guards
            "roi_drop": SafetyThreshold(
                metric="roi",
                operator="lt", 
                value=2.0,  # ROI drops below 2x
                duration_minutes=60,
                action=GuardAction.ALERT,
                severity="medium"
            ),
            "critical_roi_drop": SafetyThreshold(
                metric="roi", 
                operator="lt",
                value=0.5,  # ROI drops below 0.5x (losing money)
                duration_minutes=30,
                action=GuardAction.PAUSE,
                severity="critical"
            ),
            "ctr_collapse": SafetyThreshold(
                metric="ctr",
                operator="lt",
                value=0.5,  # CTR drops below 0.5%
                duration_minutes=45,
                action=GuardAction.THROTTLE,
                severity="high"
            ),
            "conversion_failure": SafetyThreshold(
                metric="conversion_rate",
                operator="lt",
                value=0.1,  # Conversion rate below 0.1%
                duration_minutes=30,
                action=GuardAction.PAUSE,
                severity="high"
            ),
            
            # Spend-based guards
            "spend_velocity_high": SafetyThreshold(
                metric="hourly_spend_rate",
                operator="gt",
                value=5000.0,  # Spending more than ₹5,000/hour (realistic for Indian SMEs)
                duration_minutes=15,
                action=GuardAction.THROTTLE,
                severity="high"
            ),
            "budget_exceeded": SafetyThreshold(
                metric="budget_utilization",
                operator="gt", 
                value=0.95,  # 95% of budget used
                duration_minutes=0,  # Immediate action
                action=GuardAction.PAUSE,
                severity="critical"
            ),
            "daily_spend_spike": SafetyThreshold(
                metric="daily_spend_increase",
                operator="gt",
                value=2.0,  # Daily spend increased by 200%
                duration_minutes=30,
                action=GuardAction.ALERT,
                severity="medium"
            ),
            
            # Quality-based guards
            "engagement_drop": SafetyThreshold(
                metric="engagement_rate",
                operator="lt",
                value=1.0,  # Engagement below 1%
                duration_minutes=60,
                action=GuardAction.ALERT,
                severity="medium"
            ),
            "negative_feedback_spike": SafetyThreshold(
                metric="negative_feedback_rate",
                operator="gt",
                value=0.05,  # Negative feedback above 5%
                duration_minutes=20,
                action=GuardAction.PAUSE,
                severity="high"
            )
        }
        
        # Guard state tracking
        self.active_violations: Dict[str, List[GuardViolation]] = {}
        self.guard_history: List[GuardViolation] = []
        self.campaign_metrics_cache: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_violations_per_campaign = 50
        self.violation_history_days = 30
        
    async def monitor_campaign(
        self,
        campaign_id: str,
        user_id: str,
        current_metrics: Dict[str, float],
        campaign_config: Dict[str, Any],
        db: Optional[Session] = None
    ) -> List[GuardViolation]:
        """
        Monitor campaign against all safety guards and take protective actions
        
        Args:
            campaign_id: Campaign identifier
            user_id: User identifier
            current_metrics: Current campaign performance metrics
            campaign_config: Campaign configuration
            db: Database session
            
        Returns:
            List of any violations triggered
        """
        try:
            logger.info(f"Monitoring campaign safety: {campaign_id}")
            
            violations = []
            
            # Update metrics cache
            self._update_metrics_cache(campaign_id, current_metrics, campaign_config)
            
            # Check each safety threshold
            for guard_name, threshold in self.safety_thresholds.items():
                violation = await self._check_safety_threshold(
                    guard_name, threshold, campaign_id, user_id, current_metrics, campaign_config
                )
                
                if violation:
                    violations.append(violation)
                    
                    # Record violation
                    self._record_violation(campaign_id, violation)
                    
                    # Execute safety action
                    await self._execute_safety_action(violation, db)
            
            # Check for compound violations (multiple issues at once)
            compound_violations = self._check_compound_violations(
                campaign_id, user_id, violations, current_metrics
            )
            violations.extend(compound_violations)
            
            # Clean up old violations
            self._cleanup_old_violations()
            
            if violations:
                logger.warning(
                    f"Safety violations detected for campaign {campaign_id}: "
                    f"{len(violations)} violations"
                )
            
            return violations
            
        except Exception as e:
            logger.error(f"Error monitoring campaign safety: {e}")
            # Create emergency violation for monitoring failure
            emergency_violation = GuardViolation(
                guard_name="monitoring_failure",
                trigger=GuardTrigger.ANOMALY_DETECTION,
                campaign_id=campaign_id,
                user_id=user_id,
                metric="monitoring_system",
                current_value=0.0,
                threshold_value=1.0,
                action_taken=GuardAction.EMERGENCY_STOP,
                timestamp=datetime.now(),
                message=f"Campaign monitoring system failure: {str(e)}",
                severity="critical"
            )
            return [emergency_violation]
    
    async def _check_safety_threshold(
        self,
        guard_name: str,
        threshold: SafetyThreshold,
        campaign_id: str,
        user_id: str,
        current_metrics: Dict[str, float],
        campaign_config: Dict[str, Any]
    ) -> Optional[GuardViolation]:
        """Check individual safety threshold"""
        
        try:
            # Get current metric value
            current_value = current_metrics.get(threshold.metric)
            if current_value is None:
                return None  # Metric not available
            
            # Apply operator check
            threshold_violated = False
            if threshold.operator == "gt":
                threshold_violated = current_value > threshold.value
            elif threshold.operator == "lt":
                threshold_violated = current_value < threshold.value
            elif threshold.operator == "gte":
                threshold_violated = current_value >= threshold.value
            elif threshold.operator == "lte":
                threshold_violated = current_value <= threshold.value
            elif threshold.operator == "eq":
                threshold_violated = current_value == threshold.value
            
            if not threshold_violated:
                return None  # Threshold not violated
            
            # Check duration requirement
            if threshold.duration_minutes > 0:
                if not self._has_persistent_violation(
                    campaign_id, guard_name, threshold.duration_minutes
                ):
                    return None  # Not persistent enough
            
            # Determine appropriate trigger
            trigger = self._determine_trigger_type(threshold.metric)
            
            # Create violation
            violation = GuardViolation(
                guard_name=guard_name,
                trigger=trigger,
                campaign_id=campaign_id,
                user_id=user_id,
                metric=threshold.metric,
                current_value=current_value,
                threshold_value=threshold.value,
                action_taken=threshold.action,
                timestamp=datetime.now(),
                message=self._generate_violation_message(
                    guard_name, threshold, current_value
                ),
                severity=threshold.severity
            )
            
            return violation
            
        except Exception as e:
            logger.error(f"Error checking threshold {guard_name}: {e}")
            return None
    
    def _check_compound_violations(
        self,
        campaign_id: str,
        user_id: str,
        current_violations: List[GuardViolation],
        current_metrics: Dict[str, float]
    ) -> List[GuardViolation]:
        """Check for compound violations (multiple issues together)"""
        
        compound_violations = []
        
        try:
            # Check for performance collapse (multiple performance metrics failing)
            performance_violations = [
                v for v in current_violations
                if v.metric in ["roi", "ctr", "conversion_rate", "engagement_rate"]
            ]
            
            if len(performance_violations) >= 3:
                compound_violation = GuardViolation(
                    guard_name="performance_collapse",
                    trigger=GuardTrigger.PERFORMANCE_DROP,
                    campaign_id=campaign_id,
                    user_id=user_id,
                    metric="multiple_performance",
                    current_value=len(performance_violations),
                    threshold_value=3.0,
                    action_taken=GuardAction.EMERGENCY_STOP,
                    timestamp=datetime.now(),
                    message=f"Performance collapse detected: {len(performance_violations)} metrics failing",
                    severity="critical"
                )
                compound_violations.append(compound_violation)
            
            # Check for spend + performance issue (spending money with poor performance)
            spend_violations = [v for v in current_violations if "spend" in v.metric]
            roi_violations = [v for v in current_violations if v.metric == "roi"]
            
            if spend_violations and roi_violations:
                compound_violation = GuardViolation(
                    guard_name="inefficient_spending",
                    trigger=GuardTrigger.SPEND_VELOCITY,
                    campaign_id=campaign_id,
                    user_id=user_id,
                    metric="spend_efficiency",
                    current_value=0.0,  # Combined metric
                    threshold_value=1.0,
                    action_taken=GuardAction.PAUSE,
                    timestamp=datetime.now(),
                    message="High spending with poor ROI detected",
                    severity="high"
                )
                compound_violations.append(compound_violation)
            
        except Exception as e:
            logger.error(f"Error checking compound violations: {e}")
        
        return compound_violations
    
    async def _execute_safety_action(
        self,
        violation: GuardViolation,
        db: Optional[Session] = None
    ):
        """Execute the appropriate safety action for a violation"""
        
        try:
            logger.info(f"Executing safety action: {violation.action_taken.value} for {violation.campaign_id}")
            
            if violation.action_taken == GuardAction.MONITOR:
                # Just log and continue monitoring
                await self._log_monitoring_action(violation)
                
            elif violation.action_taken == GuardAction.ALERT:
                # Send alert to user/admin
                await self._send_safety_alert(violation)
                
            elif violation.action_taken == GuardAction.THROTTLE:
                # Reduce campaign spend/pace
                await self._throttle_campaign(violation, db)
                
            elif violation.action_taken == GuardAction.PAUSE:
                # Pause campaign
                await self._pause_campaign(violation, db)
                
            elif violation.action_taken == GuardAction.ROLLBACK:
                # Rollback recent changes
                await self._rollback_campaign(violation, db)
                
            elif violation.action_taken == GuardAction.EMERGENCY_STOP:
                # Emergency stop all related activities
                await self._emergency_stop_campaign(violation, db)
            
            logger.info(f"Safety action executed successfully for violation: {violation.guard_name}")
            
        except Exception as e:
            logger.error(f"Failed to execute safety action for {violation.guard_name}: {e}")
            # Escalate to emergency action if primary action fails
            await self._emergency_stop_campaign(violation, db)
    
    async def _log_monitoring_action(self, violation: GuardViolation):
        """Log monitoring action"""
        logger.info(
            f"MONITOR: Campaign {violation.campaign_id} - {violation.message}"
        )
    
    async def _send_safety_alert(self, violation: GuardViolation):
        """Send safety alert to stakeholders"""
        
        # In production, this would integrate with notification systems
        alert_message = (
            f"🚨 Campaign Safety Alert 🚨\n"
            f"Campaign: {violation.campaign_id}\n"
            f"Issue: {violation.message}\n"
            f"Severity: {violation.severity}\n"
            f"Time: {violation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Metric: {violation.metric} = {violation.current_value:.2f} "
            f"(threshold: {violation.threshold_value:.2f})"
        )
        
        logger.warning(f"SAFETY ALERT: {alert_message}")
        
        # TODO: Integrate with email, Slack, SMS notifications
        # await self.notification_service.send_alert(violation.user_id, alert_message)
    
    async def _throttle_campaign(self, violation: GuardViolation, db: Optional[Session]):
        """Throttle campaign spend/pace"""
        
        try:
            # Reduce campaign budget by 50%
            throttle_factor = 0.5
            
            logger.warning(
                f"THROTTLE: Reducing campaign {violation.campaign_id} pace by {(1-throttle_factor)*100:.0f}%"
            )
            
            # In production, integrate with ad platform APIs
            # await self.ad_platform.update_campaign_budget(
            #     violation.campaign_id, 
            #     current_budget * throttle_factor
            # )
            
            # Record action in database if available
            if db:
                await self._record_safety_action(violation, db, {"throttle_factor": throttle_factor})
            
        except Exception as e:
            logger.error(f"Failed to throttle campaign {violation.campaign_id}: {e}")
    
    async def _pause_campaign(self, violation: GuardViolation, db: Optional[Session]):
        """Pause campaign"""
        
        try:
            logger.warning(f"PAUSE: Pausing campaign {violation.campaign_id} due to {violation.guard_name}")
            
            # In production, integrate with ad platform APIs
            # await self.ad_platform.pause_campaign(violation.campaign_id)
            
            # Record action in database
            if db:
                await self._record_safety_action(violation, db, {"paused": True})
            
        except Exception as e:
            logger.error(f"Failed to pause campaign {violation.campaign_id}: {e}")
    
    async def _rollback_campaign(self, violation: GuardViolation, db: Optional[Session]):
        """Rollback recent campaign changes"""
        
        try:
            logger.warning(f"ROLLBACK: Rolling back campaign {violation.campaign_id}")
            
            # In production, restore previous campaign settings
            # previous_config = await self.get_previous_campaign_config(violation.campaign_id)
            # await self.ad_platform.update_campaign(violation.campaign_id, previous_config)
            
            # Record action in database
            if db:
                await self._record_safety_action(violation, db, {"rollback": True})
            
        except Exception as e:
            logger.error(f"Failed to rollback campaign {violation.campaign_id}: {e}")
    
    async def _emergency_stop_campaign(self, violation: GuardViolation, db: Optional[Session]):
        """Emergency stop campaign and related activities"""
        
        try:
            logger.critical(f"EMERGENCY STOP: Emergency stopping campaign {violation.campaign_id}")
            
            # In production, immediately stop all campaign activities
            # await self.ad_platform.emergency_stop_campaign(violation.campaign_id)
            # await self.notification_service.send_critical_alert(violation)
            
            # Record critical action in database
            if db:
                await self._record_safety_action(violation, db, {"emergency_stop": True})
            
        except Exception as e:
            logger.critical(f"Failed to emergency stop campaign {violation.campaign_id}: {e}")
    
    async def _record_safety_action(
        self,
        violation: GuardViolation,
        db: Session,
        action_details: Dict[str, Any]
    ):
        """Record safety action in database"""
        
        try:
            # In production, this would store in a safety_actions table
            action_record = {
                "violation_id": f"{violation.campaign_id}_{violation.guard_name}_{violation.timestamp}",
                "campaign_id": violation.campaign_id,
                "user_id": violation.user_id,
                "action_type": violation.action_taken.value,
                "action_details": action_details,
                "timestamp": violation.timestamp,
                "severity": violation.severity
            }
            
            logger.info(f"Recorded safety action: {action_record}")
            
        except Exception as e:
            logger.error(f"Failed to record safety action: {e}")
    
    def _update_metrics_cache(
        self,
        campaign_id: str,
        current_metrics: Dict[str, float],
        campaign_config: Dict[str, Any]
    ):
        """Update campaign metrics cache for persistence checking"""
        
        try:
            if campaign_id not in self.campaign_metrics_cache:
                self.campaign_metrics_cache[campaign_id] = {
                    "history": [],
                    "config": campaign_config
                }
            
            # Add current metrics with timestamp
            metrics_entry = {
                "timestamp": datetime.now(),
                "metrics": current_metrics.copy()
            }
            
            self.campaign_metrics_cache[campaign_id]["history"].append(metrics_entry)
            
            # Keep only last 24 hours of data
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.campaign_metrics_cache[campaign_id]["history"] = [
                entry for entry in self.campaign_metrics_cache[campaign_id]["history"]
                if entry["timestamp"] > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Failed to update metrics cache: {e}")
    
    def _has_persistent_violation(
        self,
        campaign_id: str,
        guard_name: str,
        duration_minutes: int
    ) -> bool:
        """Check if violation has persisted for required duration"""
        
        try:
            if campaign_id not in self.campaign_metrics_cache:
                return False
            
            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            
            # Check if violation existed in the past duration_minutes
            history = self.campaign_metrics_cache[campaign_id]["history"]
            relevant_entries = [
                entry for entry in history
                if entry["timestamp"] > cutoff_time
            ]
            
            # If we don't have enough history, assume not persistent
            if len(relevant_entries) < 2:
                return False
            
            # For simplicity, assume persistent if we have recent entries
            # In production, would check actual threshold violations in history
            return True
            
        except Exception as e:
            logger.error(f"Error checking violation persistence: {e}")
            return False
    
    def _determine_trigger_type(self, metric: str) -> GuardTrigger:
        """Determine trigger type based on metric"""
        
        if metric in ["roi", "ctr", "conversion_rate", "engagement_rate"]:
            return GuardTrigger.PERFORMANCE_DROP
        elif "spend" in metric or "budget" in metric:
            return GuardTrigger.SPEND_VELOCITY
        elif metric in ["negative_feedback_rate"]:
            return GuardTrigger.QUALITY_DECLINE
        else:
            return GuardTrigger.ANOMALY_DETECTION
    
    def _generate_violation_message(
        self,
        guard_name: str,
        threshold: SafetyThreshold,
        current_value: float
    ) -> str:
        """Generate human-readable violation message"""
        
        messages = {
            "roi_drop": f"ROI dropped to {current_value:.1f}x (threshold: {threshold.value:.1f}x)",
            "critical_roi_drop": f"Critical ROI drop to {current_value:.1f}x - losing money!",
            "ctr_collapse": f"CTR collapsed to {current_value:.2f}% (threshold: {threshold.value:.2f}%)",
            "conversion_failure": f"Conversion rate dropped to {current_value:.2f}%",
            "spend_velocity_high": f"High spend velocity: ₹{current_value:.0f}/hour (recommended max: ₹5,000/hour)",
            "budget_exceeded": f"Budget {current_value:.1%} utilized (limit: {threshold.value:.1%})",
            "daily_spend_spike": f"Daily spend increased {current_value:.1f}x",
            "engagement_drop": f"Engagement dropped to {current_value:.2f}%",
            "negative_feedback_spike": f"Negative feedback increased to {current_value:.2%}"
        }
        
        return messages.get(
            guard_name,
            f"{threshold.metric} violation: {current_value} {threshold.operator} {threshold.value}"
        )
    
    def _record_violation(self, campaign_id: str, violation: GuardViolation):
        """Record violation in memory for tracking"""
        
        if campaign_id not in self.active_violations:
            self.active_violations[campaign_id] = []
        
        self.active_violations[campaign_id].append(violation)
        self.guard_history.append(violation)
        
        # Limit active violations per campaign
        if len(self.active_violations[campaign_id]) > self.max_violations_per_campaign:
            self.active_violations[campaign_id].pop(0)
        
        # Limit total history
        if len(self.guard_history) > 10000:
            self.guard_history = self.guard_history[-5000:]  # Keep last 5000
    
    def _cleanup_old_violations(self):
        """Clean up old resolved violations"""
        
        try:
            cutoff_time = datetime.now() - timedelta(days=self.violation_history_days)
            
            # Clean up history
            self.guard_history = [
                v for v in self.guard_history
                if v.timestamp > cutoff_time
            ]
            
            # Clean up active violations (resolved ones)
            for campaign_id in list(self.active_violations.keys()):
                self.active_violations[campaign_id] = [
                    v for v in self.active_violations[campaign_id]
                    if not v.resolved or v.timestamp > cutoff_time
                ]
                
                # Remove empty campaign entries
                if not self.active_violations[campaign_id]:
                    del self.active_violations[campaign_id]
            
        except Exception as e:
            logger.error(f"Failed to cleanup old violations: {e}")
    
    # Public API methods
    
    def get_campaign_violations(
        self,
        campaign_id: str,
        active_only: bool = False
    ) -> List[GuardViolation]:
        """Get violations for a specific campaign"""
        
        if active_only:
            return self.active_violations.get(campaign_id, [])
        else:
            return [v for v in self.guard_history if v.campaign_id == campaign_id]
    
    def get_safety_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive safety status for campaign"""
        
        try:
            violations = self.get_campaign_violations(campaign_id, active_only=True)
            
            # Count violations by severity
            severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            for violation in violations:
                severity_counts[violation.severity] += 1
            
            # Determine overall status
            if severity_counts["critical"] > 0:
                overall_status = "critical"
            elif severity_counts["high"] > 0:
                overall_status = "high_risk"
            elif severity_counts["medium"] > 0:
                overall_status = "caution"
            elif severity_counts["low"] > 0:
                overall_status = "minor_issues"
            else:
                overall_status = "healthy"
            
            return {
                "campaign_id": campaign_id,
                "overall_status": overall_status,
                "total_violations": len(violations),
                "severity_breakdown": severity_counts,
                "last_check": datetime.now().isoformat(),
                "requires_attention": overall_status in ["critical", "high_risk"]
            }
            
        except Exception as e:
            logger.error(f"Error getting safety status: {e}")
            return {
                "campaign_id": campaign_id,
                "overall_status": "unknown",
                "error": str(e)
            }
    
    def resolve_violation(
        self,
        campaign_id: str,
        violation_id: str,
        resolution_note: str = ""
    ) -> bool:
        """Mark a violation as resolved"""
        
        try:
            violations = self.active_violations.get(campaign_id, [])
            
            for violation in violations:
                violation_key = f"{violation.guard_name}_{violation.timestamp}"
                if violation_key == violation_id:
                    violation.resolved = True
                    violation.resolution_time = datetime.now()
                    logger.info(
                        f"Resolved violation {violation_id} for campaign {campaign_id}: {resolution_note}"
                    )
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving violation: {e}")
            return False
    
    def update_safety_thresholds(
        self,
        threshold_updates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Update safety thresholds (admin function)"""
        
        results = {}
        
        for guard_name, updates in threshold_updates.items():
            try:
                if guard_name in self.safety_thresholds:
                    threshold = self.safety_thresholds[guard_name]
                    
                    # Update allowed fields
                    if "value" in updates:
                        threshold.value = float(updates["value"])
                    if "duration_minutes" in updates:
                        threshold.duration_minutes = int(updates["duration_minutes"])
                    if "action" in updates:
                        threshold.action = GuardAction(updates["action"])
                    if "severity" in updates:
                        threshold.severity = updates["severity"]
                    
                    results[guard_name] = True
                    logger.info(f"Updated safety threshold: {guard_name}")
                else:
                    results[guard_name] = False
                    
            except Exception as e:
                logger.error(f"Failed to update threshold {guard_name}: {e}")
                results[guard_name] = False
        
        return results

# Global instance for use across the application
campaign_safety_guards = CampaignSafetyGuards()