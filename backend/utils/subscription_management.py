"""
Subscription Management System for AI Marketing Automation Platform
Direct Payment Model - Users pay Meta directly for ads, platform charges for automation service

CLEANED UP VERSION:
- Removed duplicate usage tracking methods (moved to UsageTrackingService)
- Removed mock/demo functions and example data
- Removed legacy dictionary-based subscription handling
- Simplified to focus on subscription creation and payment integration only
- All usage tracking and tier enforcement moved to dedicated services
"""

from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Dict, Optional, Any
from backend.integrations.payment.upi_payment_service import upi_payment_service
from backend.database.crud import BillingSubscriptionCRUD, PaymentCRUD
from backend.database.models import SubscriptionTier, SubscriptionStatus, PaymentProvider
from backend.core.config import settings

load_dotenv()

class PlatformSubscriptionManager:
    """
    Manages platform subscriptions with Google Pay integration
    Users pay Meta directly for ads, platform charges for automation services
    """

    # Subscription Pricing (Monthly INR) - Using config.py as single source of truth
    PRICING = {
        SubscriptionTier.BASIC: {
            'monthly_price': settings.PRICING_TIERS['basic']['price_monthly'],  # ₹2,999
            'campaigns_limit': settings.PRICING_TIERS['basic']['campaigns_limit'],  # 5
            'ad_accounts_limit': 1,
            'ai_generations_limit': settings.PRICING_TIERS['basic']['ai_generations_limit'],  # 150
            'analytics_retention_days': 30,
            'ad_spend_monitoring_limit': settings.PRICING_TIERS['basic']['ad_spend_monitoring_limit'],  # ₹25,000
            'platforms': ['Facebook', 'Instagram'],
            'support_level': settings.PRICING_TIERS['basic']['support_level'],
            'features': [
                '5 Facebook/Instagram campaigns per month',
                '150 AI content generations per month',
                'Basic AI content generation (text + image)',
                'Facebook & Instagram posting',
                'Basic analytics (last 30 days)',
                'Budget monitoring up to ₹25,000',
                'Email support'
            ]
        },
        SubscriptionTier.PROFESSIONAL: {
            'monthly_price': settings.PRICING_TIERS['professional']['price_monthly'],  # ₹7,999
            'campaigns_limit': settings.PRICING_TIERS['professional']['campaigns_limit'],  # 20
            'ad_accounts_limit': 3,
            'ai_generations_limit': settings.PRICING_TIERS['professional']['ai_generations_limit'],  # 500
            'analytics_retention_days': 90,
            'ad_spend_monitoring_limit': settings.PRICING_TIERS['professional']['ad_spend_monitoring_limit'],  # ₹1,00,000
            'platforms': ['Facebook', 'Instagram'],
            'support_level': settings.PRICING_TIERS['professional']['support_level'],
            'features': [
                '20 Facebook/Instagram campaigns per month',
                '500 AI content generations per month',
                'Advanced AI content generation (text + image + video thumbnails)',
                'Advanced Facebook & Instagram automation',
                'Enhanced analytics (90 days + performance tracking)',
                'Budget monitoring up to ₹1,00,000',
                'Priority email support',
                'Campaign templates library'
            ]
        },
        SubscriptionTier.BUSINESS: {
            'monthly_price': settings.PRICING_TIERS['business']['price_monthly'],  # ₹19,999
            'campaigns_limit': settings.PRICING_TIERS['business']['campaigns_limit'],  # 50
            'ad_accounts_limit': -1,  # Unlimited
            'ai_generations_limit': settings.PRICING_TIERS['business']['ai_generations_limit'],  # 1200
            'analytics_retention_days': 365,
            'ad_spend_monitoring_limit': settings.PRICING_TIERS['business']['ad_spend_monitoring_limit'],  # ₹5,00,000
            'platforms': ['Facebook', 'Instagram'],
            'support_level': settings.PRICING_TIERS['business']['support_level'],
            'features': [
                '50 Facebook/Instagram campaigns per month',
                '1200 AI content generations per month',
                'Premium AI content generation (all formats + brand customization)',
                'Full Facebook & Instagram automation suite',
                'Full analytics suite (12 months + custom reporting)',
                'Budget monitoring up to ₹5,00,000',
                'Premium email support',
                'Data export and custom reporting',
                'Advanced performance tracking'
            ]
        }
    }
    
    def __init__(self):
        self.upi_payment_service = upi_payment_service
        
        # Initialize Razorpay plan IDs if not already created
        self.razorpay_plan_ids = {
            'basic': os.getenv('RAZORPAY_BASIC_PLAN_ID'),
            'professional': os.getenv('RAZORPAY_PROFESSIONAL_PLAN_ID'),
            'business': os.getenv('RAZORPAY_BUSINESS_PLAN_ID')
        }
        
    async def create_subscription_with_upi(
        self, 
        db_session,
        user_id: str, 
        user_email: str,
        tier: SubscriptionTier, 
        trial_days: int = 30,  # Changed to 1 month (30 days)
        user_name: str = None
    ) -> Dict[str, any]:
        """
        Create new platform subscription for user
        
        Args:
            user_id: Unique user identifier
            tier: Subscription tier
            trial_days: Free trial duration
            
        Returns:
            Dict with subscription details
        """
        """Create new subscription with UPI integration"""
        try:
            
            # Create database subscription
            subscription = BillingSubscriptionCRUD.create_subscription(
                db=db_session,
                user_id=user_id,
                tier=tier,
                monthly_price=self.PRICING[tier]['monthly_price'],
                trial_days=trial_days,
                provider=PaymentProvider.UPI
            )
            
            print(f"✅ Created {tier.value} subscription for user {user_id}")
            print(f"🎁 Trial period: {trial_days} days")
            print(f"💰 Monthly price after trial: ₹{self.PRICING[tier]['monthly_price']}")
            
            return {
                "success": True,
                "subscription": {
                    "subscription_id": subscription.id,
                    "user_id": subscription.user_id,
                    "tier": subscription.tier.value,
                    "status": subscription.status.value,
                    "monthly_price": subscription.monthly_price,
                    "currency": "INR",
                    "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
                    "limits": {
                        "campaigns": subscription.max_campaigns,
                        "ai_generations": subscription.max_ai_generations,
                        "api_calls": subscription.max_api_calls,
                        "analytics_retention_days": subscription.analytics_retention_days
                    },
                    "features": self.PRICING[tier]['features']
                }
            }
            
        except Exception as e:
            print(f"❌ Error creating subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def activate_subscription_with_payment(
        self, 
        db_session,
        subscription_id: str,
        razorpay_payment_id: str,
        razorpay_order_id: str,
        razorpay_signature: str
    ) -> Dict[str, Any]:
        """Activate subscription after successful UPI payment"""
        try:
            # Verify payment first
            payment_verification = await self.upi_payment_service.verify_upi_payment(
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature
            )
            
            if not payment_verification.get("success"):
                return {
                    "success": False,
                    "error": f"Payment verification failed: {payment_verification.get('error')}"
                }
            
            # Get subscription from database
            subscription = BillingSubscriptionCRUD.get_user_subscription(db_session, subscription_id)
            if not subscription:
                return {"success": False, "error": "Subscription not found"}
            
            # Update database subscription status to active
            BillingSubscriptionCRUD.update_subscription_status(
                db=db_session,
                subscription_id=subscription_id,
                status=SubscriptionStatus.ACTIVE,
                provider_subscription_id=razorpay_payment_id  # Store payment ID as reference
            )
            
            # Record payment in database
            PaymentCRUD.create_payment(
                db=db_session,
                user_id=subscription.user_id,
                subscription_id=subscription_id,
                amount=payment_verification["payment"]["amount"] / 100,  # Convert from paise to rupees
                currency="INR",
                provider=PaymentProvider.UPI,
                provider_payment_id=razorpay_payment_id,
                status="completed"
            )
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "payment_id": razorpay_payment_id,
                "status": "active"
            }
            
        except Exception as e:
            print(f"❌ Error activating subscription: {e}")
            return {"success": False, "error": str(e)}
    
    # Removed: check_usage_limits method (functionality moved to TierEnforcementMiddleware)
    
    # Removed: track_usage method (functionality moved to UsageTrackingService)
    
    # Removed: get_subscription_summary method (functionality available in UsageTrackingService.get_usage_summary)
    
    # Removed: _calculate_trial_days_remaining method (unused after removing get_subscription_summary)
    
    # Removed: upgrade_subscription method (functionality should be handled via database CRUD operations)
    
    def get_pricing_comparison(self) -> Dict[str, any]:
        """Get pricing comparison table for frontend display"""
        comparison = {}
        
        # Map tier names to display names
        tier_names = {
            'basic': 'Basic',
            'professional': 'Professional',
            'business': 'Business'
        }
        
        for tier, details in self.PRICING.items():
            comparison[tier.value] = {
                'name': tier_names.get(tier.value, tier.value.title()),
                'price': f"₹{details['monthly_price']}/month",
                'campaigns': 'Unlimited' if details['campaigns_limit'] == -1 else f"{details['campaigns_limit']} campaigns/month",
                'ai_generations': 'Unlimited' if details['ai_generations_limit'] == -1 else f"{details['ai_generations_limit']}/month",
                'ad_accounts': 'Unlimited' if details['ad_accounts_limit'] == -1 else f"{details['ad_accounts_limit']} accounts",
                'analytics': f"{details['analytics_retention_days']} days retention",
                'platforms': details.get('platforms', []),
                'features': details['features']
            }
        
        return comparison
