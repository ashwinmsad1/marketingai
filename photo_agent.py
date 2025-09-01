import asyncio
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

from secure_config_manager import get_config

class HyperrealisticPosterAgent:
    def __init__(self):
        api_key = get_config("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
    
    def encode_image(self, image_path):
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def create_poster(self, image_path, prompt, style="hyperrealistic poster"):
        """Create a hyperrealistic poster from an input image and prompt (async)"""
        try:
            # Load and encode the input image
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Enhanced prompt for poster creation
            enhanced_prompt = f"""
            Create a {style} based on the provided image with the following requirements:
            {prompt}
            
            Style specifications:
            - Hyperrealistic quality with professional poster aesthetics
            - High contrast and vibrant colors suitable for marketing
            - Clean composition with strong visual hierarchy
            - Modern typography integration if text is needed
            - Professional marketing poster layout
            - Ensure the image is suitable for social media advertising
            """
            
            # Create content with both image and text
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[
                    types.Content(parts=[
                        types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                        types.Part.from_text(text=enhanced_prompt)
                    ])
                ]
            )
            
            # Process response
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(f"Generation details: {part.text}")
                elif part.inline_data is not None:
                    poster_image = Image.open(BytesIO(part.inline_data.data))
                    filename = f"hyperrealistic_poster_{hash(prompt) % 10000}.png"
                    poster_image.save(filename)
                    print(f"Hyperrealistic poster saved as: {filename}")
                    return filename
            
            return None
            
        except Exception as e:
            print(f"Error creating poster: {str(e)}")
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

async def image_creator(prompt, style="hyperrealistic poster"):
    """
    Create a new image from scratch based on a given prompt (async)
    
    Args:
        prompt (str): Description for image creation
        style (str): Style specification (default: "hyperrealistic poster")
    
    Returns:
        str: Path to generated image file, or None if failed
    """
    try:
        api_key = get_config("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
        
        # Enhanced prompt for image creation
        enhanced_prompt = f"""
        Create a {style} with the following requirements:
        {prompt}
        
        Style specifications:
        - Hyperrealistic quality with professional poster aesthetics
        - High contrast and vibrant colors suitable for marketing
        - Clean composition with strong visual hierarchy
        - Modern typography integration if text is needed
        - Professional marketing poster layout
        - Ensure the image is suitable for social media advertising
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[enhanced_prompt],
        )
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"Generation details: {part.text}")
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                filename = f"created_image_{hash(prompt) % 10000}.png"
                image.save(filename)
                print(f"Image created and saved as: {filename}")
                return filename
        
        return None
        
    except Exception as e:
        print(f"Error in image_creator: {str(e)}")
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