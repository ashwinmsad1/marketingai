"""
FastAPI server for AI Marketing Automation Platform
Connects React frontend to all backend systems
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
import asyncio
import uuid
import os
import json
import logging
from datetime import datetime, timedelta
import aiofiles
import base64
from pathlib import Path

# Import our enhanced backend systems
from marketing_automation import EnhancedMarketingAutomationEngine
from revenue_tracking import RevenueAttributionEngine
from performance_guarantees import PerformanceGuaranteeEngine
from industry_templates import IndustryTemplateEngine
from competitor_analyzer import CompetitorAnalyzer
from viral_engine import ViralContentEngine
from photo_agent import image_creator, poster_editor
from video_agent import video_from_prompt, video_from_image

# Import service layer
from services import CampaignService, MediaService, AnalyticsService, UserService

# Import database
from database import get_db, init_db, check_db_connection, SessionLocal
from database.models import (
    User, Subscription, Campaign, AIContent, MetaAccount,
    Analytics, Conversion, UsageTracking, SubscriptionTier,
    CampaignStatus, ContentType, ConversionType
)
from database.crud import UserCRUD, SubscriptionCRUD, CampaignCRUD, AIContentCRUD, ConversionCRUD, AnalyticsCRUD

# Import authentication
from auth import JWTHandler, PasswordHandler, get_current_user, get_current_active_user
from auth.models import (
    UserRegister, UserLogin, Token, AuthResponse, MessageResponse,
    PasswordReset, PasswordResetConfirm, PasswordChange, UserProfile,
    UserUpdate, EmailVerification
)
from auth.email_handler import EmailHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Marketing Automation API",
    description="Advanced AI-powered marketing automation platform with PostgreSQL backend",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and tables on startup"""
    logger.info("Starting up AI Marketing Automation API...")
    
    # Check database connection
    if not check_db_connection():
        logger.error("Failed to connect to database")
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise HTTPException(status_code=500, detail="Database initialization failed")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files for serving generated media
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize backend engines
marketing_engine = EnhancedMarketingAutomationEngine()
revenue_engine = RevenueAttributionEngine()
performance_engine = PerformanceGuaranteeEngine()
template_engine = IndustryTemplateEngine()
competitor_analyzer = CompetitorAnalyzer()
viral_engine = ViralContentEngine()

# Initialize service layer
campaign_service = CampaignService()
media_service = MediaService()
analytics_service = AnalyticsService()
user_service = UserService()

# Include authentication routes
from auth.routes import router as auth_router
app.include_router(auth_router)

# Include Meta integration routes
from auth.meta_routes import router as meta_router
app.include_router(meta_router)

# Pydantic models for API requests/responses
class CampaignCreateRequest(BaseModel):
    type: str = Field(..., description="Campaign type: viral, industry_optimized, competitor_beating, image, video")
    prompt: str = Field(..., description="Campaign description or prompt")
    caption: Optional[str] = Field(None, description="Caption for the campaign")
    style: Optional[str] = Field("photorealistic", description="Visual style")
    industry: Optional[str] = Field(None, description="Industry category")
    business_details: Optional[Dict[str, Any]] = Field(None, description="Business information")
    competitor_url: Optional[str] = Field(None, description="Competitor URL for analysis")
    competitor_name: Optional[str] = Field(None, description="Competitor name")
    user_id: Optional[str] = Field("default_user", description="User identifier")

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Image description")
    style: str = Field("photorealistic", description="Visual style")
    aspect_ratio: str = Field("16:9", description="Image aspect ratio")
    quality: str = Field("high", description="Image quality")
    creativity: int = Field(50, description="Creativity level 0-100")
    iterations: int = Field(1, description="Number of images to generate")

class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Video description")
    style: str = Field("commercial", description="Video style")
    duration: int = Field(15, description="Video duration in seconds")
    aspect_ratio: str = Field("16:9", description="Video aspect ratio")
    motion: str = Field("dynamic", description="Camera motion style")
    music_style: str = Field("upbeat", description="Music style")
    text_overlay: bool = Field(True, description="Include text overlays")
    brand_colors: str = Field("#3B82F6", description="Brand color hex code")

class ConversionTrackingRequest(BaseModel):
    campaign_id: str
    conversion_type: str = Field(..., description="Type of conversion: lead, sale, signup, etc.")
    value: float = Field(..., description="Monetary value of conversion")
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Remove duplicate model definitions - using auth models instead

class CampaignResponse(BaseModel):
    campaign_id: str
    user_id: str
    name: str
    type: str
    status: str
    created_at: str
    updated_at: str
    spend: Optional[float] = None
    roi: Optional[float] = None
    ctr: Optional[float] = None
    performance_status: Optional[str] = None
    created_file: Optional[str] = None
    prompt: Optional[str] = None

# Database storage - using PostgreSQL via CRUD operations
# No more in-memory storage needed

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Marketing Automation API",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Campaign Creation",
            "Image Generation", 
            "Video Generation",
            "Performance Tracking",
            "Revenue Attribution",
            "Industry Templates",
            "Competitor Analysis",
            "Viral Content Engine"
        ]
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "marketing_engine": "active",
            "photo_agent": "active",
            "video_agent": "active",
            "revenue_tracking": "active",
            "performance_guarantees": "active"
        }
    }

# User Management
@app.get("/api/users/{user_id}")
async def get_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID using user service - requires authentication"""
    # Users can only access their own profile
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        return user_service.get_user_profile(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@app.get("/api/users/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard data for user using analytics service - requires authentication"""
    # Users can only access their own dashboard
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        return analytics_service.get_user_dashboard_data(db, user_id)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Campaign Management
@app.post("/api/campaigns")
async def create_campaign(
    request: CampaignCreateRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new marketing campaign - requires authentication"""
    try:
        campaign_id = str(uuid.uuid4())
        
        # Use authenticated user ID instead of request user ID
        user_id = current_user.id
        logger.info(f"Creating campaign: {request.type} for user {user_id}")
        
        # Create campaign based on type
        if request.type == "viral":
            campaign_result = await viral_engine.generate_viral_campaign(
                user_id=user_id,
                industry=request.industry or "general"
            )
            
        elif request.type == "industry_optimized":
            if not request.business_details:
                raise HTTPException(status_code=400, detail="Business details required for industry campaigns")
                
            campaign_result = await marketing_engine.create_industry_optimized_campaign(
                industry=request.industry or "general",
                business_details=request.business_details,
                user_id=user_id
            )
            
        elif request.type == "competitor_beating":
            if not request.competitor_url:
                raise HTTPException(status_code=400, detail="Competitor URL required")
                
            # Analyze competitor first
            competitor_id = await competitor_analyzer.analyze_competitor_content(
                url=request.competitor_url,
                content_type="webpage"
            )
            
            campaign_result = await competitor_analyzer.generate_competitive_campaign(
                competitor_content_id=competitor_id,
                user_id=user_id
            )
            
        elif request.type == "image":
            # Generate image campaign
            image_result = await image_creator(
                prompt=request.prompt,
                style=request.style or "professional marketing poster"
            )
            
            campaign_result = {
                "campaign_id": campaign_id,
                "name": f"Image Campaign - {request.prompt[:50]}...",
                "type": "image",
                "status": "active",
                "created_file": image_result.get("image_path"),
                "prompt": request.prompt,
                "performance_metrics": {
                    "estimated_ctr": 3.5,
                    "estimated_engagement": 4.2
                }
            }
            
        elif request.type == "video":
            # Generate video campaign
            video_result = await video_from_prompt(
                prompt=request.prompt,
                style="marketing commercial"
            )
            
            campaign_result = {
                "campaign_id": campaign_id,
                "name": f"Video Campaign - {request.prompt[:50]}...",
                "type": "video", 
                "status": "active",
                "created_file": video_result.get("video_path"),
                "prompt": request.prompt,
                "performance_metrics": {
                    "estimated_ctr": 4.8,
                    "estimated_engagement": 6.2
                }
            }
            
        else:
            # Default campaign creation
            campaign_result = await marketing_engine.create_campaign(
                prompt=request.prompt,
                campaign_type=request.type,
                user_id=user_id
            )
        
        # Store campaign using campaign service with proper session handling
        campaign_name = campaign_result.get("name", f"{request.type.title()} Campaign")
        
        # Use campaign service to create campaign with proper database handling
        campaign_data_input = {
            "name": campaign_name,
            "prompt": request.prompt,
            "created_file": campaign_result.get("created_file"),
            "estimated_ctr": campaign_result.get("performance_metrics", {}).get("estimated_ctr", 0.0),
            "industry": request.industry
        }
        
        # Create database session manually for this specific operation
        db = SessionLocal()
        try:
            campaign_response_data = await campaign_service.create_campaign(
                db,
                user_id=user_id,
                campaign_data=campaign_data_input,
                campaign_type=request.type
            )
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        
        campaign_data = campaign_response_data
        
        # Start performance monitoring in background
        background_tasks.add_task(monitor_campaign_performance, campaign_data["campaign_id"])
        
        return {
            "success": True,
            "campaign_id": campaign_data["campaign_id"],
            "data": campaign_data,
            "message": f"Successfully created {request.type} campaign"
        }
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@app.get("/api/campaigns")
async def get_campaigns(
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get campaigns for authenticated user from database"""
    try:
        # Use campaign service to get campaigns
        user_campaigns = campaign_service.get_user_campaigns(db, current_user.id, limit=limit)
        
        return {
            "success": True,
            "data": user_campaigns,
            "total": len(user_campaigns)
        }
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get campaigns")

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific campaign details from database - requires authentication"""
    try:
        # Use campaign service to get campaign with performance metrics and access control
        campaign_data = await campaign_service.get_campaign_with_performance(db, campaign_id)
        
        # Verify user has access to this campaign
        if campaign_data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"success": True, "data": campaign_data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a campaign from database - requires authentication"""
    try:
        # First check if campaign exists and user has access
        campaign = CampaignCRUD.get_campaign(db, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Users can only delete their own campaigns
        if campaign.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Use campaign service to delete campaign
        success = campaign_service.delete_campaign(db, campaign_id)
        if success:
            return {"success": True, "message": "Campaign deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete campaign")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete campaign")

# Media Generation
@app.post("/api/media/images/generate")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate marketing images using AI - requires authentication"""
    try:
        logger.info(f"Generating image: {request.prompt}")
        
        # Create database session manually for this operation
        db = SessionLocal()
        try:
            # Use media service to generate images
            generated_images = await media_service.generate_images(
                db,
                user_id=current_user.id,
                prompt=request.prompt,
                style=request.style,
                aspect_ratio=request.aspect_ratio,
                iterations=request.iterations
            )
            
            return {
                "success": True,
                "data": {
                    "images": generated_images,
                    "count": len(generated_images)
                },
                "message": f"Successfully generated {len(generated_images)} images"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")

@app.post("/api/media/videos/generate")
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate marketing videos using AI - requires authentication"""
    try:
        logger.info(f"Generating video: {request.prompt}")
        
        # Create database session manually for this operation
        db = SessionLocal()
        try:
            # Use media service to generate video
            media_entry = await media_service.generate_video(
                db,
                user_id=current_user.id,
                prompt=request.prompt,
                style=request.style,
                duration=request.duration,
                aspect_ratio=request.aspect_ratio
            )
            
            return {
                "success": True,
                "data": media_entry,
                "message": "Successfully generated marketing video"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")

@app.get("/api/media")
async def get_media(
    media_type: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get generated media for authenticated user from database"""
    try:
        # Convert media_type string to ContentType enum
        content_type = None
        if media_type:
            try:
                content_type = ContentType(media_type.lower())
            except ValueError:
                pass
        
        # Get authenticated user's AI-generated content from database
        ai_content_list = AIContentCRUD.get_user_content(db, current_user.id, content_type=content_type, limit=100)
        
        # Convert to API response format
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
        
        return {
            "success": True,
            "data": user_media,
            "total": len(user_media)
        }
        
    except Exception as e:
        logger.error(f"Error getting media: {e}")
        raise HTTPException(status_code=500, detail="Failed to get media")

# Performance Tracking
@app.post("/api/tracking/conversion")
async def track_conversion(request: ConversionTrackingRequest, db: Session = Depends(get_db)):
    """Track a conversion for revenue attribution using database"""
    try:
        # Use revenue engine to track conversion (now uses PostgreSQL)
        conversion_id = await revenue_engine.track_conversion(
            campaign_id=request.campaign_id,
            conversion_type=request.conversion_type,
            value=request.value,
            customer_id=request.customer_id
        )
        
        # Update campaign performance metrics in database
        campaign = CampaignCRUD.get_campaign(db, request.campaign_id)
        if campaign:
            # Get all conversions for this campaign to calculate totals
            conversions = ConversionCRUD.get_campaign_conversions(db, request.campaign_id)
            total_revenue = sum(c.value for c in conversions if c.value)
            conversion_count = len(conversions)
            
            # Update campaign with new metrics
            CampaignCRUD.update_campaign_performance(
                db, 
                request.campaign_id,
                {"conversions": conversion_count}
            )
            
            # Recalculate ROAS (Return on Ad Spend)
            if campaign.spend and campaign.spend > 0:
                roas = total_revenue / campaign.spend
                CampaignCRUD.update_campaign(db, request.campaign_id, roas=roas)
        
        return {
            "success": True,
            "conversion_id": conversion_id,
            "message": "Conversion tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to track conversion")

@app.get("/api/analytics/dashboard/{user_id}")
async def get_analytics_dashboard(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get analytics dashboard data from database - requires authentication"""
    # Users can only access their own analytics
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get analytics summary from database
        analytics_summary = AnalyticsCRUD.get_user_analytics_summary(db, user_id, days=30)
        
        # Get campaigns for additional calculations
        user_campaigns = CampaignCRUD.get_user_campaigns(db, user_id, limit=100)
        
        # Get revenue attribution data
        revenue_attribution = ConversionCRUD.get_revenue_attribution(db, user_id, days=30)
        
        # Calculate additional metrics
        total_campaigns = len(user_campaigns)
        total_revenue = analytics_summary.get('revenue', 0)
        total_spend = analytics_summary.get('spend', 0)
        total_conversions = analytics_summary.get('conversions', 0)
        overall_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
        avg_ctr = analytics_summary.get('ctr', 0)
        
        # Find top performing campaign
        top_campaign = ""
        if revenue_attribution:
            top_campaign = max(revenue_attribution, key=lambda x: x['revenue'])['campaign_name']
        
        analytics_data = {
            "overview": {
                "total_revenue": total_revenue,
                "total_spent": total_spend,
                "overall_roi": overall_roi,
                "total_conversions": total_conversions,
                "avg_ctr": avg_ctr,
                "top_performing_campaign": top_campaign
            },
            "revenue_by_campaign": revenue_attribution[:10],  # Top 10 campaigns
            "performance_trends": [],  # Would implement time-series analysis
            "campaign_types": {
                "total_campaigns": total_campaigns,
                "active_campaigns": len([c for c in user_campaigns if c.status == CampaignStatus.ACTIVE])
            }
        }
        
        return {"success": True, "data": analytics_data}
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# Industry Templates
@app.get("/api/templates/industries")
async def get_industry_templates():
    """Get available industry templates"""
    try:
        templates = await template_engine.get_all_templates()
        return {"success": True, "data": templates}
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

@app.get("/api/templates/industries/{industry}")
async def get_industry_template(industry: str):
    """Get specific industry template"""
    try:
        template = await template_engine.get_template_by_industry(industry)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"success": True, "data": template}
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template")

# Viral Opportunities
@app.get("/api/viral/opportunities")
async def get_viral_opportunities():
    """Get current viral opportunities"""
    try:
        opportunities = await viral_engine.get_viral_opportunities()
        return {"success": True, "data": opportunities}
    except Exception as e:
        logger.error(f"Error getting viral opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get viral opportunities")

# Background task for campaign monitoring
async def monitor_campaign_performance(campaign_id: str):
    """Monitor campaign performance and optimize if needed using database"""
    try:
        await asyncio.sleep(300)  # Wait 5 minutes before first check
        
        # Get campaign from database with proper session management
        db = SessionLocal()
        try:
            campaign = CampaignCRUD.get_campaign(db, campaign_id)
            if not campaign:
                logger.warning(f"Campaign {campaign_id} not found for monitoring")
                return
            
            # Check performance and optimize if needed
            optimization_result = await performance_engine.auto_optimize_campaign(
                campaign_id=campaign_id,
                user_id=campaign.user_id
            )
            
            if optimization_result.get("optimized"):
                logger.info(f"Campaign {campaign_id} automatically optimized")
                
                # Update campaign status in database
                CampaignCRUD.update_campaign(
                    db,
                    campaign_id, 
                    description=f"{campaign.description} [Auto-optimized: {datetime.now().isoformat()}]"
                )
        except Exception as e:
            db.rollback()
            logger.error(f"Error in campaign monitoring database operation: {e}")
        finally:
            db.close()
                
    except Exception as e:
        logger.error(f"Error monitoring campaign {campaign_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    logger.info("Starting AI Marketing Automation API Server")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )