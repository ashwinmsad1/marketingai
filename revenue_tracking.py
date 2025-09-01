"""
Enhanced Revenue Attribution Engine for AI Marketing Automation Platform
Using PostgreSQL database with proper CRUD operations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import uuid
import logging

from database import get_db
from database.models import Campaign, Conversion, User, Analytics, CampaignStatus, ConversionType
from database.crud import CampaignCRUD, ConversionCRUD, AnalyticsCRUD
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CampaignConversion:
    """Data structure for campaign conversions"""
    conversion_id: str
    campaign_id: str
    user_id: str
    conversion_type: str
    value: float
    timestamp: datetime
    source_platform: str
    creative_asset: str
    attribution_window: int = 7

@dataclass
class ROIMetrics:
    """ROI calculation results"""
    campaign_id: str
    total_spend: float
    total_revenue: float
    roi_percentage: float
    cost_per_conversion: float
    conversion_count: int
    lifetime_value: float

class RevenueAttributionEngine:
    """
    Complete revenue tracking and attribution system using PostgreSQL
    """
    
    def __init__(self):
        """Initialize the revenue attribution engine"""
        logger.info("Revenue Attribution Engine initialized with PostgreSQL backend")
    
    def _get_db_session(self) -> Session:
        """Get database session - in production this would use dependency injection"""
        return next(get_db())

    async def track_campaign_launch(self, campaign_id: str, user_id: str, campaign_name: str, 
                                  creative_asset: str, platform: str) -> bool:
        """Track new campaign launch using PostgreSQL"""
        try:
            # Validate input parameters
            if not all([campaign_id, user_id, campaign_name, platform]):
                raise ValueError("All required parameters must be provided")
            
            db = self._get_db_session()
            try:
                # Check if campaign already exists
                existing_campaign = CampaignCRUD.get_campaign(db, campaign_id)
                if existing_campaign:
                    # Update existing campaign
                    CampaignCRUD.update_campaign(
                        db, campaign_id, 
                        name=campaign_name,
                        description=f"Platform: {platform}, Asset: {creative_asset}"
                    )
                else:
                    # Create new campaign
                    CampaignCRUD.create_campaign(
                        db, 
                        user_id=user_id,
                        name=campaign_name,
                        description=f"Platform: {platform}, Asset: {creative_asset}",
                        status=CampaignStatus.ACTIVE
                    )
                
                logger.info(f"Campaign {campaign_id} tracked for revenue attribution")
                return True
                
            finally:
                db.close()
            
        except ValueError as e:
            logger.error(f"Validation error tracking campaign launch: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error tracking campaign launch: {e}")
            return False

    async def track_conversion(self, campaign_id: str, conversion_type: str, 
                             value: float, customer_id: Optional[str] = None) -> str:
        """Track a conversion and attribute it to a campaign using PostgreSQL"""
        try:
            # Validate input parameters
            if not campaign_id or not conversion_type or value < 0:
                raise ValueError("Invalid conversion parameters")
            
            db = self._get_db_session()
            try:
                # Get campaign details
                campaign = CampaignCRUD.get_campaign(db, campaign_id)
                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")
                
                # Convert conversion type to enum
                try:
                    conv_type = ConversionType(conversion_type.lower())
                except ValueError:
                    conv_type = ConversionType.SALE  # Default fallback
                
                # Create conversion record
                conversion = ConversionCRUD.create_conversion(
                    db,
                    user_id=campaign.user_id,
                    campaign_id=campaign_id,
                    conversion_type=conv_type,
                    value=value,
                    customer_id=customer_id,
                    platform="facebook"  # Default platform, could be passed as parameter
                )
                
                logger.info(f"Conversion tracked: {conversion_type} worth ${value} from campaign {campaign_id}")
                return conversion.id
                
            finally:
                db.close()
            
        except ValueError as e:
            logger.error(f"Validation error tracking conversion: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error tracking conversion: {e}")
            return ""

    async def update_campaign_spend(self, campaign_id: str, ad_spend: float) -> ROIMetrics:
        """Update campaign spending and calculate ROI using PostgreSQL"""
        try:
            db = self._get_db_session()
            try:
                # Update campaign spend
                campaign = CampaignCRUD.update_campaign(
                    db, campaign_id,
                    spend=ad_spend
                )
                
                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")
                
                # Get conversions for this campaign
                conversions = ConversionCRUD.get_campaign_conversions(db, campaign_id)
                
                # Calculate metrics
                total_revenue = sum(c.value for c in conversions if c.value)
                conversion_count = len(conversions)
                roi_percentage = ((total_revenue - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
                cost_per_conversion = ad_spend / conversion_count if conversion_count > 0 else 0
                
                # Create ROI metrics
                roi_metrics = ROIMetrics(
                    campaign_id=campaign_id,
                    total_spend=ad_spend,
                    total_revenue=total_revenue,
                    roi_percentage=roi_percentage,
                    cost_per_conversion=cost_per_conversion,
                    conversion_count=conversion_count,
                    lifetime_value=total_revenue  # Simplified LTV calculation
                )
                
                logger.info(f"Campaign spend updated: ${ad_spend}, ROI: {roi_percentage:.2f}%")
                return roi_metrics
                
            finally:
                db.close()
                
        except ValueError as e:
            logger.error(f"Validation error updating campaign spend: {e}")
            return self._empty_roi_metrics(campaign_id)
        except Exception as e:
            logger.error(f"Error updating campaign spend: {e}")
            return self._empty_roi_metrics(campaign_id)

    async def get_campaign_roi(self, campaign_id: str) -> ROIMetrics:
        """Calculate current ROI for a campaign"""
        try:
            db = self._get_db_session()
            try:
                campaign = CampaignCRUD.get_campaign(db, campaign_id)
                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")
                
                conversions = ConversionCRUD.get_campaign_conversions(db, campaign_id)
                
                total_revenue = sum(c.value for c in conversions if c.value)
                conversion_count = len(conversions)
                total_spend = campaign.spend or 0
                
                roi_percentage = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
                cost_per_conversion = total_spend / conversion_count if conversion_count > 0 else 0
                
                return ROIMetrics(
                    campaign_id=campaign_id,
                    total_spend=total_spend,
                    total_revenue=total_revenue,
                    roi_percentage=roi_percentage,
                    cost_per_conversion=cost_per_conversion,
                    conversion_count=conversion_count,
                    lifetime_value=total_revenue
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error calculating campaign ROI: {e}")
            return self._empty_roi_metrics(campaign_id)

    async def generate_revenue_report(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive revenue report for user"""
        try:
            db = self._get_db_session()
            try:
                # Get analytics summary
                analytics_summary = AnalyticsCRUD.get_user_analytics_summary(db, user_id, days)
                
                # Get revenue attribution
                revenue_attribution = ConversionCRUD.get_revenue_attribution(db, user_id, days)
                
                # Calculate additional metrics
                total_campaigns = len(CampaignCRUD.get_user_campaigns(db, user_id))
                
                report = {
                    "user_id": user_id,
                    "period_days": days,
                    "generated_at": datetime.now().isoformat(),
                    "overview": analytics_summary,
                    "revenue_by_campaign": revenue_attribution,
                    "total_campaigns": total_campaigns,
                    "performance_insights": {
                        "top_performing_campaign": max(revenue_attribution, key=lambda x: x['revenue'])['campaign_name'] if revenue_attribution else "",
                        "best_roi_campaign": "",  # Would need additional calculation
                        "conversion_trends": []  # Could add time-series analysis
                    }
                }
                
                logger.info(f"Revenue report generated for user {user_id}")
                return report
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error generating revenue report: {e}")
            return {
                "user_id": user_id,
                "period_days": days,
                "generated_at": datetime.now().isoformat(),
                "error": str(e)
            }

    def _empty_roi_metrics(self, campaign_id: str) -> ROIMetrics:
        """Return empty ROI metrics for error cases"""
        return ROIMetrics(
            campaign_id=campaign_id,
            total_spend=0.0,
            total_revenue=0.0,
            roi_percentage=0.0,
            cost_per_conversion=0.0,
            conversion_count=0,
            lifetime_value=0.0
        )

# Test function
async def test_revenue_engine():
    """Test revenue attribution engine functionality"""
    print("🔍 Testing Revenue Attribution Engine...")
    
    engine = RevenueAttributionEngine()
    
    # Test campaign tracking
    campaign_tracked = await engine.track_campaign_launch(
        campaign_id="test-campaign-001",
        user_id="test-user-001", 
        campaign_name="Test Campaign",
        creative_asset="test_image.jpg",
        platform="facebook"
    )
    print(f"✅ Campaign tracking: {'Success' if campaign_tracked else 'Failed'}")
    
    # Test conversion tracking
    conversion_id = await engine.track_conversion(
        campaign_id="test-campaign-001",
        conversion_type="sale",
        value=99.99,
        customer_id="customer-001"
    )
    print(f"✅ Conversion tracking: {'Success' if conversion_id else 'Failed'}")
    
    # Test ROI calculation
    roi_metrics = await engine.get_campaign_roi("test-campaign-001")
    print(f"✅ ROI calculation: Revenue=${roi_metrics.total_revenue}, ROI={roi_metrics.roi_percentage}%")
    
    print("🎉 Revenue engine tests completed!")

if __name__ == "__main__":
    asyncio.run(test_revenue_engine())