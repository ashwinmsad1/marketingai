"""
FastAPI server for AI Marketing Automation Platform
Connects React frontend to all backend systems
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
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
from viral_engine import ViralEngine
from photo_agent import PhotoAgent
from video_agent import VideoAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Marketing Automation API",
    description="Advanced AI-powered marketing automation platform",
    version="1.0.0"
)

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
viral_engine = ViralEngine()
photo_agent = PhotoAgent()
video_agent = VideoAgent()

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

class User(BaseModel):
    id: str
    email: str
    name: str
    subscription_tier: str
    industry: Optional[str] = None

class Campaign(BaseModel):
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

# Mock user data (in production, this would come from a database)
MOCK_USERS = {
    "default_user": {
        "id": "default_user",
        "name": "John Doe",
        "email": "john@example.com",
        "subscription_tier": "professional",
        "industry": "Restaurant"
    }
}

# In-memory storage (in production, use proper database)
campaigns_db = {}
media_db = {}

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
async def get_user(user_id: str):
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return MOCK_USERS[user_id]

@app.get("/api/users/{user_id}/dashboard")
async def get_user_dashboard(user_id: str):
    """Get dashboard data for user"""
    try:
        # Get campaigns for user
        user_campaigns = [c for c in campaigns_db.values() if c.get("user_id") == user_id]
        
        # Calculate summary metrics
        total_campaigns = len(user_campaigns)
        total_revenue = sum(c.get("revenue", 0) for c in user_campaigns)
        total_spend = sum(c.get("spend", 0) for c in user_campaigns)
        overall_roi = (total_revenue / total_spend * 100) if total_spend > 0 else 0
        
        dashboard_data = {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "success_summary": {
                "total_campaigns": total_campaigns,
                "total_revenue": total_revenue,
                "overall_roi": overall_roi,
                "guarantee_success_rate": 92.3
            },
            "recent_campaigns": user_campaigns[-5:] if user_campaigns else []
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Campaign Management
@app.post("/api/campaigns")
async def create_campaign(request: CampaignCreateRequest, background_tasks: BackgroundTasks):
    """Create a new marketing campaign"""
    try:
        campaign_id = str(uuid.uuid4())
        
        logger.info(f"Creating campaign: {request.type} for user {request.user_id}")
        
        # Create campaign based on type
        if request.type == "viral":
            campaign_result = await viral_engine.generate_viral_campaign(
                user_id=request.user_id,
                industry=request.industry or "general"
            )
            
        elif request.type == "industry_optimized":
            if not request.business_details:
                raise HTTPException(status_code=400, detail="Business details required for industry campaigns")
                
            campaign_result = await marketing_engine.create_industry_optimized_campaign(
                industry=request.industry or "general",
                business_details=request.business_details,
                user_id=request.user_id
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
                user_id=request.user_id
            )
            
        elif request.type == "image":
            # Generate image campaign
            image_result = await photo_agent.generate_poster_async(
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
            video_result = await video_agent.generate_video_async(
                prompt=request.prompt,
                duration=30,
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
                user_id=request.user_id
            )
        
        # Store campaign in database
        campaign_data = {
            "campaign_id": campaign_id,
            "user_id": request.user_id,
            "name": campaign_result.get("name", f"{request.type.title()} Campaign"),
            "type": request.type,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "prompt": request.prompt,
            "created_file": campaign_result.get("created_file"),
            "spend": 0.0,
            "revenue": 0.0,
            "roi": 0.0,
            "ctr": campaign_result.get("performance_metrics", {}).get("estimated_ctr", 0.0),
            "performance_status": "pending"
        }
        
        campaigns_db[campaign_id] = campaign_data
        
        # Start performance monitoring in background
        background_tasks.add_task(monitor_campaign_performance, campaign_id)
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "data": campaign_data,
            "message": f"Successfully created {request.type} campaign"
        }
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@app.get("/api/campaigns")
async def get_campaigns(user_id: Optional[str] = "default_user", limit: int = 50):
    """Get campaigns for a user"""
    try:
        user_campaigns = [
            c for c in campaigns_db.values() 
            if c.get("user_id") == user_id
        ]
        
        # Sort by creation date (newest first)
        user_campaigns.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "success": True,
            "data": user_campaigns[:limit],
            "total": len(user_campaigns)
        }
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get campaigns")

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get specific campaign details"""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    # Get performance metrics from performance engine
    try:
        performance_metrics = await performance_engine.get_campaign_performance(campaign_id)
        campaign["performance_metrics"] = performance_metrics
    except:
        pass
        
    return {"success": True, "data": campaign}

@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign"""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    del campaigns_db[campaign_id]
    return {"success": True, "message": "Campaign deleted successfully"}

# Media Generation
@app.post("/api/media/images/generate")
async def generate_image(request: ImageGenerationRequest):
    """Generate marketing images using AI"""
    try:
        logger.info(f"Generating image: {request.prompt}")
        
        # Generate multiple images if requested
        generated_images = []
        
        for i in range(request.iterations):
            result = await photo_agent.generate_poster_async(
                prompt=request.prompt,
                style=f"{request.style} marketing image, {request.aspect_ratio} aspect ratio"
            )
            
            if result.get("success") and result.get("image_path"):
                image_id = str(uuid.uuid4())
                media_entry = {
                    "id": image_id,
                    "type": "image",
                    "url": f"/uploads/{os.path.basename(result['image_path'])}",
                    "prompt": request.prompt,
                    "style": request.style,
                    "aspect_ratio": request.aspect_ratio,
                    "created_at": datetime.now().isoformat(),
                    "file_path": result["image_path"]
                }
                
                media_db[image_id] = media_entry
                generated_images.append(media_entry)
        
        if not generated_images:
            raise HTTPException(status_code=500, detail="Failed to generate any images")
            
        return {
            "success": True,
            "data": {
                "images": generated_images,
                "count": len(generated_images)
            },
            "message": f"Successfully generated {len(generated_images)} images"
        }
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")

@app.post("/api/media/videos/generate")
async def generate_video(request: VideoGenerationRequest):
    """Generate marketing videos using AI"""
    try:
        logger.info(f"Generating video: {request.prompt}")
        
        result = await video_agent.generate_video_async(
            prompt=request.prompt,
            duration=request.duration,
            style=f"{request.style} marketing video, {request.aspect_ratio} format"
        )
        
        if not result.get("success") or not result.get("video_path"):
            raise HTTPException(status_code=500, detail="Failed to generate video")
        
        video_id = str(uuid.uuid4())
        media_entry = {
            "id": video_id,
            "type": "video",
            "url": f"/uploads/{os.path.basename(result['video_path'])}",
            "thumbnail": result.get("thumbnail_path", ""),
            "prompt": request.prompt,
            "style": request.style,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "created_at": datetime.now().isoformat(),
            "file_path": result["video_path"]
        }
        
        media_db[video_id] = media_entry
        
        return {
            "success": True,
            "data": media_entry,
            "message": "Successfully generated marketing video"
        }
        
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")

@app.get("/api/media")
async def get_media(user_id: Optional[str] = "default_user", media_type: Optional[str] = None):
    """Get generated media for user"""
    try:
        user_media = list(media_db.values())
        
        if media_type:
            user_media = [m for m in user_media if m.get("type") == media_type]
        
        # Sort by creation date (newest first)
        user_media.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
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
async def track_conversion(request: ConversionTrackingRequest):
    """Track a conversion for revenue attribution"""
    try:
        conversion_id = await revenue_engine.track_conversion(
            campaign_id=request.campaign_id,
            conversion_type=request.conversion_type,
            value=request.value,
            customer_id=request.customer_id
        )
        
        # Update campaign metrics
        if request.campaign_id in campaigns_db:
            campaign = campaigns_db[request.campaign_id]
            campaign["revenue"] = campaign.get("revenue", 0) + request.value
            campaign["conversions"] = campaign.get("conversions", 0) + 1
            
            # Recalculate ROI
            spend = campaign.get("spend", 0)
            if spend > 0:
                campaign["roi"] = (campaign["revenue"] / spend) * 100
        
        return {
            "success": True,
            "conversion_id": conversion_id,
            "message": "Conversion tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to track conversion")

@app.get("/api/analytics/dashboard/{user_id}")
async def get_analytics_dashboard(user_id: str):
    """Get analytics dashboard data"""
    try:
        user_campaigns = [c for c in campaigns_db.values() if c.get("user_id") == user_id]
        
        # Calculate analytics
        total_campaigns = len(user_campaigns)
        total_revenue = sum(c.get("revenue", 0) for c in user_campaigns)
        total_spend = sum(c.get("spend", 0) for c in user_campaigns)
        total_conversions = sum(c.get("conversions", 0) for c in user_campaigns)
        overall_roi = (total_revenue / total_spend * 100) if total_spend > 0 else 0
        avg_ctr = sum(c.get("ctr", 0) for c in user_campaigns) / total_campaigns if total_campaigns > 0 else 0
        
        analytics_data = {
            "overview": {
                "total_revenue": total_revenue,
                "total_spent": total_spend,
                "overall_roi": overall_roi,
                "total_conversions": total_conversions,
                "avg_ctr": avg_ctr,
                "top_performing_campaign": max(user_campaigns, key=lambda c: c.get("revenue", 0))["name"] if user_campaigns else ""
            },
            "revenue_by_campaign": [
                {
                    "name": c["name"],
                    "revenue": c.get("revenue", 0),
                    "spend": c.get("spend", 0),
                    "roi": c.get("roi", 0)
                }
                for c in sorted(user_campaigns, key=lambda x: x.get("revenue", 0), reverse=True)[:10]
            ],
            "performance_trends": [],  # Would calculate time-series data in production
            "campaign_types": {}  # Would group by campaign types
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
    """Monitor campaign performance and optimize if needed"""
    try:
        await asyncio.sleep(300)  # Wait 5 minutes before first check
        
        # Check performance and optimize if needed
        optimization_result = await performance_engine.auto_optimize_campaign(
            campaign_id=campaign_id,
            user_id=campaigns_db[campaign_id]["user_id"]
        )
        
        if optimization_result.get("optimized"):
            logger.info(f"Campaign {campaign_id} automatically optimized")
            
            # Update campaign status
            if campaign_id in campaigns_db:
                campaigns_db[campaign_id]["performance_status"] = "optimized"
                campaigns_db[campaign_id]["updated_at"] = datetime.now().isoformat()
                
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