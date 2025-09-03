"""Add database indexes and constraints for performance optimization

Revision ID: 001
Revises: 
Create Date: 2025-09-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes and constraints for performance optimization."""
    
    # Users table indexes
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_is_verified', 'users', ['is_verified'])
    op.create_index('idx_users_company_name', 'users', ['company_name'])
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    
    # Campaigns table indexes and constraints
    op.create_index('idx_campaigns_user_id', 'campaigns', ['user_id'])
    op.create_index('idx_campaigns_status', 'campaigns', ['status'])
    op.create_index('idx_campaigns_created_at', 'campaigns', ['created_at'])
    op.create_index('idx_campaigns_user_status', 'campaigns', ['user_id', 'status'])
    op.create_index('idx_campaigns_user_created', 'campaigns', ['user_id', 'created_at'])
    
    # Campaigns check constraints
    op.create_check_constraint('chk_campaigns_budget_daily_positive', 'campaigns', 'budget_daily >= 0')
    op.create_check_constraint('chk_campaigns_budget_total_positive', 'campaigns', 'budget_total >= 0')
    op.create_check_constraint('chk_campaigns_impressions_positive', 'campaigns', 'impressions >= 0')
    op.create_check_constraint('chk_campaigns_clicks_positive', 'campaigns', 'clicks >= 0')
    op.create_check_constraint('chk_campaigns_spend_positive', 'campaigns', 'spend >= 0')
    op.create_check_constraint('chk_campaigns_conversions_positive', 'campaigns', 'conversions >= 0')
    
    # Analytics table indexes and constraints
    op.create_index('idx_analytics_campaign_date', 'analytics', ['campaign_id', 'date'])
    op.create_index('idx_analytics_user_date', 'analytics', ['user_id', 'date'])
    op.create_index('idx_analytics_date', 'analytics', ['date'])
    op.create_index('idx_analytics_campaign_id', 'analytics', ['campaign_id'])
    op.create_index('idx_analytics_user_id', 'analytics', ['user_id'])
    
    # Analytics unique constraint and check constraints
    op.create_unique_constraint('uq_analytics_campaign_date', 'analytics', ['campaign_id', 'date'])
    op.create_check_constraint('chk_analytics_impressions_positive', 'analytics', 'impressions >= 0')
    op.create_check_constraint('chk_analytics_clicks_positive', 'analytics', 'clicks >= 0')
    op.create_check_constraint('chk_analytics_spend_positive', 'analytics', 'spend >= 0')
    op.create_check_constraint('chk_analytics_conversions_positive', 'analytics', 'conversions >= 0')
    op.create_check_constraint('chk_analytics_revenue_positive', 'analytics', 'revenue >= 0')
    
    # Payments table indexes and constraints
    op.create_index('idx_payments_user_id', 'payments', ['user_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_user_status', 'payments', ['user_id', 'status'])
    op.create_index('idx_payments_created_at', 'payments', ['created_at'])
    op.create_index('idx_payments_provider', 'payments', ['provider'])
    op.create_index('idx_payments_provider_payment_id', 'payments', ['provider_payment_id'])
    
    # Payments check constraints
    op.create_check_constraint('chk_payments_amount_positive', 'payments', 'amount > 0')
    
    # Billing Subscriptions table indexes and constraints
    op.create_index('idx_billing_subscriptions_user_id', 'billing_subscriptions', ['user_id'])
    op.create_index('idx_billing_subscriptions_status', 'billing_subscriptions', ['status'])
    op.create_index('idx_billing_subscriptions_tier', 'billing_subscriptions', ['tier'])
    op.create_index('idx_billing_subscriptions_user_status', 'billing_subscriptions', ['user_id', 'status'])
    op.create_index('idx_billing_subscriptions_next_billing_date', 'billing_subscriptions', ['next_billing_date'])
    op.create_index('idx_billing_subscriptions_expires_at', 'billing_subscriptions', ['expires_at'])
    
    # Billing Subscriptions check constraints
    op.create_check_constraint('chk_billing_subscriptions_monthly_price_positive', 'billing_subscriptions', 'monthly_price > 0')
    op.create_check_constraint('chk_billing_subscriptions_max_campaigns_positive', 'billing_subscriptions', 'max_campaigns >= 0')
    op.create_check_constraint('chk_billing_subscriptions_max_ai_generations_positive', 'billing_subscriptions', 'max_ai_generations >= 0')
    op.create_check_constraint('chk_billing_subscriptions_max_api_calls_positive', 'billing_subscriptions', 'max_api_calls >= 0')
    
    # Competitor Content table indexes and constraints
    op.create_index('idx_competitor_content_competitor_name', 'competitor_content', ['competitor_name'])
    op.create_index('idx_competitor_content_platform', 'competitor_content', ['platform'])
    op.create_index('idx_competitor_content_content_type', 'competitor_content', ['content_type'])
    op.create_index('idx_competitor_content_user_id', 'competitor_content', ['user_id'])
    op.create_index('idx_competitor_content_discovered_at', 'competitor_content', ['discovered_at'])
    op.create_index('idx_competitor_content_performance_score', 'competitor_content', ['performance_score'])
    
    # Competitor Content unique constraint and check constraints
    op.create_unique_constraint('uq_competitor_content_name_url', 'competitor_content', ['competitor_name', 'content_url'])
    op.create_check_constraint('chk_competitor_content_likes_positive', 'competitor_content', 'likes >= 0')
    op.create_check_constraint('chk_competitor_content_comments_positive', 'competitor_content', 'comments >= 0')
    op.create_check_constraint('chk_competitor_content_shares_positive', 'competitor_content', 'shares >= 0')
    op.create_check_constraint('chk_competitor_content_performance_score_positive', 'competitor_content', 'performance_score >= 0')


def downgrade():
    """Remove indexes and constraints."""
    
    # Drop Competitor Content constraints and indexes
    op.drop_constraint('chk_competitor_content_performance_score_positive', 'competitor_content')
    op.drop_constraint('chk_competitor_content_shares_positive', 'competitor_content')
    op.drop_constraint('chk_competitor_content_comments_positive', 'competitor_content')
    op.drop_constraint('chk_competitor_content_likes_positive', 'competitor_content')
    op.drop_constraint('uq_competitor_content_name_url', 'competitor_content')
    
    op.drop_index('idx_competitor_content_performance_score', 'competitor_content')
    op.drop_index('idx_competitor_content_discovered_at', 'competitor_content')
    op.drop_index('idx_competitor_content_user_id', 'competitor_content')
    op.drop_index('idx_competitor_content_content_type', 'competitor_content')
    op.drop_index('idx_competitor_content_platform', 'competitor_content')
    op.drop_index('idx_competitor_content_competitor_name', 'competitor_content')
    
    # Drop Billing Subscriptions constraints and indexes
    op.drop_constraint('chk_billing_subscriptions_max_api_calls_positive', 'billing_subscriptions')
    op.drop_constraint('chk_billing_subscriptions_max_ai_generations_positive', 'billing_subscriptions')
    op.drop_constraint('chk_billing_subscriptions_max_campaigns_positive', 'billing_subscriptions')
    op.drop_constraint('chk_billing_subscriptions_monthly_price_positive', 'billing_subscriptions')
    
    op.drop_index('idx_billing_subscriptions_expires_at', 'billing_subscriptions')
    op.drop_index('idx_billing_subscriptions_next_billing_date', 'billing_subscriptions')
    op.drop_index('idx_billing_subscriptions_user_status', 'billing_subscriptions')
    op.drop_index('idx_billing_subscriptions_tier', 'billing_subscriptions')
    op.drop_index('idx_billing_subscriptions_status', 'billing_subscriptions')
    op.drop_index('idx_billing_subscriptions_user_id', 'billing_subscriptions')
    
    # Drop Payments constraints and indexes
    op.drop_constraint('chk_payments_amount_positive', 'payments')
    
    op.drop_index('idx_payments_provider_payment_id', 'payments')
    op.drop_index('idx_payments_provider', 'payments')
    op.drop_index('idx_payments_created_at', 'payments')
    op.drop_index('idx_payments_user_status', 'payments')
    op.drop_index('idx_payments_status', 'payments')
    op.drop_index('idx_payments_user_id', 'payments')
    
    # Drop Analytics constraints and indexes
    op.drop_constraint('chk_analytics_revenue_positive', 'analytics')
    op.drop_constraint('chk_analytics_conversions_positive', 'analytics')
    op.drop_constraint('chk_analytics_spend_positive', 'analytics')
    op.drop_constraint('chk_analytics_clicks_positive', 'analytics')
    op.drop_constraint('chk_analytics_impressions_positive', 'analytics')
    op.drop_constraint('uq_analytics_campaign_date', 'analytics')
    
    op.drop_index('idx_analytics_user_id', 'analytics')
    op.drop_index('idx_analytics_campaign_id', 'analytics')
    op.drop_index('idx_analytics_date', 'analytics')
    op.drop_index('idx_analytics_user_date', 'analytics')
    op.drop_index('idx_analytics_campaign_date', 'analytics')
    
    # Drop Campaigns constraints and indexes
    op.drop_constraint('chk_campaigns_conversions_positive', 'campaigns')
    op.drop_constraint('chk_campaigns_spend_positive', 'campaigns')
    op.drop_constraint('chk_campaigns_clicks_positive', 'campaigns')
    op.drop_constraint('chk_campaigns_impressions_positive', 'campaigns')
    op.drop_constraint('chk_campaigns_budget_total_positive', 'campaigns')
    op.drop_constraint('chk_campaigns_budget_daily_positive', 'campaigns')
    
    op.drop_index('idx_campaigns_user_created', 'campaigns')
    op.drop_index('idx_campaigns_user_status', 'campaigns')
    op.drop_index('idx_campaigns_created_at', 'campaigns')
    op.drop_index('idx_campaigns_status', 'campaigns')
    op.drop_index('idx_campaigns_user_id', 'campaigns')
    
    # Drop Users indexes
    op.drop_index('idx_users_last_login', 'users')
    op.drop_index('idx_users_company_name', 'users')
    op.drop_index('idx_users_is_verified', 'users')
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_created_at', 'users')