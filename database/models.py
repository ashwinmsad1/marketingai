"""
SQLAlchemy models for AI Marketing Automation Platform
Multi-tenant SaaS architecture with comprehensive user management
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

class SubscriptionTier(PyEnum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class CampaignStatus(PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class ContentType(PyEnum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"

class ConversionType(PyEnum):
    LEAD = "lead"
    SALE = "sale"
    CLICK = "click"
    VIEW = "view"

# Core User Management
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String)
    last_name = Column(String)
    company_name = Column(String)
    phone = Column(String)
    
    # Authentication
    password_hash = Column(String)  # For web auth (future)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    meta_accounts = relationship("MetaAccount", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")
    ai_content = relationship("AIContent", back_populates="user")
    usage_tracking = relationship("UsageTracking", back_populates="user")
    conversions = relationship("Conversion", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Subscription Details
    tier = Column(Enum(SubscriptionTier), nullable=False)
    status = Column(String, default="active")  # active, cancelled, expired, trial
    
    # Pricing
    monthly_price = Column(Float)
    currency = Column(String, default="USD")
    
    # Billing
    stripe_subscription_id = Column(String)  # For Stripe integration
    stripe_customer_id = Column(String)
    
    # Trial
    trial_end = Column(DateTime)
    is_trial = Column(Boolean, default=False)
    
    # Usage Limits
    max_campaigns = Column(Integer)
    max_ai_generations = Column(Integer)
    max_api_calls = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class UsageTracking(Base):
    __tablename__ = "usage_tracking"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    
    # Usage Metrics
    campaigns_created = Column(Integer, default=0)
    ai_generations_used = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)
    
    # Content Generation Breakdown
    images_generated = Column(Integer, default=0)
    videos_generated = Column(Integer, default=0)
    
    # Period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    billing_cycle = Column(String)  # monthly, yearly
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="usage_tracking")

# Meta Integration
class MetaAccount(Base):
    __tablename__ = "meta_accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Meta Credentials (Encrypted)
    access_token = Column(Text)  # Encrypted long-lived token
    app_id = Column(String)
    app_secret = Column(Text)  # Encrypted
    
    # Account Details
    ad_account_id = Column(String)
    facebook_page_id = Column(String)
    instagram_business_id = Column(String)
    
    # Account Info
    account_name = Column(String)
    currency = Column(String)
    timezone = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    token_expires_at = Column(DateTime)
    last_sync = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meta_accounts")
    campaigns = relationship("Campaign", back_populates="meta_account")

# Campaign Management
class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    meta_account_id = Column(String, ForeignKey("meta_accounts.id"))
    
    # Campaign Details
    name = Column(String, nullable=False)
    description = Column(Text)
    objective = Column(String)  # BRAND_AWARENESS, TRAFFIC, CONVERSIONS, etc.
    
    # Meta Campaign Data
    meta_campaign_id = Column(String)  # Facebook Campaign ID
    meta_adset_id = Column(String)
    meta_ad_id = Column(String)
    
    # Targeting
    target_audience = Column(JSON)  # JSON object with targeting parameters
    budget_daily = Column(Float)
    budget_total = Column(Float)
    
    # Performance
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    
    # Calculated Metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpm = Column(Float, default=0.0)  # Cost per mille
    roas = Column(Float, default=0.0)  # Return on ad spend
    
    # Status
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # AI Enhancement
    industry = Column(String)
    template_used = Column(String)
    is_ai_optimized = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    meta_account = relationship("MetaAccount", back_populates="campaigns")
    ai_content = relationship("AIContent", back_populates="campaign")
    conversions = relationship("Conversion", back_populates="campaign")
    analytics = relationship("Analytics", back_populates="campaign")

# AI Content Management
class AIContent(Base):
    __tablename__ = "ai_content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Content Details
    content_type = Column(Enum(ContentType), nullable=False)
    prompt = Column(Text, nullable=False)
    style = Column(String)
    
    # Generated Content
    file_path = Column(String)  # Path to generated file
    file_url = Column(String)   # Public URL for serving
    file_size = Column(Integer) # File size in bytes
    
    # Generation Parameters
    aspect_ratio = Column(String)
    duration = Column(Integer)  # For videos, in seconds
    quality = Column(String)
    creativity_level = Column(Integer)
    
    # Performance Tracking
    usage_count = Column(Integer, default=0)  # How many times used in campaigns
    performance_score = Column(Float)  # AI-calculated performance score
    
    # Generation Info
    model_used = Column(String)  # gemini-2.5-flash-image-preview, veo-3.0, etc.
    generation_time = Column(Float)  # Time taken to generate in seconds
    cost = Column(Float)  # API cost for generation
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_content")
    campaign = relationship("Campaign", back_populates="ai_content")

# Revenue Tracking & Attribution
class Conversion(Base):
    __tablename__ = "conversions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Conversion Details
    conversion_type = Column(Enum(ConversionType), nullable=False)
    value = Column(Float)  # Revenue value
    currency = Column(String, default="USD")
    
    # Attribution
    customer_email = Column(String)
    customer_id = Column(String)
    meta_conversion_id = Column(String)  # Facebook Conversion ID
    
    # Source Attribution
    creative_asset_id = Column(String, ForeignKey("ai_content.id"))  # Which AI content led to conversion
    platform = Column(String)  # facebook, instagram
    placement = Column(String)  # feed, stories, etc.
    
    # Customer Journey
    touchpoint_sequence = Column(JSON)  # Array of touchpoints
    time_to_conversion = Column(Integer)  # Hours from first touch
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    conversion_date = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversions")
    campaign = relationship("Campaign", back_populates="conversions")

# Analytics & Reporting
class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Reporting Period
    date = Column(DateTime, nullable=False)
    period_type = Column(String)  # daily, weekly, monthly
    
    # Performance Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Calculated KPIs
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Platform Breakdown
    facebook_metrics = Column(JSON)
    instagram_metrics = Column(JSON)
    
    # Industry Benchmarks
    industry_avg_ctr = Column(Float)
    industry_avg_cpc = Column(Float)
    performance_vs_industry = Column(Float)  # Percentage above/below industry average
    
    # AI Performance
    ai_content_performance = Column(JSON)  # Performance by AI-generated content
    optimization_suggestions = Column(JSON)  # AI suggestions for improvement
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="analytics")

# Additional Models for Enhanced Features

class Industry(Base):
    __tablename__ = "industries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    # Industry Benchmarks
    avg_ctr = Column(Float)
    avg_cpc = Column(Float)
    avg_cpm = Column(Float)
    avg_conversion_rate = Column(Float)
    
    # Template Configuration
    default_templates = Column(JSON)
    recommended_styles = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())

class CompetitorAnalysis(Base):
    __tablename__ = "competitor_analysis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Competitor Info
    competitor_name = Column(String, nullable=False)
    competitor_url = Column(String)
    industry = Column(String)
    
    # Analysis Results
    content_analysis = Column(JSON)  # AI analysis of competitor content
    performance_insights = Column(JSON)
    improvement_suggestions = Column(JSON)
    
    # Generated Improvements
    improved_content_id = Column(String, ForeignKey("ai_content.id"))
    performance_prediction = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ViralTrend(Base):
    __tablename__ = "viral_trends"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Trend Details
    topic = Column(String, nullable=False)
    industry = Column(String)
    platform = Column(String)  # tiktok, instagram, facebook, etc.
    
    # Trend Metrics
    virality_score = Column(Float)
    engagement_rate = Column(Float)
    growth_rate = Column(Float)
    
    # Content Framework
    framework_type = Column(String)  # challenge, transformation, tutorial, etc.
    key_elements = Column(JSON)
    recommended_hashtags = Column(JSON)
    
    # Timing
    peak_time = Column(DateTime)
    trend_lifespan = Column(Integer)  # Expected days
    optimal_posting_times = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)