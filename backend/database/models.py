"""
SQLAlchemy models for AI Marketing Automation Platform
Multi-tenant SaaS architecture with comprehensive user management
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum, JSON, Index, UniqueConstraint, CheckConstraint
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
    billing_subscriptions = relationship("BillingSubscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    meta_accounts = relationship("MetaAccount", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")
    ai_content = relationship("AIContent", back_populates="user")
    usage_tracking = relationship("UsageTracking", back_populates="user")
    conversions = relationship("Conversion", back_populates="user")
    
    # Performance optimization indexes
    __table_args__ = (
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_is_verified', 'is_verified'),
        Index('idx_users_company_name', 'company_name'),
        Index('idx_users_last_login', 'last_login')
    )

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Subscription Details
    tier = Column(Enum(SubscriptionTier), nullable=False)
    status = Column(String, default="active")  # active, cancelled, expired, trial
    
    # Pricing
    monthly_price = Column(Float)
    currency = Column(String, default="INR")
    
    # UPI Billing
    provider_subscription_id = Column(String)  # For UPI/Razorpay integration
    
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
    
    # Core Usage Metrics (aligned with pricing tiers)
    campaigns_created = Column(Integer, default=0)
    ai_generations_used = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)
    
    # Content Generation Breakdown
    images_generated = Column(Integer, default=0)
    videos_generated = Column(Integer, default=0)
    text_generations = Column(Integer, default=0)  # For captions, descriptions
    
    # Ad Spend Monitoring (new for tier enforcement)
    ad_spend_monitored = Column(Float, default=0.0)  # Total ad spend monitored this period
    
    # Feature Usage Tracking
    analytics_exports = Column(Integer, default=0)  # For business tier feature
    custom_reports_generated = Column(Integer, default=0)  # For business tier feature
    
    # Current Subscription Tier (cached for performance)
    current_tier = Column(String)  # basic, professional, business
    
    # Period Configuration
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    billing_cycle = Column(String, default="monthly")  # monthly, yearly
    
    # Reset tracking
    reset_count = Column(Integer, default=0)  # How many times usage was reset
    last_reset_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="usage_tracking")
    
    # Performance optimization indexes and constraints
    __table_args__ = (
        Index('idx_usage_tracking_user_id', 'user_id'),
        Index('idx_usage_tracking_period_start', 'period_start'),
        Index('idx_usage_tracking_current_tier', 'current_tier'),
        Index('idx_usage_tracking_user_period', 'user_id', 'period_start'),
        Index('idx_usage_tracking_billing_cycle', 'billing_cycle'),
        UniqueConstraint('user_id', 'period_start', name='uq_usage_tracking_user_period'),
        CheckConstraint('campaigns_created >= 0', name='chk_usage_tracking_campaigns_positive'),
        CheckConstraint('ai_generations_used >= 0', name='chk_usage_tracking_ai_generations_positive'),
        CheckConstraint('ad_spend_monitored >= 0', name='chk_usage_tracking_ad_spend_positive'),
    )

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
    
    # Performance optimization indexes and constraints
    __table_args__ = (
        Index('idx_campaigns_user_id', 'user_id'),
        Index('idx_campaigns_status', 'status'),
        Index('idx_campaigns_created_at', 'created_at'),
        Index('idx_campaigns_user_status', 'user_id', 'status'),
        Index('idx_campaigns_user_created', 'user_id', 'created_at'),
        CheckConstraint('budget_daily >= 0', name='chk_campaigns_budget_daily_positive'),
        CheckConstraint('budget_total >= 0', name='chk_campaigns_budget_total_positive'),
        CheckConstraint('impressions >= 0', name='chk_campaigns_impressions_positive'),
        CheckConstraint('clicks >= 0', name='chk_campaigns_clicks_positive'),
        CheckConstraint('spend >= 0', name='chk_campaigns_spend_positive'),
        CheckConstraint('conversions >= 0', name='chk_campaigns_conversions_positive')
    )

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
    currency = Column(String, default="INR")
    
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
    
    # Performance optimization indexes and constraints
    __table_args__ = (
        Index('idx_analytics_campaign_date', 'campaign_id', 'date'),
        Index('idx_analytics_user_date', 'user_id', 'date'),
        Index('idx_analytics_date', 'date'),
        Index('idx_analytics_campaign_id', 'campaign_id'),
        Index('idx_analytics_user_id', 'user_id'),
        UniqueConstraint('campaign_id', 'date', name='uq_analytics_campaign_date'),
        CheckConstraint('impressions >= 0', name='chk_analytics_impressions_positive'),
        CheckConstraint('clicks >= 0', name='chk_analytics_clicks_positive'),
        CheckConstraint('spend >= 0', name='chk_analytics_spend_positive'),
        CheckConstraint('conversions >= 0', name='chk_analytics_conversions_positive'),
        CheckConstraint('revenue >= 0', name='chk_analytics_revenue_positive')
    )

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


class ViralTrend(Base):
    __tablename__ = "viral_trends"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Trend Details
    topic = Column(String, nullable=False)
    industry = Column(String)
    platform = Column(String)  # instagram, facebook
    
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

# Payment and Billing Models for Google Pay Integration

class PaymentProvider(PyEnum):
    UPI = "upi"
    GOOGLE_PAY = "google_pay"
    RAZORPAY = "razorpay"
    PAYU = "payu"
    CASHFREE = "cashfree"

class PaymentStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"

class SubscriptionStatus(PyEnum):
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    EXPIRED = "expired"

class BillingSubscription(Base):
    __tablename__ = "billing_subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Subscription Details
    tier = Column(Enum(SubscriptionTier), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    
    # Pricing
    monthly_price = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    
    # Trial Information
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    is_trial = Column(Boolean, default=True)
    
    # Billing Cycle
    billing_cycle_start = Column(DateTime)
    next_billing_date = Column(DateTime)
    
    # Payment Provider Integration
    provider = Column(Enum(PaymentProvider), default=PaymentProvider.UPI)
    provider_subscription_id = Column(String)  # UPI/Razorpay subscription ID
    
    # Usage Limits
    max_campaigns = Column(Integer)
    max_ai_generations = Column(Integer)
    max_api_calls = Column(Integer)
    analytics_retention_days = Column(Integer, default=30)
    
    # Current Period Usage
    campaigns_used = Column(Integer, default=0)
    ai_generations_used = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    canceled_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="billing_subscriptions")
    payments = relationship("Payment", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")
    
    # Performance optimization indexes and constraints
    __table_args__ = (
        Index('idx_billing_subscriptions_user_id', 'user_id'),
        Index('idx_billing_subscriptions_status', 'status'),
        Index('idx_billing_subscriptions_tier', 'tier'),
        Index('idx_billing_subscriptions_user_status', 'user_id', 'status'),
        Index('idx_billing_subscriptions_next_billing_date', 'next_billing_date'),
        Index('idx_billing_subscriptions_expires_at', 'expires_at'),
        CheckConstraint('monthly_price > 0', name='chk_billing_subscriptions_monthly_price_positive'),
        CheckConstraint('max_campaigns >= 0', name='chk_billing_subscriptions_max_campaigns_positive'),
        CheckConstraint('max_ai_generations >= 0', name='chk_billing_subscriptions_max_ai_generations_positive'),
        CheckConstraint('max_api_calls >= 0', name='chk_billing_subscriptions_max_api_calls_positive')
    )

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("billing_subscriptions.id"))
    
    # Payment Details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    description = Column(String)
    
    # Payment Provider Information
    provider = Column(Enum(PaymentProvider), nullable=False)
    provider_payment_id = Column(String)  # UPI/Razorpay payment ID
    provider_transaction_id = Column(String)
    
    # UPI specific fields
    upi_transaction_id = Column(String)
    upi_vpa = Column(String)  # Virtual Payment Address
    
    # Status and Processing
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    failure_reason = Column(String)
    failure_code = Column(String)
    
    # Customer Information
    customer_email = Column(String)
    billing_address = Column(JSON)  # Billing address details
    
    # Transaction Metadata
    transaction_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("BillingSubscription", back_populates="payments")
    
    # Performance optimization indexes and constraints
    __table_args__ = (
        Index('idx_payments_user_id', 'user_id'),
        Index('idx_payments_status', 'status'),
        Index('idx_payments_user_status', 'user_id', 'status'),
        Index('idx_payments_created_at', 'created_at'),
        Index('idx_payments_provider', 'provider'),
        Index('idx_payments_provider_payment_id', 'provider_payment_id'),
        CheckConstraint('amount > 0', name='chk_payments_amount_positive')
    )

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("billing_subscriptions.id"), nullable=False)
    payment_id = Column(String, ForeignKey("payments.id"))
    
    # Invoice Details
    invoice_number = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    
    # Billing Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Invoice Status
    status = Column(String, default="draft")  # draft, open, paid, void, uncollectible
    
    # Line Items (JSON array)
    line_items = Column(JSON)
    
    # Tax and Discounts
    subtotal = Column(Float)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    due_date = Column(DateTime)
    paid_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="invoices")
    subscription = relationship("BillingSubscription", back_populates="invoices")
    payment = relationship("Payment")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Payment Method Details
    provider = Column(Enum(PaymentProvider), nullable=False)
    provider_method_id = Column(String)  # Provider's payment method ID
    
    # Method Type and Details
    type = Column(String)  # card, bank_account, google_pay, etc.
    card_last4 = Column(String)
    card_brand = Column(String)
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)
    
    # Google Pay specific
    google_pay_merchant_id = Column(String)
    google_pay_gateway = Column(String)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payment_methods")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Webhook Details
    provider = Column(Enum(PaymentProvider), nullable=False)
    event_type = Column(String, nullable=False)
    provider_event_id = Column(String, unique=True)
    
    # Event Data
    data = Column(JSON, nullable=False)
    
    # Processing Status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    error_message = Column(String)
    
    # Request Information
    request_headers = Column(JSON)
    request_signature = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Related Objects
    user_id = Column(String, ForeignKey("users.id"))
    payment_id = Column(String, ForeignKey("payments.id"))
    subscription_id = Column(String, ForeignKey("billing_subscriptions.id"))


# Enhanced Personalization Models

class BusinessSizeEnum(PyEnum):
    STARTUP = "startup"
    SMB = "smb" 
    ENTERPRISE = "enterprise"

class BudgetRangeEnum(PyEnum):
    MICRO = "micro"      # ₹5,000-₹10,000/month
    SMALL = "small"      # ₹10,000-₹25,000/month  
    MEDIUM = "medium"    # ₹25,000-₹50,000/month
    LARGE = "large"      # ₹50,000-₹1,00,000/month
    ENTERPRISE = "enterprise"  # ₹1,00,000+/month

class AgeGroupEnum(PyEnum):
    GEN_Z = "gen_z"           # 16-26
    MILLENNIAL = "millennial"  # 27-42
    GEN_X = "gen_x"           # 43-58
    BOOMER = "boomer"         # 59-77

class BrandVoiceEnum(PyEnum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"
    LUXURY = "luxury"
    AUTHENTIC = "authentic"
    BOLD = "bold"

class CampaignObjectiveEnum(PyEnum):
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    APP_INSTALLS = "app_installs"

class ContentPreferenceEnum(PyEnum):
    VIDEO_FIRST = "video_first"
    IMAGE_HEAVY = "image_heavy"
    TEXT_FOCUSED = "text_focused"
    MIXED = "mixed"

class PlatformPriorityEnum(PyEnum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class MetaUserProfile(Base):
    """Enhanced user profile for deep personalization"""
    __tablename__ = "meta_user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Business Information
    business_size = Column(Enum(BusinessSizeEnum))
    industry = Column(String, nullable=False)
    business_name = Column(String)
    website_url = Column(String)
    years_in_business = Column(Integer)
    
    # Marketing Budget & Goals
    monthly_budget = Column(Enum(BudgetRangeEnum))
    primary_objective = Column(Enum(CampaignObjectiveEnum))
    secondary_objectives = Column(JSON)  # List of secondary objectives
    
    # Target Demographics
    target_age_groups = Column(JSON)  # List of age groups
    target_locations = Column(JSON)  # Geographic targeting
    target_interests = Column(JSON)  # List of interests
    target_behaviors = Column(JSON)  # List of behaviors
    
    # Brand & Content Preferences
    brand_voice = Column(Enum(BrandVoiceEnum), default=BrandVoiceEnum.PROFESSIONAL)
    content_preference = Column(Enum(ContentPreferenceEnum), default=ContentPreferenceEnum.MIXED)
    platform_priorities = Column(JSON)  # List of platform priorities
    brand_colors = Column(JSON)  # Hex color codes
    
    # Performance Preferences
    roi_focus = Column(Boolean, default=True)
    risk_tolerance = Column(String, default="medium")  # conservative, medium, aggressive
    automation_level = Column(String, default="medium")  # low, medium, high
    
    # Learning Data
    campaign_history = Column(JSON)
    performance_patterns = Column(JSON)
    learned_preferences = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_campaign = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="meta_profile")
    campaign_recommendations = relationship("CampaignRecommendation", back_populates="user_profile")
    ab_tests = relationship("ABTest", back_populates="user_profile")
    learning_insights = relationship("LearningInsight", back_populates="user_profile")
    
    # Performance optimization indexes
    __table_args__ = (
        Index('idx_meta_user_profiles_user_id', 'user_id'),
        Index('idx_meta_user_profiles_industry', 'industry'),
        Index('idx_meta_user_profiles_business_size', 'business_size'),
        Index('idx_meta_user_profiles_monthly_budget', 'monthly_budget'),
        Index('idx_meta_user_profiles_primary_objective', 'primary_objective'),
        Index('idx_meta_user_profiles_updated_at', 'updated_at'),
    )

class CampaignRecommendation(Base):
    """Personalized campaign recommendations"""
    __tablename__ = "campaign_recommendations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recommendation_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_profile_id = Column(String, ForeignKey("meta_user_profiles.id"))
    
    # Campaign Details
    recommended_type = Column(String, nullable=False)
    campaign_name = Column(String, nullable=False)
    description = Column(Text)
    reasoning = Column(Text)
    
    # Content Specifications
    content_prompts = Column(JSON)  # List of content prompts
    caption_templates = Column(JSON)  # List of caption templates
    visual_style = Column(String)
    content_type = Column(String)  # image, video, carousel
    
    # Targeting & Budget
    recommended_budget = Column(Float)
    target_audience = Column(JSON)
    platform_allocation = Column(JSON)  # Platform -> budget percentage
    
    # Performance Predictions
    predicted_ctr = Column(Float)
    predicted_engagement_rate = Column(Float)
    predicted_conversion_rate = Column(Float)
    predicted_roi = Column(Float)
    confidence_score = Column(Float)  # 0-1
    
    # A/B Testing Variants
    ab_variants = Column(JSON)
    
    # Status and Usage
    is_implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    actual_performance = Column(JSON)  # Track actual vs predicted
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)
    
    # Relationships
    user_profile = relationship("MetaUserProfile", back_populates="campaign_recommendations")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_campaign_recommendations_user_id', 'user_id'),
        Index('idx_campaign_recommendations_recommended_type', 'recommended_type'),
        Index('idx_campaign_recommendations_confidence_score', 'confidence_score'),
        Index('idx_campaign_recommendations_created_at', 'created_at'),
        Index('idx_campaign_recommendations_is_implemented', 'is_implemented'),
        CheckConstraint('recommended_budget >= 0', name='chk_campaign_recommendations_budget_positive'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='chk_campaign_recommendations_confidence_range'),
    )

# A/B Testing Framework Models

class TestStatusEnum(PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TestTypeEnum(PyEnum):
    SIMPLE_AB = "simple_ab"
    MULTIVARIATE = "multivariate"
    SPLIT_URL = "split_url"
    CONTENT_VARIATION = "content_variation"

class StatisticalSignificanceEnum(PyEnum):
    NOT_SIGNIFICANT = "not_significant"
    APPROACHING = "approaching"
    SIGNIFICANT = "significant"
    HIGHLY_SIGNIFICANT = "highly_significant"

class ABTest(Base):
    """A/B test configuration and management"""
    __tablename__ = "ab_tests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_profile_id = Column(String, ForeignKey("meta_user_profiles.id"))
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Test Configuration
    name = Column(String, nullable=False)
    description = Column(Text)
    test_type = Column(Enum(TestTypeEnum), default=TestTypeEnum.SIMPLE_AB)
    hypothesis = Column(Text)
    
    # Test Parameters
    confidence_threshold = Column(Float, default=0.95)  # 95% confidence
    min_sample_size = Column(Integer, default=1000)
    max_duration_days = Column(Integer, default=14)
    traffic_split = Column(JSON)  # Traffic allocation per variant
    
    # Status and Timing
    status = Column(Enum(TestStatusEnum), default=TestStatusEnum.DRAFT)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    
    # Results
    winning_variant_id = Column(String)
    confidence_level = Column(Float)
    significance_status = Column(Enum(StatisticalSignificanceEnum), default=StatisticalSignificanceEnum.NOT_SIGNIFICANT)
    p_value = Column(Float)
    effect_size = Column(Float)
    
    # Business Impact
    projected_lift = Column(Float)
    estimated_revenue_impact = Column(Float)
    actual_revenue_impact = Column(Float)
    
    # Recommendations
    recommendation = Column(Text)
    next_steps = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user_profile = relationship("MetaUserProfile", back_populates="ab_tests")
    campaign = relationship("Campaign")
    test_variations = relationship("TestVariation", back_populates="ab_test", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="ab_test", cascade="all, delete-orphan")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_ab_tests_user_id', 'user_id'),
        Index('idx_ab_tests_status', 'status'),
        Index('idx_ab_tests_test_type', 'test_type'),
        Index('idx_ab_tests_start_date', 'start_date'),
        Index('idx_ab_tests_significance_status', 'significance_status'),
        Index('idx_ab_tests_user_status', 'user_id', 'status'),
        CheckConstraint('confidence_threshold > 0 AND confidence_threshold < 1', name='chk_ab_tests_confidence_range'),
        CheckConstraint('min_sample_size > 0', name='chk_ab_tests_sample_size_positive'),
        CheckConstraint('max_duration_days > 0', name='chk_ab_tests_duration_positive'),
    )

class TestVariation(Base):
    """Individual A/B test variations"""
    __tablename__ = "test_variations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    variation_id = Column(String, nullable=False)
    ab_test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False)
    
    # Variation Details
    name = Column(String, nullable=False)
    description = Column(Text)
    traffic_percentage = Column(Float, nullable=False)
    
    # Content Configuration
    content_config = Column(JSON)
    
    # Performance Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Calculated Metrics
    ctr = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    revenue_per_visitor = Column(Float, default=0.0)
    
    # Statistical Analysis
    confidence_interval_lower = Column(Float, default=0.0)
    confidence_interval_upper = Column(Float, default=0.0)
    statistical_power = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    ab_test = relationship("ABTest", back_populates="test_variations")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_test_variations_ab_test_id', 'ab_test_id'),
        Index('idx_test_variations_variation_id', 'variation_id'),
        Index('idx_test_variations_conversion_rate', 'conversion_rate'),
        Index('idx_test_variations_ctr', 'ctr'),
        UniqueConstraint('ab_test_id', 'variation_id', name='uq_test_variations_test_variant'),
        CheckConstraint('traffic_percentage >= 0 AND traffic_percentage <= 100', name='chk_test_variations_traffic_range'),
        CheckConstraint('impressions >= 0', name='chk_test_variations_impressions_positive'),
        CheckConstraint('clicks >= 0', name='chk_test_variations_clicks_positive'),
        CheckConstraint('conversions >= 0', name='chk_test_variations_conversions_positive'),
    )

class TestResult(Base):
    """A/B test statistical results"""
    __tablename__ = "test_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ab_test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False)
    
    # Test Summary
    total_impressions = Column(Integer)
    total_conversions = Column(Integer)
    test_duration_days = Column(Integer)
    
    # Statistical Results
    p_value = Column(Float)
    effect_size = Column(Float)
    power_analysis = Column(JSON)
    
    # Winner Analysis
    winning_variation_id = Column(String)
    confidence_level = Column(Float)
    significance_status = Column(Enum(StatisticalSignificanceEnum))
    
    # Business Impact
    projected_lift = Column(Float)
    estimated_revenue_impact = Column(Float)
    
    # Detailed Analysis
    variation_comparisons = Column(JSON)  # Detailed comparison data
    statistical_details = Column(JSON)   # Additional statistical metrics
    
    # Recommendations
    recommendation = Column(Text)
    next_steps = Column(JSON)
    
    # Timestamps
    calculated_at = Column(DateTime, default=func.now())
    
    # Relationships
    ab_test = relationship("ABTest", back_populates="test_results")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_test_results_ab_test_id', 'ab_test_id'),
        Index('idx_test_results_significance_status', 'significance_status'),
        Index('idx_test_results_calculated_at', 'calculated_at'),
        Index('idx_test_results_confidence_level', 'confidence_level'),
    )

# Adaptive Learning System Models

class LearningInsight(Base):
    """Adaptive learning insights and patterns"""
    __tablename__ = "learning_insights"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    insight_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_profile_id = Column(String, ForeignKey("meta_user_profiles.id"))
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Insight Details
    insight_type = Column(String, nullable=False)  # performance, audience, content, timing
    category = Column(String)
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Performance Data
    baseline_metric = Column(Float)
    improved_metric = Column(Float)
    improvement_percentage = Column(Float)
    confidence_score = Column(Float)
    
    # Pattern Analysis
    identified_patterns = Column(JSON)
    contributing_factors = Column(JSON)
    correlation_data = Column(JSON)
    
    # Recommendations
    optimization_recommendations = Column(JSON)
    implementation_priority = Column(String)  # high, medium, low
    expected_impact = Column(String)  # high, medium, low
    
    # Learning Context
    sample_size = Column(Integer)
    time_period_days = Column(Integer)
    data_quality_score = Column(Float)
    
    # Status
    is_implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    actual_results = Column(JSON)
    
    # Timestamps
    discovered_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user_profile = relationship("MetaUserProfile", back_populates="learning_insights")
    campaign = relationship("Campaign")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_learning_insights_user_id', 'user_id'),
        Index('idx_learning_insights_insight_type', 'insight_type'),
        Index('idx_learning_insights_confidence_score', 'confidence_score'),
        Index('idx_learning_insights_improvement_percentage', 'improvement_percentage'),
        Index('idx_learning_insights_is_implemented', 'is_implemented'),
        Index('idx_learning_insights_discovered_at', 'discovered_at'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='chk_learning_insights_confidence_range'),
        CheckConstraint('sample_size >= 0', name='chk_learning_insights_sample_size_positive'),
    )

class PerformancePattern(Base):
    """Detected performance patterns for adaptive learning"""
    __tablename__ = "performance_patterns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Pattern Details
    pattern_type = Column(String, nullable=False)  # temporal, audience, content, budget
    pattern_name = Column(String, nullable=False)
    description = Column(Text)
    
    # Pattern Data
    pattern_conditions = Column(JSON)  # Conditions that trigger this pattern
    performance_impact = Column(JSON)  # Impact on various metrics
    frequency_observed = Column(Integer)  # How often this pattern occurs
    
    # Statistical Significance
    confidence_level = Column(Float)
    p_value = Column(Float)
    effect_size = Column(Float)
    
    # Learning Context
    campaigns_analyzed = Column(Integer)
    time_period_analyzed = Column(Integer)  # Days
    first_observed = Column(DateTime)
    last_observed = Column(DateTime)
    
    # Actionability
    actionable_insights = Column(JSON)
    automation_potential = Column(String)  # high, medium, low, none
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Performance optimization
    __table_args__ = (
        Index('idx_performance_patterns_user_id', 'user_id'),
        Index('idx_performance_patterns_pattern_type', 'pattern_type'),
        Index('idx_performance_patterns_confidence_level', 'confidence_level'),
        Index('idx_performance_patterns_frequency_observed', 'frequency_observed'),
        Index('idx_performance_patterns_last_observed', 'last_observed'),
        CheckConstraint('confidence_level >= 0 AND confidence_level <= 1', name='chk_performance_patterns_confidence_range'),
        CheckConstraint('frequency_observed >= 0', name='chk_performance_patterns_frequency_positive'),
    )

# Dynamic Content Generation Models

class ContentTemplate(Base):
    """Dynamic content templates for personalization"""
    __tablename__ = "content_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Template Details
    name = Column(String, nullable=False)
    description = Column(Text)
    template_type = Column(String, nullable=False)  # image, video, text, carousel
    category = Column(String)  # industry, objective, style
    
    # Template Configuration
    base_prompt = Column(Text, nullable=False)
    personalization_variables = Column(JSON)  # Variables that can be personalized
    style_parameters = Column(JSON)
    content_structure = Column(JSON)
    
    # Performance Tracking
    usage_count = Column(Integer, default=0)
    avg_performance_score = Column(Float)
    success_rate = Column(Float)  # Percentage of successful generations
    
    # Personalization Context
    target_industries = Column(JSON)
    target_objectives = Column(JSON)
    target_demographics = Column(JSON)
    
    # Template Metadata
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Available to all users
    created_by = Column(String)  # user_id or 'system'
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_used = Column(DateTime)
    
    # Performance optimization
    __table_args__ = (
        Index('idx_content_templates_user_id', 'user_id'),
        Index('idx_content_templates_template_type', 'template_type'),
        Index('idx_content_templates_category', 'category'),
        Index('idx_content_templates_avg_performance_score', 'avg_performance_score'),
        Index('idx_content_templates_usage_count', 'usage_count'),
        Index('idx_content_templates_is_active', 'is_active'),
        Index('idx_content_templates_is_public', 'is_public'),
        CheckConstraint('usage_count >= 0', name='chk_content_templates_usage_count_positive'),
        CheckConstraint('success_rate >= 0 AND success_rate <= 100', name='chk_content_templates_success_rate_range'),
    )

class PersonalizedContent(Base):
    """Generated personalized content instances"""
    __tablename__ = "personalized_content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    template_id = Column(String, ForeignKey("content_templates.id"))
    
    # Content Details
    content_type = Column(String, nullable=False)
    personalized_prompt = Column(Text, nullable=False)
    personalization_context = Column(JSON)  # Context used for personalization
    
    # Generated Content
    file_path = Column(String)
    file_url = Column(String)
    file_size = Column(Integer)
    content_metadata = Column(JSON)
    
    # Personalization Applied
    personalization_variables_used = Column(JSON)
    demographic_targeting = Column(JSON)
    behavioral_targeting = Column(JSON)
    contextual_targeting = Column(JSON)
    
    # Performance Tracking
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    engagement_score = Column(Float)
    performance_vs_template = Column(Float)  # Performance compared to template average
    
    # Generation Details
    model_used = Column(String)
    generation_time = Column(Float)
    generation_cost = Column(Float)
    quality_score = Column(Float)
    
    # Usage Status
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_used = Column(DateTime)
    
    # Relationships
    campaign = relationship("Campaign")
    template = relationship("ContentTemplate")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_personalized_content_user_id', 'user_id'),
        Index('idx_personalized_content_campaign_id', 'campaign_id'),
        Index('idx_personalized_content_template_id', 'template_id'),
        Index('idx_personalized_content_content_type', 'content_type'),
        Index('idx_personalized_content_engagement_score', 'engagement_score'),
        Index('idx_personalized_content_performance_vs_template', 'performance_vs_template'),
        Index('idx_personalized_content_created_at', 'created_at'),
        CheckConstraint('impressions >= 0', name='chk_personalized_content_impressions_positive'),
        CheckConstraint('clicks >= 0', name='chk_personalized_content_clicks_positive'),
        CheckConstraint('conversions >= 0', name='chk_personalized_content_conversions_positive'),
        CheckConstraint('usage_count >= 0', name='chk_personalized_content_usage_count_positive'),
    )

# ML Prediction Models

class MLPredictionType(PyEnum):
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    AUDIENCE_RESPONSE = "audience_response"
    CONTENT_EFFECTIVENESS = "content_effectiveness"
    BUDGET_OPTIMIZATION = "budget_optimization"
    VIRAL_POTENTIAL = "viral_potential"

class ConfidenceLevel(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class MLPredictionResult(Base):
    """AI-powered marketing prediction results from Claude ML predictor"""
    __tablename__ = "ml_prediction_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Prediction Configuration
    prediction_type = Column(Enum(MLPredictionType), nullable=False)
    input_features = Column(JSON, nullable=False)  # Campaign config or content config used for prediction
    model_version = Column(String, default="claude-3.5-sonnet-v1.0")
    
    # Prediction Results
    predicted_metrics = Column(JSON, nullable=False)  # roi, ctr, conversion_rate, engagement, etc.
    confidence_level = Column(Enum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM)
    confidence_score = Column(Float)  # 0-1 numeric confidence
    
    # AI Insights
    prediction_reasoning = Column(Text)  # Claude's explanation of the prediction
    key_factors = Column(JSON)  # List of key factors influencing prediction
    risk_factors = Column(JSON)  # List of potential risks
    optimization_opportunities = Column(JSON)  # List of optimization suggestions
    
    # Recommendations
    recommended_adjustments = Column(JSON)  # Specific recommended changes
    expected_outcomes = Column(JSON)  # Best/most likely/worst case scenarios
    
    # Performance Tracking
    actual_metrics = Column(JSON)  # Actual results when campaign completes
    prediction_accuracy_score = Column(Float)  # How accurate the prediction was
    
    # Caching and Invalidation
    cache_key = Column(String, index=True)  # For caching similar predictions
    expires_at = Column(DateTime)  # When prediction becomes stale
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    campaign = relationship("Campaign")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_ml_predictions_user_id', 'user_id'),
        Index('idx_ml_predictions_campaign_id', 'campaign_id'),
        Index('idx_ml_predictions_prediction_type', 'prediction_type'),
        Index('idx_ml_predictions_confidence_level', 'confidence_level'),
        Index('idx_ml_predictions_cache_key', 'cache_key'),
        Index('idx_ml_predictions_expires_at', 'expires_at'),
        Index('idx_ml_predictions_created_at', 'created_at'),
        Index('idx_ml_predictions_user_type', 'user_id', 'prediction_type'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='chk_ml_predictions_confidence_range'),
        CheckConstraint('prediction_accuracy_score >= 0 AND prediction_accuracy_score <= 1', name='chk_ml_predictions_accuracy_range'),
    )

class CampaignPredictionScenario(Base):
    """Alternative scenarios generated by ML predictor for campaign optimization"""
    __tablename__ = "campaign_prediction_scenarios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_result_id = Column(String, ForeignKey("ml_prediction_results.id"), nullable=False)
    scenario_id = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Scenario Details
    scenario_name = Column(String, nullable=False)  # budget_optimized, reach_maximized, etc.
    scenario_description = Column(Text)
    
    # Scenario Modifications
    scenario_modifications = Column(JSON)  # Changes from original campaign
    modified_metrics = Column(JSON)  # Predicted metrics for this scenario
    
    # Scenario Analysis
    scenario_reasoning = Column(Text)  # Why this scenario would work
    key_benefits = Column(JSON)  # Benefits of this approach
    potential_drawbacks = Column(JSON)  # Risks or limitations
    
    # Implementation
    is_recommended = Column(Boolean, default=False)
    priority_ranking = Column(Integer)  # 1-10 ranking among scenarios
    implementation_difficulty = Column(String)  # easy, medium, hard
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    prediction_result = relationship("MLPredictionResult", backref="scenarios")
    user = relationship("User")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_campaign_scenarios_prediction_result_id', 'prediction_result_id'),
        Index('idx_campaign_scenarios_user_id', 'user_id'),
        Index('idx_campaign_scenarios_scenario_name', 'scenario_name'),
        Index('idx_campaign_scenarios_is_recommended', 'is_recommended'),
        Index('idx_campaign_scenarios_priority_ranking', 'priority_ranking'),
    )

class MLPredictionCache(Base):
    """Caching table for ML predictions to avoid repeated expensive API calls"""
    __tablename__ = "ml_prediction_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Cache Content
    prediction_type = Column(Enum(MLPredictionType), nullable=False)
    input_hash = Column(String, nullable=False, index=True)  # Hash of input parameters
    prediction_data = Column(JSON, nullable=False)  # Cached prediction result
    
    # Cache Metadata
    model_version = Column(String)
    generation_cost = Column(Float)  # API cost for this prediction
    generation_time = Column(Float)  # Time taken to generate (seconds)
    
    # Cache Management
    hit_count = Column(Integer, default=0)  # How many times this cache entry was used
    last_accessed = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_ml_cache_cache_key', 'cache_key'),
        Index('idx_ml_cache_input_hash', 'input_hash'),
        Index('idx_ml_cache_user_id', 'user_id'),
        Index('idx_ml_cache_prediction_type', 'prediction_type'),
        Index('idx_ml_cache_expires_at', 'expires_at'),
        Index('idx_ml_cache_last_accessed', 'last_accessed'),
        Index('idx_ml_cache_user_type', 'user_id', 'prediction_type'),
        CheckConstraint('hit_count >= 0', name='chk_ml_cache_hit_count_positive'),
        CheckConstraint('generation_cost >= 0', name='chk_ml_cache_cost_positive'),
        CheckConstraint('generation_time >= 0', name='chk_ml_cache_time_positive'),
    )

class MLPredictionFeedback(Base):
    """User feedback on ML predictions for improving accuracy"""
    __tablename__ = "ml_prediction_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_result_id = Column(String, ForeignKey("ml_prediction_results.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Feedback Details
    accuracy_rating = Column(Integer)  # 1-5 rating of prediction accuracy
    usefulness_rating = Column(Integer)  # 1-5 rating of prediction usefulness
    followed_recommendations = Column(Boolean)  # Whether user followed the recommendations
    
    # Feedback Content
    feedback_text = Column(Text)  # Optional text feedback
    specific_issues = Column(JSON)  # Specific problems with the prediction
    suggestions = Column(JSON)  # User suggestions for improvement
    
    # Outcome Data
    actual_campaign_results = Column(JSON)  # Actual results vs predictions
    outcome_satisfaction = Column(Integer)  # 1-5 satisfaction with actual outcome
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    prediction_result = relationship("MLPredictionResult", backref="feedback")
    user = relationship("User")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_ml_feedback_prediction_result_id', 'prediction_result_id'),
        Index('idx_ml_feedback_user_id', 'user_id'),
        Index('idx_ml_feedback_accuracy_rating', 'accuracy_rating'),
        Index('idx_ml_feedback_usefulness_rating', 'usefulness_rating'),
        Index('idx_ml_feedback_created_at', 'created_at'),
        CheckConstraint('accuracy_rating >= 1 AND accuracy_rating <= 5', name='chk_ml_feedback_accuracy_range'),
        CheckConstraint('usefulness_rating >= 1 AND usefulness_rating <= 5', name='chk_ml_feedback_usefulness_range'),
        CheckConstraint('outcome_satisfaction >= 1 AND outcome_satisfaction <= 5', name='chk_ml_feedback_satisfaction_range'),
    )

# Enhanced Campaign Personalization Models

class CampaignPersonalizationSettings(Base):
    """Detailed personalization settings for campaigns"""
    __tablename__ = "campaign_personalization_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, unique=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Personalization Configuration
    personalization_level = Column(String, default="medium")  # low, medium, high, maximum
    auto_optimization_enabled = Column(Boolean, default=True)
    dynamic_content_enabled = Column(Boolean, default=True)
    adaptive_bidding_enabled = Column(Boolean, default=True)
    
    # Targeting Personalization
    audience_personalization = Column(JSON)  # Personalized audience settings
    demographic_weights = Column(JSON)  # Weights for different demographics
    behavioral_triggers = Column(JSON)  # Behavioral targeting triggers
    
    # Content Personalization
    content_rotation_strategy = Column(String, default="performance_based")
    personalized_templates = Column(JSON)  # Template IDs for this campaign
    dynamic_elements = Column(JSON)  # Elements that change based on user data
    
    # Budget & Bidding Personalization
    budget_allocation_strategy = Column(JSON)
    bid_adjustments = Column(JSON)  # Personalized bid adjustments
    performance_targets = Column(JSON)  # Personalized performance targets
    
    # Learning & Optimization
    learning_priority = Column(String, default="medium")  # high, medium, low
    optimization_frequency = Column(String, default="daily")  # hourly, daily, weekly
    performance_thresholds = Column(JSON)  # Thresholds for automatic actions
    
    # Advanced Features
    ab_testing_enabled = Column(Boolean, default=True)
    predictive_scaling_enabled = Column(Boolean, default=False)
    real_time_optimization = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", backref="personalization_settings")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_campaign_personalization_campaign_id', 'campaign_id'),
        Index('idx_campaign_personalization_user_id', 'user_id'),
        Index('idx_campaign_personalization_personalization_level', 'personalization_level'),
        Index('idx_campaign_personalization_auto_optimization_enabled', 'auto_optimization_enabled'),
    )


# Budget Safety and Monitoring Models

class BudgetAlert(Base):
    """Budget alerts and spending monitoring"""
    __tablename__ = "budget_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Alert Details
    alert_type = Column(String, nullable=False)  # budget_exceeded, spending_high, limit_approached
    severity = Column(String, default="medium")  # low, medium, high, critical
    
    # Alert Content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Spending Details
    current_spending = Column(Float)
    budget_limit = Column(Float)
    spending_percentage = Column(Float)
    
    # Alert Status
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    
    # Actions Taken
    actions_taken = Column(JSON)  # List of automated actions
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    campaign = relationship("Campaign")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_budget_alerts_user_id', 'user_id'),
        Index('idx_budget_alerts_campaign_id', 'campaign_id'),
        Index('idx_budget_alerts_alert_type', 'alert_type'),
        Index('idx_budget_alerts_severity', 'severity'),
        Index('idx_budget_alerts_is_acknowledged', 'is_acknowledged'),
        Index('idx_budget_alerts_is_resolved', 'is_resolved'),
        Index('idx_budget_alerts_created_at', 'created_at'),
        CheckConstraint('current_spending >= 0', name='chk_budget_alerts_spending_positive'),
        CheckConstraint('budget_limit > 0', name='chk_budget_alerts_limit_positive'),
        CheckConstraint('spending_percentage >= 0 AND spending_percentage <= 200', name='chk_budget_alerts_percentage_range'),
    )


class SpendingLimit(Base):
    """User-defined spending limits and controls"""
    __tablename__ = "spending_limits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Limit Configuration
    limit_type = Column(String, nullable=False)  # daily, weekly, monthly, campaign, total
    limit_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Scope
    applies_to = Column(String, default="all")  # all, campaign_id, platform
    target_id = Column(String)  # Specific campaign ID or platform
    
    # Alert Thresholds
    warning_threshold = Column(Float, default=80.0)  # Percentage at which to warn
    critical_threshold = Column(Float, default=95.0)  # Percentage at which to alert
    
    # Actions
    auto_pause_at_limit = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_spending_limits_user_id', 'user_id'),
        Index('idx_spending_limits_limit_type', 'limit_type'),
        Index('idx_spending_limits_is_active', 'is_active'),
        Index('idx_spending_limits_user_active', 'user_id', 'is_active'),
        CheckConstraint('limit_amount > 0', name='chk_spending_limits_amount_positive'),
        CheckConstraint('warning_threshold >= 0 AND warning_threshold <= 100', name='chk_spending_limits_warning_range'),
        CheckConstraint('critical_threshold >= 0 AND critical_threshold <= 100', name='chk_spending_limits_critical_range'),
    )


class BudgetTransaction(Base):
    """Track all budget-related transactions and movements"""
    __tablename__ = "budget_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    
    # Transaction Details
    transaction_type = Column(String, nullable=False)  # allocation, spend, refund, adjustment
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Context
    description = Column(String)
    reference_id = Column(String)  # External reference (Meta transaction ID, etc.)
    
    # Balances (before and after transaction)
    balance_before = Column(Float)
    balance_after = Column(Float)
    
    # Transaction metadata
    transaction_meta = Column(JSON)
    
    # Status
    status = Column(String, default="completed")  # pending, completed, failed, reversed
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    campaign = relationship("Campaign")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_budget_transactions_user_id', 'user_id'),
        Index('idx_budget_transactions_campaign_id', 'campaign_id'),
        Index('idx_budget_transactions_transaction_type', 'transaction_type'),
        Index('idx_budget_transactions_status', 'status'),
        Index('idx_budget_transactions_created_at', 'created_at'),
        Index('idx_budget_transactions_user_created', 'user_id', 'created_at'),
        CheckConstraint('amount != 0', name='chk_budget_transactions_amount_nonzero'),
    )


class RateLimitRecord(Base):
    """Track API rate limiting per user"""
    __tablename__ = "rate_limit_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Rate Limit Details
    endpoint = Column(String, nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Limits
    requests_made = Column(Integer, default=1)
    requests_limit = Column(Integer, nullable=False)
    window_start = Column(DateTime, nullable=False)
    window_duration_minutes = Column(Integer, default=60)
    
    # Status
    is_blocked = Column(Boolean, default=False)
    blocked_until = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    # Performance optimization
    __table_args__ = (
        Index('idx_rate_limit_records_user_id', 'user_id'),
        Index('idx_rate_limit_records_endpoint', 'endpoint'),
        Index('idx_rate_limit_records_ip_address', 'ip_address'),
        Index('idx_rate_limit_records_window_start', 'window_start'),
        Index('idx_rate_limit_records_is_blocked', 'is_blocked'),
        Index('idx_rate_limit_records_user_endpoint', 'user_id', 'endpoint'),
        UniqueConstraint('user_id', 'endpoint', 'window_start', name='uq_rate_limit_user_endpoint_window'),
        CheckConstraint('requests_made >= 0', name='chk_rate_limit_requests_positive'),
        CheckConstraint('requests_limit > 0', name='chk_rate_limit_limit_positive'),
    )