"""
Subscription Management System for AI Marketing Automation Platform
Direct Payment Model - Users pay Meta directly for ads, platform charges for automation service
"""

from dotenv import load_dotenv
import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Tuple
from enum import Enum
import uuid

load_dotenv()

class SubscriptionTier(Enum):
    """Platform subscription tiers"""
    STARTER = "starter"
    PROFESSIONAL = "professional" 
    ENTERPRISE = "enterprise"

class SubscriptionStatus(Enum):
    """Subscription status options"""
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"

class PlatformSubscriptionManager:
    """
    Manages platform subscriptions for users who pay Meta directly for ads
    Platform charges only for automation services and features
    """
    
    # Subscription Pricing (Monthly USD)
    PRICING = {
        SubscriptionTier.STARTER: {
            'monthly_price': 29.99,
            'campaigns_limit': 5,
            'ad_accounts_limit': 1,
            'ai_generations_limit': 100,
            'analytics_retention_days': 30,
            'features': [
                'Basic AI content generation',
                'Campaign automation',
                'Performance analytics',
                'Email support'
            ]
        },
        SubscriptionTier.PROFESSIONAL: {
            'monthly_price': 99.99,
            'campaigns_limit': 25,
            'ad_accounts_limit': 3,
            'ai_generations_limit': 500,
            'analytics_retention_days': 90,
            'features': [
                'Advanced AI content generation',
                'Multi-platform automation',
                'Advanced analytics & reporting',
                'A/B testing tools',
                'Priority support',
                'Custom audiences'
            ]
        },
        SubscriptionTier.ENTERPRISE: {
            'monthly_price': 299.99,
            'campaigns_limit': -1,  # Unlimited
            'ad_accounts_limit': -1,  # Unlimited
            'ai_generations_limit': -1,  # Unlimited
            'analytics_retention_days': 365,
            'features': [
                'Unlimited AI content generation',
                'White-label platform access',
                'Advanced automation rules',
                'Custom integrations',
                'Dedicated account manager',
                'API access',
                'Team collaboration tools'
            ]
        }
    }
    
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
    def create_subscription(self, user_id: str, tier: SubscriptionTier, trial_days: int = 14) -> Dict[str, any]:
        """
        Create new platform subscription for user
        
        Args:
            user_id: Unique user identifier
            tier: Subscription tier
            trial_days: Free trial duration
            
        Returns:
            Dict with subscription details
        """
        subscription_id = str(uuid.uuid4())
        trial_end = datetime.now(timezone.utc) + timedelta(days=trial_days)
        
        subscription = {
            'subscription_id': subscription_id,
            'user_id': user_id,
            'tier': tier.value,
            'status': SubscriptionStatus.TRIAL.value,
            'trial_start': datetime.now(timezone.utc).isoformat(),
            'trial_end': trial_end.isoformat(),
            'billing_cycle_start': trial_end.isoformat(),
            'next_billing_date': trial_end.isoformat(),
            'monthly_price': self.PRICING[tier]['monthly_price'],
            'limits': {
                'campaigns': self.PRICING[tier]['campaigns_limit'],
                'ad_accounts': self.PRICING[tier]['ad_accounts_limit'],
                'ai_generations': self.PRICING[tier]['ai_generations_limit'],
                'analytics_retention_days': self.PRICING[tier]['analytics_retention_days']
            },
            'features': self.PRICING[tier]['features'],
            'usage_current_period': {
                'campaigns_created': 0,
                'ai_generations_used': 0,
                'api_calls_made': 0
            },
            'meta_ad_spend': 0,  # User pays Meta directly - this is for reporting only
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        print(f"✅ Created {tier.value} subscription for user {user_id}")
        print(f"🎁 Trial period: {trial_days} days (until {trial_end.strftime('%Y-%m-%d')})")
        print(f"💰 Monthly price after trial: ${self.PRICING[tier]['monthly_price']}")
        
        return subscription
    
    def check_usage_limits(self, subscription: Dict[str, any], action: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user can perform action within subscription limits
        
        Args:
            subscription: User's subscription data
            action: Action to check (campaigns, ai_generations, etc.)
            
        Returns:
            Tuple of (allowed: bool, limit_message: Optional[str])
        """
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
        
        elif action == 'connect_ad_account':
            if limits['ad_accounts'] == -1:  # Unlimited
                return True, None
            # This would need to check actual connected accounts count
            # For now, assume it's within limits
            return True, None
        
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
        
        for tier, details in self.PRICING.items():
            comparison[tier.value] = {
                'name': tier.value.title(),
                'price': f"${details['monthly_price']}/month",
                'campaigns': 'Unlimited' if details['campaigns_limit'] == -1 else f"{details['campaigns_limit']} campaigns",
                'ai_generations': 'Unlimited' if details['ai_generations_limit'] == -1 else f"{details['ai_generations_limit']}/month",
                'ad_accounts': 'Unlimited' if details['ad_accounts_limit'] == -1 else f"{details['ad_accounts_limit']} accounts",
                'analytics': f"{details['analytics_retention_days']} days retention",
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