import asyncio
from google import genai
from google.genai import types
import os
from secure_config_manager import get_config

class VideoAgent:
    def __init__(self):
        api_key = get_config("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
    
    async def create_video_from_prompt(self, prompt, style="cinematic", aspect_ratio="16:9"):
        """Create video from text prompt using Veo 3.0"""
        try:
            enhanced_prompt = f"{style} style video: {prompt}"
            
            print(f"🚀 Starting video generation...")
            print(f"⚠️  Note: Veo 3.0 generates fixed 8-second videos")
            
            # Generate video using Veo 3.0
            operation = self.client.models.generate_videos(
                model="veo-3.0-generate-preview",
                prompt=enhanced_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio
                )
            )
            
            # Poll for completion
            while not operation.done:
                await asyncio.sleep(10)
                operation = self.client.operations.get(operation)
                print("⏳ Still generating...")
            
            if hasattr(operation, 'error') and operation.error:
                print(f"❌ Error: {operation.error}")
                return None
            
            # Get video data
            if not hasattr(operation.result, 'generated_videos') or not operation.result.generated_videos:
                print("❌ No videos generated")
                return None
                
            video_result = operation.result.generated_videos[0]
            video_obj = video_result.video
            
            if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                video_data = video_obj.video_bytes
                
                # Check for API error in response
                if isinstance(video_data, bytes) and video_data.startswith(b'{'):
                    error_text = video_data.decode('utf-8')
                    print(f"❌ API Error: {error_text}")
                    return None
                
                # Save video
                filename = f"video_{hash(prompt) % 10000}.mp4"
                with open(filename, "wb") as f:
                    f.write(video_data)
                
                # Validate file
                file_size = os.path.getsize(filename)
                if file_size < 1000:
                    print("❌ Generated file is too small - likely corrupted")
                    os.remove(filename)
                    return None
                
                print(f"✅ Video saved: {filename} ({file_size} bytes)")
                return filename
            
            else:
                print("❌ No video data available")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"❌ API Quota Exceeded: You've hit the rate limit or usage quota for the Veo 3.0 API")
                print(f"💡 Please check your Google AI API billing and quota settings")
            elif "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
                print(f"❌ Invalid Request: {error_msg}")
            else:
                print(f"❌ Error: {error_msg}")
            return None
    
    async def create_video_from_image(self, image_path, prompt, style="cinematic", aspect_ratio="16:9"):
        """Create video from image using Veo 3.0"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_path}")
                return None
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            enhanced_prompt = f"{style} animation: {prompt}"
            
            print(f"🚀 Creating video from image...")
            print(f"⚠️  Note: Veo 3.0 generates fixed 8-second videos")
            
            operation = self.client.models.generate_videos(
                model="veo-3.0-generate-preview",
                prompt=enhanced_prompt,
                config=types.GenerateVideosConfig(aspect_ratio=aspect_ratio),
                image=types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
            )
            
            # Poll for completion
            while not operation.done:
                await asyncio.sleep(10)
                operation = self.client.operations.get(operation)
                print("⏳ Still generating...")
            
            if hasattr(operation, 'error') and operation.error:
                print(f"❌ Error: {operation.error}")
                return None
            
            # Get and save video data
            if not hasattr(operation.result, 'generated_videos') or not operation.result.generated_videos:
                print("❌ No videos generated")
                return None
                
            video_result = operation.result.generated_videos[0]
            video_obj = video_result.video
            
            if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                video_data = video_obj.video_bytes
                
                # Check for API error
                if isinstance(video_data, bytes) and video_data.startswith(b'{'):
                    error_text = video_data.decode('utf-8')
                    print(f"❌ API Error: {error_text}")
                    return None
                
                filename = f"image_video_{hash(prompt) % 10000}.mp4"
                with open(filename, "wb") as f:
                    f.write(video_data)
                
                file_size = os.path.getsize(filename)
                if file_size < 1000:
                    print("❌ Generated file is too small - likely corrupted")
                    os.remove(filename)
                    return None
                
                print(f"✅ Video saved: {filename} ({file_size} bytes)")
                return filename
            
            else:
                print("❌ No video data available")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"❌ API Quota Exceeded: You've hit the rate limit or usage quota for the Veo 3.0 API")
                print(f"💡 Please check your Google AI API billing and quota settings")
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