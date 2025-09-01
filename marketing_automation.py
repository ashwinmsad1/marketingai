import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import uuid

# Import our AI agents
from photo_agent import poster_editor, image_creator
from video_agent import video_from_prompt, video_from_image
from facebook_agent import post_content_everywhere, FacebookMarketingAgent

# Import new enhanced systems
from revenue_tracking import RevenueAttributionEngine, track_campaign_success
from performance_guarantees import PerformanceGuaranteeEngine, monitor_campaign
from industry_templates import IndustryTemplateEngine, create_custom_campaign
from competitor_analyzer import CompetitorAnalysisEngine, create_better_campaign
from viral_engine import ViralContentEngine, create_viral_campaign

class EnhancedMarketingAutomationEngine:
    """
    Complete AI-powered marketing automation engine with performance guarantees,
    ROI tracking, competitive intelligence, and viral content creation
    """
    
    def __init__(self):
        self.facebook_agent = FacebookMarketingAgent()
        
        # Initialize enhanced systems
        self.revenue_engine = RevenueAttributionEngine()
        self.performance_engine = PerformanceGuaranteeEngine()
        self.template_engine = IndustryTemplateEngine()
        self.competitor_engine = CompetitorAnalysisEngine()
        self.viral_engine = ViralContentEngine()
        
        # Success tracking
        self.campaign_counter = 0
    
    async def create_and_post_image_campaign(self, prompt: str, caption: str = "", style: str = "hyperrealistic poster", 
                                           user_id: str = "default_user", industry: str = "general", 
                                           track_performance: bool = True) -> Dict[str, Any]:
        """
        Create image content and post to all social media platforms with enhanced tracking
        
        Args:
            prompt (str): Description for image creation
            caption (str): Caption for social media posts
            style (str): Style for image generation
            user_id (str): User identifier for tracking
            industry (str): Industry for performance benchmarking
            track_performance (bool): Enable performance tracking and guarantees
            
        Returns:
            Dict with creation, posting, and tracking results
        """
        print(f"🚀 Starting enhanced image campaign: {prompt[:50]}...")
        
        # Generate campaign ID
        campaign_id = f"img_camp_{user_id}_{int(datetime.now().timestamp())}"
        
        results = {
            'campaign_id': campaign_id,
            'content_creation': None,
            'social_posting': None,
            'revenue_tracking': None,
            'performance_monitoring': None,
            'success': False,
            'created_file': None,
            'campaign_type': 'image',
            'tracking_enabled': track_performance
        }
        
        try:
            # Step 1: Create image content
            print("🎨 Creating AI-optimized image content...")
            image_file = await image_creator(prompt, style)
            
            if not image_file:
                results['content_creation'] = {'success': False, 'error': 'Failed to create image'}
                return results
            
            results['content_creation'] = {'success': True, 'file': image_file}
            results['created_file'] = image_file
            print(f"✅ Image created: {image_file}")
            
            # Step 2: Setup revenue tracking if enabled
            if track_performance:
                print("💰 Setting up revenue tracking...")
                tracking_success = await self.revenue_engine.track_campaign_launch(
                    campaign_id, user_id, f"Image Campaign: {prompt[:30]}", image_file, "facebook"
                )
                results['revenue_tracking'] = {'enabled': tracking_success}
            
            # Step 3: Post to social media
            print("📱 Posting to social media platforms...")
            social_results = await post_content_everywhere(image_file, caption)
            results['social_posting'] = social_results
            
            # Step 4: Initialize performance monitoring
            if track_performance and social_results['success_count'] > 0:
                print("📊 Initializing performance monitoring...")
                try:
                    performance_metrics = await self.performance_engine.monitor_campaign_performance(
                        campaign_id, user_id, industry
                    )
                    results['performance_monitoring'] = {
                        'status': performance_metrics.performance_status.value,
                        'guarantee_met': performance_metrics.guarantee_threshold_met,
                        'needs_optimization': performance_metrics.needs_optimization
                    }
                except Exception as e:
                    results['performance_monitoring'] = {'error': str(e)}
            
            if social_results['success_count'] > 0:
                results['success'] = True
                print(f"🎉 Enhanced campaign completed! Posted to {social_results['success_count']} platforms")
                if track_performance:
                    print(f"📈 Performance tracking active for campaign {campaign_id}")
            else:
                print("❌ Failed to post to any platforms")
            
            return results
            
        except Exception as e:
            print(f"❌ Campaign error: {str(e)}")
            results['error'] = str(e)
            return results
    
    async def create_and_post_video_campaign(self, prompt: str, caption: str = "", style: str = "cinematic", aspect_ratio: str = "16:9") -> Dict[str, Any]:
        """
        Create video content and post to all social media platforms
        
        Args:
            prompt (str): Description for video creation
            caption (str): Caption for social media posts
            style (str): Style for video generation
            aspect_ratio (str): Video aspect ratio
            
        Returns:
            Dict with creation and posting results
        """
        print(f"🚀 Starting video campaign: {prompt[:50]}...")
        
        results = {
            'content_creation': None,
            'social_posting': None,
            'success': False,
            'created_file': None,
            'campaign_type': 'video'
        }
        
        try:
            # Step 1: Create video content
            print("🎬 Creating video content...")
            video_file = await video_from_prompt(prompt, style, aspect_ratio)
            
            if not video_file:
                results['content_creation'] = {'success': False, 'error': 'Failed to create video'}
                return results
            
            results['content_creation'] = {'success': True, 'file': video_file}
            results['created_file'] = video_file
            print(f"✅ Video created: {video_file}")
            
            # Step 2: Post to social media
            print("📱 Posting to social media platforms...")
            social_results = await post_content_everywhere(video_file, caption)
            results['social_posting'] = social_results
            
            if social_results['success_count'] > 0:
                results['success'] = True
                print(f"🎉 Campaign completed! Posted to {social_results['success_count']} platforms")
            else:
                print("❌ Failed to post to any platforms")
            
            return results
            
        except Exception as e:
            print(f"❌ Campaign error: {str(e)}")
            results['error'] = str(e)
            return results
    
    async def create_and_post_image_to_video_campaign(self, image_path: str, animation_prompt: str, caption: str = "", style: str = "cinematic") -> Dict[str, Any]:
        """
        Create video from existing image and post to social media
        
        Args:
            image_path (str): Path to source image
            animation_prompt (str): Description for video animation
            caption (str): Caption for social media posts
            style (str): Style for video generation
            
        Returns:
            Dict with creation and posting results
        """
        print(f"🚀 Starting image-to-video campaign...")
        
        results = {
            'content_creation': None,
            'social_posting': None,
            'success': False,
            'created_file': None,
            'campaign_type': 'image_to_video',
            'source_image': image_path
        }
        
        try:
            if not os.path.exists(image_path):
                results['content_creation'] = {'success': False, 'error': f'Source image not found: {image_path}'}
                return results
            
            # Step 1: Create video from image
            print("🎬 Creating video from image...")
            video_file = await video_from_image(image_path, animation_prompt, style)
            
            if not video_file:
                results['content_creation'] = {'success': False, 'error': 'Failed to create video from image'}
                return results
            
            results['content_creation'] = {'success': True, 'file': video_file}
            results['created_file'] = video_file
            print(f"✅ Video created from image: {video_file}")
            
            # Step 2: Post to social media
            print("📱 Posting to social media platforms...")
            social_results = await post_content_everywhere(video_file, caption)
            results['social_posting'] = social_results
            
            if social_results['success_count'] > 0:
                results['success'] = True
                print(f"🎉 Campaign completed! Posted to {social_results['success_count']} platforms")
            else:
                print("❌ Failed to post to any platforms")
            
            return results
            
        except Exception as e:
            print(f"❌ Campaign error: {str(e)}")
            results['error'] = str(e)
            return results
    
    async def run_batch_campaigns(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run multiple campaigns in batch
        
        Args:
            campaigns (List[Dict]): List of campaign configurations
            
        Returns:
            List of campaign results
        """
        print(f"🚀 Starting batch execution of {len(campaigns)} campaigns...")
        
        results = []
        successful_campaigns = 0
        
        for i, campaign in enumerate(campaigns, 1):
            print(f"\n--- Campaign {i}/{len(campaigns)} ---")
            
            campaign_type = campaign.get('type', 'image')
            
            if campaign_type == 'image':
                result = await self.create_and_post_image_campaign(
                    campaign['prompt'],
                    campaign.get('caption', ''),
                    campaign.get('style', 'hyperrealistic poster')
                )
            elif campaign_type == 'video':
                result = await self.create_and_post_video_campaign(
                    campaign['prompt'],
                    campaign.get('caption', ''),
                    campaign.get('style', 'cinematic'),
                    campaign.get('aspect_ratio', '16:9')
                )
            elif campaign_type == 'image_to_video':
                result = await self.create_and_post_image_to_video_campaign(
                    campaign['image_path'],
                    campaign['animation_prompt'],
                    campaign.get('caption', ''),
                    campaign.get('style', 'cinematic')
                )
            else:
                result = {'success': False, 'error': f'Unknown campaign type: {campaign_type}'}
            
            result['campaign_index'] = i
            result['campaign_config'] = campaign
            results.append(result)
            
            if result['success']:
                successful_campaigns += 1
            
            # Add delay between campaigns to avoid rate limiting
            if i < len(campaigns):
                print("⏳ Waiting 30 seconds before next campaign...")
                await asyncio.sleep(30)
        
        print(f"\n🎉 Batch execution completed!")
        print(f"✅ Successful campaigns: {successful_campaigns}/{len(campaigns)}")
        
        return results
    
    async def get_campaign_analytics(self) -> Optional[Dict[str, Any]]:
        """Get analytics for recent campaigns"""
        try:
            print("📊 Retrieving campaign analytics...")
            insights = await self.facebook_agent.get_page_insights()
            return insights
        except Exception as e:
            print(f"❌ Error getting analytics: {str(e)}")
            return None
    
    # ==================== ENHANCED FEATURES ====================
    
    async def create_industry_optimized_campaign(self, industry: str, business_details: Dict[str, Any], 
                                               user_id: str = "default_user") -> Dict[str, Any]:
        """Create campaign using industry-specific templates"""
        try:
            print(f"🏭 Creating industry-optimized campaign for {industry}...")
            
            # Get industry templates
            templates = await self.template_engine.get_templates_by_industry(industry)
            if not templates:
                return {'success': False, 'error': f'No templates found for {industry}'}
            
            # Select best template
            template = templates[0]  # Use first template for demo
            
            # Generate customized campaign
            campaign_config = await self.template_engine.generate_campaign_from_template(
                template.template_id, business_details
            )
            
            if not campaign_config['success']:
                return campaign_config
            
            # Create campaign using template
            config = campaign_config['campaign_config']
            result = await self.create_and_post_image_campaign(
                config['image_prompt'],
                config['caption'],
                user_id=user_id,
                industry=industry,
                track_performance=True
            )
            
            result['template_used'] = template.name
            result['industry_optimization'] = True
            return result
            
        except Exception as e:
            print(f"❌ Error creating industry campaign: {e}")
            return {'success': False, 'error': str(e)}
    
    async def create_viral_trend_campaign(self, user_id: str, industry: str = "general") -> Dict[str, Any]:
        """Create campaign based on current viral trends"""
        try:
            print(f"🔥 Creating viral trend campaign for {industry}...")
            
            # Generate viral campaign
            viral_campaign = await self.viral_engine.generate_viral_campaign(user_id, industry)
            
            # Use the viral content in our campaign system
            result = await self.create_and_post_image_campaign(
                viral_campaign.viral_content.viral_prompt,
                viral_campaign.viral_content.viral_caption,
                user_id=user_id,
                industry=industry,
                track_performance=True
            )
            
            result['viral_campaign'] = True
            result['trending_topic'] = viral_campaign.trending_topic.topic_name
            result['virality_score'] = viral_campaign.viral_content.virality_score
            result['performance_prediction'] = viral_campaign.performance_prediction
            
            return result
            
        except Exception as e:
            print(f"❌ Error creating viral campaign: {e}")
            return {'success': False, 'error': str(e)}
    
    async def create_competitor_beating_campaign(self, competitor_url: str, competitor_name: str, 
                                               user_id: str) -> Dict[str, Any]:
        """Create campaign that outperforms competitor content"""
        try:
            print(f"🥊 Creating competitor-beating campaign vs {competitor_name}...")
            
            # Analyze competitor content
            analysis = await self.competitor_engine.analyze_competitor_url(competitor_url, competitor_name)
            
            if not analysis['success']:
                return analysis
            
            # Generate improved campaign
            improved_campaign = await self.competitor_engine.generate_competitive_campaign(
                analysis['content_id'], user_id
            )
            
            if not improved_campaign['success']:
                return improved_campaign
            
            # Post the improved content
            result = await post_content_everywhere(
                improved_campaign['generated_asset'],
                improved_campaign['improved_caption']
            )
            
            return {
                'success': True,
                'competitive_campaign': True,
                'competitor_analyzed': competitor_name,
                'generated_asset': improved_campaign['generated_asset'],
                'performance_lift_estimate': improved_campaign['estimated_performance_lift'],
                'competitive_advantages': improved_campaign['competitive_advantages'],
                'social_posting': result
            }
            
        except Exception as e:
            print(f"❌ Error creating competitor-beating campaign: {e}")
            return {'success': False, 'error': str(e)}
    
    async def track_conversion(self, campaign_id: str, conversion_type: str, 
                              value: float, customer_id: str = None) -> bool:
        """Track conversion for campaign ROI calculation"""
        try:
            conversion_id = await self.revenue_engine.track_conversion(
                campaign_id, conversion_type, value, customer_id
            )
            return bool(conversion_id)
        except Exception as e:
            print(f"❌ Error tracking conversion: {e}")
            return False
    
    async def get_campaign_roi(self, campaign_id: str, ad_spend: float = 0) -> Dict[str, Any]:
        """Get comprehensive ROI analysis for campaign"""
        try:
            roi_metrics = await self.revenue_engine.calculate_campaign_roi(campaign_id, ad_spend)
            return {
                'campaign_id': campaign_id,
                'total_revenue': roi_metrics.total_revenue,
                'total_spend': roi_metrics.total_spend,
                'roi_percentage': roi_metrics.roi_percentage,
                'cost_per_conversion': roi_metrics.cost_per_conversion,
                'conversion_count': roi_metrics.conversion_count,
                'lifetime_value': roi_metrics.lifetime_value
            }
        except Exception as e:
            print(f"❌ Error getting ROI: {e}")
            return {'error': str(e)}
    
    async def get_success_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive success dashboard for user"""
        try:
            print(f"📊 Generating success dashboard for {user_id}...")
            
            # Get revenue report
            revenue_report = await self.revenue_engine.generate_success_report(user_id)
            
            # Get performance dashboard
            performance_dashboard = await self.performance_engine.get_performance_dashboard(user_id)
            
            # Get attribution insights
            attribution_insights = await self.revenue_engine.get_attribution_insights(user_id)
            
            return {
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'revenue_analytics': revenue_report,
                'performance_metrics': performance_dashboard,
                'attribution_insights': attribution_insights,
                'success_summary': {
                    'total_campaigns': revenue_report.get('overall_metrics', {}).get('total_campaigns', 0),
                    'total_revenue': revenue_report.get('overall_metrics', {}).get('total_revenue', 0),
                    'overall_roi': revenue_report.get('overall_metrics', {}).get('overall_roi', 0),
                    'guarantee_success_rate': performance_dashboard.get('summary', {}).get('guarantee_success_rate', 0)
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            return {'error': str(e)}

# Helper functions for easy campaign creation
async def quick_image_campaign(prompt: str, caption: str = "", user_id: str = "default_user", industry: str = "general"):
    """Quick enhanced image campaign creation and posting"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_and_post_image_campaign(prompt, caption, user_id=user_id, industry=industry)

async def quick_video_campaign(prompt: str, caption: str = ""):
    """Quick video campaign creation and posting"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_and_post_video_campaign(prompt, caption)

async def quick_image_to_video_campaign(image_path: str, animation_prompt: str, caption: str = ""):
    """Quick image-to-video campaign creation and posting"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_and_post_image_to_video_campaign(image_path, animation_prompt, caption)

# Enhanced helper functions
async def create_industry_campaign(industry: str, business_details: Dict[str, Any], user_id: str = "default_user"):
    """Quick industry-optimized campaign"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_industry_optimized_campaign(industry, business_details, user_id)

async def create_viral_campaign(user_id: str, industry: str = "general"):
    """Quick viral trend campaign"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_viral_trend_campaign(user_id, industry)

async def beat_competitor(competitor_url: str, competitor_name: str, user_id: str):
    """Quick competitor-beating campaign"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_competitor_beating_campaign(competitor_url, competitor_name, user_id)

async def get_dashboard(user_id: str):
    """Quick success dashboard"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.get_success_dashboard(user_id)

async def main():
    print("🤖 Marketing Automation Engine")
    print("=" * 40)
    print("1. Create & post image campaign")
    print("2. Create & post video campaign") 
    print("3. Create & post image-to-video campaign")
    print("4. Run batch campaigns")
    print("5. Get campaign analytics")
    print("6. Run sample campaign suite")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == "1":
        prompt = input("Enter image prompt: ").strip()
        caption = input("Enter caption for social media: ").strip()
        style = input("Style (default 'hyperrealistic poster'): ").strip() or "hyperrealistic poster"
        
        result = await quick_image_campaign(prompt, caption)
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "2":
        prompt = input("Enter video prompt: ").strip()
        caption = input("Enter caption for social media: ").strip()
        style = input("Style (default 'cinematic'): ").strip() or "cinematic"
        
        result = await quick_video_campaign(prompt, caption)
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "3":
        image_path = input("Enter image path: ").strip()
        animation_prompt = input("Enter animation description: ").strip()
        caption = input("Enter caption for social media: ").strip()
        
        result = await quick_image_to_video_campaign(image_path, animation_prompt, caption)
        print(f"\n📊 Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "4":
        industry = input("Enter industry (restaurant/fitness/beauty/etc): ").strip()
        business_name = input("Enter business name: ").strip()
        signature_item = input("Enter signature product/service: ").strip()
        phone = input("Enter phone number: ").strip()
        
        business_details = {
            'business_name': business_name,
            'signature_dish': signature_item if industry == 'restaurant' else signature_item,
            'phone': phone
        }
        
        result = await create_industry_campaign(industry, business_details, "user_123")
        print(f"\n📊 Industry Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "5":
        industry = input("Enter industry (general/fitness/beauty/restaurant): ").strip() or "general"
        
        result = await create_viral_campaign("user_123", industry)
        print(f"\n📊 Viral Campaign Result: {json.dumps(result, indent=2)}")
    
    elif choice == "6":
        competitor_url = input("Enter competitor content URL: ").strip()
        competitor_name = input("Enter competitor name: ").strip()
        
        result = await beat_competitor(competitor_url, competitor_name, "user_123")
        print(f"\n📊 Competitor-Beating Result: {json.dumps(result, indent=2)}")
    
    elif choice == "7":
        user_id = input("Enter user ID (or press enter for demo_user): ").strip() or "demo_user"
        
        dashboard = await get_dashboard(user_id)
        print(f"\n📊 Success Dashboard: {json.dumps(dashboard, indent=2)}")
    
    elif choice == "8":
        # Sample batch campaigns
        campaigns = [
            {
                'type': 'image',
                'prompt': 'A stunning sunset over a mountain lake with golden reflections',
                'caption': '🌅 Golden hour magic at the lake! #sunset #nature #photography'
            },
            {
                'type': 'video', 
                'prompt': 'A peaceful forest with sunlight filtering through trees',
                'caption': '🌲 Find peace in nature\'s embrace #forest #peace #mindfulness'
            }
        ]
        
        engine = EnhancedMarketingAutomationEngine()
        results = await engine.run_batch_campaigns(campaigns)
        print(f"\n📊 Batch Results: {json.dumps(results, indent=2)}")
    
    elif choice == "9":
        engine = EnhancedMarketingAutomationEngine()
        analytics = await engine.get_campaign_analytics()
        if analytics:
            print(f"\n📊 Analytics: {json.dumps(analytics, indent=2)}")
        else:
            print("\n❌ Failed to retrieve analytics")
    
    elif choice == "10":
        print("🚀 Running sample campaign suite...")
        
        # Create a mixed campaign suite
        campaigns = [
            {
                'type': 'image',
                'prompt': 'Professional business team celebrating success in modern office',
                'caption': '🎉 Success is a team effort! #teamwork #business #success',
                'style': 'hyperrealistic poster'
            },
            {
                'type': 'video',
                'prompt': 'Inspiring entrepreneur working late at night with city lights in background',
                'caption': '💼 The grind never stops! #entrepreneur #hustle #motivation',
                'style': 'cinematic'
            }
        ]
        
        engine = EnhancedMarketingAutomationEngine()
        results = await engine.run_batch_campaigns(campaigns)
        
        # Show summary
        print(f"\n🎯 Campaign Suite Summary:")
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"  Campaign {result['campaign_index']}: {status}")
            if result.get('created_file'):
                print(f"    File: {result['created_file']}")
            if result.get('social_posting', {}).get('success_count'):
                print(f"    Posted to: {result['social_posting']['success_count']} platforms")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())