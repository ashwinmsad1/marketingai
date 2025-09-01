"""
AI-Powered Meta Ads Automation Platform
Supports Facebook and Instagram ad campaign automation using Meta Marketing API
"""

from dotenv import load_dotenv
import os
import asyncio
import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import time

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.adcreative import AdCreative
    from facebook_business.adobjects.ad import Ad
    from facebook_business.adobjects.adimage import AdImage
    from facebook_business.adobjects.advideo import AdVideo
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    print("⚠️  Facebook Business SDK not installed. Run: pip install facebook-business")

load_dotenv()

class MetaAdsAutomationEngine:
    """
    Complete AI-powered automation engine for Facebook and Instagram ads
    """
    
    def __init__(self):
        # Meta API Configuration
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET") 
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("META_AD_ACCOUNT_ID")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        # Initialize Facebook Ads API
        if all([self.app_id, self.app_secret, self.access_token]):
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.account = AdAccount(f'act_{self.ad_account_id}')
        else:
            raise ValueError("Missing required Meta API credentials in environment variables")
    
    # CAMPAIGN OBJECTIVES MAPPING
    CAMPAIGN_OBJECTIVES = {
        'brand_awareness': Campaign.Objective.outcome_awareness,
        'traffic': Campaign.Objective.outcome_traffic,
        'engagement': Campaign.Objective.outcome_engagement,
        'leads': Campaign.Objective.outcome_leads,
        'app_promotion': Campaign.Objective.outcome_app_promotion,
        'sales': Campaign.Objective.outcome_sales,
        'conversions': Campaign.Objective.outcome_sales  # Most common for e-commerce
    }
    
    async def create_ai_optimized_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete AI-optimized campaign with automatic cross-platform setup
        
        Args:
            campaign_config (Dict): Campaign configuration including:
                - name: Campaign name
                - objective: Campaign objective (brand_awareness, traffic, conversions, etc.)
                - daily_budget: Daily budget in USD
                - target_audience: Audience targeting parameters
                - creative_assets: List of images/videos
                - platforms: ['facebook', 'instagram'] or both
                - placements: Specific placement targeting
        
        Returns:
            Dict with campaign creation results and IDs
        """
        print(f"🚀 Creating AI-optimized campaign: {campaign_config['name']}")
        
        results = {
            'success': False,
            'campaign_id': None,
            'adset_ids': [],
            'ad_ids': [],
            'creative_ids': [],
            'total_ads_created': 0,
            'platforms': campaign_config.get('platforms', ['facebook', 'instagram']),
            'error': None
        }
        
        try:
            # Step 1: Create Campaign
            campaign = await self._create_campaign(campaign_config)
            results['campaign_id'] = campaign['id']
            print(f"✅ Campaign created: {campaign['id']}")
            
            # Step 2: Create platform-specific ad sets
            platforms = campaign_config.get('platforms', ['facebook', 'instagram'])
            
            for platform in platforms:
                print(f"📱 Setting up {platform.upper()} ad targeting...")
                
                # Create optimized ad set for each platform
                adset_config = self._optimize_adset_for_platform(campaign_config, platform)
                adset = await self._create_adset(campaign['id'], adset_config, platform)
                results['adset_ids'].append(adset['id'])
                print(f"✅ {platform.upper()} ad set created: {adset['id']}")
                
                # Step 3: Create AI-optimized creatives for platform
                creative_assets = campaign_config.get('creative_assets', [])
                for i, asset in enumerate(creative_assets):
                    creative = await self._create_creative(asset, platform, i)
                    if creative:
                        results['creative_ids'].append(creative['id'])
                        
                        # Step 4: Create ad linking creative to ad set
                        ad = await self._create_ad(adset['id'], creative['id'], f"{platform}_ad_{i+1}")
                        if ad:
                            results['ad_ids'].append(ad['id'])
                            results['total_ads_created'] += 1
                            print(f"✅ {platform.upper()} ad created: {ad['id']}")
            
            results['success'] = True
            print(f"🎉 Campaign setup complete! Created {results['total_ads_created']} ads across {len(platforms)} platforms")
            
            return results
            
        except Exception as e:
            print(f"❌ Campaign creation failed: {str(e)}")
            results['error'] = str(e)
            return results
    
    async def _create_campaign(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Create Meta advertising campaign"""
        objective = self.CAMPAIGN_OBJECTIVES.get(config['objective'], Campaign.Objective.outcome_sales)
        
        campaign = self.account.create_campaign(
            fields=[],
            params={
                Campaign.Field.name: config['name'],
                Campaign.Field.objective: objective,
                Campaign.Field.status: Campaign.Status.paused,  # Start paused for safety
                Campaign.Field.buying_type: Campaign.BuyingType.auction,
            }
        )
        return campaign
    
    async def _create_adset(self, campaign_id: str, config: Dict[str, Any], platform: str) -> Dict[str, str]:
        """Create optimized ad set for specific platform"""
        
        # Platform-specific targeting and placements
        targeting = config['targeting'].copy()
        targeting['publisher_platforms'] = [platform]
        
        # Set platform-specific placements
        if platform == 'facebook':
            targeting['facebook_positions'] = config.get('facebook_placements', ['feed', 'right_hand_column'])
        elif platform == 'instagram':
            targeting['instagram_positions'] = config.get('instagram_placements', ['stream', 'story', 'explore'])
        
        adset = self.account.create_ad_set(
            fields=[],
            params={
                AdSet.Field.name: f"{config['name']} - {platform.upper()}",
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.daily_budget: int(config['daily_budget'] * 100),  # Convert to cents
                AdSet.Field.targeting: targeting,
                AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
                AdSet.Field.optimization_goal: config.get('optimization_goal', AdSet.OptimizationGoal.link_clicks),
                AdSet.Field.status: AdSet.Status.active,
            }
        )
        return adset
    
    async def _create_creative(self, asset_config: Dict[str, Any], platform: str, index: int) -> Optional[Dict[str, str]]:
        """Create platform-optimized ad creative"""
        try:
            creative_spec = {
                'name': f"Creative_{platform}_{index+1}",
                'object_story_spec': {
                    'page_id': self.page_id,
                }
            }
            
            # Handle different asset types
            if asset_config['type'] == 'image':
                # Upload image first
                image = AdImage(parent_id=self.account.get_id())
                image[AdImage.Field.filename] = asset_config['path']
                image.remote_create()
                
                creative_spec['object_story_spec']['link_data'] = {
                    'image_hash': image[AdImage.Field.hash],
                    'link': asset_config.get('link', 'https://example.com'),
                    'message': self._optimize_copy_for_platform(asset_config.get('message', ''), platform),
                    'call_to_action': {
                        'type': asset_config.get('cta_type', 'LEARN_MORE'),
                        'value': {'link': asset_config.get('link', 'https://example.com')}
                    }
                }
                
            elif asset_config['type'] == 'video':
                # Upload video first
                video = AdVideo(parent_id=self.account.get_id())
                video[AdVideo.Field.filename] = asset_config['path']
                video.remote_create()
                
                creative_spec['object_story_spec']['video_data'] = {
                    'video_id': video['id'],
                    'message': self._optimize_copy_for_platform(asset_config.get('message', ''), platform),
                    'call_to_action': {
                        'type': asset_config.get('cta_type', 'LEARN_MORE'),
                        'value': {'link': asset_config.get('link', 'https://example.com')}
                    }
                }
            
            creative = self.account.create_ad_creative(
                fields=[],
                params=creative_spec
            )
            
            return creative
            
        except Exception as e:
            print(f"❌ Creative creation failed: {str(e)}")
            return None
    
    async def _create_ad(self, adset_id: str, creative_id: str, ad_name: str) -> Optional[Dict[str, str]]:
        """Create individual ad"""
        try:
            ad = self.account.create_ad(
                fields=[],
                params={
                    Ad.Field.name: ad_name,
                    Ad.Field.adset_id: adset_id,
                    Ad.Field.creative: {'creative_id': creative_id},
                    Ad.Field.status: Ad.Status.active,
                }
            )
            return ad
            
        except Exception as e:
            print(f"❌ Ad creation failed: {str(e)}")
            return None
    
    def _optimize_adset_for_platform(self, config: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """AI optimization for platform-specific ad set configuration"""
        base_targeting = config['target_audience'].copy()
        
        # Platform-specific optimizations
        if platform == 'instagram':
            # Instagram users tend to be younger
            if 'age_max' in base_targeting:
                base_targeting['age_max'] = min(base_targeting.get('age_max', 65), 45)
            
            # Instagram-specific interests
            if 'interests' in base_targeting:
                base_targeting['interests'].extend([
                    {'id': '6003277229526', 'name': 'Photography'},  # Popular on Instagram
                    {'id': '6003348604581', 'name': 'Fashion'}       # Visual platform interests
                ])
        
        elif platform == 'facebook':
            # Facebook has broader age demographics
            base_targeting['age_min'] = base_targeting.get('age_min', 25)
            base_targeting['age_max'] = base_targeting.get('age_max', 65)
        
        return {
            'name': f"{config['name']} - {platform.upper()}",
            'daily_budget': config['daily_budget'] / len(config.get('platforms', [platform])),  # Split budget
            'targeting': base_targeting,
            'optimization_goal': config.get('optimization_goal', AdSet.OptimizationGoal.link_clicks),
            'facebook_placements': config.get('facebook_placements', ['feed', 'right_hand_column']),
            'instagram_placements': config.get('instagram_placements', ['stream', 'story'])
        }
    
    def _optimize_copy_for_platform(self, message: str, platform: str) -> str:
        """AI-powered copy optimization for each platform"""
        if platform == 'instagram':
            # Instagram users respond to more visual, emoji-rich content
            if not any(emoji in message for emoji in ['🔥', '✨', '💫', '🌟']):
                message = f"✨ {message}"
            
            # Add relevant hashtags if not present
            if '#' not in message:
                message += " #innovation #inspiration"
                
        elif platform == 'facebook':
            # Facebook users prefer more detailed, informative content
            if len(message) < 50:
                message += " Learn more about how this can benefit you!"
        
        return message
    
    async def get_campaign_insights(self, campaign_id: str, days: int = 7) -> Dict[str, Any]:
        """Get detailed campaign performance analytics"""
        try:
            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(
                fields=[
                    'impressions',
                    'clicks', 
                    'spend',
                    'cpm',
                    'ctr',
                    'cpc',
                    'conversions',
                    'cost_per_conversion',
                    'reach',
                    'frequency'
                ],
                params={
                    'breakdowns': ['publisher_platform', 'placement'],
                    'date_preset': f'last_{days}_days'
                }
            )
            
            return {
                'campaign_id': campaign_id,
                'insights': [dict(insight) for insight in insights],
                'summary': self._calculate_performance_summary(insights)
            }
            
        except Exception as e:
            print(f"❌ Failed to get insights: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_performance_summary(self, insights) -> Dict[str, float]:
        """Calculate performance summary across all platforms"""
        total_spend = sum(float(insight.get('spend', 0)) for insight in insights)
        total_impressions = sum(int(insight.get('impressions', 0)) for insight in insights)
        total_clicks = sum(int(insight.get('clicks', 0)) for insight in insights)
        total_conversions = sum(int(insight.get('conversions', 0)) for insight in insights)
        
        return {
            'total_spend': total_spend,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'overall_ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            'overall_cpc': (total_spend / total_clicks) if total_clicks > 0 else 0,
            'overall_roas': (total_conversions / total_spend) if total_spend > 0 else 0
        }
    
    async def ai_campaign_optimizer(self, campaign_id: str) -> Dict[str, Any]:
        """AI-powered campaign optimization based on performance data"""
        print(f"🤖 Running AI optimization for campaign {campaign_id}")
        
        # Get current performance
        insights = await self.get_campaign_insights(campaign_id, days=3)
        if 'error' in insights:
            return {'success': False, 'error': insights['error']}
        
        optimizations = []
        
        # Analyze performance by platform
        for insight in insights['insights']:
            platform = insight.get('publisher_platform')
            ctr = float(insight.get('ctr', 0))
            cpc = float(insight.get('cpc', 0))
            
            # AI Decision Making
            if ctr < 1.0:  # Low CTR
                optimizations.append({
                    'type': 'creative_refresh',
                    'platform': platform,
                    'reason': f'Low CTR ({ctr:.2f}%) - recommend new creatives'
                })
            
            if cpc > 2.0:  # High CPC
                optimizations.append({
                    'type': 'audience_expansion',
                    'platform': platform,
                    'reason': f'High CPC (${cpc:.2f}) - expand targeting'
                })
        
        # Execute optimizations
        for optimization in optimizations:
            await self._execute_optimization(campaign_id, optimization)
        
        return {
            'success': True,
            'optimizations_applied': len(optimizations),
            'details': optimizations
        }
    
    async def _execute_optimization(self, campaign_id: str, optimization: Dict[str, Any]):
        """Execute specific optimization action"""
        print(f"⚡ Applying {optimization['type']} for {optimization['platform']}: {optimization['reason']}")
        
        # Implementation would depend on optimization type
        # This is a placeholder for the actual optimization logic
        if optimization['type'] == 'creative_refresh':
            # Logic to create new creatives
            pass
        elif optimization['type'] == 'audience_expansion':
            # Logic to expand audience targeting
            pass

# Wrapper functions for easy campaign creation
async def create_awareness_campaign(name: str, daily_budget: float, target_audience: Dict[str, Any], creative_assets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create brand awareness campaign across Facebook and Instagram"""
    engine = MetaAdsAutomationEngine()
    
    config = {
        'name': name,
        'objective': 'brand_awareness',
        'daily_budget': daily_budget,
        'target_audience': target_audience,
        'creative_assets': creative_assets,
        'platforms': ['facebook', 'instagram']
    }
    
    return await engine.create_ai_optimized_campaign(config)

async def create_conversion_campaign(name: str, daily_budget: float, target_audience: Dict[str, Any], creative_assets: List[Dict[str, Any]], landing_url: str) -> Dict[str, Any]:
    """Create conversion-focused campaign with AI optimization"""
    engine = MetaAdsAutomationEngine()
    
    # Add landing URL to all creative assets
    for asset in creative_assets:
        asset['link'] = landing_url
        asset['cta_type'] = 'SHOP_NOW'
    
    config = {
        'name': name,
        'objective': 'conversions',
        'daily_budget': daily_budget,
        'target_audience': target_audience,
        'creative_assets': creative_assets,
        'platforms': ['facebook', 'instagram'],
        'optimization_goal': AdSet.OptimizationGoal.conversions
    }
    
    return await engine.create_ai_optimized_campaign(config)

async def main():
    print("🤖 Meta Ads AI Automation Platform")
    print("=" * 40)
    print("1. Create awareness campaign")
    print("2. Create conversion campaign")
    print("3. Get campaign insights")
    print("4. Run AI campaign optimizer") 
    print("5. Demo: Complete campaign setup")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        # Sample awareness campaign
        target_audience = {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 55,
            'interests': [
                {'id': '6003139266461', 'name': 'Online shopping'},
                {'id': '6004037027412', 'name': 'Technology'}
            ]
        }
        
        creative_assets = [
            {
                'type': 'image',
                'path': '/path/to/your/image.jpg',
                'message': 'Discover amazing products that change your life!',
                'cta_type': 'LEARN_MORE'
            }
        ]
        
        result = await create_awareness_campaign(
            name="AI Brand Awareness Campaign",
            daily_budget=50.0,
            target_audience=target_audience,
            creative_assets=creative_assets
        )
        
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "2":
        # Sample conversion campaign
        target_audience = {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 45,
            'interests': [
                {'id': '6003139266461', 'name': 'Online shopping'}
            ]
        }
        
        creative_assets = [
            {
                'type': 'image',
                'path': '/path/to/your/product.jpg',
                'message': 'Get 50% off your first order! Limited time offer.',
                'cta_type': 'SHOP_NOW'
            }
        ]
        
        result = await create_conversion_campaign(
            name="AI Conversion Campaign",
            daily_budget=100.0,
            target_audience=target_audience,
            creative_assets=creative_assets,
            landing_url="https://yourstore.com/sale"
        )
        
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "3":
        campaign_id = input("Enter campaign ID: ").strip()
        engine = MetaAdsAutomationEngine()
        insights = await engine.get_campaign_insights(campaign_id)
        print(f"\n📊 Campaign Insights: {json.dumps(insights, indent=2)}")
    
    elif choice == "4":
        campaign_id = input("Enter campaign ID to optimize: ").strip()
        engine = MetaAdsAutomationEngine()
        result = await engine.ai_campaign_optimizer(campaign_id)
        print(f"\n🤖 Optimization Result: {json.dumps(result, indent=2)}")
    
    elif choice == "5":
        print("🚀 Running complete demo campaign setup...")
        
        # Demo configuration
        demo_config = {
            'name': 'AI Demo Campaign - Cross Platform',
            'objective': 'traffic',
            'daily_budget': 25.0,
            'target_audience': {
                'geo_locations': {'countries': ['US']},
                'age_min': 25,
                'age_max': 55
            },
            'creative_assets': [
                {
                    'type': 'image',
                    'path': '/path/to/demo/image.jpg',  # Replace with actual path
                    'message': 'Discover the future of AI automation!',
                    'link': 'https://example.com',
                    'cta_type': 'LEARN_MORE'
                }
            ],
            'platforms': ['facebook', 'instagram']
        }
        
        engine = MetaAdsAutomationEngine()
        result = await engine.create_ai_optimized_campaign(demo_config)
        
        print(f"\n🎉 Demo Campaign Results:")
        print(f"✅ Success: {result['success']}")
        if result['success']:
            print(f"📝 Campaign ID: {result['campaign_id']}")
            print(f"📱 Platforms: {', '.join(result['platforms'])}")
            print(f"🎯 Total Ads Created: {result['total_ads_created']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())