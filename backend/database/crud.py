"""
Database CRUD operations for AI Marketing Automation Platform
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from database.models import (
    User, Subscription, Campaign, AIContent, MetaAccount,
    Analytics, Conversion, UsageTracking, SubscriptionTier,
    CampaignStatus, ContentType, ConversionType, ContentTemplate, 
    MetaUserProfile, CampaignRecommendation, BusinessSizeEnum, 
    BudgetRangeEnum, CampaignObjectiveEnum, BrandVoiceEnum, ContentPreferenceEnum,
    BillingSubscription, Payment, Invoice, PaymentMethod, WebhookEvent,
    SubscriptionStatus, PaymentStatus, PaymentProvider,
    # ML Prediction Models
    MLPredictionResult, CampaignPredictionScenario, MLPredictionCache,
    MLPredictionFeedback, MLPredictionType, ConfidenceLevel
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
    def create_or_update_usage(db: Session, user_id: str, current_tier: str = "basic", **increments) -> UsageTracking:
        """Create or update usage tracking with tier awareness"""
        usage = UsageTrackingCRUD.get_current_usage(db, user_id)
        
        if not usage:
            now = datetime.utcnow()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (start_of_month + timedelta(days=32)).replace(day=1)
            
            usage = UsageTracking(
                id=str(uuid.uuid4()),
                user_id=user_id,
                current_tier=current_tier,
                period_start=start_of_month,
                period_end=next_month,
                billing_cycle="monthly"
            )
            db.add(usage)
        else:
            # Update tier if changed
            usage.current_tier = current_tier
        
        # Apply increments
        for field, value in increments.items():
            if hasattr(usage, field):
                current_value = getattr(usage, field) or 0
                setattr(usage, field, current_value + value)
        
        usage.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(usage)
        return usage
    
    @staticmethod
    def check_tier_limits(db: Session, user_id: str, settings_instance) -> Dict[str, Any]:
        """Check if user is within their tier limits"""
        usage = UsageTrackingCRUD.get_current_usage(db, user_id)
        if not usage:
            return {
                "within_limits": True,
                "tier": "basic",
                "usage": {},
                "limits": {},
                "warnings": []
            }
        
        # Get tier configuration
        tier = usage.current_tier or "basic"
        tier_config = settings_instance.get_tier_config(tier)
        
        # Current usage
        current_usage = {
            "campaigns": usage.campaigns_created or 0,
            "ai_generations": usage.ai_generations_used or 0,
            "ad_spend": usage.ad_spend_monitored or 0.0
        }
        
        # Check limits
        validation = settings_instance.validate_tier_limits(tier, current_usage)
        
        # Calculate percentages and warnings
        warnings = []
        usage_percentages = {}
        
        campaigns_pct = (current_usage["campaigns"] / tier_config["campaigns_limit"]) * 100 if tier_config["campaigns_limit"] > 0 else 0
        ai_pct = (current_usage["ai_generations"] / tier_config["ai_generations_limit"]) * 100 if tier_config["ai_generations_limit"] > 0 else 0
        spend_pct = (current_usage["ad_spend"] / tier_config["ad_spend_monitoring_limit"]) * 100 if tier_config["ad_spend_monitoring_limit"] > 0 else 0
        
        usage_percentages = {
            "campaigns": campaigns_pct,
            "ai_generations": ai_pct,
            "ad_spend": spend_pct
        }
        
        # Generate warnings based on thresholds
        warning_thresholds = settings_instance.USAGE_WARNING_THRESHOLDS
        for threshold in warning_thresholds:
            threshold_pct = threshold * 100
            if campaigns_pct >= threshold_pct and validation["campaigns_ok"]:
                warnings.append(f"Campaign usage at {campaigns_pct:.1f}% of limit")
            if ai_pct >= threshold_pct and validation["ai_generations_ok"]:
                warnings.append(f"AI generation usage at {ai_pct:.1f}% of limit")
            if spend_pct >= threshold_pct and validation["ad_spend_ok"]:
                warnings.append(f"Ad spend monitoring at {spend_pct:.1f}% of limit")
        
        return {
            "within_limits": all(validation.values()),
            "tier": tier,
            "usage": current_usage,
            "limits": {
                "campaigns": tier_config["campaigns_limit"],
                "ai_generations": tier_config["ai_generations_limit"],
                "ad_spend": tier_config["ad_spend_monitoring_limit"]
            },
            "usage_percentages": usage_percentages,
            "validation": validation,
            "warnings": warnings
        }
    
    @staticmethod
    def reset_usage_period(db: Session, user_id: str) -> UsageTracking:
        """Reset usage for a new billing period"""
        # Archive current usage
        current_usage = UsageTrackingCRUD.get_current_usage(db, user_id)
        if current_usage:
            current_usage.period_end = datetime.utcnow()
            
        # Create new usage period
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start_of_month + timedelta(days=32)).replace(day=1)
        
        new_usage = UsageTracking(
            id=str(uuid.uuid4()),
            user_id=user_id,
            current_tier=current_usage.current_tier if current_usage else "basic",
            period_start=start_of_month,
            period_end=next_month,
            billing_cycle="monthly",
            reset_count=(current_usage.reset_count + 1) if current_usage else 1,
            last_reset_date=now
        )
        db.add(new_usage)
        db.commit()
        db.refresh(new_usage)
        return new_usage

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


# Personalization Operations
class PersonalizationCRUD:
    """Optimized CRUD operations for personalization initialization and management"""
    
    @staticmethod
    def verify_table_exists(db: Session, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = :table_name
                );
            """), {"table_name": table_name})
            return result.scalar()
        except Exception:
            return False
    
    @staticmethod
    def verify_all_personalization_tables(db: Session) -> Dict[str, bool]:
        """Verify that all personalization tables exist"""
        required_tables = [
            'meta_user_profiles', 'campaign_recommendations', 'ab_tests',
            'test_variations', 'test_results', 'learning_insights',
            'performance_patterns', 'content_templates', 'personalized_content',
            'campaign_personalization_settings'
        ]
        
        # Optimized single query to check multiple tables
        tables_str = "', '".join(required_tables)
        result = db.execute(text(f"""
            SELECT table_name,
                   EXISTS (SELECT FROM information_schema.tables WHERE table_name = tables.table_name) as exists
            FROM (VALUES ('{tables_str.replace("', '", "'), ('")}')) AS tables(table_name);
        """))
        
        return {row.table_name: row.exists for row in result}
    
    @staticmethod
    def get_index_count_for_personalization_tables(db: Session) -> int:
        """Get the count of indexes for personalization tables"""
        try:
            result = db.execute(text("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE tablename IN (
                    'meta_user_profiles', 'campaign_recommendations', 'ab_tests',
                    'test_variations', 'test_results', 'learning_insights',
                    'performance_patterns', 'content_templates', 'personalized_content',
                    'campaign_personalization_settings'
                );
            """))
            return result.scalar() or 0
        except Exception:
            return 0
    
    @staticmethod
    def create_monitoring_views(db: Session) -> bool:
        """Create optimized monitoring views for personalization metrics"""
        try:
            monitoring_views = [
                """
                CREATE OR REPLACE VIEW personalization_metrics AS
                SELECT 
                    COUNT(DISTINCT mup.user_id) as users_with_profiles,
                    COUNT(DISTINCT cr.user_id) as users_with_recommendations,
                    COUNT(DISTINCT ab.user_id) as users_with_ab_tests,
                    COUNT(DISTINCT li.user_id) as users_with_insights,
                    COALESCE(AVG(cr.confidence_score), 0) as avg_recommendation_confidence
                FROM meta_user_profiles mup
                FULL OUTER JOIN campaign_recommendations cr ON mup.user_id = cr.user_id
                FULL OUTER JOIN ab_tests ab ON mup.user_id = ab.user_id  
                FULL OUTER JOIN learning_insights li ON mup.user_id = li.user_id;
                """,
                """
                CREATE OR REPLACE VIEW ab_test_performance AS
                SELECT 
                    ab.status,
                    ab.test_type,
                    COUNT(*) as test_count,
                    COALESCE(AVG(ab.confidence_level), 0) as avg_confidence,
                    COUNT(CASE WHEN ab.significance_status = 'significant' THEN 1 END) as significant_tests
                FROM ab_tests ab
                GROUP BY ab.status, ab.test_type;
                """,
                """
                CREATE OR REPLACE VIEW content_template_performance AS
                SELECT 
                    ct.template_type,
                    ct.category,
                    COUNT(*) as template_count,
                    COALESCE(AVG(ct.usage_count), 0) as avg_usage,
                    COALESCE(AVG(ct.avg_performance_score), 0) as avg_performance,
                    COALESCE(AVG(ct.success_rate), 0) as avg_success_rate
                FROM content_templates ct
                WHERE ct.is_active = true
                GROUP BY ct.template_type, ct.category;
                """
            ]
            
            for view_sql in monitoring_views:
                db.execute(text(view_sql))
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise e


class ContentTemplateCRUD:
    """Optimized CRUD operations for ContentTemplate"""
    
    @staticmethod
    def create_template(
        db: Session,
        template_id: str,
        name: str,
        description: str,
        template_type: str,
        category: str,
        base_prompt: str,
        personalization_variables: Dict[str, Any],
        target_industries: List[str],
        target_objectives: List[str],
        is_public: bool = True,
        created_by: str = "system"
    ) -> ContentTemplate:
        """Create a new content template with optimized validation"""
        template = ContentTemplate(
            id=str(uuid.uuid4()),
            template_id=template_id,
            name=name,
            description=description,
            template_type=template_type,
            category=category,
            base_prompt=base_prompt,
            personalization_variables=personalization_variables,
            target_industries=target_industries,
            target_objectives=target_objectives,
            is_public=is_public,
            created_by=created_by,
            is_active=True,
            usage_count=0,
            created_at=datetime.now()
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def get_template_by_id(db: Session, template_id: str) -> Optional[ContentTemplate]:
        """Get template by template_id with optimized query"""
        return db.query(ContentTemplate).filter(
            ContentTemplate.template_id == template_id
        ).first()
    
    @staticmethod
    def batch_check_existing_templates(db: Session, template_ids: List[str]) -> List[str]:
        """Efficiently check which templates already exist"""
        existing = db.query(ContentTemplate.template_id).filter(
            ContentTemplate.template_id.in_(template_ids)
        ).all()
        return [t.template_id for t in existing]
    
    @staticmethod
    def create_default_templates(db: Session) -> List[ContentTemplate]:
        """Create default content templates with batch optimization"""
        default_templates_data = [
            {
                "template_id": "default_image_ecommerce",
                "name": "E-commerce Product Showcase",
                "description": "High-converting product showcase template for e-commerce",
                "template_type": "image", "category": "ecommerce",
                "base_prompt": "Create a professional product showcase image featuring {product_name} with {brand_colors} color scheme, showcasing {key_benefits} for {target_demographic}",
                "personalization_variables": {"product_name": "string", "brand_colors": "array", "key_benefits": "array", "target_demographic": "string"},
                "target_industries": ["ecommerce", "retail", "fashion"],
                "target_objectives": ["sales", "brand_awareness"]
            },
            {
                "template_id": "default_video_services",
                "name": "Service-Based Business Video",
                "description": "Engaging video template for service-based businesses",
                "template_type": "video", "category": "services",
                "base_prompt": "Create a professional service showcase video for {business_name} highlighting {service_benefits} with {brand_voice} tone, targeting {target_age_group}",
                "personalization_variables": {"business_name": "string", "service_benefits": "array", "brand_voice": "enum", "target_age_group": "enum"},
                "target_industries": ["consulting", "healthcare", "finance"],
                "target_objectives": ["lead_generation", "brand_awareness"]
            },
            {
                "template_id": "default_carousel_multi",
                "name": "Multi-Product Carousel",
                "description": "Carousel template showcasing multiple products or services",
                "template_type": "carousel", "category": "multi_product",
                "base_prompt": "Create a {slide_count}-slide carousel showcasing {products} with consistent {brand_colors} theme, each slide highlighting {unique_selling_points}",
                "personalization_variables": {"slide_count": "integer", "products": "array", "brand_colors": "array", "unique_selling_points": "array"},
                "target_industries": ["ecommerce", "saas", "education"],
                "target_objectives": ["engagement", "traffic"]
            }
        ]
        
        # Batch check existing templates
        template_ids = [t["template_id"] for t in default_templates_data]
        existing_ids = ContentTemplateCRUD.batch_check_existing_templates(db, template_ids)
        
        # Create only non-existing templates
        created_templates = []
        for template_data in default_templates_data:
            if template_data["template_id"] not in existing_ids:
                template = ContentTemplateCRUD.create_template(
                    db, 
                    is_public=True, 
                    created_by="system",
                    **template_data
                )
                created_templates.append(template)
        
        return created_templates


class MetaUserProfileCRUD:
    """Optimized CRUD operations for MetaUserProfile"""
    
    @staticmethod
    def create_sample_profile(
        db: Session,
        user_id: str,
        business_name: str = "Sample E-commerce Store"
    ) -> MetaUserProfile:
        """Create a sample MetaUserProfile with optimized defaults"""
        profile = MetaUserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            business_size=BusinessSizeEnum.SMB,
            industry="ecommerce",
            business_name=business_name,
            monthly_budget=BudgetRangeEnum.MEDIUM,
            primary_objective=CampaignObjectiveEnum.SALES,
            secondary_objectives=["brand_awareness", "traffic"],
            target_age_groups=["millennial", "gen_x"],
            target_locations=["united_states", "canada"],
            target_interests=["shopping", "fashion", "lifestyle"],
            brand_voice=BrandVoiceEnum.PROFESSIONAL,
            content_preference=ContentPreferenceEnum.IMAGE_HEAVY,
            platform_priorities=["instagram", "facebook"],
            brand_colors=["#FF6B6B", "#4ECDC4", "#45B7D1"],
            roi_focus=True,
            risk_tolerance="medium",
            automation_level="high",
            created_at=datetime.now()
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    
    @staticmethod
    def get_profile_by_user_id(db: Session, user_id: str) -> Optional[MetaUserProfile]:
        """Get MetaUserProfile by user_id with optimized query"""
        return db.query(MetaUserProfile).filter(
            MetaUserProfile.user_id == user_id
        ).first()
    
    @staticmethod
    def upsert_profile(db: Session, user_id: str, **profile_data) -> MetaUserProfile:
        """Create or update MetaUserProfile with single query"""
        existing = MetaUserProfileCRUD.get_profile_by_user_id(db, user_id)
        
        if existing:
            for key, value in profile_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            return MetaUserProfileCRUD.create_sample_profile(db, user_id, **profile_data)


# Payment Operations
class BillingSubscriptionCRUD:
    """Optimized CRUD operations for billing subscriptions"""
    
    @staticmethod
    def get_user_active_subscription(db: Session, user_id: str) -> Optional[BillingSubscription]:
        """Get user's active subscription with optimized query"""
        return db.query(BillingSubscription).filter(
            BillingSubscription.user_id == user_id,
            BillingSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).first()
    
    @staticmethod
    def create_subscription(
        db: Session, user_id: str, tier: SubscriptionTier, monthly_price: float,
        trial_days: int = 14, provider: PaymentProvider = PaymentProvider.GOOGLE_PAY
    ) -> BillingSubscription:
        """Create billing subscription with optimized tier limits"""
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=trial_days)
        
        # Optimized tier limits configuration
        tier_limits = {
            SubscriptionTier.STARTER: {'max_campaigns': 10, 'max_ai_generations': -1, 'max_api_calls': 2000, 'analytics_retention_days': 30},
            SubscriptionTier.PROFESSIONAL: {'max_campaigns': 50, 'max_ai_generations': -1, 'max_api_calls': 10000, 'analytics_retention_days': 90},
            SubscriptionTier.ENTERPRISE: {'max_campaigns': -1, 'max_ai_generations': -1, 'max_api_calls': -1, 'analytics_retention_days': 365}
        }
        
        limits = tier_limits.get(tier, tier_limits[SubscriptionTier.STARTER])
        
        subscription = BillingSubscription(
            id=str(uuid.uuid4()), user_id=user_id, tier=tier, status=SubscriptionStatus.TRIAL,
            monthly_price=monthly_price, trial_start=trial_start, trial_end=trial_end,
            is_trial=True, billing_cycle_start=trial_end, next_billing_date=trial_end,
            provider=provider, **limits
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def update_subscription_status(
        db: Session, subscription_id: str, status: SubscriptionStatus,
        provider_subscription_id: str = None
    ) -> Optional[BillingSubscription]:
        """Update subscription status with idempotency"""
        subscription = db.query(BillingSubscription).filter(
            BillingSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            return None
        
        # Prevent double-processing for active subscriptions
        if status == SubscriptionStatus.ACTIVE and subscription.status == SubscriptionStatus.ACTIVE:
            return subscription
            
        subscription.status = status
        subscription.updated_at = datetime.utcnow()
        
        if provider_subscription_id:
            subscription.provider_subscription_id = provider_subscription_id
        
        if status == SubscriptionStatus.ACTIVE and subscription.is_trial:
            subscription.is_trial = False
            subscription.billing_cycle_start = datetime.utcnow()
            subscription.next_billing_date = datetime.utcnow() + timedelta(days=30)
        
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def track_usage(db: Session, subscription_id: str, usage_type: str, amount: int = 1) -> Optional[BillingSubscription]:
        """Track usage with optimized field updates"""
        subscription = db.query(BillingSubscription).filter(
            BillingSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            return None
        
        usage_fields = {
            'campaigns': 'campaigns_used',
            'ai_generations': 'ai_generations_used', 
            'api_calls': 'api_calls_used'
        }
        
        field = usage_fields.get(usage_type)
        if field:
            current_value = getattr(subscription, field, 0)
            setattr(subscription, field, current_value + amount)
            subscription.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(subscription)
        
        return subscription


class PaymentCRUD:
    """Optimized CRUD operations for payments"""
    
    @staticmethod
    def create_payment(
        db: Session, user_id: str, subscription_id: str, amount: float,
        provider: PaymentProvider, description: str = "Monthly subscription", currency: str = "INR"
    ) -> Payment:
        """Create payment with optimized defaults"""
        payment = Payment(
            id=str(uuid.uuid4()), user_id=user_id, subscription_id=subscription_id,
            amount=amount, currency=currency, description=description,
            provider=provider, status=PaymentStatus.PENDING
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def update_payment_status(
        db: Session, payment_id: str, status: PaymentStatus,
        provider_payment_id: str = None, provider_transaction_id: str = None,
        failure_reason: str = None, failure_code: str = None
    ) -> Optional[Payment]:
        """Update payment status with batch field updates"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return None
        
        # Batch update all fields
        updates = {
            'status': status,
            'updated_at': datetime.utcnow(),
            'provider_payment_id': provider_payment_id or payment.provider_payment_id,
            'provider_transaction_id': provider_transaction_id or payment.provider_transaction_id,
            'failure_reason': failure_reason or payment.failure_reason,
            'failure_code': failure_code or payment.failure_code
        }
        
        if status == PaymentStatus.SUCCEEDED:
            updates['processed_at'] = datetime.utcnow()
        
        for key, value in updates.items():
            setattr(payment, key, value)
        
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_user_payments(
        db: Session, user_id: str, limit: int = 50, status: PaymentStatus = None
    ) -> List[Payment]:
        """Get user payments with optimized filtering"""
        query = db.query(Payment).filter(Payment.user_id == user_id)
        
        if status:
            query = query.filter(Payment.status == status)
        
        return query.order_by(Payment.created_at.desc()).limit(limit).all()


# ML Prediction Operations
class MLPredictionCRUD:
    """CRUD operations for ML predictions and related data"""
    
    @staticmethod
    def create_prediction_result(
        db: Session,
        prediction_id: str,
        user_id: str,
        prediction_type: MLPredictionType,
        input_features: Dict[str, Any],
        predicted_metrics: Dict[str, float],
        confidence_level: ConfidenceLevel,
        confidence_score: float,
        **kwargs
    ) -> MLPredictionResult:
        """Create a new ML prediction result"""
        prediction = MLPredictionResult(
            id=str(uuid.uuid4()),
            prediction_id=prediction_id,
            user_id=user_id,
            prediction_type=prediction_type,
            input_features=input_features,
            predicted_metrics=predicted_metrics,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            **kwargs
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction
    
    @staticmethod
    def get_prediction_by_id(db: Session, prediction_id: str) -> Optional[MLPredictionResult]:
        """Get prediction by prediction_id"""
        return db.query(MLPredictionResult).filter(
            MLPredictionResult.prediction_id == prediction_id
        ).first()
    
    @staticmethod
    def get_user_predictions(
        db: Session,
        user_id: str,
        prediction_type: Optional[MLPredictionType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MLPredictionResult]:
        """Get user's ML predictions with optional filtering"""
        query = db.query(MLPredictionResult).filter(
            MLPredictionResult.user_id == user_id
        )
        
        if prediction_type:
            query = query.filter(MLPredictionResult.prediction_type == prediction_type)
        
        return query.order_by(
            MLPredictionResult.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_prediction_accuracy(
        db: Session,
        prediction_id: str,
        actual_metrics: Dict[str, float],
        prediction_accuracy_score: float
    ) -> Optional[MLPredictionResult]:
        """Update prediction with actual results and accuracy score"""
        prediction = db.query(MLPredictionResult).filter(
            MLPredictionResult.prediction_id == prediction_id
        ).first()
        
        if prediction:
            prediction.actual_metrics = actual_metrics
            prediction.prediction_accuracy_score = prediction_accuracy_score
            prediction.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(prediction)
        
        return prediction
    
    @staticmethod
    def create_prediction_scenario(
        db: Session,
        prediction_result_id: str,
        scenario_id: str,
        user_id: str,
        scenario_name: str,
        modified_metrics: Dict[str, float],
        **kwargs
    ) -> CampaignPredictionScenario:
        """Create a prediction scenario"""
        scenario = CampaignPredictionScenario(
            id=str(uuid.uuid4()),
            prediction_result_id=prediction_result_id,
            scenario_id=scenario_id,
            user_id=user_id,
            scenario_name=scenario_name,
            modified_metrics=modified_metrics,
            **kwargs
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario
    
    @staticmethod
    def get_prediction_scenarios(
        db: Session,
        prediction_result_id: str
    ) -> List[CampaignPredictionScenario]:
        """Get all scenarios for a prediction"""
        return db.query(CampaignPredictionScenario).filter(
            CampaignPredictionScenario.prediction_result_id == prediction_result_id
        ).order_by(CampaignPredictionScenario.priority_ranking.asc()).all()
    
    @staticmethod
    def get_cache_entry(
        db: Session,
        cache_key: str,
        user_id: str
    ) -> Optional[MLPredictionCache]:
        """Get cached prediction entry"""
        return db.query(MLPredictionCache).filter(
            and_(
                MLPredictionCache.cache_key == cache_key,
                MLPredictionCache.user_id == user_id,
                MLPredictionCache.expires_at > datetime.utcnow(),
                MLPredictionCache.is_valid == True
            )
        ).first()
    
    @staticmethod
    def create_cache_entry(
        db: Session,
        cache_key: str,
        user_id: str,
        prediction_type: MLPredictionType,
        input_hash: str,
        prediction_data: Dict[str, Any],
        expires_at: datetime,
        **kwargs
    ) -> MLPredictionCache:
        """Create cache entry for prediction"""
        cache_entry = MLPredictionCache(
            id=str(uuid.uuid4()),
            cache_key=cache_key,
            user_id=user_id,
            prediction_type=prediction_type,
            input_hash=input_hash,
            prediction_data=prediction_data,
            expires_at=expires_at,
            **kwargs
        )
        db.add(cache_entry)
        db.commit()
        db.refresh(cache_entry)
        return cache_entry
    
    @staticmethod
    def update_cache_hit(db: Session, cache_entry_id: str) -> None:
        """Update cache hit count and last accessed time"""
        cache_entry = db.query(MLPredictionCache).filter(
            MLPredictionCache.id == cache_entry_id
        ).first()
        
        if cache_entry:
            cache_entry.hit_count += 1
            cache_entry.last_accessed = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def cleanup_expired_cache(db: Session, user_id: Optional[str] = None) -> int:
        """Clean up expired cache entries"""
        query = db.query(MLPredictionCache).filter(
            MLPredictionCache.expires_at <= datetime.utcnow()
        )
        
        if user_id:
            query = query.filter(MLPredictionCache.user_id == user_id)
        
        expired_entries = query.all()
        count = len(expired_entries)
        
        for entry in expired_entries:
            db.delete(entry)
        
        db.commit()
        return count
    
    @staticmethod
    def create_prediction_feedback(
        db: Session,
        prediction_result_id: str,
        user_id: str,
        accuracy_rating: int,
        usefulness_rating: int,
        **kwargs
    ) -> MLPredictionFeedback:
        """Create user feedback for a prediction"""
        feedback = MLPredictionFeedback(
            id=str(uuid.uuid4()),
            prediction_result_id=prediction_result_id,
            user_id=user_id,
            accuracy_rating=accuracy_rating,
            usefulness_rating=usefulness_rating,
            **kwargs
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    @staticmethod
    def get_prediction_feedback_stats(
        db: Session,
        user_id: Optional[str] = None,
        prediction_type: Optional[MLPredictionType] = None
    ) -> Dict[str, Any]:
        """Get aggregated feedback statistics"""
        query = db.query(MLPredictionFeedback)
        
        if user_id:
            query = query.filter(MLPredictionFeedback.user_id == user_id)
        
        if prediction_type:
            query = query.join(MLPredictionResult).filter(
                MLPredictionResult.prediction_type == prediction_type
            )
        
        feedback_entries = query.all()
        
        if not feedback_entries:
            return {
                "total_feedback": 0,
                "average_accuracy_rating": 0,
                "average_usefulness_rating": 0,
                "followed_recommendations_percentage": 0
            }
        
        total_feedback = len(feedback_entries)
        avg_accuracy = sum(f.accuracy_rating or 0 for f in feedback_entries) / total_feedback
        avg_usefulness = sum(f.usefulness_rating or 0 for f in feedback_entries) / total_feedback
        
        followed_count = sum(1 for f in feedback_entries if f.followed_recommendations)
        followed_percentage = (followed_count / total_feedback) * 100 if total_feedback > 0 else 0
        
        return {
            "total_feedback": total_feedback,
            "average_accuracy_rating": round(avg_accuracy, 2),
            "average_usefulness_rating": round(avg_usefulness, 2),
            "followed_recommendations_percentage": round(followed_percentage, 1)
        }
    
    @staticmethod
    def get_prediction_accuracy_trends(
        db: Session,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get prediction accuracy trends over time"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(MLPredictionResult).filter(
            and_(
                MLPredictionResult.created_at >= start_date,
                MLPredictionResult.prediction_accuracy_score.isnot(None)
            )
        )
        
        if user_id:
            query = query.filter(MLPredictionResult.user_id == user_id)
        
        predictions = query.order_by(MLPredictionResult.created_at.asc()).all()
        
        if not predictions:
            return {
                "total_predictions_with_results": 0,
                "average_accuracy": 0,
                "accuracy_trend": "no_data"
            }
        
        total_predictions = len(predictions)
        avg_accuracy = sum(p.prediction_accuracy_score for p in predictions) / total_predictions
        
        # Calculate trend (comparing first half vs second half)
        if total_predictions >= 10:
            mid_point = total_predictions // 2
            first_half_avg = sum(p.prediction_accuracy_score for p in predictions[:mid_point]) / mid_point
            second_half_avg = sum(p.prediction_accuracy_score for p in predictions[mid_point:]) / (total_predictions - mid_point)
            
            if second_half_avg > first_half_avg + 0.05:
                trend = "improving"
            elif second_half_avg < first_half_avg - 0.05:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "total_predictions_with_results": total_predictions,
            "average_accuracy": round(avg_accuracy, 3),
            "accuracy_trend": trend,
            "accuracy_by_type": {
                prediction_type.value: {
                    "count": len([p for p in predictions if p.prediction_type == prediction_type]),
                    "avg_accuracy": round(
                        sum(p.prediction_accuracy_score for p in predictions if p.prediction_type == prediction_type) / 
                        len([p for p in predictions if p.prediction_type == prediction_type]), 3
                    ) if [p for p in predictions if p.prediction_type == prediction_type] else 0
                }
                for prediction_type in MLPredictionType
            }
        }


