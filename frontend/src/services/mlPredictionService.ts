/**
 * ML Prediction Service for Frontend
 * Provides TypeScript interfaces and API calls for all ML prediction features
 */

import api from './api';

// Types for ML Predictions
export interface CampaignPredictionRequest {
  campaign_config: {
    name: string;
    type: string;
    budget: {
      daily_budget: number;
      total_budget: number;
      duration_days: number;
    };
    targeting: {
      demographics: string[];
      interests: string[];
      locations: string[];
    };
    platforms: {
      facebook: boolean;
      instagram: boolean;
    };
    industry?: string;
    business_description?: string;
  };
  historical_data?: Array<{
    campaign_id: string;
    roi: number;
    ctr: number;
    conversion_rate: number;
  }>;
  use_cache?: boolean;
}

export interface ViralPotentialRequest {
  content_config: {
    content_type: 'image' | 'video' | 'text';
    topic: string;
    style: string;
    target_emotion?: string;
    language?: string;
    duration?: number;
  };
  use_cache?: boolean;
}

export interface PredictionResponse {
  success: boolean;
  prediction_id: string;
  prediction_type: string;
  predicted_metrics: {
    roi?: number;
    ctr?: number;
    conversion_rate?: number;
    engagement_rate?: number;
    cost_per_click?: number;
    cost_per_conversion?: number;
    estimated_reach?: number;
    share_rate?: number;
    comment_rate?: number;
    viral_coefficient?: number;
  };
  confidence_level: 'low' | 'medium' | 'high' | 'very_high';
  confidence_score: number;
  prediction_reasoning: string;
  key_factors: string[];
  risk_factors?: string[];
  optimization_opportunities: string[];
  recommended_adjustments: string[];
  expected_outcomes: Record<string, string>;
  model_version: string;
  cached?: boolean;
  cache_hit_count?: number;
  created_at?: string;
  alternative_scenarios?: Array<{
    scenario_id: string;
    predicted_metrics: Record<string, number>;
    confidence_score: number;
    reasoning: string;
    key_factors: string[];
  }>;
  optimization_strategy?: string;
  expected_budget_efficiency?: number;
}

export interface PredictionHistory {
  predictions: Array<{
    prediction_id: string;
    prediction_type: string;
    created_at: string;
    confidence_score: number;
    predicted_metrics: Record<string, number>;
    cached: boolean;
  }>;
  total_count: number;
  page: number;
  per_page: number;
}

export interface PredictionInsights {
  user_id: string;
  claude_insights: {
    total_predictions: number;
    average_confidence: number;
    confidence_trend: string;
    top_success_factors: string[];
    top_optimization_opportunities: string[];
    recent_predictions: Array<{
      id: string;
      type: string;
      confidence: number;
      key_metric: number;
      date: string;
    }>;
    model_performance: {
      version: string;
      predictions_made: number;
      average_confidence: number;
    };
  };
  database_insights: {
    total_predictions: number;
    accuracy_trends: Record<string, number>;
    feedback_statistics: Record<string, number>;
    prediction_types_used: string[];
    date_range: {
      earliest: string;
      latest: string;
    };
  };
  prediction_service_info: {
    service_version: string;
    cache_enabled: boolean;
    cache_ttl_hours: number;
    fallback_enabled: boolean;
  };
  generated_at: string;
}

export interface AccuracyUpdateRequest {
  actual_metrics: {
    roi?: number;
    ctr?: number;
    conversion_rate?: number;
    engagement_rate?: number;
    reach?: number;
    impressions?: number;
    clicks?: number;
    conversions?: number;
  };
}

export interface AccuracyUpdateResponse {
  success: boolean;
  prediction_id: string;
  accuracy_score: number;
  updated_at: string;
  message: string;
}

export interface MLConfigResponse {
  enabled: boolean;
  api_key_configured: boolean;
  model_version: string;
  cache_ttl_hours: number;
  max_cache_entries: number;
  fallback_enabled: boolean;
  prediction_types: string[];
  supported_metrics: string[];
  cache_cleanup_interval_hours: number;
  max_prediction_age_days: number;
  subscription_limits: {
    max_predictions_per_day: number;
    max_predictions_per_month: number;
    cache_enabled: boolean;
    advanced_scenarios: boolean;
  };
}

/**
 * ML Prediction API Service
 */
export const mlPredictionService = {
  
  /**
   * Predict campaign performance using Claude ML analysis
   */
  predictCampaignPerformance: async (request: CampaignPredictionRequest): Promise<PredictionResponse> => {
    const response = await api.post('/api/v1/personalization/predictions/campaign-performance', request);
    return response.data;
  },

  /**
   * Predict viral potential of content
   */
  predictViralPotential: async (request: ViralPotentialRequest): Promise<PredictionResponse> => {
    const response = await api.post('/api/v1/personalization/predictions/viral-potential', request);
    return response.data;
  },

  /**
   * Predict audience response to content
   */
  predictAudienceResponse: async (request: {
    content_config: any;
    audience_demographics: any;
    use_cache?: boolean;
  }): Promise<PredictionResponse> => {
    const response = await api.post('/api/v1/personalization/predictions/audience-response', request);
    return response.data;
  },

  /**
   * Predict content effectiveness
   */
  predictContentEffectiveness: async (request: {
    content_config: any;
    campaign_objectives: string[];
    use_cache?: boolean;
  }): Promise<PredictionResponse> => {
    const response = await api.post('/api/v1/personalization/predictions/content-effectiveness', request);
    return response.data;
  },

  /**
   * Optimize budget allocation using ML predictions
   */
  optimizeBudget: async (request: {
    current_budget: any;
    campaign_goals: any;
    historical_performance?: any;
    use_cache?: boolean;
  }): Promise<PredictionResponse> => {
    const response = await api.post('/api/v1/personalization/predictions/budget-optimization', request);
    return response.data;
  },

  /**
   * Get prediction history with optional filtering
   */
  getPredictionHistory: async (options?: {
    prediction_type?: string;
    page?: number;
    per_page?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<PredictionHistory> => {
    const response = await api.get('/api/v1/personalization/predictions/history', {
      params: options
    });
    return response.data;
  },

  /**
   * Get comprehensive prediction insights
   */
  getPredictionInsights: async (options?: {
    prediction_type?: string;
  }): Promise<PredictionInsights> => {
    const response = await api.get('/api/v1/personalization/predictions/insights', {
      params: options
    });
    return response.data;
  },

  /**
   * Update prediction accuracy with actual results
   */
  updatePredictionAccuracy: async (
    predictionId: string, 
    actualMetrics: AccuracyUpdateRequest
  ): Promise<AccuracyUpdateResponse> => {
    const response = await api.post(
      `/api/v1/personalization/predictions/${predictionId}/accuracy`, 
      actualMetrics
    );
    return response.data;
  },

  /**
   * Get ML configuration and subscription limits
   */
  getMLConfig: async (): Promise<MLConfigResponse> => {
    const response = await api.get('/api/v1/personalization/predictions/config');
    return response.data;
  },

  /**
   * Provide feedback on prediction quality
   */
  providePredictionFeedback: async (request: {
    prediction_id: string;
    feedback_type: 'helpful' | 'not_helpful' | 'inaccurate' | 'excellent';
    rating: number; // 1-5
    comments?: string;
    actual_outcome?: 'better' | 'worse' | 'as_expected';
  }): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/api/v1/personalization/predictions/feedback', request);
    return response.data;
  },

  /**
   * Clean up expired cache entries (admin function)
   */
  cleanupExpiredCache: async (): Promise<{ cleaned_up: number; cleanup_time: string }> => {
    const response = await api.post('/api/v1/personalization/predictions/cache/cleanup');
    return response.data;
  },

};

/**
 * Utility functions for ML predictions
 */
export const mlPredictionUtils = {
  
  /**
   * Format prediction confidence level for display
   */
  formatConfidenceLevel: (level: string): string => {
    const levels: Record<string, string> = {
      'low': 'Low Confidence',
      'medium': 'Medium Confidence', 
      'high': 'High Confidence',
      'very_high': 'Very High Confidence'
    };
    return levels[level] || level;
  },

  /**
   * Get confidence color for UI styling
   */
  getConfidenceColor: (score: number): string => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'blue';
    if (score >= 0.4) return 'yellow';
    return 'red';
  },

  /**
   * Format prediction metrics for display
   */
  formatMetric: (metricName: string, value: number): string => {
    const formatters: Record<string, (val: number) => string> = {
      'roi': (val) => `${val.toFixed(1)}%`,
      'ctr': (val) => `${val.toFixed(2)}%`,
      'conversion_rate': (val) => `${val.toFixed(2)}%`,
      'engagement_rate': (val) => `${val.toFixed(2)}%`,
      'cost_per_click': (val) => `$${val.toFixed(2)}`,
      'cost_per_conversion': (val) => `$${val.toFixed(2)}`,
      'estimated_reach': (val) => val.toLocaleString(),
      'share_rate': (val) => `${val.toFixed(2)}%`,
      'viral_coefficient': (val) => val.toFixed(3)
    };
    
    const formatter = formatters[metricName];
    return formatter ? formatter(value) : value.toString();
  },

  /**
   * Validate prediction request before sending
   */
  validatePredictionRequest: (request: any, type: string): string[] => {
    const errors: string[] = [];
    
    if (type === 'campaign_performance') {
      if (!request.campaign_config) {
        errors.push('Campaign configuration is required');
      } else {
        if (!request.campaign_config.budget) {
          errors.push('Budget information is required');
        }
        if (!request.campaign_config.targeting) {
          errors.push('Targeting information is required');
        }
      }
    }
    
    if (type === 'viral_potential') {
      if (!request.content_config) {
        errors.push('Content configuration is required');
      } else {
        if (!request.content_config.content_type) {
          errors.push('Content type is required');
        }
        if (!request.content_config.topic) {
          errors.push('Content topic is required');
        }
      }
    }
    
    return errors;
  },

  /**
   * Check if prediction is cached
   */
  isCachedPrediction: (prediction: PredictionResponse): boolean => {
    return prediction.cached === true;
  },

  /**
   * Get cache age in hours
   */
  getCacheAge: (prediction: PredictionResponse): number | null => {
    if (!prediction.created_at || !prediction.cached) return null;
    
    const createdAt = new Date(prediction.created_at);
    const now = new Date();
    const diffMs = now.getTime() - createdAt.getTime();
    return diffMs / (1000 * 60 * 60); // Convert to hours
  },

  /**
   * Determine if prediction needs refresh based on age
   */
  needsRefresh: (prediction: PredictionResponse, maxAgeHours: number = 24): boolean => {
    const age = mlPredictionUtils.getCacheAge(prediction);
    return age ? age > maxAgeHours : true;
  }

};

export default mlPredictionService;