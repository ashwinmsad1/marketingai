"""
Budget validation and monitoring service
Implements critical budget safety controls to prevent overspend
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import logging

from backend.database.models import (
    User, Campaign, BillingSubscription, SubscriptionTier,
    CampaignStatus, Payment, PaymentStatus
)
from backend.core.config import settings
from backend.core.schemas import BudgetValidationResult, CampaignBudget
from backend.core.exceptions import BudgetValidationError, InsufficientFundsError

logger = logging.getLogger(__name__)

class BudgetService:
    """Service for budget validation and spending controls"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def validate_campaign_budget(
        self, 
        user: User, 
        budget: CampaignBudget,
        campaign_id: Optional[str] = None
    ) -> BudgetValidationResult:
        """
        Comprehensive budget validation for campaign creation/updates
        
        Args:
            user: User creating/updating the campaign
            budget: Budget configuration from request
            campaign_id: Optional campaign ID for updates
            
        Returns:
            BudgetValidationResult with validation status and details
            
        Raises:
            BudgetValidationError: If budget validation fails critically
        """
        try:
            # Get user's subscription and tier
            subscription = self._get_active_subscription(user.id)
            tier = subscription.tier if subscription else SubscriptionTier.STARTER
            
            # Get budget limits for tier
            budget_limits = settings.get_budget_limits(tier.value)
            
            # Initialize result
            result = BudgetValidationResult(
                is_valid=True,
                remaining_budget=0.0,
                monthly_limit=budget_limits["monthly_limit"],
                campaigns_this_month=0,
                max_campaigns_per_month=budget_limits["max_campaigns_per_month"]
            )
            
            # Validate individual budget limits
            self._validate_budget_limits(budget, budget_limits, result)
            
            # Check monthly spending limits
            if budget_limits["requires_balance_check"]:
                self._validate_monthly_limits(user.id, budget, budget_limits, result, campaign_id)
            
            # Check campaign count limits
            self._validate_campaign_limits(user.id, budget_limits, result, campaign_id)
            
            # Check user balance if required
            if budget_limits["requires_balance_check"]:
                self._validate_user_balance(user.id, budget, result)
            
            # Final validation
            if result.errors:
                result.is_valid = False
                logger.warning(f"Budget validation failed for user {user.id}: {result.errors}")
            
            return result
            
        except Exception as e:
            logger.error(f"Budget validation error for user {user.id}: {str(e)}")
            raise BudgetValidationError(f"Budget validation failed: {str(e)}")
    
    def _validate_budget_limits(
        self, 
        budget: CampaignBudget, 
        limits: Dict, 
        result: BudgetValidationResult
    ) -> None:
        """Validate budget against tier limits"""
        
        # Check minimum budget
        if budget.total_budget and budget.total_budget < limits["min_campaign_budget"]:
            result.errors.append(
                f"Campaign budget ${budget.total_budget} is below minimum ${limits['min_campaign_budget']}"
            )
        
        if budget.daily_budget and budget.daily_budget < limits["min_campaign_budget"]:
            result.errors.append(
                f"Daily budget ${budget.daily_budget} is below minimum ${limits['min_campaign_budget']}"
            )
        
        # Check maximum budget
        if budget.total_budget and budget.total_budget > limits["max_campaign_budget"]:
            result.errors.append(
                f"Campaign budget ${budget.total_budget} exceeds maximum ${limits['max_campaign_budget']} for your tier"
            )
        
        # Check daily budget against monthly limit
        if (budget.daily_budget and limits["monthly_limit"] > 0 and 
            budget.daily_budget * 30 > limits["monthly_limit"]):
            result.warnings.append(
                f"Daily budget of ${budget.daily_budget} would exceed monthly limit if run for 30 days"
            )
    
    def _validate_monthly_limits(
        self, 
        user_id: str, 
        budget: CampaignBudget, 
        limits: Dict,
        result: BudgetValidationResult,
        campaign_id: Optional[str] = None
    ) -> None:
        """Validate against monthly spending limits"""
        
        # Skip if unlimited
        if limits["monthly_limit"] <= 0:
            result.remaining_budget = float('inf')
            return
        
        # Calculate current month spending
        current_month_spending = self._get_current_month_spending(user_id, campaign_id)
        result.remaining_budget = limits["monthly_limit"] - current_month_spending
        
        # Check if new campaign would exceed monthly limit
        campaign_budget = budget.total_budget or (budget.daily_budget * (budget.duration_days or 30))
        
        if campaign_budget > result.remaining_budget:
            result.errors.append(
                f"Campaign budget ${campaign_budget} would exceed remaining monthly budget ${result.remaining_budget:.2f}"
            )
        
        # Warnings for high spending
        utilization = (current_month_spending + campaign_budget) / limits["monthly_limit"]
        if utilization > 0.8:
            result.warnings.append(
                f"This campaign will use {utilization*100:.1f}% of your monthly budget limit"
            )
    
    def _validate_campaign_limits(
        self, 
        user_id: str, 
        limits: Dict,
        result: BudgetValidationResult,
        campaign_id: Optional[str] = None
    ) -> None:
        """Validate campaign count limits"""
        
        # Get current month campaign count
        current_month_campaigns = self._get_current_month_campaigns(user_id, campaign_id)
        result.campaigns_this_month = current_month_campaigns
        
        # Check limits
        if limits["max_campaigns_per_month"] > 0:
            if current_month_campaigns >= limits["max_campaigns_per_month"]:
                result.errors.append(
                    f"Monthly campaign limit of {limits['max_campaigns_per_month']} reached"
                )
            elif current_month_campaigns >= limits["max_campaigns_per_month"] * 0.8:
                result.warnings.append(
                    f"Approaching monthly campaign limit ({current_month_campaigns}/{limits['max_campaigns_per_month']})"
                )
    
    def _validate_user_balance(
        self, 
        user_id: str, 
        budget: CampaignBudget,
        result: BudgetValidationResult
    ) -> None:
        """Validate user has sufficient balance"""
        
        # Get user's available balance (simplified - in real implementation, integrate with payment provider)
        available_balance = self._get_user_balance(user_id)
        campaign_budget = budget.total_budget or (budget.daily_budget * (budget.duration_days or 30))
        
        if campaign_budget > available_balance:
            result.errors.append(
                f"Insufficient balance. Campaign requires ${campaign_budget}, available: ${available_balance}"
            )
    
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
    
    def _get_current_month_spending(self, user_id: str, exclude_campaign_id: Optional[str] = None) -> float:
        """Calculate user's spending for current month"""
        
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        query = (
            self.db.query(func.coalesce(func.sum(Campaign.budget_total), 0))
            .filter(
                Campaign.user_id == user_id,
                Campaign.created_at >= month_start,
                Campaign.status.in_([
                    CampaignStatus.ACTIVE,
                    CampaignStatus.COMPLETED,
                    CampaignStatus.PAUSED
                ])
            )
        )
        
        if exclude_campaign_id:
            query = query.filter(Campaign.id != exclude_campaign_id)
        
        result = query.scalar()
        return float(result or 0)
    
    def _get_current_month_campaigns(self, user_id: str, exclude_campaign_id: Optional[str] = None) -> int:
        """Count user's campaigns for current month"""
        
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        query = (
            self.db.query(func.count(Campaign.id))
            .filter(
                Campaign.user_id == user_id,
                Campaign.created_at >= month_start,
                Campaign.status != CampaignStatus.FAILED
            )
        )
        
        if exclude_campaign_id:
            query = query.filter(Campaign.id != exclude_campaign_id)
        
        return query.scalar() or 0
    
    def _get_user_balance(self, user_id: str) -> float:
        """Get user's available balance (simplified implementation)"""
        
        # In a real implementation, this would integrate with payment provider
        # For now, return a placeholder that allows testing
        
        # Sum successful payments
        total_payments = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.SUCCEEDED
            )
            .scalar() or 0
        )
        
        # Subtract current month spending
        current_spending = self._get_current_month_spending(user_id)
        
        return max(0, float(total_payments) - current_spending)
    
    def track_campaign_spend(self, campaign_id: str, amount: float) -> None:
        """Track campaign spending (called when ads are actually spent)"""
        
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found for spend tracking")
            return
        
        # Update campaign spend
        campaign.spend = (campaign.spend or 0) + amount
        
        # Check if spending exceeds budget
        if campaign.budget_total and campaign.spend > campaign.budget_total * 1.1:  # 10% buffer
            logger.warning(
                f"Campaign {campaign_id} spending ${campaign.spend} exceeds budget ${campaign.budget_total}"
            )
            # In production, this would trigger alerts and potentially pause the campaign
        
        self.db.commit()
        logger.info(f"Tracked ${amount} spend for campaign {campaign_id}, total: ${campaign.spend}")
    
    def get_spending_summary(self, user_id: str) -> Dict[str, float]:
        """Get user's spending summary"""
        
        now = datetime.utcnow()
        
        # Current month
        month_start = datetime(now.year, now.month, 1)
        current_month = self._get_current_month_spending(user_id)
        
        # Last 30 days
        thirty_days_ago = now - timedelta(days=30)
        last_30_days = (
            self.db.query(func.coalesce(func.sum(Campaign.spend), 0))
            .filter(
                Campaign.user_id == user_id,
                Campaign.created_at >= thirty_days_ago
            )
            .scalar() or 0
        )
        
        # All time
        total_spend = (
            self.db.query(func.coalesce(func.sum(Campaign.spend), 0))
            .filter(Campaign.user_id == user_id)
            .scalar() or 0
        )
        
        return {
            "current_month_budget": current_month,
            "current_month_spend": 0.0,  # Actual spend vs budget
            "last_30_days": float(last_30_days),
            "total_spend": float(total_spend),
            "available_balance": self._get_user_balance(user_id)
        }