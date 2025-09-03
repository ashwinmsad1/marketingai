"""
Subscription Management System for AI Marketing Automation Platform
Direct Payment Model - Users pay Meta directly for ads, platform charges for automation service
"""

from dotenv import load_dotenv
import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
import uuid
from upi_payment_service import upi_payment_service
from database.payment_crud import BillingSubscriptionCRUD, PaymentCRUD
from database.models import SubscriptionTier, SubscriptionStatus, PaymentProvider

load_dotenv()

# Import enums from models instead of duplicating them

class PlatformSubscriptionManager:
    """
    Manages platform subscriptions with Google Pay integration
    Users pay Meta directly for ads, platform charges for automation services
    """
    
    # Subscription Pricing (Monthly INR) - Simplified Business Consultant Recommended Plans
    PRICING = {
        SubscriptionTier.STARTER: {
            'monthly_price': 599.00,  # ₹599 - Essential Plan
            'campaigns_limit': 10,
            'ad_accounts_limit': 1,
            'ai_generations_limit': -1,  # Unlimited basic AI content
            'analytics_retention_days': 30,
            'platforms': ['Facebook', 'Instagram'],  # Facebook/Instagram only
            'features': [
                '10 Facebook/Instagram campaigns per month',
                'Basic AI content generation (text + image)',
                'Facebook & Instagram posting',
                'Basic analytics (last 30 days)',
                'Email support'
            ]
        },
        SubscriptionTier.PROFESSIONAL: {
            'monthly_price': 1299.00,  # ₹1,299 - Growth Plan
            'campaigns_limit': 50,
            'ad_accounts_limit': 3,
            'ai_generations_limit': -1,  # Unlimited advanced AI content
            'analytics_retention_days': 90,
            'platforms': ['Facebook', 'Instagram'],  # Facebook/Instagram only
            'features': [
                '50 Facebook/Instagram campaigns per month',
                'Advanced AI content generation (text + image + video thumbnails)',
                'Advanced Facebook & Instagram automation',
                'Performance analytics (90 days + basic insights)',
                'Phone + email support',
                'Campaign templates library'
            ]
        },
        SubscriptionTier.ENTERPRISE: {
            'monthly_price': 2499.00,  # ₹2,499 - Professional Plan
            'campaigns_limit': -1,  # Unlimited
            'ad_accounts_limit': -1,  # Unlimited
            'ai_generations_limit': -1,  # Unlimited premium AI content
            'analytics_retention_days': 365,
            'platforms': ['Facebook', 'Instagram'],  # Facebook/Instagram only
            'features': [
                'Unlimited Facebook/Instagram campaigns',
                'Premium AI content generation (all formats + brand customization)',
                'Full Facebook & Instagram automation suite',
                'Advanced analytics + reporting (12 months + competitor insights)',
                'White-label capabilities',
                'Dedicated account manager',
                'Priority support (2-hour response)'
            ]
        }
    }
    
    def __init__(self):
        self.upi_payment_service = upi_payment_service
        
        # Initialize Razorpay plan IDs if not already created
        self.razorpay_plan_ids = {
            'starter': os.getenv('RAZORPAY_STARTER_PLAN_ID'),
            'professional': os.getenv('RAZORPAY_PROFESSIONAL_PLAN_ID'), 
            'enterprise': os.getenv('RAZORPAY_ENTERPRISE_PLAN_ID')
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
    
    def check_usage_limits(self, subscription, action: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user can perform action within subscription limits
        
        Args:
            subscription: User's subscription data
            action: Action to check (campaigns, ai_generations, etc.)
            
        Returns:
            Tuple of (allowed: bool, limit_message: Optional[str])
        """
        """Check if action is allowed within subscription limits"""
        if hasattr(subscription, 'status'):
            # Database model object
            if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]:
                return False, f"Subscription is {subscription.status.value}. Please update billing information."
            
            if action == 'create_campaign':
                if subscription.max_campaigns == -1:  # Unlimited
                    return True, None
                if subscription.campaigns_used >= subscription.max_campaigns:
                    return False, f"Campaign limit reached ({subscription.max_campaigns}). Upgrade to create more campaigns."
            
            elif action == 'ai_generation':
                if subscription.max_ai_generations == -1:  # Unlimited
                    return True, None
                if subscription.ai_generations_used >= subscription.max_ai_generations:
                    return False, f"AI generation limit reached ({subscription.max_ai_generations}). Upgrade for more generations."
            
            elif action == 'api_calls':
                if subscription.max_api_calls == -1:  # Unlimited
                    return True, None
                if subscription.api_calls_used >= subscription.max_api_calls:
                    return False, f"API call limit reached ({subscription.max_api_calls}). Upgrade your plan."
        else:
            # Legacy dictionary format support
            if subscription['status'] not in [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value]:
                return False, f"Subscription is {subscription['status']}. Please update billing information."
            
            limits = subscription['limits']
            usage = subscription['usage_current_period']
            
            if action == 'create_campaign':
                if limits['campaigns'] == -1:  # Unlimited
                    return True, None
                if usage['campaigns_created'] >= limits['campaigns']:
                    return False, f"Campaign limit reached ({limits['campaigns']}). Upgrade to create more campaigns."
            
            elif action == 'ai_generation':
                if limits['ai_generations'] == -1:  # Unlimited
                    return True, None
                if usage['ai_generations_used'] >= limits['ai_generations']:
                    return False, f"AI generation limit reached ({limits['ai_generations']}). Upgrade for more generations."
        
        return True, None
    
    def track_usage(self, subscription: Dict[str, any], action: str, amount: int = 1) -> Dict[str, any]:
        """
        Track usage for current billing period
        
        Args:
            subscription: User's subscription data
            action: Action being tracked
            amount: Amount to add to usage
            
        Returns:
            Updated subscription data
        """
        usage = subscription['usage_current_period']
        
        if action == 'create_campaign':
            usage['campaigns_created'] += amount
        elif action == 'ai_generation':
            usage['ai_generations_used'] += amount
        elif action == 'api_call':
            usage['api_calls_made'] += amount
        
        subscription['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        return subscription
    
    def get_subscription_summary(self, subscription: Dict[str, any]) -> Dict[str, any]:
        """Generate user-friendly subscription summary"""
        tier_name = subscription['tier'].title()
        limits = subscription['limits']
        usage = subscription['usage_current_period']
        
        # Calculate usage percentages
        campaigns_used = usage['campaigns_created']
        campaigns_limit = limits['campaigns']
        campaigns_percentage = (campaigns_used / campaigns_limit * 100) if campaigns_limit != -1 else 0
        
        ai_used = usage['ai_generations_used']
        ai_limit = limits['ai_generations']
        ai_percentage = (ai_used / ai_limit * 100) if ai_limit != -1 else 0
        
        return {
            'tier': tier_name,
            'status': subscription['status'],
            'monthly_price': f"${subscription['monthly_price']}",
            'next_billing_date': subscription['next_billing_date'],
            'usage_summary': {
                'campaigns': {
                    'used': campaigns_used,
                    'limit': campaigns_limit if campaigns_limit != -1 else 'Unlimited',
                    'percentage': campaigns_percentage
                },
                'ai_generations': {
                    'used': ai_used,
                    'limit': ai_limit if ai_limit != -1 else 'Unlimited',
                    'percentage': ai_percentage
                }
            },
            'features': subscription['features'],
            'trial_info': {
                'is_trial': subscription['status'] == SubscriptionStatus.TRIAL.value,
                'trial_end': subscription.get('trial_end'),
                'days_remaining': self._calculate_trial_days_remaining(subscription)
            }
        }
    
    def _calculate_trial_days_remaining(self, subscription: Dict[str, any]) -> Optional[int]:
        """Calculate days remaining in trial period"""
        if subscription['status'] != SubscriptionStatus.TRIAL.value:
            return None
        
        trial_end = datetime.fromisoformat(subscription['trial_end'].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        if trial_end > now:
            return (trial_end - now).days
        else:
            return 0
    
    def upgrade_subscription(self, subscription: Dict[str, any], new_tier: SubscriptionTier) -> Dict[str, any]:
        """
        Upgrade user subscription to higher tier
        
        Args:
            subscription: Current subscription data
            new_tier: Target subscription tier
            
        Returns:
            Updated subscription data
        """
        old_tier = subscription['tier']
        old_price = subscription['monthly_price']
        
        # Update subscription details
        subscription['tier'] = new_tier.value
        subscription['monthly_price'] = self.PRICING[new_tier]['monthly_price']
        subscription['limits'] = {
            'campaigns': self.PRICING[new_tier]['campaigns_limit'],
            'ad_accounts': self.PRICING[new_tier]['ad_accounts_limit'],
            'ai_generations': self.PRICING[new_tier]['ai_generations_limit'],
            'analytics_retention_days': self.PRICING[new_tier]['analytics_retention_days']
        }
        subscription['features'] = self.PRICING[new_tier]['features']
        subscription['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        print(f"✅ Upgraded subscription from {old_tier} to {new_tier.value}")
        print(f"💰 Price change: ${old_price} → ${subscription['monthly_price']}")
        
        return subscription
    
    def get_pricing_comparison(self) -> Dict[str, any]:
        """Get pricing comparison table for frontend display"""
        comparison = {}
        
        # Map tier names to display names
        tier_names = {
            'starter': 'Essential',
            'professional': 'Growth', 
            'enterprise': 'Professional'
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

class UsageTracker:
    """
    Track platform usage for billing and analytics
    Note: Ad spend tracking is for reporting only - users pay Meta directly
    """
    
    def __init__(self):
        self.subscription_manager = PlatformSubscriptionManager()
    
    async def track_campaign_creation(self, user_id: str, campaign_data: Dict[str, any]) -> Dict[str, any]:
        """Track when user creates a new campaign"""
        # This would integrate with your database to get/update subscription
        # For now, using example data
        subscription = self._get_user_subscription(user_id)  # Mock function
        
        # Check if user can create campaign
        allowed, message = self.subscription_manager.check_usage_limits(subscription, 'create_campaign')
        if not allowed:
            return {'success': False, 'error': message}
        
        # Track usage
        updated_subscription = self.subscription_manager.track_usage(subscription, 'create_campaign')
        self._save_user_subscription(user_id, updated_subscription)  # Mock function
        
        return {
            'success': True,
            'message': 'Campaign created successfully',
            'usage_remaining': {
                'campaigns': updated_subscription['limits']['campaigns'] - updated_subscription['usage_current_period']['campaigns_created']
            }
        }
    
    async def track_ai_generation(self, user_id: str, generation_type: str) -> Dict[str, any]:
        """Track AI content generation usage"""
        subscription = self._get_user_subscription(user_id)
        
        allowed, message = self.subscription_manager.check_usage_limits(subscription, 'ai_generation')
        if not allowed:
            return {'success': False, 'error': message}
        
        updated_subscription = self.subscription_manager.track_usage(subscription, 'ai_generation')
        self._save_user_subscription(user_id, updated_subscription)
        
        return {
            'success': True,
            'generation_type': generation_type,
            'usage_remaining': {
                'ai_generations': updated_subscription['limits']['ai_generations'] - updated_subscription['usage_current_period']['ai_generations_used']
            }
        }
    
    def _get_user_subscription(self, user_id: str) -> Dict[str, any]:
        """Mock function - would get from database"""
        # This is example data - replace with actual database call
        return {
            'subscription_id': 'sub_123',
            'user_id': user_id,
            'tier': 'professional',
            'status': 'active',
            'monthly_price': 99.99,
            'limits': {'campaigns': 25, 'ai_generations': 500},
            'usage_current_period': {'campaigns_created': 3, 'ai_generations_used': 45}
        }
    
    def _save_user_subscription(self, user_id: str, subscription: Dict[str, any]):
        """Mock function - would save to database"""
        print(f"💾 Updated subscription usage for user {user_id}")

async def main():
    """Demo subscription management system"""
    print("💳 AI Marketing Platform - Subscription Management")
    print("=" * 55)
    print("Payment Model: Users pay Meta directly for ads")
    print("Platform Revenue: Subscription fees for automation services\n")
    
    manager = PlatformSubscriptionManager()
    
    # Demo: Create subscriptions for different tiers
    print("🎯 Creating demo subscriptions...")
    
    starter_sub = manager.create_subscription("user_123", SubscriptionTier.STARTER)
    print()
    
    pro_sub = manager.create_subscription("user_456", SubscriptionTier.PROFESSIONAL)
    print()
    
    enterprise_sub = manager.create_subscription("user_789", SubscriptionTier.ENTERPRISE)
    print()
    
    # Demo: Check usage limits
    print("📊 Checking usage limits...")
    allowed, message = manager.check_usage_limits(starter_sub, 'create_campaign')
    print(f"Starter user can create campaign: {allowed}")
    
    # Demo: Track usage
    print("\n📈 Tracking usage...")
    updated_sub = manager.track_usage(starter_sub, 'create_campaign', 1)
    updated_sub = manager.track_usage(updated_sub, 'ai_generation', 5)
    
    # Demo: Get subscription summary
    print("\n📋 Subscription Summary:")
    summary = manager.get_subscription_summary(updated_sub)
    print(json.dumps(summary, indent=2))
    
    # Demo: Pricing comparison
    print("\n💰 Pricing Comparison:")
    pricing = manager.get_pricing_comparison()
    for tier, details in pricing.items():
        print(f"\n{details['name']} - {details['price']}")
        print(f"  • {details['campaigns']}")
        print(f"  • {details['ai_generations']}")
        print(f"  • {details['analytics']}")

if __name__ == "__main__":
    asyncio.run(main())