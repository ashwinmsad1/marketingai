"""
Database CRUD operations for AI Marketing Automation Platform
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from .models import (
    User, Subscription, Campaign, AIContent, MetaAccount,
    Analytics, Conversion, UsageTracking, SubscriptionTier,
    CampaignStatus, ContentType, ConversionType
)

# User Operations
class UserCRUD:
    @staticmethod
    def create_user(db: Session, email: str, **kwargs) -> User:
        """Create a new user"""
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user_id: str, **kwargs) -> Optional[User]:
        """Update user information"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user

# Subscription Operations
class SubscriptionCRUD:
    @staticmethod
    def create_subscription(db: Session, user_id: str, tier: SubscriptionTier, **kwargs) -> Subscription:
        """Create a new subscription"""
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tier=tier,
            **kwargs
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def get_active_subscription(db: Session, user_id: str) -> Optional[Subscription]:
        """Get user's active subscription"""
        return db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
        ).first()
    
    @staticmethod
    def update_subscription(db: Session, subscription_id: str, **kwargs) -> Optional[Subscription]:
        """Update subscription"""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if subscription:
            for key, value in kwargs.items():
                setattr(subscription, key, value)
            subscription.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(subscription)
        return subscription

# Campaign Operations
class CampaignCRUD:
    @staticmethod
    def create_campaign(db: Session, user_id: str, name: str, **kwargs) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            **kwargs
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign
    
    @staticmethod
    def get_campaign(db: Session, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID"""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    @staticmethod
    def get_user_campaigns(db: Session, user_id: str, limit: int = 50, offset: int = 0) -> List[Campaign]:
        """Get user's campaigns"""
        return db.query(Campaign).filter(
            Campaign.user_id == user_id
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_campaign(db: Session, campaign_id: str, **kwargs) -> Optional[Campaign]:
        """Update campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            for key, value in kwargs.items():
                setattr(campaign, key, value)
            campaign.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(campaign)
        return campaign
    
    @staticmethod
    def update_campaign_performance(db: Session, campaign_id: str, metrics: Dict[str, Any]) -> Optional[Campaign]:
        """Update campaign performance metrics"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            # Update performance fields
            campaign.impressions = metrics.get('impressions', campaign.impressions)
            campaign.clicks = metrics.get('clicks', campaign.clicks)
            campaign.spend = metrics.get('spend', campaign.spend)
            campaign.conversions = metrics.get('conversions', campaign.conversions)
            
            # Calculate derived metrics
            if campaign.impressions > 0:
                campaign.ctr = (campaign.clicks / campaign.impressions) * 100
            if campaign.clicks > 0:
                campaign.cpc = campaign.spend / campaign.clicks
            if campaign.impressions > 0:
                campaign.cpm = (campaign.spend / campaign.impressions) * 1000
            
            campaign.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(campaign)
        return campaign

# AI Content Operations
class AIContentCRUD:
    @staticmethod
    def create_content(db: Session, user_id: str, content_type: ContentType, prompt: str, **kwargs) -> AIContent:
        """Create AI-generated content record"""
        content = AIContent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content_type=content_type,
            prompt=prompt,
            **kwargs
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        return content
    
    @staticmethod
    def get_user_content(db: Session, user_id: str, content_type: Optional[ContentType] = None, limit: int = 50) -> List[AIContent]:
        """Get user's AI-generated content"""
        query = db.query(AIContent).filter(AIContent.user_id == user_id)
        if content_type:
            query = query.filter(AIContent.content_type == content_type)
        return query.order_by(AIContent.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def update_content_usage(db: Session, content_id: str) -> Optional[AIContent]:
        """Increment content usage count"""
        content = db.query(AIContent).filter(AIContent.id == content_id).first()
        if content:
            content.usage_count += 1
            db.commit()
            db.refresh(content)
        return content

# Usage Tracking Operations
class UsageTrackingCRUD:
    @staticmethod
    def get_current_usage(db: Session, user_id: str) -> Optional[UsageTracking]:
        """Get current billing period usage"""
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return db.query(UsageTracking).filter(
            and_(
                UsageTracking.user_id == user_id,
                UsageTracking.period_start >= start_of_month
            )
        ).first()
    
    @staticmethod
    def create_or_update_usage(db: Session, user_id: str, **increments) -> UsageTracking:
        """Create or update usage tracking"""
        usage = UsageTrackingCRUD.get_current_usage(db, user_id)
        
        if not usage:
            now = datetime.utcnow()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (start_of_month + timedelta(days=32)).replace(day=1)
            
            usage = UsageTracking(
                id=str(uuid.uuid4()),
                user_id=user_id,
                period_start=start_of_month,
                period_end=next_month,
                billing_cycle="monthly"
            )
            db.add(usage)
        
        # Apply increments
        for field, value in increments.items():
            if hasattr(usage, field):
                current_value = getattr(usage, field) or 0
                setattr(usage, field, current_value + value)
        
        usage.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(usage)
        return usage

# Analytics Operations
class AnalyticsCRUD:
    @staticmethod
    def create_analytics_record(db: Session, user_id: str, campaign_id: str, date: datetime, **metrics) -> Analytics:
        """Create analytics record"""
        analytics = Analytics(
            id=str(uuid.uuid4()),
            user_id=user_id,
            campaign_id=campaign_id,
            date=date,
            **metrics
        )
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics
    
    @staticmethod
    def get_campaign_analytics(db: Session, campaign_id: str, days: int = 30) -> List[Analytics]:
        """Get campaign analytics for specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(Analytics).filter(
            and_(
                Analytics.campaign_id == campaign_id,
                Analytics.date >= start_date
            )
        ).order_by(Analytics.date.desc()).all()
    
    @staticmethod
    def get_user_analytics_summary(db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user's analytics summary"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            func.sum(Analytics.impressions).label('total_impressions'),
            func.sum(Analytics.clicks).label('total_clicks'),
            func.sum(Analytics.spend).label('total_spend'),
            func.sum(Analytics.conversions).label('total_conversions'),
            func.sum(Analytics.revenue).label('total_revenue'),
            func.avg(Analytics.ctr).label('avg_ctr'),
            func.avg(Analytics.cpc).label('avg_cpc'),
            func.avg(Analytics.roas).label('avg_roas')
        ).filter(
            and_(
                Analytics.user_id == user_id,
                Analytics.date >= start_date
            )
        ).first()
        
        return {
            'impressions': results.total_impressions or 0,
            'clicks': results.total_clicks or 0,
            'spend': float(results.total_spend or 0),
            'conversions': results.total_conversions or 0,
            'revenue': float(results.total_revenue or 0),
            'ctr': float(results.avg_ctr or 0),
            'cpc': float(results.avg_cpc or 0),
            'roas': float(results.avg_roas or 0)
        }

# Conversion Operations
class ConversionCRUD:
    @staticmethod
    def create_conversion(db: Session, user_id: str, campaign_id: str, conversion_type: ConversionType, **kwargs) -> Conversion:
        """Create conversion record"""
        conversion = Conversion(
            id=str(uuid.uuid4()),
            user_id=user_id,
            campaign_id=campaign_id,
            conversion_type=conversion_type,
            conversion_date=datetime.utcnow(),
            **kwargs
        )
        db.add(conversion)
        db.commit()
        db.refresh(conversion)
        return conversion
    
    @staticmethod
    def get_campaign_conversions(db: Session, campaign_id: str) -> List[Conversion]:
        """Get all conversions for a campaign"""
        return db.query(Conversion).filter(Conversion.campaign_id == campaign_id).all()
    
    @staticmethod
    def get_revenue_attribution(db: Session, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get revenue attribution data"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            Campaign.name.label('campaign_name'),
            func.count(Conversion.id).label('conversion_count'),
            func.sum(Conversion.value).label('total_revenue')
        ).join(
            Conversion, Campaign.id == Conversion.campaign_id
        ).filter(
            and_(
                Campaign.user_id == user_id,
                Conversion.conversion_date >= start_date
            )
        ).group_by(Campaign.id, Campaign.name).all()
        
        return [
            {
                'campaign_name': result.campaign_name,
                'conversions': result.conversion_count,
                'revenue': float(result.total_revenue or 0)
            }
            for result in results
        ]