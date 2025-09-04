// User and Authentication Types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  // Computed property for full name
  name?: string;
  subscription_tier?: 'starter' | 'professional' | 'enterprise';
  industry?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Campaign Types
export interface Campaign {
  id: string; // Backend uses 'id' not 'campaign_id'
  campaign_id?: string; // Keep for backwards compatibility
  user_id: string;
  name: string;
  description?: string;
  objective?: string;
  type?: 'image' | 'video' | 'industry_optimized' | 'viral' | 'competitor_beating';
  status: 'draft' | 'active' | 'paused' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  start_date?: string;
  end_date?: string;
  
  // Budget and Performance Metrics
  budget_daily?: number;
  budget_total?: number;
  spend?: number;
  impressions?: number;
  clicks?: number;
  conversions?: number;
  
  // Calculated Metrics
  ctr?: number;
  cpc?: number;
  cpm?: number;
  roas?: number;
  roi?: number;
  
  // Meta Integration
  meta_campaign_id?: string;
  meta_adset_id?: string;
  meta_ad_id?: string;
  target_audience?: Record<string, any>;
  
  // AI Enhancement
  industry?: string;
  template_used?: string;
  is_ai_optimized?: boolean;
  
  // Legacy fields for backwards compatibility
  budget?: number;
  created_file?: string;
  prompt?: string;
  caption?: string;
  performance_status?: 'excellent' | 'good' | 'poor' | 'critical';
  guarantee_met?: boolean;
}

// Campaign Creation Types
export interface CampaignCreateRequest {
  type: 'image' | 'video' | 'industry_optimized' | 'viral' | 'competitor_beating';
  prompt: string;
  caption?: string;
  style?: string;
  industry?: string;
  business_details?: Record<string, any>;
  competitor_url?: string;
  competitor_name?: string;
}

// Performance Metrics
export interface PerformanceMetrics {
  campaign_id: string;
  ctr: number;
  cpc: number;
  conversion_rate: number;
  roi: number;
  performance_status: 'excellent' | 'good' | 'poor' | 'critical';
  needs_optimization: boolean;
  guarantee_threshold_met: boolean;
  industry_benchmark_ctr: number;
  industry_benchmark_cpc: number;
}

// Revenue Tracking
export interface RevenueMetrics {
  campaign_id: string;
  total_spend: number;
  total_revenue: number;
  roi_percentage: number;
  cost_per_conversion: number;
  conversion_count: number;
  lifetime_value: number;
}

// Success Dashboard
export interface DashboardData {
  user_id: string;
  generated_at: string;
  success_summary: {
    total_campaigns: number;
    total_revenue: number;
    overall_roi: number;
    guarantee_success_rate: number;
  };
  revenue_analytics: {
    overall_metrics: {
      total_campaigns: number;
      total_spend: number;
      total_conversions: number;
      total_revenue: number;
      overall_roi: number;
      avg_cost_per_conversion: number;
    };
    campaign_performance: CampaignPerformance[];
    top_performing_creatives: CreativePerformance[];
  };
  performance_metrics: {
    summary: {
      total_campaigns: number;
      avg_ctr: number;
      avg_roi: number;
      guarantee_success_rate: number;
      campaigns_optimized: number;
    };
  };
}

export interface CampaignPerformance {
  campaign_id: string;
  name: string;
  creative_asset: string;
  spend: number;
  conversions: number;
  revenue: number;
  roi: number;
}

export interface CreativePerformance {
  asset: string;
  conversions: number;
  revenue: number;
}

// Industry Templates
export interface IndustryTemplate {
  template_id: string;
  industry: string;
  name: string;
  description: string;
  expected_performance: {
    ctr: number;
    conversion_rate: number;
    engagement_rate: number;
  };
}

// Viral Opportunities
export interface ViralOpportunity {
  topic_id: string;
  topic_name: string;
  trend_score: number;
  peak_period: string;
  engagement_potential: number;
  urgency_level: 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';
}

// API Response Types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Notification Types
export interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// Personalization API Request/Response Types
export interface PersonalizationProfileRequest {
  business_name: string;
  industry: string;
  business_type: 'B2C' | 'B2B' | 'Both';
  target_audience: string;
  primary_location: string;
  budget_range: string;
  signature_product_service: string;
  unique_value_proposition: string;
  brand_voice: string;
  primary_goals: string[];
  peak_sales_times?: string;
  customer_pain_points?: string;
  preferred_content_types?: string[];
  brand_colors?: string;
  brand_fonts?: string;
  competitor_analysis?: string;
  seasonal_trends?: string;
  marketing_channels?: string[];
  content_calendar_preferences?: string;
  performance_priorities?: string[];
}

export interface CampaignStrategyRequest {
  profile_id: string;
  strategy_type: 'awareness' | 'conversion' | 'engagement' | 'retention';
  budget_range: string;
  duration_days: number;
  specific_goals?: string[];
  target_audience_preferences?: Record<string, any>;
  content_preferences?: string[];
}

export interface ABTestRequest {
  campaign_name: string;
  test_type: 'content' | 'audience' | 'creative' | 'timing';
  variant_a: {
    name: string;
    description: string;
    content: Record<string, any>;
  };
  variant_b: {
    name: string;
    description: string;
    content: Record<string, any>;
  };
  traffic_split: number;
  sample_size: number;
  confidence_level: number;
  duration_days: number;
}

export interface PersonalizationAskRequest {
  question: string;
  context?: {
    campaign_id?: string;
    profile_id?: string;
    specific_context?: string;
  };
}

export interface PersonalizationAskResponse {
  answer: string;
  confidence: number;
  recommendations?: string[];
  related_insights?: string[];
  suggested_actions?: string[];
}

// Subscription Types
export interface SubscriptionLimits {
  campaigns_per_month: number;
  ai_generations_per_month: number;
  api_calls_per_month: number;
  features: string[];
}

export interface SubscriptionUsage {
  campaigns_used: number;
  ai_generations_used: number;
  api_calls_used: number;
  reset_date: string;
}

// Form Types
export interface BusinessOnboardingForm {
  business_name: string;
  industry: string;
  business_type: string;
  location: string;
  target_audience: string;
  budget_range: string;
  primary_goals: string[];
  signature_product_service: string;
  phone?: string;
  website?: string;
  current_marketing?: string[];
}

// Personalization Types
export interface MetaUserProfile {
  user_id: string;
  business_name: string;
  industry: string;
  business_type: 'B2C' | 'B2B' | 'Both';
  target_audience: string;
  primary_location: string;
  budget_range: string;
  signature_product_service: string;
  unique_value_proposition: string;
  brand_voice: string;
  primary_goals: string[];
  peak_sales_times: string;
  customer_pain_points: string;
  preferred_content_types: string[];
  brand_colors?: string;
  brand_fonts?: string;
  competitor_analysis?: string;
  seasonal_trends?: string;
  marketing_channels?: string[];
  content_calendar_preferences?: string;
  performance_priorities: string[];
  created_at?: string;
  updated_at?: string;
}

// A/B Testing Types
export interface ABTest {
  test_id: string;
  user_id: string;
  campaign_name: string;
  test_type: 'content' | 'audience' | 'creative' | 'timing';
  status: 'draft' | 'running' | 'completed' | 'paused';
  variant_a: ABTestVariant;
  variant_b: ABTestVariant;
  traffic_split: number; // 0-100 percentage for variant A
  start_date?: string;
  end_date?: string;
  sample_size: number;
  confidence_level: number;
  statistical_significance?: number;
  winner?: 'A' | 'B' | 'inconclusive';
  results?: ABTestResults;
  created_at: string;
  updated_at: string;
}

export interface ABTestVariant {
  name: string;
  description: string;
  content: {
    headline?: string;
    description?: string;
    creative_asset?: string;
    call_to_action?: string;
    audience_targeting?: Record<string, any>;
  };
  metrics?: {
    impressions: number;
    clicks: number;
    conversions: number;
    spend: number;
    ctr: number;
    conversion_rate: number;
    cost_per_conversion: number;
  };
}

export interface ABTestResults {
  winner: 'A' | 'B' | 'inconclusive';
  confidence: number;
  significance: number;
  lift: number; // percentage improvement of winner
  summary: string;
  recommendations: string[];
}

// Campaign Strategy Types
export interface CampaignStrategy {
  strategy_id: string;
  user_id: string;
  profile_id: string;
  strategy_type: 'awareness' | 'conversion' | 'engagement' | 'retention';
  meta_campaign_objective: string;
  audience_segments: AudienceSegment[];
  content_themes: ContentTheme[];
  budget_allocation: BudgetAllocation;
  timing_strategy: TimingStrategy;
  creative_recommendations: CreativeRecommendation[];
  expected_performance: {
    estimated_reach: number;
    expected_ctr: number;
    expected_conversion_rate: number;
    estimated_cost_per_result: number;
  };
  confidence_score: number;
  created_at: string;
  updated_at: string;
}

export interface AudienceSegment {
  segment_id: string;
  name: string;
  description: string;
  targeting_criteria: {
    demographics: Record<string, any>;
    interests: string[];
    behaviors: string[];
    custom_audiences?: string[];
    lookalike_audiences?: string[];
  };
  estimated_size: number;
  recommended_budget_percentage: number;
}

export interface ContentTheme {
  theme_id: string;
  name: string;
  description: string;
  content_pillars: string[];
  messaging_angles: string[];
  visual_style: string;
  tone_of_voice: string;
  content_types: string[];
  performance_prediction: number;
}

export interface BudgetAllocation {
  total_budget: number;
  daily_budget: number;
  allocation_by_objective: Record<string, number>;
  allocation_by_audience: Record<string, number>;
  allocation_by_placement: Record<string, number>;
  recommended_bid_strategy: string;
}

export interface TimingStrategy {
  optimal_days: string[];
  optimal_hours: number[];
  time_zone: string;
  seasonal_adjustments: Record<string, number>;
  day_parting_recommendations: Record<string, number[]>;
}

export interface CreativeRecommendation {
  creative_type: 'image' | 'video' | 'carousel' | 'story';
  template_id: string;
  content_suggestions: {
    headline_options: string[];
    description_options: string[];
    visual_elements: string[];
    call_to_action_options: string[];
  };
  personalization_variables: string[];
  predicted_performance_score: number;
}

// Personalization Insights
export interface PersonalizationInsights {
  user_id: string;
  generated_at: string;
  performance_summary: {
    personalized_campaigns: number;
    average_lift: number;
    total_additional_revenue: number;
    best_performing_segments: string[];
  };
  audience_insights: {
    top_segments: AudienceInsight[];
    segment_performance: Record<string, number>;
    new_opportunities: string[];
  };
  content_insights: {
    top_performing_themes: string[];
    content_recommendations: ContentRecommendation[];
    trending_topics: string[];
  };
  optimization_opportunities: OptimizationOpportunity[];
  predictive_analytics: {
    next_month_forecast: Record<string, number>;
    seasonal_predictions: Record<string, number>;
    growth_opportunities: string[];
  };
}

export interface AudienceInsight {
  segment_name: string;
  size: number;
  engagement_rate: number;
  conversion_rate: number;
  lifetime_value: number;
  growth_trend: number;
  recommended_content: string[];
}

export interface ContentRecommendation {
  content_type: string;
  theme: string;
  predicted_engagement: number;
  optimal_timing: string;
  target_audience: string;
  creative_elements: string[];
}

export interface OptimizationOpportunity {
  opportunity_id: string;
  type: 'audience' | 'content' | 'budget' | 'timing';
  title: string;
  description: string;
  potential_impact: {
    metric: string;
    estimated_improvement: number;
    confidence: number;
  };
  implementation_difficulty: 'easy' | 'medium' | 'hard';
  recommended_actions: string[];
  priority_score: number;
}

// Dynamic Content Types
export interface ContentTemplate {
  template_id: string;
  name: string;
  description: string;
  category: string;
  industry: string;
  content_type: 'image' | 'video' | 'carousel' | 'story';
  template_structure: {
    layout: string;
    placeholders: ContentPlaceholder[];
    styling: Record<string, any>;
  };
  personalization_variables: PersonalizationVariable[];
  performance_data: {
    usage_count: number;
    average_ctr: number;
    average_conversion_rate: number;
    industries_used: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface ContentPlaceholder {
  id: string;
  type: 'text' | 'image' | 'video' | 'button' | 'logo';
  position: { x: number; y: number; width: number; height: number };
  default_content?: string;
  personalization_mapping?: string;
  styling?: Record<string, any>;
}

export interface PersonalizationVariable {
  variable_name: string;
  variable_type: 'text' | 'image' | 'color' | 'number';
  source: 'profile' | 'audience' | 'performance' | 'external';
  description: string;
  possible_values?: string[];
  default_value?: string;
}

// Campaign Recommendations
export interface CampaignRecommendation {
  recommendation_id: string;
  user_id: string;
  type: 'new_campaign' | 'optimization' | 'audience_expansion' | 'budget_adjustment';
  title: string;
  description: string;
  reasoning: string[];
  predicted_impact: {
    metric: 'reach' | 'conversions' | 'roi' | 'engagement';
    estimated_change: number;
    confidence: number;
  };
  implementation: {
    difficulty: 'easy' | 'medium' | 'hard';
    time_required: string;
    steps: string[];
    estimated_cost?: number;
  };
  priority: 'high' | 'medium' | 'low';
  expiry_date?: string;
  campaign_config?: Record<string, any>;
  created_at: string;
}

// Learning Analytics
export interface LearningInsights {
  user_id: string;
  time_period: string;
  learning_summary: {
    patterns_discovered: number;
    performance_improvements: number;
    optimization_applied: number;
    confidence_score: number;
  };
  performance_patterns: PerformancePattern[];
  audience_learnings: AudienceLearning[];
  content_learnings: ContentLearning[];
  seasonal_insights: SeasonalInsight[];
  predictive_models: {
    audience_response_model: ModelInsight;
    content_performance_model: ModelInsight;
    optimal_timing_model: ModelInsight;
  };
  action_recommendations: ActionRecommendation[];
}

export interface PerformancePattern {
  pattern_id: string;
  pattern_type: 'audience' | 'content' | 'timing' | 'budget';
  description: string;
  frequency: number;
  impact_score: number;
  conditions: Record<string, any>;
  outcomes: Record<string, number>;
  reliability_score: number;
}

export interface AudienceLearning {
  segment_name: string;
  key_insights: string[];
  behavioral_patterns: string[];
  content_preferences: string[];
  optimal_timing: string[];
  engagement_drivers: string[];
  conversion_factors: string[];
}

export interface ContentLearning {
  content_type: string;
  successful_elements: string[];
  performance_factors: Record<string, number>;
  audience_resonance: Record<string, number>;
  optimal_combinations: string[];
  improvement_opportunities: string[];
}

export interface SeasonalInsight {
  time_period: string;
  performance_trends: Record<string, number>;
  audience_behavior_changes: string[];
  content_performance_shifts: Record<string, number>;
  budget_optimization_opportunities: string[];
  predictive_adjustments: Record<string, number>;
}

export interface ModelInsight {
  model_name: string;
  accuracy_score: number;
  key_features: string[];
  prediction_confidence: number;
  last_updated: string;
  performance_metrics: Record<string, number>;
}

export interface ActionRecommendation {
  action_id: string;
  category: 'immediate' | 'short_term' | 'long_term';
  title: string;
  description: string;
  expected_impact: number;
  implementation_effort: 'low' | 'medium' | 'high';
  required_resources: string[];
  success_metrics: string[];
  timeline: string;
}