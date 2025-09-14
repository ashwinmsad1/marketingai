from dotenv import load_dotenv
import os
import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import mimetypes

# Configure logging
logger = logging.getLogger(__name__)

from ..utils.config_manager import get_config, ConfigurationError
from ..utils.meta_response_formatter import MetaResponseFormatter, MetaErrorType, MetaPlatform, classify_meta_error
from ..utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenError
from ..utils.meta_health_check import get_meta_health_status, get_cached_meta_health_status
from ..utils.meta_config import get_meta_config, validate_meta_config
from ..utils.meta_startup_validator import get_startup_validation_summary

load_dotenv()

# Import Meta API error classes for consistency
class FacebookAPIError(Exception):
    """Base exception for Facebook API errors"""
    pass

class FacebookRateLimitError(FacebookAPIError):
    """Facebook rate limit exceeded error"""
    pass

class FacebookAuthError(FacebookAPIError):
    """Facebook authentication error"""
    pass

class FacebookUploadError(FacebookAPIError):
    """Facebook content upload error"""
    pass

def facebook_retry(max_attempts=3):
    """Retry decorator for Facebook API calls"""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    error_type, should_retry, delay = self._classify_facebook_error(e)
                    
                    if should_retry and attempt < max_attempts - 1:
                        logger.warning(f"Facebook API error (attempt {attempt + 1}/{max_attempts}): {e}")
                        if delay > 0:
                            logger.info(f"Waiting {delay}s before retry...")
                            await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error(f"Facebook API failed after {attempt + 1} attempts: {e}")
                        raise e
            return None
        return wrapper
    return decorator

class FacebookMarketingAgent:
    def __init__(self):
        try:
            # Load centralized Meta configuration
            self.meta_config = get_meta_config()
            
            # Validate configuration
            is_valid, errors = validate_meta_config()
            if not is_valid:
                raise ConfigurationError(f"Meta configuration validation failed: {'; '.join(errors)}")
            
            # Extract commonly used values for convenience
            self.access_token = self.meta_config.access_token
            self.page_id = self.meta_config.facebook_page_id
            self.instagram_business_id = self.meta_config.instagram_business_id
            self.api_version = self.meta_config.graph_api_version
            self.graph_api_url = f"https://graph.facebook.com/{self.api_version}"
            self.timeout = self.meta_config.api_timeout
            self.retry_count = self.meta_config.retry_count
            
            if not self.access_token:
                raise ConfigurationError("META_ACCESS_TOKEN is required for Facebook Agent")
                
            logger.info(f"Facebook Agent initialized with centralized config (API: {self.api_version}, Environment: {self.meta_config.environment.value})")
        except ConfigurationError as e:
            logger.error(f"Facebook agent configuration error: {e}")
            raise ValueError(f"Facebook agent configuration error: {e}")
    
    def _classify_facebook_error(self, error: Exception) -> tuple[str, bool, float]:
        """
        Classify Facebook API errors and determine retry strategy
        Uses standardized Meta error classification
        
        Returns:
            tuple: (error_type, should_retry, delay_seconds)
        """
        error_type, should_retry, delay = classify_meta_error(error)
        return error_type.value, should_retry, delay
    
    def _create_error_response(self, platform: str, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Create standardized error response for any exception
        
        Args:
            platform: Platform name (facebook, instagram, both)
            error: Exception that occurred
            context: Additional context about the error
        
        Returns:
            Standardized error response dictionary
        """
        # Handle circuit breaker open errors specially
        if isinstance(error, CircuitBreakerOpenError):
            return MetaResponseFormatter.error_response(
                platform=platform,
                error_message=f"Service temporarily unavailable due to circuit breaker: {str(error)}",
                error_type=MetaErrorType.SERVER_ERROR,
                retry_suggested=True,
                data={'circuit_breaker': error.circuit_name, 'retry_after': error.retry_after}
            )
        
        # Use standard error classification
        error_type, should_retry, delay = classify_meta_error(error)
        
        error_message = f"{context}: {str(error)}" if context else str(error)
        
        return MetaResponseFormatter.error_response(
            platform=platform,
            error_message=error_message,
            error_type=error_type,
            retry_suggested=should_retry
        )
    
    async def get_health_status(self, run_checks: bool = True) -> Dict[str, Any]:
        """
        Get health status of Meta API services
        
        Args:
            run_checks: Whether to run new health checks or use cached results
        
        Returns:
            Health status dictionary
        """
        try:
            if run_checks:
                return await get_meta_health_status()
            else:
                return get_cached_meta_health_status()
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                'overall_status': 'UNKNOWN',
                'message': f'Health check failed: {str(e)}',
                'timestamp': None,
                'services': {}
            }
    
    async def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for all Meta API services"""
        try:
            from ..utils.circuit_breaker import circuit_manager
            return circuit_manager.get_health_status()
        except Exception as e:
            logger.error(f"Failed to get circuit breaker status: {e}")
            return {
                'error': str(e),
                'overall_status': 'UNKNOWN'
            }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get Facebook Agent configuration summary"""
        try:
            from ..utils.meta_config import get_meta_config_summary
            return get_meta_config_summary()
        except Exception as e:
            logger.error(f"Failed to get configuration summary: {e}")
            return {
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_startup_validation_status(self) -> Dict[str, Any]:
        """Get Meta API startup validation status"""
        try:
            return get_startup_validation_summary()
        except Exception as e:
            logger.error(f"Failed to get startup validation status: {e}")
            return {
                'error': str(e),
                'status': 'unknown'
            }

    @circuit_breaker(
        name="facebook_video_upload",
        failure_threshold=3,
        timeout=300.0,  # 5 minutes
        expected_exception=Exception
    )
    @facebook_retry(max_attempts=3)
    async def upload_video_to_facebook(self, video_path: str, caption: str = "", scheduled_time: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Upload video to Facebook Page
        
        Args:
            video_path (str): Path to video file
            caption (str): Caption for the video post
            scheduled_time (int, optional): Unix timestamp for scheduled posting
            
        Returns:
            Dict containing post_id and success status, or None if failed
        """
        try:
            if not os.path.exists(video_path):
                print(f"❌ Video file not found: {video_path}")
                return None
            
            # Validate video file
            file_size = os.path.getsize(video_path)
            if file_size > 4 * 1024 * 1024 * 1024:  # 4GB limit
                print(f"❌ Video file too large: {file_size} bytes (4GB limit)")
                return None
            
            if file_size < 1000:
                print(f"❌ Video file too small: {file_size} bytes")
                return None
            
            print(f"🚀 Uploading video to Facebook: {os.path.basename(video_path)} ({file_size} bytes)")
            
            # Step 1: Initialize upload session
            init_url = f"{self.graph_api_url}/{self.page_id}/videos"
            
            async with aiohttp.ClientSession() as session:
                # Safely read video file using context manager
                try:
                    with open(video_path, 'rb') as video_file:
                        video_data = video_file.read()
                except IOError as e:
                    logger.error(f"Failed to read video file {video_path}: {e}")
                    print(f"❌ Failed to read video file: {e}")
                    return None
                
                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field('access_token', self.access_token)
                form_data.add_field('description', caption)
                
                if scheduled_time:
                    form_data.add_field('scheduled_publish_time', str(scheduled_time))
                    form_data.add_field('published', 'false')
                
                # Add video file
                form_data.add_field('source', video_data, filename=os.path.basename(video_path), content_type='video/mp4')
                
                # Upload video
                async with session.post(init_url, data=form_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Facebook video uploaded successfully!")
                        print(f"📝 Post ID: {result.get('id')}")
                        return MetaResponseFormatter.success_response(
                            platform=MetaPlatform.FACEBOOK.value,
                            post_id=result.get('id'),
                            message='Video uploaded to Facebook successfully'
                        )
                    else:
                        error_text = await response.text()
                        print(f"❌ Facebook upload failed: {response.status}")
                        print(f"❌ Error: {error_text}")
                        
                        # Classify error based on status code and message
                        error_type = MetaErrorType.CLIENT_ERROR
                        retry_suggested = False
                        
                        if response.status == 429:
                            error_type = MetaErrorType.RATE_LIMIT
                            retry_suggested = True
                        elif response.status >= 500:
                            error_type = MetaErrorType.SERVER_ERROR
                            retry_suggested = True
                        elif response.status == 401:
                            error_type = MetaErrorType.AUTH_ERROR
                        elif response.status == 403:
                            error_type = MetaErrorType.PERMISSION_ERROR
                        
                        return MetaResponseFormatter.error_response(
                            platform=MetaPlatform.FACEBOOK.value,
                            error_message=f"Facebook upload failed: {response.status} - {error_text}",
                            error_type=error_type,
                            retry_suggested=retry_suggested
                        )
                        
        except FileNotFoundError as e:
            logger.error(f"Video file not found: {e}")
            print(f"❌ Video file not found: {str(e)}")
            return self._create_error_response(
                platform=MetaPlatform.FACEBOOK.value,
                error=e,
                context="Video file not found"
            )
        except PermissionError as e:
            logger.error(f"Permission denied accessing video file: {e}")
            print(f"❌ Permission denied: {str(e)}")
            return self._create_error_response(
                platform=MetaPlatform.FACEBOOK.value,
                error=e,
                context="Permission denied accessing video file"
            )
        except aiohttp.ClientError as e:
            logger.error(f"Network error uploading to Facebook: {e}")
            print(f"❌ Network error: {str(e)}")
            return self._create_error_response(
                platform=MetaPlatform.FACEBOOK.value,
                error=e,
                context="Network error uploading to Facebook"
            )
        except Exception as e:
            logger.error(f"Unexpected error uploading to Facebook: {e}")
            print(f"❌ Error uploading to Facebook: {str(e)}")
            return self._create_error_response(
                platform=MetaPlatform.FACEBOOK.value,
                error=e,
                context="Unexpected error uploading to Facebook"
            )
    
    @circuit_breaker(
        name="instagram_video_upload",
        failure_threshold=3,
        timeout=300.0,  # 5 minutes
        expected_exception=Exception
    )
    @facebook_retry(max_attempts=3)
    async def upload_video_to_instagram(self, video_path: str, caption: str = "") -> Optional[Dict[str, Any]]:
        """
        Upload video to Instagram Business Account (Reels)
        
        Args:
            video_path (str): Path to video file
            caption (str): Caption for the video post
            
        Returns:
            Dict containing creation_id and success status, or None if failed
        """
        try:
            if not self.instagram_business_id:
                print("❌ Instagram Business ID not configured")
                return None
            
            if not os.path.exists(video_path):
                print(f"❌ Video file not found: {video_path}")
                return None
                
            file_size = os.path.getsize(video_path)
            print(f"🚀 Uploading video to Instagram: {os.path.basename(video_path)} ({file_size} bytes)")
            
            # Step 1: Create media container
            container_url = f"{self.graph_api_url}/{self.instagram_business_id}/media"
            
            async with aiohttp.ClientSession() as session:
                # Create media container for video/reel
                container_params = {
                    'access_token': self.access_token,
                    'media_type': 'REELS',
                    'video_url': f'file://{os.path.abspath(video_path)}',  # This needs to be publicly accessible URL
                    'caption': caption
                }
                
                # Note: For production, you'll need to upload the video to a publicly accessible URL first
                # This is a limitation of Instagram Graph API - it requires publicly accessible URLs
                print("⚠️  Note: Instagram Graph API requires publicly accessible video URLs")
                print("⚠️  In production, upload video to cloud storage (S3/GCS) first")
                
                async with session.post(container_url, params=container_params) as response:
                    if response.status == 200:
                        container_result = await response.json()
                        creation_id = container_result.get('id')
                        print(f"📦 Media container created: {creation_id}")
                        
                        # Step 2: Publish the media
                        publish_url = f"{self.graph_api_url}/{self.instagram_business_id}/media_publish"
                        publish_params = {
                            'access_token': self.access_token,
                            'creation_id': creation_id
                        }
                        
                        async with session.post(publish_url, params=publish_params) as publish_response:
                            if publish_response.status == 200:
                                publish_result = await publish_response.json()
                                print(f"✅ Instagram video published successfully!")
                                print(f"📝 Media ID: {publish_result.get('id')}")
                                
                                return {
                                    'platform': 'instagram',
                                    'media_id': publish_result.get('id'),
                                    'creation_id': creation_id,
                                    'success': True,
                                    'message': 'Video uploaded to Instagram successfully'
                                }
                            else:
                                error_text = await publish_response.text()
                                print(f"❌ Instagram publish failed: {publish_response.status}")
                                print(f"❌ Error: {error_text}")
                                return None
                    else:
                        error_text = await response.text()
                        print(f"❌ Instagram container creation failed: {response.status}")
                        print(f"❌ Error: {error_text}")
                        return None
                        
        except FileNotFoundError as e:
            logger.error(f"Video file not found for Instagram: {e}")
            print(f"❌ Video file not found: {str(e)}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied accessing video file for Instagram: {e}")
            print(f"❌ Permission denied: {str(e)}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error uploading to Instagram: {e}")
            print(f"❌ Network error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to Instagram: {e}")
            print(f"❌ Error uploading to Instagram: {str(e)}")
            return None
    
    @circuit_breaker(
        name="facebook_image_upload",
        failure_threshold=3,
        timeout=180.0,  # 3 minutes
        expected_exception=Exception
    )
    @facebook_retry(max_attempts=3)
    async def upload_image_to_facebook(self, image_path: str, caption: str = "") -> Optional[Dict[str, Any]]:
        """Upload image to Facebook Page"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            file_size = os.path.getsize(image_path)
            print(f"🚀 Uploading image to Facebook: {os.path.basename(image_path)} ({file_size} bytes)")
            
            url = f"{self.graph_api_url}/{self.page_id}/photos"
            
            async with aiohttp.ClientSession() as session:
                # Safely read image file using context manager
                try:
                    with open(image_path, 'rb') as image_file:
                        image_data = image_file.read()
                except IOError as e:
                    logger.error(f"Failed to read image file {image_path}: {e}")
                    print(f"❌ Failed to read image file: {e}")
                    return None
                
                form_data = aiohttp.FormData()
                form_data.add_field('access_token', self.access_token)
                form_data.add_field('message', caption)
                form_data.add_field('source', image_data, filename=os.path.basename(image_path), content_type='image/jpeg')
                
                async with session.post(url, data=form_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Facebook image uploaded successfully!")
                        print(f"📝 Post ID: {result.get('post_id')}")
                        return {
                            'platform': 'facebook',
                            'post_id': result.get('post_id'),
                            'success': True,
                            'message': 'Image uploaded to Facebook successfully'
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Facebook image upload failed: {response.status}")
                        print(f"❌ Error: {error_text}")
                        return None
                        
        except FileNotFoundError as e:
            logger.error(f"Image file not found: {e}")
            print(f"❌ Image file not found: {str(e)}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied accessing image file: {e}")
            print(f"❌ Permission denied: {str(e)}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error uploading image to Facebook: {e}")
            print(f"❌ Network error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading image to Facebook: {e}")
            print(f"❌ Error uploading image to Facebook: {str(e)}")
            return None
    
    @circuit_breaker(
        name="instagram_image_upload",
        failure_threshold=3,
        timeout=180.0,  # 3 minutes
        expected_exception=Exception
    )
    @facebook_retry(max_attempts=3)
    async def upload_image_to_instagram(self, image_path: str, caption: str = "") -> Optional[Dict[str, Any]]:
        """Upload image to Instagram Business Account"""
        try:
            if not self.instagram_business_id:
                print("❌ Instagram Business ID not configured")
                return None
            
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            file_size = os.path.getsize(image_path)
            print(f"🚀 Uploading image to Instagram: {os.path.basename(image_path)} ({file_size} bytes)")
            
            # Step 1: Create media container
            container_url = f"{self.graph_api_url}/{self.instagram_business_id}/media"
            
            async with aiohttp.ClientSession() as session:
                container_params = {
                    'access_token': self.access_token,
                    'image_url': f'file://{os.path.abspath(image_path)}',  # Needs publicly accessible URL
                    'caption': caption
                }
                
                print("⚠️  Note: Instagram Graph API requires publicly accessible image URLs")
                print("⚠️  In production, upload image to cloud storage (S3/GCS) first")
                
                async with session.post(container_url, params=container_params) as response:
                    if response.status == 200:
                        container_result = await response.json()
                        creation_id = container_result.get('id')
                        print(f"📦 Media container created: {creation_id}")
                        
                        # Step 2: Publish the media
                        publish_url = f"{self.graph_api_url}/{self.instagram_business_id}/media_publish"
                        publish_params = {
                            'access_token': self.access_token,
                            'creation_id': creation_id
                        }
                        
                        async with session.post(publish_url, params=publish_params) as publish_response:
                            if publish_response.status == 200:
                                publish_result = await publish_response.json()
                                print(f"✅ Instagram image published successfully!")
                                print(f"📝 Media ID: {publish_result.get('id')}")
                                
                                return {
                                    'platform': 'instagram',
                                    'media_id': publish_result.get('id'),
                                    'creation_id': creation_id,
                                    'success': True,
                                    'message': 'Image uploaded to Instagram successfully'
                                }
                            else:
                                error_text = await publish_response.text()
                                print(f"❌ Instagram publish failed: {publish_response.status}")
                                print(f"❌ Error: {error_text}")
                                return None
                    else:
                        error_text = await response.text()
                        print(f"❌ Instagram container creation failed: {response.status}")
                        print(f"❌ Error: {error_text}")
                        return None
                        
        except FileNotFoundError as e:
            logger.error(f"Image file not found for Instagram: {e}")
            print(f"❌ Image file not found: {str(e)}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied accessing image file for Instagram: {e}")
            print(f"❌ Permission denied: {str(e)}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error uploading image to Instagram: {e}")
            print(f"❌ Network error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading image to Instagram: {e}")
            print(f"❌ Error uploading image to Instagram: {str(e)}")
            return None
    
    async def get_page_insights(self, metrics: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get Facebook Page insights/analytics"""
        try:
            if not metrics:
                metrics = ['page_impressions', 'page_engaged_users', 'page_video_views', 'page_post_engagements']
            
            url = f"{self.graph_api_url}/{self.page_id}/insights"
            params = {
                'access_token': self.access_token,
                'metric': ','.join(metrics),
                'period': 'day',
                'since': 'yesterday',
                'until': 'today'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Retrieved Facebook Page insights")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to get insights: {response.status}")
                        print(f"❌ Error: {error_text}")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error getting page insights: {e}")
            print(f"❌ Network error getting insights: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Invalid response getting page insights: {e}")
            print(f"❌ Invalid response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting page insights: {e}")
            print(f"❌ Error getting page insights: {str(e)}")
            return None

# Wrapper functions for easy import
async def post_video_to_facebook(video_path: str, caption: str = "", scheduled_time: Optional[int] = None):
    """Post video to Facebook Page"""
    agent = FacebookMarketingAgent()
    return await agent.upload_video_to_facebook(video_path, caption, scheduled_time)

async def post_video_to_instagram(video_path: str, caption: str = ""):
    """Post video to Instagram Business Account"""
    agent = FacebookMarketingAgent()
    return await agent.upload_video_to_instagram(video_path, caption)

async def post_image_to_facebook(image_path: str, caption: str = ""):
    """Post image to Facebook Page"""
    agent = FacebookMarketingAgent()
    return await agent.upload_image_to_facebook(image_path, caption)

async def post_image_to_instagram(image_path: str, caption: str = ""):
    """Post image to Instagram Business Account"""
    agent = FacebookMarketingAgent()
    return await agent.upload_image_to_instagram(image_path, caption)

@circuit_breaker(
    name="multi_platform_posting",
    failure_threshold=2,
    timeout=600.0,  # 10 minutes
    expected_exception=Exception
)
@facebook_retry(max_attempts=3)
async def post_content_everywhere(content_path: str, caption: str = ""):
    """
    Post content to both Facebook and Instagram using standardized batch response
    
    Args:
        content_path (str): Path to image or video file
        caption (str): Caption for the posts
        
    Returns:
        Standardized batch response with results from both platforms
    """
    agent = FacebookMarketingAgent()
    
    # Determine if content is video or image
    file_ext = Path(content_path).suffix.lower()
    is_video = file_ext in ['.mp4', '.mov', '.avi', '.mkv']
    
    print(f"🚀 Posting {'video' if is_video else 'image'} to all platforms...")
    
    # Collect results from both platforms
    platform_results = []
    
    # Post to Facebook
    if is_video:
        facebook_result = await agent.upload_video_to_facebook(content_path, caption)
    else:
        facebook_result = await agent.upload_image_to_facebook(content_path, caption)
    
    platform_results.append(facebook_result)
    
    # Post to Instagram
    if is_video:
        instagram_result = await agent.upload_video_to_instagram(content_path, caption)
    else:
        instagram_result = await agent.upload_image_to_instagram(content_path, caption)
    
    platform_results.append(instagram_result)
    
    # Create standardized batch response
    batch_response = MetaResponseFormatter.batch_response(
        platform=MetaPlatform.BOTH.value,
        results=platform_results
    )
    
    success_count = batch_response['successful_operations']
    total_count = batch_response['total_operations']
    
    print(f"✅ Posted to {success_count}/{total_count} platforms successfully")
    
    return batch_response

async def main():
    print("📱 Facebook & Instagram Marketing Agent")
    print("=" * 40)
    print("1. Post video to Facebook")
    print("2. Post video to Instagram") 
    print("3. Post image to Facebook")
    print("4. Post image to Instagram")
    print("5. Post content to all platforms")
    print("6. Get Facebook Page insights")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice in ["1", "2", "3", "4", "5"]:
        content_path = input("Enter path to content file: ").strip()
        if not os.path.exists(content_path):
            print("❌ File not found!")
            return
        
        caption = input("Enter caption (optional): ").strip()
        
        if choice == "1":
            result = await post_video_to_facebook(content_path, caption)
        elif choice == "2":
            result = await post_video_to_instagram(content_path, caption)
        elif choice == "3":
            result = await post_image_to_facebook(content_path, caption)
        elif choice == "4":
            result = await post_image_to_instagram(content_path, caption)
        elif choice == "5":
            result = await post_content_everywhere(content_path, caption)
        
        if result:
            print(f"\n🎉 Success! Result: {result}")
        else:
            print("\n❌ Failed to post content")
    
    elif choice == "6":
        agent = FacebookMarketingAgent()
        insights = await agent.get_page_insights()
        if insights:
            print(f"\n📊 Facebook Page Insights: {json.dumps(insights, indent=2)}")
        else:
            print("\n❌ Failed to get insights")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())