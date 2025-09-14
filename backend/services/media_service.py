"""
Media Service Layer
Handles AI content generation and management
"""

import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import AIContent, ContentType
from backend.database.crud import AIContentCRUD
from backend.agents.photo_agent import image_creator
from backend.agents.video_agent import video_from_prompt

logger = logging.getLogger(__name__)

class MediaService:
    """Service class for media generation and management"""
    
    def __init__(self):
        """Initialize media service"""
        pass
    
    async def generate_images(
        self, 
        db: Session,
        user_id: str,
        prompt: str,
        style: str = "photorealistic",
        aspect_ratio: str = "16:9",
        iterations: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generate AI images and store in database
        
        Args:
            db: Database session
            user_id: User requesting generation
            prompt: Image description
            style: Visual style
            aspect_ratio: Image aspect ratio
            iterations: Number of images to generate
            
        Returns:
            List of generated image data
        """
        try:
            generated_images = []
            
            for i in range(iterations):
                # Generate image using photo agent
                image_path = await image_creator(
                    prompt=prompt,
                    style=f"{style} marketing image",
                    aspect_ratio=aspect_ratio
                )
                
                if image_path:
                    # Store in database
                    ai_content = AIContentCRUD.create_content(
                        db,
                        user_id=user_id,
                        content_type=ContentType.IMAGE,
                        prompt=prompt,
                        style=style,
                        file_path=image_path,
                        file_url=f"/uploads/{os.path.basename(image_path)}",
                        aspect_ratio=aspect_ratio
                    )
                    
                    # Format response
                    media_entry = {
                        "id": ai_content.id,
                        "type": "image",
                        "url": ai_content.file_url,
                        "prompt": ai_content.prompt,
                        "style": ai_content.style,
                        "aspect_ratio": ai_content.aspect_ratio,
                        "created_at": ai_content.created_at.isoformat(),
                        "file_path": ai_content.file_path
                    }
                    
                    generated_images.append(media_entry)
            
            logger.info(f"Generated {len(generated_images)} images for user {user_id}")
            return generated_images
            
        except Exception as e:
            logger.error(f"Error generating images: {e}")
            raise
    
    async def generate_video(
        self,
        db: Session,
        user_id: str,
        prompt: str,
        style: str = "commercial",
        duration: int = 15,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Generate AI video and store in database
        
        Args:
            db: Database session
            user_id: User requesting generation
            prompt: Video description
            style: Video style
            duration: Video duration in seconds
            aspect_ratio: Video aspect ratio
            
        Returns:
            Generated video data
        """
        try:
            # Generate video using video agent
            video_path = await video_from_prompt(
                prompt=prompt,
                style=f"{style} marketing video",
                aspect_ratio=aspect_ratio
            )
            
            if not video_path:
                raise ValueError("Failed to generate video")
            
            # Store in database
            ai_content = AIContentCRUD.create_content(
                db,
                user_id=user_id,
                content_type=ContentType.VIDEO,
                prompt=prompt,
                style=style,
                file_path=video_path,
                file_url=f"/uploads/{os.path.basename(video_path)}",
                duration=duration,
                aspect_ratio=aspect_ratio
            )
            
            # Format response
            media_entry = {
                "id": ai_content.id,
                "type": "video",
                "url": ai_content.file_url,
                "thumbnail": "",  # No thumbnail for now
                "prompt": ai_content.prompt,
                "style": ai_content.style,
                "duration": ai_content.duration,
                "aspect_ratio": ai_content.aspect_ratio,
                "created_at": ai_content.created_at.isoformat(),
                "file_path": ai_content.file_path
            }
            
            logger.info(f"Generated video for user {user_id}")
            return media_entry
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise
    
    def get_user_media(
        self,
        db: Session,
        user_id: str,
        media_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get user's generated media from database
        
        Args:
            db: Database session
            user_id: User ID
            media_type: Filter by media type (image, video)
            limit: Maximum number of items
            
        Returns:
            List of media items
        """
        try:
            # Convert media_type string to ContentType enum
            content_type = None
            if media_type:
                try:
                    content_type = ContentType(media_type.lower())
                except ValueError:
                    pass
            
            # Get content from database
            ai_content_list = AIContentCRUD.get_user_content(
                db, user_id, content_type=content_type, limit=limit
            )
            
            # Format response
            user_media = []
            for content in ai_content_list:
                media_entry = {
                    "id": content.id,
                    "type": content.content_type.value,
                    "url": content.file_url or f"/uploads/{os.path.basename(content.file_path or '')}",
                    "prompt": content.prompt,
                    "style": content.style,
                    "created_at": content.created_at.isoformat(),
                    "file_path": content.file_path
                }
                
                # Add type-specific fields
                if content.content_type == ContentType.VIDEO:
                    media_entry["duration"] = content.duration
                if content.aspect_ratio:
                    media_entry["aspect_ratio"] = content.aspect_ratio
                    
                user_media.append(media_entry)
            
            logger.info(f"Retrieved {len(user_media)} media items for user {user_id}")
            return user_media
            
        except Exception as e:
            logger.error(f"Error getting user media: {e}")
            raise
    
    def update_content_usage(self, db: Session, content_id: str) -> bool:
        """
        Increment usage count for content
        
        Args:
            db: Database session
            content_id: Content ID
            
        Returns:
            True if updated successfully
        """
        try:
            content = AIContentCRUD.update_content_usage(db, content_id)
            return content is not None
            
        except Exception as e:
            logger.error(f"Error updating content usage: {e}")
            return False