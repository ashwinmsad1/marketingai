// User and Authentication Types
export interface User {
  id: string;
  email: string;
  name: string;
  subscription_tier: 'starter' | 'professional' | 'enterprise';
  created_at: string;
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
  campaign_id: string;
  user_id: string;
  name: string;
  type: 'image' | 'video' | 'industry_optimized' | 'viral' | 'competitor_beating';
  status: 'active' | 'paused' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  budget?: number;
  spend?: number;
  impressions?: number;
  clicks?: number;
  conversions?: number;
  roi?: number;
  ctr?: number;
  cpc?: number;
  created_file?: string;
  prompt?: string;
  caption?: string;
  industry?: string;
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