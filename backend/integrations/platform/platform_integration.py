"""
Platform Integration Layer - Direct Payment Model
Integrates AI content generation + Meta ads automation with subscription management
Users pay Meta directly for ads, platform charges for automation services
"""

import asyncio
import json
from typing import Dict, Optional, List, Any
from datetime import datetime

# Import our modules
from backend.utils.subscription_management import PlatformSubscriptionManager, SubscriptionTier, UsageTracker
from backend.integrations.meta.meta_ads_automation import MetaAdsAutomationEngine
from backend.agents.photo_agent import poster_editor, image_creator
from backend.agents.video_agent import video_from_prompt, video_from_image
from backend.agents.facebook_agent import post_content_everywhere

class AIMarketingPlatform:
    """
    Complete AI Marketing Automation Platform
    Direct Payment Model - Users manage their own Meta ad spend
    Platform provides AI content creation + campaign automation services
    """
    
    def __init__(self):
        self.subscription_manager = PlatformSubscriptionManager()
        self.usage_tracker = UsageTracker()
        self.meta_engine = None  # Initialize when user connects Meta account
    
    async def onboard_new_user(self, user_email: str, tier: SubscriptionTier = SubscriptionTier.STARTER) -> Dict[str, Any]:
        """
        Complete user onboarding flow
        
        Args:
            user_email: User's email address
            tier: Initial subscription tier
            
        Returns:
            Onboarding result with subscription and next steps
        """
        print(f"🚀 Starting onboarding for {user_email}")
        
        # Step 1: Create platform subscription (14-day free trial)
        user_id = f"user_{hash(user_email) % 100000}"
        subscription = self.subscription_manager.create_subscription(user_id, tier, trial_days=14)
        
        # Step 2: Provide Meta OAuth setup instructions
        onboarding_result = {
            'user_id': user_id,
            'subscription': subscription,
            'next_steps': [
                {
                    'step': 1,
                    'title': 'Connect Your Meta Advertising Account',
                    'description': 'Link your Facebook Ad Account and Pages to start automating campaigns',
                    'action': 'Run: python meta_auth_setup.py',
                    'required': True
                },
                {
                    'step': 2,
                    'title': 'Create Your First AI Campaign',
                    'description': 'Generate AI content and launch automated ad campaigns',
                    'action': 'Use platform dashboard or API',
                    'required': False
                },
                {
                    'step': 3,
                    'title': 'Set Up Budget Alerts',
                    'description': 'Configure notifications for your Meta ad spend (paid directly to Meta)',
                    'action': 'Configure in Meta Ads Manager',
                    'required': False
                }
            ],
            'trial_info': {
                'duration': '14 days free trial',
                'included': [
                    f"Up to {subscription['limits']['campaigns']} automated campaigns",
                    f"Up to {subscription['limits']['ai_generations']} AI content generations",
                    "Full platform access during trial"
                ],
                'billing_note': 'You pay Meta directly for ad spend. Platform only charges for automation services.'
            }
        }
        
        print(f"✅ User onboarded successfully!")
        print(f"🎁 Trial: 14 days free ({subscription['limits']['ai_generations']} AI generations included)")
        print(f"💳 Billing: ₹{subscription['monthly_price']}/month after trial for platform services")
        
        return onboarding_result
    
    async def create_ai_campaign_with_limits(self, user_id: str, campaign_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create AI-powered campaign with subscription limit checking
        
        Args:
            user_id: User identifier
            campaign_request: Campaign configuration
            
        Returns:
            Campaign creation result
        """
        print(f"🤖 Creating AI campaign for user {user_id}")
        
        # Step 1: Check subscription limits
        usage_check = await self.usage_tracker.track_campaign_creation(user_id, campaign_request)
        if not usage_check['success']:
            return {
                'success': False,
                'error': usage_check['error'],
                'upgrade_suggestion': self._get_upgrade_suggestion(user_id)
            }
        
        try:
            # Step 2: Generate AI content based on request
            content_results = await self._generate_campaign_content(user_id, campaign_request)
            if not content_results['success']:
                return content_results
            
            # Step 3: Create Meta ad campaign (user's ad account, their money)
            meta_result = await self._create_meta_campaign(user_id, campaign_request, content_results['assets'])
            
            # Step 4: Track platform usage for billing
            await self._track_campaign_usage(user_id, campaign_request, content_results, meta_result)
            
            return {
                'success': True,
                'campaign_id': meta_result.get('campaign_id'),
                'content_generated': content_results['assets'],
                'meta_campaign': meta_result,
                'billing_note': f"Campaign created using your Meta ad account. Ad spend billed directly by Meta.",
                'platform_usage': usage_check.get('usage_remaining', {})
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Campaign creation failed: {str(e)}",
                'support_message': "Contact support if this issue persists."
            }
    
    async def _generate_campaign_content(self, user_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI content for campaign"""
        print("🎨 Generating AI content...")
        
        assets = []
        content_type = request.get('content_type', 'image')
        
        try:
            # Check AI generation limits
            ai_check = await self.usage_tracker.track_ai_generation(user_id, content_type)
            if not ai_check['success']:
                return {'success': False, 'error': ai_check['error']}
            
            if content_type == 'image':
                # Generate image using our AI agent
                image_file = await image_creator(
                    request['prompt'], 
                    request.get('style', 'hyperrealistic poster')
                )
                
                if image_file:
                    assets.append({
                        'type': 'image',
                        'path': image_file,
                        'prompt': request['prompt'],
                        'style': request.get('style', 'hyperrealistic poster')
                    })
            
            elif content_type == 'video':
                # Generate video using our AI agent
                video_file = await video_from_prompt(
                    request['prompt'],
                    request.get('style', 'cinematic'),
                    request.get('aspect_ratio', '16:9')
                )
                
                if video_file:
                    assets.append({
                        'type': 'video',
                        'path': video_file,
                        'prompt': request['prompt'],
                        'style': request.get('style', 'cinematic')
                    })
            
            if not assets:
                return {'success': False, 'error': 'Failed to generate AI content'}
            
            print(f"✅ Generated {len(assets)} AI asset(s)")
            return {'success': True, 'assets': assets}
            
        except Exception as e:
            return {'success': False, 'error': f'Content generation failed: {str(e)}'}
    
    async def _create_meta_campaign(self, user_id: str, request: Dict[str, Any], assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create Meta ad campaign using user's connected account"""
        print("📱 Creating Meta ad campaign...")
        
        try:
            # Initialize Meta engine with user's credentials
            # In production, this would load user's stored Meta tokens
            if not self.meta_engine:
                self.meta_engine = MetaAdsAutomationEngine()
            
            # Prepare campaign configuration
            campaign_config = {
                'name': request.get('campaign_name', f"AI Campaign - {datetime.now().strftime('%Y-%m-%d')}"),
                'objective': request.get('objective', 'traffic'),
                'daily_budget': request.get('daily_budget', 25.0),  # User's money, their choice
                'target_audience': request.get('target_audience', {
                    'geo_locations': {'countries': ['US']},
                    'age_min': 25,
                    'age_max': 55
                }),
                'creative_assets': [
                    {
                        'type': asset['type'],
                        'path': asset['path'],
                        'message': request.get('ad_copy', 'Discover amazing products!'),
                        'link': request.get('landing_url', 'https://example.com'),
                        'cta_type': request.get('cta_type', 'LEARN_MORE')
                    }
                    for asset in assets
                ],
                'platforms': request.get('platforms', ['facebook', 'instagram'])
            }
            
            # Create campaign via Meta API (user's ad account)
            result = await self.meta_engine.create_ai_optimized_campaign(campaign_config)
            
            if result['success']:
                print(f"✅ Meta campaign created: {result['campaign_id']}")
                print(f"💰 Ad spend will be charged to user's Meta ad account")
                
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Meta campaign creation failed: {str(e)}'}
    
    async def _track_campaign_usage(self, user_id: str, request: Dict[str, Any], content_results: Dict[str, Any], meta_result: Dict[str, Any]):
        """Track platform usage for billing purposes"""
        # Track AI generations used
        ai_generations = len(content_results.get('assets', []))
        if ai_generations > 0:
            await self.usage_tracker.track_ai_generation(user_id, f"campaign_content_{ai_generations}")
        
        # Log campaign creation (already tracked in create_ai_campaign_with_limits)
        print(f"📊 Tracked usage: {ai_generations} AI generations for user {user_id}")
    
    def _get_upgrade_suggestion(self, user_id: str) -> Dict[str, Any]:
        """Suggest subscription upgrade when limits are reached"""
        return {
            'message': 'Upgrade your subscription to create more campaigns and generate more AI content',
            'recommended_tier': 'professional',
            'benefits': [
                '25 campaigns per month (vs 5 current)',
                '500 AI generations per month (vs 100 current)',
                'Advanced analytics and A/B testing',
                'Priority support'
            ],
            'pricing': '₹5,000/month',
            'note': 'You still pay Meta directly for ad spend - this covers platform automation services only'
        }
    
    async def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user"""
        # In production, this would query your database
        subscription = self.usage_tracker._get_user_subscription(user_id)  # Mock data
        summary = self.subscription_manager.get_subscription_summary(subscription)
        
        # Get Meta campaign performance (if available)
        campaign_performance = await self._get_user_campaign_performance(user_id)
        
        return {
            'subscription_info': summary,
            'campaign_performance': campaign_performance,
            'quick_actions': [
                {'title': 'Create AI Campaign', 'action': 'create_campaign', 'enabled': True},
                {'title': 'Generate AI Content', 'action': 'generate_content', 'enabled': True},
                {'title': 'View Analytics', 'action': 'view_analytics', 'enabled': True},
                {'title': 'Upgrade Plan', 'action': 'upgrade', 'enabled': summary['status'] == 'active'}
            ],
            'billing_model': {
                'platform_charges': f"${summary['monthly_price']}/month for automation services",
                'ad_spend': 'Paid directly to Meta from your connected ad account',
                'next_billing': summary['next_billing_date']
            }
        }
    
    async def _get_user_campaign_performance(self, user_id: str) -> Dict[str, Any]:
        """Get user's campaign performance from Meta"""
        # Mock data - in production, would fetch from Meta Insights API
        return {
            'total_campaigns': 3,
            'active_campaigns': 2,
            'total_ad_spend_this_month': '₹10,350',  # From user's Meta account
            'total_clicks': 1247,
            'total_conversions': 23,
            'average_cpc': '₹20',
            'note': 'Ad spend data from your Meta ad account - not charged by platform'
        }

# Wrapper functions for easy API integration
async def create_user_campaign(user_id: str, campaign_request: Dict[str, Any]) -> Dict[str, Any]:
    """Create campaign with automatic limit checking and billing"""
    platform = AIMarketingPlatform()
    return await platform.create_ai_campaign_with_limits(user_id, campaign_request)

async def onboard_user(email: str, tier: str = "starter") -> Dict[str, Any]:
    """Onboard new user with subscription setup"""
    platform = AIMarketingPlatform()
    tier_enum = SubscriptionTier(tier.lower())
    return await platform.onboard_new_user(email, tier_enum)

async def get_dashboard(user_id: str) -> Dict[str, Any]:
    """Get user dashboard data"""
    platform = AIMarketingPlatform()
    return await platform.get_user_dashboard_data(user_id)

async def main():
    """Demo the complete platform integration"""
    print("🚀 AI Marketing Platform - Direct Payment Model Demo")
    print("=" * 60)
    
    platform = AIMarketingPlatform()
    
    # Demo 1: User onboarding
    print("👤 Demo: User Onboarding")
    onboarding_result = await platform.onboard_new_user("demo@example.com", SubscriptionTier.PROFESSIONAL)
    user_id = onboarding_result['user_id']
    print(f"✅ User ID: {user_id}")
    print()
    
    # Demo 2: Create AI campaign
    print("🤖 Demo: AI Campaign Creation")
    campaign_request = {
        'campaign_name': 'AI Demo Campaign',
        'content_type': 'image',
        'prompt': 'Professional business team celebrating success in modern office',
        'ad_copy': 'Boost your business with AI-powered solutions! 🚀',
        'objective': 'traffic',
        'daily_budget': 50.0,
        'landing_url': 'https://demo-business.com',
        'platforms': ['facebook', 'instagram']
    }
    
    campaign_result = await platform.create_ai_campaign_with_limits(user_id, campaign_request)
    print(f"Campaign Success: {campaign_result['success']}")
    if campaign_result['success']:
        print(f"Campaign ID: {campaign_result.get('campaign_id', 'N/A (demo mode)')}")
        print(f"Content Generated: {len(campaign_result.get('content_generated', []))} assets")
    print()
    
    # Demo 3: User dashboard
    print("📊 Demo: User Dashboard")
    dashboard = await platform.get_user_dashboard_data(user_id)
    print(f"Subscription Tier: {dashboard['subscription_info']['tier']}")
    print(f"Platform Billing: {dashboard['billing_model']['platform_charges']}")
    print(f"Ad Spend: {dashboard['billing_model']['ad_spend']}")
    print(f"Active Campaigns: {dashboard['campaign_performance']['active_campaigns']}")
    
    print("\n💡 Key Benefits of Direct Payment Model:")
    print("✅ Users maintain full control of their Meta ad accounts")
    print("✅ Platform has predictable subscription revenue")
    print("✅ No financial risk from user ad spend")
    print("✅ Simpler compliance and faster Meta App Review")
    print("✅ Users see transparent separation of costs")

if __name__ == "__main__":
    asyncio.run(main())