"""
Budget monitoring and alert service
Provides real-time budget monitoring, alerts, and automated protective actions
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from backend.database.models import (
    User, Campaign, BudgetAlert, SpendingLimit, BudgetTransaction,
    BillingSubscription, CampaignStatus
)
from backend.core.config import settings

logger = logging.getLogger(__name__)

class BudgetMonitoringService:
    """Service for monitoring spending and generating alerts"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def monitor_campaign_spending(self, campaign_id: str) -> Dict:
        """Monitor individual campaign spending and generate alerts if needed"""
        
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found for monitoring")
            return {"error": "Campaign not found"}
        
        alerts_created = []
        actions_taken = []
        
        try:
            # Check campaign budget vs spending
            if campaign.budget_total and campaign.spend:
                spending_percentage = (campaign.spend / campaign.budget_total) * 100
                
                # Create alerts based on thresholds
                if spending_percentage >= 95 and not self._has_recent_alert(campaign_id, "budget_critical"):
                    alert = self._create_budget_alert(
                        user_id=campaign.user_id,
                        campaign_id=campaign_id,
                        alert_type="budget_critical",
                        severity="critical",
                        current_spending=campaign.spend,
                        budget_limit=campaign.budget_total,
                        spending_percentage=spending_percentage
                    )
                    alerts_created.append(alert)
                    
                    # Automatic action: Pause campaign
                    if self._should_auto_pause_campaign(campaign.user_id, campaign_id):
                        self._pause_campaign(campaign_id)
                        actions_taken.append("campaign_paused")
                
                elif spending_percentage >= 80 and not self._has_recent_alert(campaign_id, "budget_warning"):
                    alert = self._create_budget_alert(
                        user_id=campaign.user_id,
                        campaign_id=campaign_id,
                        alert_type="budget_warning",
                        severity="medium",
                        current_spending=campaign.spend,
                        budget_limit=campaign.budget_total,
                        spending_percentage=spending_percentage
                    )
                    alerts_created.append(alert)
            
            return {
                "campaign_id": campaign_id,
                "alerts_created": len(alerts_created),
                "actions_taken": actions_taken,
                "current_spending": campaign.spend or 0,
                "budget_limit": campaign.budget_total or 0
            }
            
        except Exception as e:
            logger.error(f"Error monitoring campaign {campaign_id}: {str(e)}")
            return {"error": str(e)}
    
    def monitor_user_spending(self, user_id: str) -> Dict:
        """Monitor user's overall spending across all campaigns"""
        
        try:
            # Get user's subscription and limits
            subscription = self._get_active_subscription(user_id)
            tier = subscription.tier.value if subscription else "starter"
            budget_limits = settings.get_budget_limits(tier)
            
            # Calculate current month spending
            current_spending = self._get_current_month_spending(user_id)
            monthly_limit = budget_limits["monthly_limit"]
            
            alerts_created = []
            actions_taken = []
            
            if monthly_limit > 0:  # Skip if unlimited
                spending_percentage = (current_spending / monthly_limit) * 100
                
                # Create alerts based on thresholds
                if spending_percentage >= 90 and not self._has_recent_alert(user_id, "monthly_limit_critical"):
                    alert = self._create_budget_alert(
                        user_id=user_id,
                        alert_type="monthly_limit_critical",
                        severity="critical",
                        current_spending=current_spending,
                        budget_limit=monthly_limit,
                        spending_percentage=spending_percentage
                    )
                    alerts_created.append(alert)
                    
                    # Consider pausing all active campaigns
                    if spending_percentage >= 100:
                        paused_campaigns = self._pause_user_campaigns(user_id)
                        if paused_campaigns:
                            actions_taken.append(f"paused_{paused_campaigns}_campaigns")
                
                elif spending_percentage >= 75 and not self._has_recent_alert(user_id, "monthly_limit_warning"):
                    alert = self._create_budget_alert(
                        user_id=user_id,
                        alert_type="monthly_limit_warning",
                        severity="medium",
                        current_spending=current_spending,
                        budget_limit=monthly_limit,
                        spending_percentage=spending_percentage
                    )
                    alerts_created.append(alert)
            
            return {
                "user_id": user_id,
                "subscription_tier": tier,
                "alerts_created": len(alerts_created),
                "actions_taken": actions_taken,
                "current_spending": current_spending,
                "monthly_limit": monthly_limit,
                "spending_percentage": (current_spending / monthly_limit) * 100 if monthly_limit > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error monitoring user {user_id} spending: {str(e)}")
            return {"error": str(e)}
    
    def check_spending_limits(self, user_id: str) -> List[Dict]:
        """Check user-defined spending limits and generate alerts"""
        
        try:
            # Get active spending limits
            limits = (
                self.db.query(SpendingLimit)
                .filter(
                    SpendingLimit.user_id == user_id,
                    SpendingLimit.is_active == True
                )
                .all()
            )
            
            alerts = []
            
            for limit in limits:
                current_spending = self._calculate_spending_for_limit(user_id, limit)
                spending_percentage = (current_spending / limit.limit_amount) * 100
                
                # Check thresholds
                if spending_percentage >= limit.critical_threshold:
                    if not self._has_recent_limit_alert(limit.id, "critical"):
                        alert = self._create_spending_limit_alert(limit, current_spending, "critical")
                        alerts.append(alert)
                        
                        # Take automatic action if configured
                        if limit.auto_pause_at_limit:
                            self._execute_limit_action(limit, "pause")
                
                elif spending_percentage >= limit.warning_threshold:
                    if not self._has_recent_limit_alert(limit.id, "warning"):
                        alert = self._create_spending_limit_alert(limit, current_spending, "warning")
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking spending limits for user {user_id}: {str(e)}")
            return []
    
    def create_budget_transaction(
        self,
        user_id: str,
        campaign_id: Optional[str],
        transaction_type: str,
        amount: float,
        description: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Optional[BudgetTransaction]:
        """Create a budget transaction record"""
        
        try:
            # Get current balance
            current_balance = self._get_user_balance(user_id)
            
            # Create transaction
            transaction = BudgetTransaction(
                user_id=user_id,
                campaign_id=campaign_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                reference_id=reference_id,
                balance_before=current_balance,
                balance_after=current_balance + amount if transaction_type in ["allocation", "refund"] else current_balance - amount,
                processed_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            logger.info(f"Created budget transaction: {transaction_type} ${amount} for user {user_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating budget transaction: {str(e)}")
            self.db.rollback()
            return None
    
    def get_budget_alerts(self, user_id: str, unacknowledged_only: bool = False) -> List[BudgetAlert]:
        """Get budget alerts for user"""
        
        query = self.db.query(BudgetAlert).filter(BudgetAlert.user_id == user_id)
        
        if unacknowledged_only:
            query = query.filter(BudgetAlert.is_acknowledged == False)
        
        return query.order_by(BudgetAlert.created_at.desc()).limit(50).all()
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Mark alert as acknowledged by user"""
        
        try:
            alert = (
                self.db.query(BudgetAlert)
                .filter(
                    BudgetAlert.id == alert_id,
                    BudgetAlert.user_id == user_id
                )
                .first()
            )
            
            if not alert:
                return False
            
            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
            return False
    
    def _create_budget_alert(
        self,
        user_id: str,
        alert_type: str,
        severity: str,
        current_spending: float,
        budget_limit: float,
        spending_percentage: float,
        campaign_id: Optional[str] = None
    ) -> BudgetAlert:
        """Create a budget alert"""
        
        # Generate alert title and message
        title, message = self._generate_alert_content(
            alert_type, current_spending, budget_limit, spending_percentage, campaign_id
        )
        
        alert = BudgetAlert(
            user_id=user_id,
            campaign_id=campaign_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            current_spending=current_spending,
            budget_limit=budget_limit,
            spending_percentage=spending_percentage
        )
        
        self.db.add(alert)
        self.db.commit()
        
        logger.warning(f"Created budget alert for user {user_id}: {title}")
        return alert
    
    def _generate_alert_content(
        self, 
        alert_type: str, 
        current_spending: float, 
        budget_limit: float, 
        spending_percentage: float,
        campaign_id: Optional[str] = None
    ) -> tuple[str, str]:
        """Generate alert title and message"""
        
        messages = {
            "budget_critical": {
                "title": "Critical: Campaign Budget Nearly Exhausted",
                "message": f"Campaign spending has reached ${current_spending:.2f} ({spending_percentage:.1f}%) of the ${budget_limit:.2f} budget. Campaign may be automatically paused to prevent overspending."
            },
            "budget_warning": {
                "title": "Warning: High Campaign Spending",
                "message": f"Campaign spending has reached ${current_spending:.2f} ({spending_percentage:.1f}%) of the ${budget_limit:.2f} budget. Please monitor spending closely."
            },
            "monthly_limit_critical": {
                "title": "Critical: Monthly Spending Limit Reached",
                "message": f"Monthly spending has reached ${current_spending:.2f} ({spending_percentage:.1f}%) of the ${budget_limit:.2f} limit. Active campaigns may be paused to prevent overspending."
            },
            "monthly_limit_warning": {
                "title": "Warning: Approaching Monthly Spending Limit",
                "message": f"Monthly spending has reached ${current_spending:.2f} ({spending_percentage:.1f}%) of the ${budget_limit:.2f} limit. Consider reviewing your campaigns."
            }
        }
        
        alert_content = messages.get(alert_type, {
            "title": "Budget Alert",
            "message": f"Spending alert: ${current_spending:.2f} of ${budget_limit:.2f} ({spending_percentage:.1f}%)"
        })
        
        return alert_content["title"], alert_content["message"]
    
    def _has_recent_alert(self, target_id: str, alert_type: str, hours: int = 24) -> bool:
        """Check if a similar alert was created recently"""
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Check by campaign_id or user_id
        query = (
            self.db.query(BudgetAlert)
            .filter(
                BudgetAlert.alert_type == alert_type,
                BudgetAlert.created_at >= cutoff
            )
        )
        
        # Determine if it's campaign or user alert
        if alert_type in ["budget_critical", "budget_warning"]:
            query = query.filter(BudgetAlert.campaign_id == target_id)
        else:
            query = query.filter(BudgetAlert.user_id == target_id)
        
        return query.first() is not None
    
    def _get_active_subscription(self, user_id: str) -> Optional[BillingSubscription]:
        """Get user's active subscription"""
        return (
            self.db.query(BillingSubscription)
            .filter(
                BillingSubscription.user_id == user_id,
                BillingSubscription.status.in_(["active", "trial"])
            )
            .first()
        )
    
    def _get_current_month_spending(self, user_id: str) -> float:
        """Calculate user's spending for current month"""
        
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        result = (
            self.db.query(func.coalesce(func.sum(Campaign.spend), 0))
            .filter(
                Campaign.user_id == user_id,
                Campaign.created_at >= month_start
            )
            .scalar()
        )
        
        return float(result or 0)
    
    def _should_auto_pause_campaign(self, user_id: str, campaign_id: str) -> bool:
        """Determine if campaign should be automatically paused"""
        
        # Check if user has auto-pause disabled
        # In a real implementation, this could be a user preference
        return True  # Default to auto-pause for safety
    
    def _pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign"""
        
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign and campaign.status == CampaignStatus.ACTIVE:
                campaign.status = CampaignStatus.PAUSED
                self.db.commit()
                
                logger.warning(f"Auto-paused campaign {campaign_id} due to budget limit")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {str(e)}")
            return False
    
    def _pause_user_campaigns(self, user_id: str) -> int:
        """Pause all active campaigns for a user"""
        
        try:
            updated = (
                self.db.query(Campaign)
                .filter(
                    Campaign.user_id == user_id,
                    Campaign.status == CampaignStatus.ACTIVE
                )
                .update({Campaign.status: CampaignStatus.PAUSED})
            )
            
            self.db.commit()
            
            if updated > 0:
                logger.warning(f"Auto-paused {updated} campaigns for user {user_id} due to spending limit")
            
            return updated
            
        except Exception as e:
            logger.error(f"Error pausing campaigns for user {user_id}: {str(e)}")
            return 0
    
    def _get_user_balance(self, user_id: str) -> float:
        """Get user's current balance"""
        
        # Sum all transactions
        result = (
            self.db.query(func.coalesce(func.sum(
                func.case(
                    (BudgetTransaction.transaction_type.in_(["allocation", "refund"]), BudgetTransaction.amount),
                    else_=-BudgetTransaction.amount
                )
            ), 0))
            .filter(BudgetTransaction.user_id == user_id)
            .scalar()
        )
        
        return float(result or 0)
    
    def _calculate_spending_for_limit(self, user_id: str, limit: SpendingLimit) -> float:
        """Calculate spending based on limit configuration"""
        
        now = datetime.utcnow()
        
        if limit.limit_type == "daily":
            start_time = datetime(now.year, now.month, now.day)
        elif limit.limit_type == "weekly":
            days_since_monday = now.weekday()
            start_time = now - timedelta(days=days_since_monday)
            start_time = datetime(start_time.year, start_time.month, start_time.day)
        elif limit.limit_type == "monthly":
            start_time = datetime(now.year, now.month, 1)
        else:
            # Total spending
            start_time = datetime(2020, 1, 1)  # Beginning of time for this platform
        
        # Calculate spending in the time period
        query = (
            self.db.query(func.coalesce(func.sum(Campaign.spend), 0))
            .filter(
                Campaign.user_id == user_id,
                Campaign.created_at >= start_time
            )
        )
        
        # Apply scope filter if specified
        if limit.applies_to == "campaign_id" and limit.target_id:
            query = query.filter(Campaign.id == limit.target_id)
        
        return float(query.scalar() or 0)
    
    def _has_recent_limit_alert(self, limit_id: str, threshold_type: str, hours: int = 24) -> bool:
        """Check if a limit alert was created recently"""
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # For this implementation, we'll use a simple approach
        # In production, you might want a separate table to track limit alerts
        return False
    
    def _create_spending_limit_alert(self, limit: SpendingLimit, current_spending: float, threshold_type: str) -> Dict:
        """Create an alert for spending limit threshold"""
        
        spending_percentage = (current_spending / limit.limit_amount) * 100
        
        return {
            "limit_id": limit.id,
            "threshold_type": threshold_type,
            "current_spending": current_spending,
            "limit_amount": limit.limit_amount,
            "spending_percentage": spending_percentage,
            "created_at": datetime.utcnow()
        }
    
    def _execute_limit_action(self, limit: SpendingLimit, action: str) -> bool:
        """Execute automatic action for spending limit"""
        
        try:
            if action == "pause":
                if limit.applies_to == "all":
                    self._pause_user_campaigns(limit.user_id)
                elif limit.applies_to == "campaign_id" and limit.target_id:
                    self._pause_campaign(limit.target_id)
                
                # Update limit to track when it was triggered
                limit.last_triggered = datetime.utcnow()
                self.db.commit()
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing limit action: {str(e)}")
            return False