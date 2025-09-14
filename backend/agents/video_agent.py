import asyncio
from google import genai
from google.genai import types
import os
import sys

# Add project root to path for direct execution
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from backend.utils.config_manager import get_config
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.config_manager import get_config

class VideoAgent:
    def __init__(self):
        api_key = get_config("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
        
        # Create client for the new Google Gen AI SDK
        self.client = genai.Client(api_key=api_key)
    
    async def create_video_from_prompt(self, prompt, style="cinematic", aspect_ratio="16:9"):
        """Create marketing video from text prompt using Veo 3.0"""
        try:
            # Enhanced prompt for marketing videos
            enhanced_prompt = f"""
            Create a {style} style marketing video: {prompt}
            
            Video requirements:
            - Professional quality suitable for advertising
            - {style} cinematography with smooth motion
            - Eye-catching visuals perfect for social media marketing
            - High production value for commercial use
            - Engaging content optimized for digital advertising
            """
            
            print(f"🎬 Starting marketing video generation...")
            print(f"⚠️  Note: Veo 3.0 generates 8-second videos with audio")
            
            # Generate video using Veo 3.0 via the new SDK
            response = self.client.models.generate_videos(
                model='veo-3.0-generate-001',
                prompt=enhanced_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    negative_prompt="low quality, blurry, distorted"
                )
            )
            
            if response.generated_videos:
                # Save the generated video
                generated_video = response.generated_videos[0]
                filename = f"marketing_video_{hash(prompt) % 10000}.mp4"
                generated_video.video.save(filename)
                
                # Verify file was created
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    print(f"✅ Marketing video created: {filename} ({file_size} bytes)")
                    return filename
                else:
                    print("❌ Failed to save video file")
                    return None
            
            else:
                print("❌ No videos generated")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"❌ API Quota Exceeded: Rate limit or usage quota reached")
                print(f"💡 Check your Google AI API billing and quota settings")
            elif "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
                print(f"❌ Invalid Request: {error_msg}")
            else:
                print(f"❌ Error: {error_msg}")
            return None
    
    async def create_video_from_image(self, image_path, prompt, style="cinematic", aspect_ratio="16:9"):
        """Animate an image into a marketing video using Veo 3.0"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_path}")
                return None
            
            # Enhanced prompt for image-to-video animation
            enhanced_prompt = f"""
            Animate this image with {style} style: {prompt}
            
            Animation requirements:
            - Smooth, professional {style} motion
            - Marketing-quality animation suitable for advertising
            - Engaging movement that enhances the visual appeal
            - High production value for commercial use
            - Maintain image quality while adding dynamic elements
            """
            
            print(f"🎬 Animating image into marketing video...")
            print(f"⚠️  Note: Veo 3.0 generates 8-second videos with audio")
            
            # Load and prepare the image
            import base64
            import mimetypes
            from PIL import Image
            from io import BytesIO
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Load image with PIL for compatibility
            image = Image.open(BytesIO(image_data))
            
            # Generate video from image using Veo 3.0 via the new SDK
            response = self.client.models.generate_videos(
                model='veo-3.0-generate-001',
                prompt=enhanced_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    negative_prompt="static, frozen, no movement"
                ),
                image=image
            )
            
            if response.generated_videos:
                # Save the generated video
                generated_video = response.generated_videos[0]
                filename = f"animated_video_{hash(prompt) % 10000}.mp4"
                generated_video.video.save(filename)
                
                # Verify file was created
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    print(f"✅ Animated marketing video created: {filename} ({file_size} bytes)")
                    return filename
                else:
                    print("❌ Failed to save animated video")
                    return None
            
            else:
                print("❌ No videos generated from image")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"❌ API Quota Exceeded: Rate limit or usage quota reached")
                print(f"💡 Check your Google AI API billing and quota settings")
            elif "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
                print(f"❌ Invalid Request: {error_msg}")
            else:
                print(f"❌ Error: {error_msg}")
            return None

# Wrapper functions for easy import
async def video_from_prompt(prompt, style="cinematic", aspect_ratio="16:9"):
    """Create video from text prompt"""
    agent = VideoAgent()
    return await agent.create_video_from_prompt(prompt, style, aspect_ratio)

async def video_from_image(image_path, prompt, style="cinematic", aspect_ratio="16:9"):
    """Create video from image"""
    agent = VideoAgent()
    return await agent.create_video_from_image(image_path, prompt, style, aspect_ratio)

async def main():
    print("🎬 AI Video Generator")
    print("=" * 25)
    print("1. Create video from text")
    print("2. Create video from image")
    
    choice = input("\nSelect option (1-2): ").strip()
    
    if choice == "1":
        prompt = input("Enter video description: ").strip()
        if not prompt:
            print("❌ Prompt required!")
            return
        
        style = input("Style (default 'cinematic'): ").strip() or "cinematic"
        aspect_ratio = input("Aspect ratio (default '16:9'): ").strip() or "16:9"
        
        result = await video_from_prompt(prompt, style, aspect_ratio)
        
        if result:
            print(f"\n🎉 Success! Video: {result}")
        else:
            print("\n❌ Failed to create video")
    
    elif choice == "2":
        image_path = input("Enter image path: ").strip()
        prompt = input("Enter animation description: ").strip()
        
        if not prompt:
            print("❌ Animation description required!")
            return
        
        style = input("Style (default 'cinematic'): ").strip() or "cinematic"
        aspect_ratio = input("Aspect ratio (default '16:9'): ").strip() or "16:9"
        
        result = await video_from_image(image_path, prompt, style, aspect_ratio)
        
        if result:
            print(f"\n🎉 Success! Video: {result}")
        else:
            print("\n❌ Failed to create video")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())