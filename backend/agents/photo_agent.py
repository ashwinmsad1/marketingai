import asyncio
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
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

class HyperrealisticPosterAgent:
    def __init__(self):
        api_key = get_config("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
        
        # Create client for the new Google Gen AI SDK
        self.client = genai.Client(api_key=api_key)
        
        # Vision model for image analysis (still using Gemini)
        import google.generativeai as old_genai
        old_genai.configure(api_key=api_key)
        self.vision_model = old_genai.GenerativeModel('gemini-1.5-pro-latest')
    
    def encode_image(self, image_path):
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def create_poster(self, image_path, prompt, style="hyperrealistic poster"):
        """Edit existing image to create a marketing poster using image analysis and generation"""
        try:
            # First, analyze the existing image with Gemini Vision
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            image = Image.open(BytesIO(image_data))
            
            # Use Gemini to analyze the image and create an enhanced prompt
            analysis_prompt = f"""
            Analyze this image and create a detailed prompt to transform it into a {style}.
            Requirements: {prompt}
            
            Create a comprehensive prompt for image generation that includes:
            - Visual elements from the original image to preserve
            - {style} aesthetic enhancements
            - Professional marketing poster qualities
            - High contrast, vibrant colors for advertising
            - Modern composition and layout
            - Social media advertising optimization
            """
            
            analysis_response = self.vision_model.generate_content([analysis_prompt, image])
            enhanced_prompt = analysis_response.text
            
            print(f"🔍 Image analyzed, creating enhanced poster...")
            
            # Generate new image based on enhanced prompt using Imagen 4.0
            response = self.client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=enhanced_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1"  # Square format for social media
                )
            )
            
            if response.generated_images:
                # Save the generated poster
                generated_image = response.generated_images[0]
                filename = f"poster_edited_{hash(prompt) % 10000}.png"
                generated_image.image.save(filename)
                print(f"✅ Marketing poster created: {filename}")
                return filename
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating poster: {str(e)}")
            return None

async def poster_editor(image_path, prompt, style="hyperrealistic poster"):
    """
    Edit an existing image with a given prompt to create a poster (async)
    
    Args:
        image_path (str): Path to the input image
        prompt (str): Description for poster editing
        style (str): Style specification (default: "hyperrealistic poster")
    
    Returns:
        str: Path to generated poster file, or None if failed
    """
    try:
        agent = HyperrealisticPosterAgent()
        return await agent.create_poster(image_path, prompt, style)
    except Exception as e:
        print(f"Error in poster_editor: {str(e)}")
        return None

async def image_creator(prompt, style="hyperrealistic poster", aspect_ratio="1:1"):
    """
    Create a new marketing poster from scratch using Imagen (async)
    
    Args:
        prompt (str): Description for image creation
        style (str): Style specification (default: "hyperrealistic poster")
        aspect_ratio (str): Image aspect ratio (default: "1:1" for social media)
    
    Returns:
        str: Path to generated image file, or None if failed
    """
    try:
        api_key = get_config("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
        
        # Create client for the new Google Gen AI SDK
        client = genai.Client(api_key=api_key)
        
        # Enhanced prompt for marketing poster creation
        enhanced_prompt = f"""
        Create a {style} for marketing and advertising with these specifications:
        {prompt}
        
        Professional marketing requirements:
        - {style} quality with stunning visual appeal
        - High contrast and vibrant colors perfect for advertising
        - Clean, professional composition with visual hierarchy
        - Eye-catching design optimized for social media advertising
        - Modern aesthetic suitable for digital marketing campaigns
        - Professional poster layout with balanced elements
        - Marketing-ready quality for commercial use
        """
        
        print(f"🎨 Creating new marketing image...")
        
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=enhanced_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio
            )
        )
        
        if response.generated_images:
            # Save the generated image
            generated_image = response.generated_images[0]
            filename = f"marketing_poster_{hash(prompt) % 10000}.png"
            generated_image.image.save(filename)
            print(f"✅ Marketing poster created: {filename}")
            return filename
        
        return None
        
    except Exception as e:
        print(f"❌ Error in image_creator: {str(e)}")
        return None

async def main():
    print("🎨 AI Poster & Image Generator (Async)")
    print("=" * 40)
    print("1. Edit existing image (poster_editor)")
    print("2. Create new image (image_creator)")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        image_path = input("Enter path to input image: ").strip()
        if not os.path.exists(image_path):
            print("❌ Image file not found!")
            return
        
        prompt = input("Enter editing prompt: ").strip()
        if not prompt:
            print("❌ Prompt cannot be empty!")
            return
        
        print("\n🚀 Editing image...")
        result = await poster_editor(image_path, prompt)
        
        if result:
            print(f"✅ Success! Edited poster saved as: {result}")
        else:
            print("❌ Failed to edit image")
            
    elif choice == "2":
        prompt = input("Enter image creation prompt: ").strip()
        if not prompt:
            print("❌ Prompt cannot be empty!")
            return
        
        print("\n🚀 Creating new image...")
        result = await image_creator(prompt)
        
        if result:
            print(f"✅ Success! New image saved as: {result}")
        else:
            print("❌ Failed to create image")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())