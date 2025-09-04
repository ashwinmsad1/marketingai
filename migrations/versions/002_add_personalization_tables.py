"""Add comprehensive personalization tables and features

Revision ID: 002
Revises: 001
Create Date: 2025-09-04 16:30:00.000000

This migration adds all the new personalization features including:
- Enhanced user profiling with MetaUserProfile
- A/B testing framework tables
- Adaptive learning system tables  
- Dynamic content generation tables
- Campaign personalization settings

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add all personalization tables and features."""
    
    # Create enum types
    op.execute("""
        CREATE TYPE businesssizeenum AS ENUM ('startup', 'smb', 'enterprise');
        CREATE TYPE budgetrangeenum AS ENUM ('micro', 'small', 'medium', 'large', 'enterprise');
        CREATE TYPE agegroupenum AS ENUM ('gen_z', 'millennial', 'gen_x', 'boomer');
        CREATE TYPE brandvoiceenum AS ENUM ('professional', 'casual', 'playful', 'luxury', 'authentic', 'bold');
        CREATE TYPE campaignobjectiveenum AS ENUM ('brand_awareness', 'lead_generation', 'sales', 'engagement', 'traffic', 'app_installs');
        CREATE TYPE contentpreferenceenum AS ENUM ('video_first', 'image_heavy', 'text_focused', 'mixed');
        CREATE TYPE platformpriorityenum AS ENUM ('instagram', 'facebook', 'tiktok', 'linkedin', 'youtube');
        CREATE TYPE teststatusenum AS ENUM ('draft', 'active', 'paused', 'completed', 'cancelled');
        CREATE TYPE testtypeenum AS ENUM ('simple_ab', 'multivariate', 'split_url', 'content_variation');
        CREATE TYPE statisticalsignificanceenum AS ENUM ('not_significant', 'approaching', 'significant', 'highly_significant');
    """)
    
    # 1. MetaUserProfile table
    op.create_table('meta_user_profiles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('business_size', sa.Enum('startup', 'smb', 'enterprise', name='businesssizeenum'), nullable=True),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('business_name', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('years_in_business', sa.Integer(), nullable=True),
        sa.Column('monthly_budget', sa.Enum('micro', 'small', 'medium', 'large', 'enterprise', name='budgetrangeenum'), nullable=True),
        sa.Column('primary_objective', sa.Enum('brand_awareness', 'lead_generation', 'sales', 'engagement', 'traffic', 'app_installs', name='campaignobjectiveenum'), nullable=True),
        sa.Column('secondary_objectives', sa.JSON(), nullable=True),
        sa.Column('target_age_groups', sa.JSON(), nullable=True),
        sa.Column('target_locations', sa.JSON(), nullable=True),
        sa.Column('target_interests', sa.JSON(), nullable=True),
        sa.Column('target_behaviors', sa.JSON(), nullable=True),
        sa.Column('brand_voice', sa.Enum('professional', 'casual', 'playful', 'luxury', 'authentic', 'bold', name='brandvoiceenum'), nullable=True),
        sa.Column('content_preference', sa.Enum('video_first', 'image_heavy', 'text_focused', 'mixed', name='contentpreferenceenum'), nullable=True),
        sa.Column('platform_priorities', sa.JSON(), nullable=True),
        sa.Column('brand_colors', sa.JSON(), nullable=True),
        sa.Column('competitor_urls', sa.JSON(), nullable=True),
        sa.Column('roi_focus', sa.Boolean(), nullable=True),
        sa.Column('risk_tolerance', sa.String(), nullable=True),
        sa.Column('automation_level', sa.String(), nullable=True),
        sa.Column('campaign_history', sa.JSON(), nullable=True),
        sa.Column('performance_patterns', sa.JSON(), nullable=True),
        sa.Column('learned_preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_campaign', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id')
    )
    
    # 2. CampaignRecommendation table
    op.create_table('campaign_recommendations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('recommendation_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('user_profile_id', sa.String(), nullable=True),
        sa.Column('recommended_type', sa.String(), nullable=False),
        sa.Column('campaign_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('content_prompts', sa.JSON(), nullable=True),
        sa.Column('caption_templates', sa.JSON(), nullable=True),
        sa.Column('visual_style', sa.String(), nullable=True),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('recommended_budget', sa.Float(), nullable=True),
        sa.Column('target_audience', sa.JSON(), nullable=True),
        sa.Column('platform_allocation', sa.JSON(), nullable=True),
        sa.Column('predicted_ctr', sa.Float(), nullable=True),
        sa.Column('predicted_engagement_rate', sa.Float(), nullable=True),
        sa.Column('predicted_conversion_rate', sa.Float(), nullable=True),
        sa.Column('predicted_roi', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('ab_variants', sa.JSON(), nullable=True),
        sa.Column('is_implemented', sa.Boolean(), nullable=True),
        sa.Column('implementation_date', sa.DateTime(), nullable=True),
        sa.Column('actual_performance', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_profile_id'], ['meta_user_profiles.id'], ),
        sa.UniqueConstraint('recommendation_id'),
        sa.CheckConstraint('recommended_budget >= 0', name='chk_campaign_recommendations_budget_positive'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='chk_campaign_recommendations_confidence_range')
    )
    
    # 3. ABTest table
    op.create_table('ab_tests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('test_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('user_profile_id', sa.String(), nullable=True),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('test_type', sa.Enum('simple_ab', 'multivariate', 'split_url', 'content_variation', name='testtypeenum'), nullable=True),
        sa.Column('hypothesis', sa.Text(), nullable=True),
        sa.Column('confidence_threshold', sa.Float(), nullable=True),
        sa.Column('min_sample_size', sa.Integer(), nullable=True),
        sa.Column('max_duration_days', sa.Integer(), nullable=True),
        sa.Column('traffic_split', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'completed', 'cancelled', name='teststatusenum'), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('actual_end_date', sa.DateTime(), nullable=True),
        sa.Column('winning_variant_id', sa.String(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('significance_status', sa.Enum('not_significant', 'approaching', 'significant', 'highly_significant', name='statisticalsignificanceenum'), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('effect_size', sa.Float(), nullable=True),
        sa.Column('projected_lift', sa.Float(), nullable=True),
        sa.Column('estimated_revenue_impact', sa.Float(), nullable=True),
        sa.Column('actual_revenue_impact', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('next_steps', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_profile_id'], ['meta_user_profiles.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.UniqueConstraint('test_id'),
        sa.CheckConstraint('confidence_threshold > 0 AND confidence_threshold < 1', name='chk_ab_tests_confidence_range'),
        sa.CheckConstraint('min_sample_size > 0', name='chk_ab_tests_sample_size_positive'),
        sa.CheckConstraint('max_duration_days > 0', name='chk_ab_tests_duration_positive')
    )
    
    # 4. TestVariation table
    op.create_table('test_variations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('variation_id', sa.String(), nullable=False),
        sa.Column('ab_test_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('traffic_percentage', sa.Float(), nullable=False),
        sa.Column('content_config', sa.JSON(), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('revenue', sa.Float(), nullable=True),
        sa.Column('ctr', sa.Float(), nullable=True),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('revenue_per_visitor', sa.Float(), nullable=True),
        sa.Column('confidence_interval_lower', sa.Float(), nullable=True),
        sa.Column('confidence_interval_upper', sa.Float(), nullable=True),
        sa.Column('statistical_power', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ab_test_id'], ['ab_tests.id'], ),
        sa.UniqueConstraint('ab_test_id', 'variation_id', name='uq_test_variations_test_variant'),
        sa.CheckConstraint('traffic_percentage >= 0 AND traffic_percentage <= 100', name='chk_test_variations_traffic_range'),
        sa.CheckConstraint('impressions >= 0', name='chk_test_variations_impressions_positive'),
        sa.CheckConstraint('clicks >= 0', name='chk_test_variations_clicks_positive'),
        sa.CheckConstraint('conversions >= 0', name='chk_test_variations_conversions_positive')
    )
    
    # 5. TestResult table
    op.create_table('test_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ab_test_id', sa.String(), nullable=False),
        sa.Column('total_impressions', sa.Integer(), nullable=True),
        sa.Column('total_conversions', sa.Integer(), nullable=True),
        sa.Column('test_duration_days', sa.Integer(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('effect_size', sa.Float(), nullable=True),
        sa.Column('power_analysis', sa.JSON(), nullable=True),
        sa.Column('winning_variation_id', sa.String(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('significance_status', sa.Enum('not_significant', 'approaching', 'significant', 'highly_significant', name='statisticalsignificanceenum'), nullable=True),
        sa.Column('projected_lift', sa.Float(), nullable=True),
        sa.Column('estimated_revenue_impact', sa.Float(), nullable=True),
        sa.Column('variation_comparisons', sa.JSON(), nullable=True),
        sa.Column('statistical_details', sa.JSON(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('next_steps', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ab_test_id'], ['ab_tests.id'], )
    )
    
    # 6. LearningInsight table
    op.create_table('learning_insights',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('insight_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('user_profile_id', sa.String(), nullable=True),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.Column('insight_type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('baseline_metric', sa.Float(), nullable=True),
        sa.Column('improved_metric', sa.Float(), nullable=True),
        sa.Column('improvement_percentage', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('identified_patterns', sa.JSON(), nullable=True),
        sa.Column('contributing_factors', sa.JSON(), nullable=True),
        sa.Column('correlation_data', sa.JSON(), nullable=True),
        sa.Column('optimization_recommendations', sa.JSON(), nullable=True),
        sa.Column('implementation_priority', sa.String(), nullable=True),
        sa.Column('expected_impact', sa.String(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('time_period_days', sa.Integer(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('is_implemented', sa.Boolean(), nullable=True),
        sa.Column('implementation_date', sa.DateTime(), nullable=True),
        sa.Column('actual_results', sa.JSON(), nullable=True),
        sa.Column('discovered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_profile_id'], ['meta_user_profiles.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.UniqueConstraint('insight_id'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='chk_learning_insights_confidence_range'),
        sa.CheckConstraint('sample_size >= 0', name='chk_learning_insights_sample_size_positive')
    )
    
    # 7. PerformancePattern table
    op.create_table('performance_patterns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pattern_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('pattern_type', sa.String(), nullable=False),
        sa.Column('pattern_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pattern_conditions', sa.JSON(), nullable=True),
        sa.Column('performance_impact', sa.JSON(), nullable=True),
        sa.Column('frequency_observed', sa.Integer(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('effect_size', sa.Float(), nullable=True),
        sa.Column('campaigns_analyzed', sa.Integer(), nullable=True),
        sa.Column('time_period_analyzed', sa.Integer(), nullable=True),
        sa.Column('first_observed', sa.DateTime(), nullable=True),
        sa.Column('last_observed', sa.DateTime(), nullable=True),
        sa.Column('actionable_insights', sa.JSON(), nullable=True),
        sa.Column('automation_potential', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('pattern_id'),
        sa.CheckConstraint('confidence_level >= 0 AND confidence_level <= 1', name='chk_performance_patterns_confidence_range'),
        sa.CheckConstraint('frequency_observed >= 0', name='chk_performance_patterns_frequency_positive')
    )
    
    # 8. ContentTemplate table
    op.create_table('content_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('template_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('base_prompt', sa.Text(), nullable=False),
        sa.Column('personalization_variables', sa.JSON(), nullable=True),
        sa.Column('style_parameters', sa.JSON(), nullable=True),
        sa.Column('content_structure', sa.JSON(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('avg_performance_score', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('target_industries', sa.JSON(), nullable=True),
        sa.Column('target_objectives', sa.JSON(), nullable=True),
        sa.Column('target_demographics', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('template_id'),
        sa.CheckConstraint('usage_count >= 0', name='chk_content_templates_usage_count_positive'),
        sa.CheckConstraint('success_rate >= 0 AND success_rate <= 100', name='chk_content_templates_success_rate_range')
    )
    
    # 9. PersonalizedContent table
    op.create_table('personalized_content',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.Column('template_id', sa.String(), nullable=True),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('personalized_prompt', sa.Text(), nullable=False),
        sa.Column('personalization_context', sa.JSON(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('content_metadata', sa.JSON(), nullable=True),
        sa.Column('personalization_variables_used', sa.JSON(), nullable=True),
        sa.Column('demographic_targeting', sa.JSON(), nullable=True),
        sa.Column('behavioral_targeting', sa.JSON(), nullable=True),
        sa.Column('contextual_targeting', sa.JSON(), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('performance_vs_template', sa.Float(), nullable=True),
        sa.Column('model_used', sa.String(), nullable=True),
        sa.Column('generation_time', sa.Float(), nullable=True),
        sa.Column('generation_cost', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['content_templates.id'], ),
        sa.UniqueConstraint('content_id'),
        sa.CheckConstraint('impressions >= 0', name='chk_personalized_content_impressions_positive'),
        sa.CheckConstraint('clicks >= 0', name='chk_personalized_content_clicks_positive'),
        sa.CheckConstraint('conversions >= 0', name='chk_personalized_content_conversions_positive'),
        sa.CheckConstraint('usage_count >= 0', name='chk_personalized_content_usage_count_positive')
    )
    
    # 10. CampaignPersonalizationSettings table
    op.create_table('campaign_personalization_settings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('personalization_level', sa.String(), nullable=True),
        sa.Column('auto_optimization_enabled', sa.Boolean(), nullable=True),
        sa.Column('dynamic_content_enabled', sa.Boolean(), nullable=True),
        sa.Column('adaptive_bidding_enabled', sa.Boolean(), nullable=True),
        sa.Column('audience_personalization', sa.JSON(), nullable=True),
        sa.Column('demographic_weights', sa.JSON(), nullable=True),
        sa.Column('behavioral_triggers', sa.JSON(), nullable=True),
        sa.Column('content_rotation_strategy', sa.String(), nullable=True),
        sa.Column('personalized_templates', sa.JSON(), nullable=True),
        sa.Column('dynamic_elements', sa.JSON(), nullable=True),
        sa.Column('budget_allocation_strategy', sa.JSON(), nullable=True),
        sa.Column('bid_adjustments', sa.JSON(), nullable=True),
        sa.Column('performance_targets', sa.JSON(), nullable=True),
        sa.Column('learning_priority', sa.String(), nullable=True),
        sa.Column('optimization_frequency', sa.String(), nullable=True),
        sa.Column('performance_thresholds', sa.JSON(), nullable=True),
        sa.Column('ab_testing_enabled', sa.Boolean(), nullable=True),
        sa.Column('predictive_scaling_enabled', sa.Boolean(), nullable=True),
        sa.Column('real_time_optimization', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('campaign_id')
    )
    
    # Create all indexes for performance optimization
    
    # MetaUserProfile indexes
    op.create_index('idx_meta_user_profiles_user_id', 'meta_user_profiles', ['user_id'])
    op.create_index('idx_meta_user_profiles_industry', 'meta_user_profiles', ['industry'])
    op.create_index('idx_meta_user_profiles_business_size', 'meta_user_profiles', ['business_size'])
    op.create_index('idx_meta_user_profiles_monthly_budget', 'meta_user_profiles', ['monthly_budget'])
    op.create_index('idx_meta_user_profiles_primary_objective', 'meta_user_profiles', ['primary_objective'])
    op.create_index('idx_meta_user_profiles_updated_at', 'meta_user_profiles', ['updated_at'])
    
    # CampaignRecommendation indexes
    op.create_index('idx_campaign_recommendations_user_id', 'campaign_recommendations', ['user_id'])
    op.create_index('idx_campaign_recommendations_recommended_type', 'campaign_recommendations', ['recommended_type'])
    op.create_index('idx_campaign_recommendations_confidence_score', 'campaign_recommendations', ['confidence_score'])
    op.create_index('idx_campaign_recommendations_created_at', 'campaign_recommendations', ['created_at'])
    op.create_index('idx_campaign_recommendations_is_implemented', 'campaign_recommendations', ['is_implemented'])
    
    # ABTest indexes
    op.create_index('idx_ab_tests_user_id', 'ab_tests', ['user_id'])
    op.create_index('idx_ab_tests_status', 'ab_tests', ['status'])
    op.create_index('idx_ab_tests_test_type', 'ab_tests', ['test_type'])
    op.create_index('idx_ab_tests_start_date', 'ab_tests', ['start_date'])
    op.create_index('idx_ab_tests_significance_status', 'ab_tests', ['significance_status'])
    op.create_index('idx_ab_tests_user_status', 'ab_tests', ['user_id', 'status'])
    
    # TestVariation indexes
    op.create_index('idx_test_variations_ab_test_id', 'test_variations', ['ab_test_id'])
    op.create_index('idx_test_variations_variation_id', 'test_variations', ['variation_id'])
    op.create_index('idx_test_variations_conversion_rate', 'test_variations', ['conversion_rate'])
    op.create_index('idx_test_variations_ctr', 'test_variations', ['ctr'])
    
    # TestResult indexes
    op.create_index('idx_test_results_ab_test_id', 'test_results', ['ab_test_id'])
    op.create_index('idx_test_results_significance_status', 'test_results', ['significance_status'])
    op.create_index('idx_test_results_calculated_at', 'test_results', ['calculated_at'])
    op.create_index('idx_test_results_confidence_level', 'test_results', ['confidence_level'])
    
    # LearningInsight indexes
    op.create_index('idx_learning_insights_user_id', 'learning_insights', ['user_id'])
    op.create_index('idx_learning_insights_insight_type', 'learning_insights', ['insight_type'])
    op.create_index('idx_learning_insights_confidence_score', 'learning_insights', ['confidence_score'])
    op.create_index('idx_learning_insights_improvement_percentage', 'learning_insights', ['improvement_percentage'])
    op.create_index('idx_learning_insights_is_implemented', 'learning_insights', ['is_implemented'])
    op.create_index('idx_learning_insights_discovered_at', 'learning_insights', ['discovered_at'])
    
    # PerformancePattern indexes
    op.create_index('idx_performance_patterns_user_id', 'performance_patterns', ['user_id'])
    op.create_index('idx_performance_patterns_pattern_type', 'performance_patterns', ['pattern_type'])
    op.create_index('idx_performance_patterns_confidence_level', 'performance_patterns', ['confidence_level'])
    op.create_index('idx_performance_patterns_frequency_observed', 'performance_patterns', ['frequency_observed'])
    op.create_index('idx_performance_patterns_last_observed', 'performance_patterns', ['last_observed'])
    
    # ContentTemplate indexes
    op.create_index('idx_content_templates_user_id', 'content_templates', ['user_id'])
    op.create_index('idx_content_templates_template_type', 'content_templates', ['template_type'])
    op.create_index('idx_content_templates_category', 'content_templates', ['category'])
    op.create_index('idx_content_templates_avg_performance_score', 'content_templates', ['avg_performance_score'])
    op.create_index('idx_content_templates_usage_count', 'content_templates', ['usage_count'])
    op.create_index('idx_content_templates_is_active', 'content_templates', ['is_active'])
    op.create_index('idx_content_templates_is_public', 'content_templates', ['is_public'])
    
    # PersonalizedContent indexes
    op.create_index('idx_personalized_content_user_id', 'personalized_content', ['user_id'])
    op.create_index('idx_personalized_content_campaign_id', 'personalized_content', ['campaign_id'])
    op.create_index('idx_personalized_content_template_id', 'personalized_content', ['template_id'])
    op.create_index('idx_personalized_content_content_type', 'personalized_content', ['content_type'])
    op.create_index('idx_personalized_content_engagement_score', 'personalized_content', ['engagement_score'])
    op.create_index('idx_personalized_content_performance_vs_template', 'personalized_content', ['performance_vs_template'])
    op.create_index('idx_personalized_content_created_at', 'personalized_content', ['created_at'])
    
    # CampaignPersonalizationSettings indexes
    op.create_index('idx_campaign_personalization_campaign_id', 'campaign_personalization_settings', ['campaign_id'])
    op.create_index('idx_campaign_personalization_user_id', 'campaign_personalization_settings', ['user_id'])
    op.create_index('idx_campaign_personalization_personalization_level', 'campaign_personalization_settings', ['personalization_level'])
    op.create_index('idx_campaign_personalization_auto_optimization_enabled', 'campaign_personalization_settings', ['auto_optimization_enabled'])


def downgrade():
    """Remove all personalization tables and features."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('campaign_personalization_settings')
    op.drop_table('personalized_content')
    op.drop_table('content_templates')
    op.drop_table('performance_patterns')
    op.drop_table('learning_insights')
    op.drop_table('test_results')
    op.drop_table('test_variations')
    op.drop_table('ab_tests')
    op.drop_table('campaign_recommendations')
    op.drop_table('meta_user_profiles')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS statisticalsignificanceenum")
    op.execute("DROP TYPE IF EXISTS testtypeenum")
    op.execute("DROP TYPE IF EXISTS teststatusenum")
    op.execute("DROP TYPE IF EXISTS platformpriorityenum")
    op.execute("DROP TYPE IF EXISTS contentpreferenceenum")
    op.execute("DROP TYPE IF EXISTS campaignobjectiveenum")
    op.execute("DROP TYPE IF EXISTS brandvoiceenum")
    op.execute("DROP TYPE IF EXISTS agegroupenum")
    op.execute("DROP TYPE IF EXISTS budgetrangeenum")
    op.execute("DROP TYPE IF EXISTS businesssizeenum")