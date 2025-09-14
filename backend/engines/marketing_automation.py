import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Import our AI agents - fix relative imports
from backend.agents.photo_agent import poster_editor, image_creator
from backend.agents.video_agent import video_from_prompt, video_from_image
from backend.agents.facebook_agent import post_content_everywhere, FacebookMarketingAgent

# Import new enhanced systems - fix imports
from .revenue_tracking import RevenueAttributionEngine, track_campaign_success
from .viral_engine import ViralContentEngine, create_viral_campaign

# Placeholder for performance guarantees
class PerformanceGuaranteeEngine:
    def __init__(self):
        pass
    def monitor_campaign(self, campaign):
        return {"status": "placeholder"}

class EnhancedMarketingAutomationEngine:
    """
    Complete AI-powered marketing automation engine with performance guarantees,
    ROI tracking, and viral content creation
    """
    
    def __init__(self):
        self.facebook_agent = FacebookMarketingAgent()
        
        # Initialize enhanced systems
        self.revenue_engine = RevenueAttributionEngine()
        self.performance_engine = PerformanceGuaranteeEngine()
        # Removed template_engine - using enhanced_personalization_service instead
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
            
        except ValueError as e:
            logger.error(f"Validation error in image campaign: {e}")
            print(f"❌ Validation error: {str(e)}")
            results['error'] = f'Validation error: {e}'
            return results
        except FileNotFoundError as e:
            logger.error(f"File not found in image campaign: {e}")
            print(f"❌ File not found: {str(e)}")
            results['error'] = f'File not found: {e}'
            return results
        except PermissionError as e:
            logger.error(f"Permission error in image campaign: {e}")
            print(f"❌ Permission error: {str(e)}")
            results['error'] = f'Permission error: {e}'
            return results
        except Exception as e:
            logger.error(f"Unexpected error in image campaign: {e}")
            print(f"❌ Campaign error: {str(e)}")
            results['error'] = f'Unexpected error: {e}'
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
            
        except ValueError as e:
            logger.error(f"Validation error in video campaign: {e}")
            print(f"❌ Validation error: {str(e)}")
            results['error'] = f'Validation error: {e}'
            return results
        except FileNotFoundError as e:
            logger.error(f"File not found in video campaign: {e}")
            print(f"❌ File not found: {str(e)}")
            results['error'] = f'File not found: {e}'
            return results
        except Exception as e:
            logger.error(f"Unexpected error in video campaign: {e}")
            print(f"❌ Campaign error: {str(e)}")
            results['error'] = f'Unexpected error: {e}'
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
            
        except ValueError as e:
            logger.error(f"Validation error in image-to-video campaign: {e}")
            print(f"❌ Validation error: {str(e)}")
            results['error'] = f'Validation error: {e}'
            return results
        except FileNotFoundError as e:
            logger.error(f"File not found in image-to-video campaign: {e}")
            print(f"❌ File not found: {str(e)}")
            results['error'] = f'File not found: {e}'
            return results
        except Exception as e:
            logger.error(f"Unexpected error in image-to-video campaign: {e}")
            print(f"❌ Campaign error: {str(e)}")
            results['error'] = f'Unexpected error: {e}'
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
        except PermissionError as e:
            logger.error(f"Permission error getting analytics: {e}")
            print(f"❌ Permission error: {str(e)}")
            return None
        except ConnectionError as e:
            logger.error(f"Connection error getting analytics: {e}")
            print(f"❌ Connection error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting analytics: {e}")
            print(f"❌ Error getting analytics: {str(e)}")
            return None
    
    # ==================== ENHANCED FEATURES ====================
    
    async def create_custom_user_campaign(
        self, 
        business_description: str, 
        target_audience: str, 
        campaign_goal: str, 
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Create campaign based on user's custom business input"""
        try:
            print(f"✨ Creating custom campaign for user {user_id}...")
            
            # Build personalized prompt from user inputs
            campaign_prompt = f"""
            Business: {business_description}
            Target Audience: {target_audience}
            Campaign Goal: {campaign_goal}
            
            Create engaging marketing content that speaks directly to the target audience and aligns with the campaign goal.
            """
            
            # Create campaign using the user's custom inputs
            result = await self.create_and_post_image_campaign(
                prompt=campaign_prompt,
                caption=f"Tailored campaign for {campaign_goal.replace('_', ' ')} - reaching {target_audience}",
                user_id=user_id,
                style="professional marketing"
            )
            
            # Add custom campaign metadata
            if result and "status" in result and result["status"] == "success":
                result["campaign_type"] = "custom"
                result["business_description"] = business_description
                result["target_audience"] = target_audience 
                result["campaign_goal"] = campaign_goal
            
            return result
            
        except Exception as e:
            print(f"❌ Error creating custom campaign: {str(e)}")
            return {"status": "error", "error": str(e)}
    
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
            
        except ValueError as e:
            logger.error(f"Validation error creating viral campaign: {e}")
            print(f"❌ Validation error: {e}")
            return {'success': False, 'error': f'Validation error: {e}'}
        except ConnectionError as e:
            logger.error(f"Connection error creating viral campaign: {e}")
            print(f"❌ Connection error: {e}")
            return {'success': False, 'error': f'Connection error: {e}'}
        except Exception as e:
            logger.error(f"Unexpected error creating viral campaign: {e}")
            print(f"❌ Error creating viral campaign: {e}")
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    async def track_conversion(self, campaign_id: str, conversion_type: str, 
                              value: float, customer_id: str = None) -> bool:
        """Track conversion for campaign ROI calculation"""
        try:
            conversion_id = await self.revenue_engine.track_conversion(
                campaign_id, conversion_type, value, customer_id
            )
            return bool(conversion_id)
        except ValueError as e:
            logger.error(f"Validation error tracking conversion: {e}")
            print(f"❌ Validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error tracking conversion: {e}")
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
        except ValueError as e:
            logger.error(f"Validation error getting ROI: {e}")
            print(f"❌ Validation error: {e}")
            return {'error': f'Validation error: {e}'}
        except Exception as e:
            logger.error(f"Unexpected error getting ROI: {e}")
            print(f"❌ Error getting ROI: {e}")
            return {'error': f'Unexpected error: {e}'}
    
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
            
        except ValueError as e:
            logger.error(f"Validation error generating dashboard: {e}")
            print(f"❌ Validation error: {e}")
            return {'error': f'Validation error: {e}'}
        except ConnectionError as e:
            logger.error(f"Connection error generating dashboard: {e}")
            print(f"❌ Connection error: {e}")
            return {'error': f'Connection error: {e}'}
        except Exception as e:
            logger.error(f"Unexpected error generating dashboard: {e}")
            print(f"❌ Error generating dashboard: {e}")
            return {'error': f'Unexpected error: {e}'}

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
async def create_custom_campaign(
    business_description: str, 
    target_audience: str, 
    campaign_goal: str, 
    user_id: str = "default_user"
):
    """Create custom campaign based on user input"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_custom_user_campaign(
        business_description, target_audience, campaign_goal, user_id
    )

async def create_viral_campaign(user_id: str, industry: str = "general"):
    """Quick viral trend campaign"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.create_viral_trend_campaign(user_id, industry)


async def get_dashboard(user_id: str):
    """Quick success dashboard"""
    engine = EnhancedMarketingAutomationEngine()
    return await engine.get_success_dashboard(user_id)

