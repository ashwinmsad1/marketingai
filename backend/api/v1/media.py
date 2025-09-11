"""
Media generation API endpoints with tier enforcement
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import Any
import logging

from backend.app.dependencies import get_db, get_current_verified_user
from backend.database.models import User
from backend.agents.photo_agent import image_creator
from backend.agents.video_agent import video_from_prompt, video_from_image
from backend.services import MediaService
from backend.core.tier_enforcement import (
    ai_generation_guard,
    TierEnforcementError
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
media_service = MediaService()


@router.post("/images/generate")
@ai_generation_guard("image")
async def generate_image(
    image_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    http_request: Request = None
) -> Any:
    """Generate AI image with tier enforcement"""
    try:
        # Set user context for tier enforcement
        if http_request:
            http_request.state.user_id = str(current_user.id)
            http_request.state.user_tier = getattr(current_user, 'subscription_tier', 'basic')
        prompt = image_data.get("prompt", "")
        style = image_data.get("style", "hyperrealistic poster")
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt is required"
            )
        
        # Generate image
        image_url = await image_creator(prompt, style)
        
        if image_url:
            # Save to database
            media_record = media_service.create_media_record(
                db=db,
                user_id=current_user.id,
                media_type="image",
                prompt=prompt,
                media_url=image_url,
                metadata={"style": style}
            )
            
            return {
                "success": True,
                "data": {
                    "image_url": image_url,
                    "media_id": media_record.id,
                    "prompt": prompt,
                    "style": style
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate image"
            )
            
    except TierEnforcementError as e:
        logger.warning(f"AI generation tier limit exceeded for user {current_user.id}: {e.detail}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "tier_limit_exceeded",
                "message": e.detail,
                "current_tier": e.current_tier,
                "suggested_tier": e.suggested_tier,
                "usage_info": e.usage_info,
                "upgrade_url": f"/subscription/upgrade/{e.suggested_tier}" if e.suggested_tier else None
            }
        )
            
    except Exception as e:
        logger.error(f"Image generation failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )


@router.post("/videos/generate")
@ai_generation_guard("video")
async def generate_video(
    video_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    http_request: Request = None
) -> Any:
    """Generate AI video with tier enforcement"""
    try:
        # Set user context for tier enforcement
        if http_request:
            http_request.state.user_id = str(current_user.id)
            http_request.state.user_tier = getattr(current_user, 'subscription_tier', 'basic')
        prompt = video_data.get("prompt", "")
        style = video_data.get("style", "cinematic")
        aspect_ratio = video_data.get("aspect_ratio", "16:9")
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt is required"
            )
        
        # Enhance prompt with user context if provided
        if video_data.get("business_description"):
            enhanced_prompt = f"{prompt}. Business context: {video_data['business_description']}"
            if video_data.get("target_audience_description"):
                enhanced_prompt += f" Target audience: {video_data['target_audience_description']}"
            if video_data.get("unique_value_proposition"):
                enhanced_prompt += f" Unique value: {video_data['unique_value_proposition']}"
        else:
            enhanced_prompt = prompt
        
        # Generate video
        video_filename = await video_from_prompt(
            enhanced_prompt, 
            style=style, 
            aspect_ratio=aspect_ratio
        )
        
        if video_filename:
            # Save to database
            media_record = media_service.create_media_record(
                db=db,
                user_id=current_user.id,
                media_type="video",
                prompt=enhanced_prompt,
                media_url=f"/uploads/{video_filename}",
                metadata={
                    "style": style,
                    "aspect_ratio": aspect_ratio,
                    "duration": "8 seconds",
                    "original_prompt": prompt
                }
            )
            
            return {
                "success": True,
                "data": {
                    "video_url": f"/uploads/{video_filename}",
                    "media_id": media_record.id,
                    "prompt": enhanced_prompt,
                    "style": style,
                    "aspect_ratio": aspect_ratio,
                    "duration": "8 seconds"
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate video"
            )
            
    except TierEnforcementError as e:
        logger.warning(f"AI generation tier limit exceeded for user {current_user.id}: {e.detail}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "tier_limit_exceeded",
                "message": e.detail,
                "current_tier": e.current_tier,
                "suggested_tier": e.suggested_tier,
                "usage_info": e.usage_info,
                "upgrade_url": f"/subscription/upgrade/{e.suggested_tier}" if e.suggested_tier else None
            }
        )
            
    except Exception as e:
        logger.error(f"Video generation failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}"
        )


@router.post("/videos/from-image")
async def generate_video_from_image(
    image: UploadFile = File(...),
    prompt: str = "",
    style: str = "cinematic",
    aspect_ratio: str = "16:9",
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate video from uploaded image"""
    try:
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Animation prompt is required"
            )
        
        # Save uploaded image temporarily
        image_content = await image.read()
        temp_image_path = f"temp_{current_user.id}_{image.filename}"
        
        with open(temp_image_path, "wb") as f:
            f.write(image_content)
        
        # Generate video from image
        video_filename = await video_from_image(
            temp_image_path, 
            prompt, 
            style=style, 
            aspect_ratio=aspect_ratio
        )
        
        # Clean up temp file
        import os
        os.remove(temp_image_path)
        
        if video_filename:
            # Save to database
            media_record = media_service.create_media_record(
                db=db,
                user_id=current_user.id,
                media_type="video",
                prompt=prompt,
                media_url=f"/uploads/{video_filename}",
                metadata={
                    "style": style,
                    "aspect_ratio": aspect_ratio,
                    "source": "image_upload",
                    "source_filename": image.filename
                }
            )
            
            return {
                "success": True,
                "data": {
                    "video_url": f"/uploads/{video_filename}",
                    "media_id": media_record.id,
                    "prompt": prompt,
                    "style": style,
                    "aspect_ratio": aspect_ratio
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate video from image"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video from image generation failed: {str(e)}"
        )


@router.get("/")
async def get_user_media(
    media_type: str = None,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's media files"""
    media_files = media_service.get_user_media(db, current_user.id, media_type)
    return {"success": True, "data": media_files}