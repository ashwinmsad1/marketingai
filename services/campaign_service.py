"""
Campaign Service Layer
Handles all campaign-related business logic
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database.models import Campaign, CampaignStatus
from database.crud import CampaignCRUD
from performance_guarantees import PerformanceGuaranteeEngine
from revenue_tracking import RevenueAttributionEngine

logger = logging.getLogger(__name__)

class CampaignService:
    """Service class for campaign management"""
    
    def __init__(self):
        """Initialize campaign service with engines"""
        self.performance_engine = PerformanceGuaranteeEngine()
        self.revenue_engine = RevenueAttributionEngine()
    
    async def create_campaign(
        self, 
        db: Session,
        user_id: str,
        campaign_data: Dict[str, Any],
        campaign_type: str
    ) -> Dict[str, Any]:
        """
        Create a new campaign with proper business logic
        
        Args:
            db: Database session
            user_id: User creating the campaign
            campaign_data: Campaign details
            campaign_type: Type of campaign (viral, image, video, etc.)
            
        Returns:
            Campaign response data
        """
        try:
            # Generate campaign name
            campaign_name = campaign_data.get("name") or f"{campaign_type.title()} Campaign"
            
            # Create campaign in database
            campaign = CampaignCRUD.create_campaign(
                db,
                user_id=user_id,
                name=campaign_name,
                description=campaign_data.get("prompt", ""),
                status=CampaignStatus.ACTIVE,
                ctr=campaign_data.get("estimated_ctr", 0.0),
                industry=campaign_data.get("industry")
            )
            
            # Track campaign launch for revenue attribution
            if campaign_data.get("platform"):
                await self.revenue_engine.track_campaign_launch(
                    campaign_id=campaign.id,
                    user_id=user_id,
                    campaign_name=campaign_name,
                    creative_asset=campaign_data.get("created_file", ""),
                    platform=campaign_data.get("platform", "facebook")
                )
            
            # Create response data
            response_data = {
                "campaign_id": campaign.id,
                "user_id": campaign.user_id,
                "name": campaign.name,
                "type": campaign_type,
                "status": campaign.status.value,
                "created_at": campaign.created_at.isoformat(),
                "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else campaign.created_at.isoformat(),
                "prompt": campaign_data.get("prompt", ""),
                "created_file": campaign_data.get("created_file"),
                "spend": campaign.spend or 0.0,
                "revenue": 0.0,
                "roi": campaign.roas or 0.0,
                "ctr": campaign.ctr or 0.0,
                "performance_status": "pending"
            }
            
            logger.info(f"Campaign {campaign.id} created successfully")
            return response_data
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            raise
    
    def get_user_campaigns(self, db: Session, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get campaigns for a user with formatted response
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of campaigns to return
            
        Returns:
            List of formatted campaign data
        """
        try:
            campaigns = CampaignCRUD.get_user_campaigns(db, user_id, limit=limit)
            
            formatted_campaigns = []
            for campaign in campaigns:
                campaign_data = {
                    "campaign_id": campaign.id,
                    "user_id": campaign.user_id,
                    "name": campaign.name,
                    "type": "standard",  # Could be stored in campaign metadata
                    "status": campaign.status.value if campaign.status else "unknown",
                    "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
                    "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else "",
                    "spend": campaign.spend or 0.0,
                    "revenue": 0.0,  # Would need to calculate from conversions
                    "roi": campaign.roas or 0.0,
                    "ctr": campaign.ctr or 0.0,
                    "performance_status": "active"
                }
                formatted_campaigns.append(campaign_data)
            
            return formatted_campaigns
            
        except Exception as e:
            logger.error(f"Error getting user campaigns: {e}")
            raise
    
    async def get_campaign_with_performance(self, db: Session, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign details with performance metrics
        
        Args:
            db: Database session
            campaign_id: Campaign ID
            
        Returns:
            Campaign data with performance metrics
        """
        try:
            campaign = CampaignCRUD.get_campaign(db, campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Convert to response format
            campaign_data = {
                "campaign_id": campaign.id,
                "user_id": campaign.user_id,
                "name": campaign.name,
                "type": "standard",
                "status": campaign.status.value if campaign.status else "unknown",
                "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
                "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else "",
                "spend": campaign.spend or 0.0,
                "revenue": 0.0,
                "roi": campaign.roas or 0.0,
                "ctr": campaign.ctr or 0.0,
                "performance_status": "active"
            }
            
            # Get performance metrics
            try:
                performance_metrics = await self.performance_engine.get_campaign_performance(campaign_id)
                campaign_data["performance_metrics"] = performance_metrics
            except Exception as e:
                logger.warning(f"Could not get performance metrics: {e}")
            
            return campaign_data
            
        except Exception as e:
            logger.error(f"Error getting campaign: {e}")
            raise
    
    def delete_campaign(self, db: Session, campaign_id: str) -> bool:
        """
        Delete a campaign
        
        Args:
            db: Database session
            campaign_id: Campaign ID
            
        Returns:
            True if deleted successfully
        """
        try:
            campaign = CampaignCRUD.get_campaign(db, campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # In production, you might want to soft delete or archive instead
            db.delete(campaign)
            db.commit()
            
            logger.info(f"Campaign {campaign_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting campaign: {e}")
            db.rollback()
            raise
    
    async def monitor_campaign_performance(self, db: Session, campaign_id: str) -> Dict[str, Any]:
        """
        Monitor and potentially optimize campaign performance
        
        Args:
            db: Database session
            campaign_id: Campaign ID
            
        Returns:
            Monitoring results
        """
        try:
            campaign = CampaignCRUD.get_campaign(db, campaign_id)
            if not campaign:
                return {"error": f"Campaign {campaign_id} not found"}
            
            # Check performance and optimize if needed
            optimization_result = await self.performance_engine.auto_optimize_campaign(
                campaign_id=campaign_id,
                user_id=campaign.user_id
            )
            
            if optimization_result.get("optimized"):
                # Update campaign status in database
                CampaignCRUD.update_campaign(
                    db,
                    campaign_id, 
                    description=f"{campaign.description} [Auto-optimized: {datetime.now().isoformat()}]"
                )
                logger.info(f"Campaign {campaign_id} automatically optimized")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error monitoring campaign performance: {e}")
            return {"error": str(e)}