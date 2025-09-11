import axios from 'axios';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for video generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Navigation handler for redirects (can be overridden by app)
let navigationHandler: ((path: string) => void) | null = null;

export const setNavigationHandler = (handler: (path: string) => void) => {
  navigationHandler = handler;
};

const handleRedirect = (path: string) => {
  if (navigationHandler) {
    navigationHandler(path);
  } else {
    // Fallback to direct navigation if no handler is set
    window.location.href = path;
  }
};

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      handleRedirect('/login');
    } else if (error.response?.status === 403) {
      // Check if this is an email verification error
      const errorDetail = error.response?.data?.detail;
      if (typeof errorDetail === 'object' && errorDetail?.error_code === 'EMAIL_NOT_VERIFIED') {
        // Redirect to email verification page with context
        handleRedirect('/verify-email');
      }
    }
    return Promise.reject(error);
  }
);

// Authentication Management
export const authService = {
  // Auth token management
  setAuthToken: (token: string | null) => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  },

  // Authentication endpoints
  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    return response;
  },

  register: async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    company_name?: string;
    phone?: string;
  }) => {
    const response = await api.post('/api/v1/auth/register', userData);
    return response;
  },

  refreshToken: async (refreshToken: string) => {
    const response = await api.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
    return response;
  },

  logout: async () => {
    const response = await api.post('/api/v1/auth/logout');
    return response;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response;
  },

  updateProfile: async (userData: any) => {
    const response = await api.put('/api/v1/auth/me', userData);
    return response;
  },

  // Email verification
  verifyEmail: async (token: string) => {
    const response = await api.post('/api/auth/verify-email', { token });
    return response;
  },

  resendVerificationEmail: async () => {
    const response = await api.post('/api/auth/resend-verification');
    return response;
  },

  getVerificationStatus: async () => {
    const response = await api.get('/api/auth/verification-status');
    return response;
  },

  // Password reset
  requestPasswordReset: async (email: string) => {
    const response = await api.post('/api/auth/request-password-reset', { email });
    return response;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post('/api/auth/reset-password', {
      token,
      new_password: newPassword
    });
    return response;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response;
  },
};

// Meta Account Management
export const metaService = {
  // Start Meta OAuth connection
  startConnection: async () => {
    const response = await api.get('/api/meta/connect/start');
    return response;
  },

  // Handle OAuth callback
  handleOAuthCallback: async (code: string, state: string) => {
    const response = await api.post('/api/meta/connect/callback', { code, state });
    return response;
  },

  // Get connected accounts
  getConnectedAccounts: async () => {
    const response = await api.get('/api/meta/accounts');
    return response;
  },

  // Disconnect account
  disconnectAccount: async (accountId: string) => {
    const response = await api.delete(`/api/meta/accounts/${accountId}`);
    return response;
  },

  // Refresh account token
  refreshToken: async (accountId: string) => {
    const response = await api.post(`/api/meta/accounts/${accountId}/refresh`);
    return response;
  },
};

// API service functions

// User Management
export const userService = {
  getUser: async (userId: string) => {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  },

  getDashboard: async (userId: string) => {
    const response = await api.get(`/api/users/${userId}/dashboard`);
    return response.data;
  },
};

// Campaign Management
export const campaignService = {
  createCampaign: async (campaignData: {
    name: string;
    description?: string;
    type: string;
    prompt: string;
    caption?: string;
    style?: string;
    aspect_ratio?: string;
    platforms: {
      facebook: boolean;
      instagram: boolean;
    };
    budget: {
      daily_budget: number;
      total_budget: number;
      duration_days: number;
    };
    targeting?: {
      demographics?: string[];
      interests?: string[];
      locations?: string[];
      age_range?: { min: number; max: number };
      gender?: string;
    };
    auto_optimization?: boolean;
    schedule_start?: string;
    schedule_end?: string;
    industry?: string;
    business_details?: Record<string, any>;
  }) => {
    const response = await api.post('/api/v1/campaigns/create', campaignData);
    return response.data;
  },

  getCampaigns: async (limit: number = 50) => {
    const response = await api.get('/api/v1/campaigns/', {
      params: { limit }
    });
    return response.data;
  },

  getCampaign: async (campaignId: string) => {
    const response = await api.get(`/api/v1/campaigns/${campaignId}`);
    return response.data;
  },

  updateCampaign: async (campaignId: string, campaignData: any) => {
    const response = await api.put(`/api/v1/campaigns/${campaignId}`, campaignData);
    return response.data;
  },

  deleteCampaign: async (campaignId: string) => {
    const response = await api.delete(`/api/v1/campaigns/${campaignId}`);
    return response.data;
  },

  getBudgetStatus: async () => {
    const response = await api.get('/api/v1/campaigns/budget-status');
    return response.data;
  },

  getUsageStatus: async () => {
    const response = await api.get('/api/v1/campaigns/usage-status');
    return response.data;
  },

  updateCampaignStatus: async (campaignId: string, status: string) => {
    const response = await api.patch(`/api/v1/campaigns/${campaignId}`, { status });
    return response.data;
  },
};

// Media Generation
export const mediaService = {
  generateImage: async (imageData: {
    prompt: string;
    style?: string;
    aspect_ratio?: string;
    quality?: string;
    creativity?: number;
    iterations?: number;
  }) => {
    const response = await api.post('/api/v1/media/images/generate', imageData);
    return response.data;
  },

  generateVideo: async (videoData: {
    prompt: string;
    style?: string;
    aspect_ratio?: string;
    business_description?: string;
    target_audience_description?: string;
    unique_value_proposition?: string;
  }) => {
    const response = await api.post('/api/v1/media/videos/generate', videoData);
    return response.data;
  },

  generateVideoFromImage: async (imageData: {
    image_url: string;
    prompt?: string;
    style?: string;
    aspect_ratio?: string;
    duration?: number;
  }) => {
    const response = await api.post('/api/v1/media/videos/from-image', imageData);
    return response.data;
  },

  getMedia: async (mediaType?: string) => {
    const response = await api.get('/api/v1/media/', {
      params: { media_type: mediaType }
    });
    return response.data;
  },

  uploadMedia: async (file: File, mediaType: 'image' | 'video') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', mediaType);

    const response = await api.post('/api/v1/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Performance Tracking
export const trackingService = {
  trackConversion: async (conversionData: {
    campaign_id: string;
    conversion_type: string;
    value: number;
    customer_id?: string;
    metadata?: Record<string, any>;
  }) => {
    const response = await api.post('/api/tracking/conversion', conversionData);
    return response.data;
  },

  getCampaignMetrics: async (campaignId: string) => {
    const response = await api.get(`/api/campaigns/${campaignId}/metrics`);
    return response.data;
  },
};

// Analytics
export const analyticsService = {
  getDashboard: async (userId: string) => {
    const response = await api.get(`/api/analytics/dashboard/${userId}`);
    return response.data;
  },

  getPerformanceMetrics: async (userId: string, dateRange?: string) => {
    const response = await api.get(`/api/analytics/performance/${userId}`, {
      params: { date_range: dateRange }
    });
    return response.data;
  },

  getRevenueAnalytics: async (userId: string) => {
    const response = await api.get(`/api/analytics/revenue/${userId}`);
    return response.data;
  },
};

// Campaign Templates (User-defined)
export const templateService = {
  getUserTemplates: async () => {
    const response = await api.get('/api/templates/user');
    return response.data;
  },

  saveUserTemplate: async (template: {
    name: string;
    description: string;
    business_description: string;
    target_audience: string;
    campaign_goal: string;
  }) => {
    const response = await api.post('/api/templates/user', template);
    return response.data;
  },

  createFromTemplate: async (templateId: string, customizations: Record<string, any>) => {
    const response = await api.post(`/api/templates/${templateId}/create`, customizations);
    return response.data;
  },
};

// Viral Content
export const viralService = {
  getViralOpportunities: async () => {
    const response = await api.get('/api/viral/opportunities');
    return response.data;
  },

  createViralCampaign: async (topicId: string, industry?: string) => {
    const response = await api.post('/api/viral/create', {
      topic_id: topicId,
      industry
    });
    return response.data;
  },
};


// Personalization Services
export const personalizationService = {
  // User Profile Management
  createProfile: async (profileData: any) => {
    const response = await api.post('/api/personalization/profile', profileData);
    return response.data;
  },

  getProfile: async (userId?: string) => {
    const url = userId 
      ? `/api/personalization/profile/${userId}`
      : '/api/personalization/profile';
    const response = await api.get(url);
    return response.data;
  },

  updateProfile: async (profileData: any, userId?: string) => {
    const url = userId 
      ? `/api/personalization/profile/${userId}`
      : '/api/personalization/profile';
    const response = await api.put(url, profileData);
    return response.data;
  },

  deleteProfile: async (userId?: string) => {
    const url = userId 
      ? `/api/personalization/profile/${userId}`
      : '/api/personalization/profile';
    const response = await api.delete(url);
    return response.data;
  },

  // Campaign Strategy
  generateCampaignStrategy: async (strategyRequest: any) => {
    const response = await api.post('/api/personalization/campaign-strategy', strategyRequest);
    return response.data;
  },

  getCampaignStrategies: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/personalization/campaign-strategy', { params });
    return response.data;
  },

  getCampaignStrategy: async (strategyId: string) => {
    const response = await api.get(`/api/personalization/campaign-strategy/${strategyId}`);
    return response.data;
  },

  updateCampaignStrategy: async (strategyId: string, updates: any) => {
    const response = await api.put(`/api/personalization/campaign-strategy/${strategyId}`, updates);
    return response.data;
  },

  deleteCampaignStrategy: async (strategyId: string) => {
    const response = await api.delete(`/api/personalization/campaign-strategy/${strategyId}`);
    return response.data;
  },

  // A/B Testing
  createABTest: async (testRequest: any) => {
    const response = await api.post('/api/personalization/ab-tests', testRequest);
    return response.data;
  },

  getABTests: async (userId?: string, status?: string) => {
    const params: any = {};
    if (userId) params.user_id = userId;
    if (status) params.status = status;
    const response = await api.get('/api/personalization/ab-tests', { params });
    return response.data;
  },

  getABTest: async (testId: string) => {
    const response = await api.get(`/api/personalization/ab-tests/${testId}`);
    return response.data;
  },

  updateABTest: async (testId: string, updates: any) => {
    const response = await api.put(`/api/personalization/ab-tests/${testId}`, updates);
    return response.data;
  },

  startABTest: async (testId: string) => {
    const response = await api.post(`/api/personalization/ab-tests/${testId}/start`);
    return response.data;
  },

  pauseABTest: async (testId: string) => {
    const response = await api.post(`/api/personalization/ab-tests/${testId}/pause`);
    return response.data;
  },

  completeABTest: async (testId: string) => {
    const response = await api.post(`/api/personalization/ab-tests/${testId}/complete`);
    return response.data;
  },

  deleteABTest: async (testId: string) => {
    const response = await api.delete(`/api/personalization/ab-tests/${testId}`);
    return response.data;
  },

  getABTestResults: async (testId: string) => {
    const response = await api.get(`/api/personalization/ab-tests/${testId}/results`);
    return response.data;
  },

  // Personalization Ask (AI Assistant)
  askPersonalizationQuestion: async (question: string, context?: any) => {
    const requestData = { question, context };
    const response = await api.post('/api/personalization/ask', requestData);
    return response.data;
  },

  // Campaign Recommendations
  getRecommendations: async (userId?: string, campaignId?: string) => {
    const params: any = {};
    if (userId) params.user_id = userId;
    if (campaignId) params.campaign_id = campaignId;
    const response = await api.get('/api/personalization/recommendations', { params });
    return response.data;
  },

  getRecommendation: async (recommendationId: string) => {
    const response = await api.get(`/api/personalization/recommendations/${recommendationId}`);
    return response.data;
  },

  applyRecommendation: async (recommendationId: string) => {
    const response = await api.post(`/api/personalization/recommendations/${recommendationId}/apply`);
    return response.data;
  },

  dismissRecommendation: async (recommendationId: string) => {
    const response = await api.post(`/api/personalization/recommendations/${recommendationId}/dismiss`);
    return response.data;
  },

  // Personalization Insights
  getInsights: async (userId?: string, timeframe?: string) => {
    const params: any = {};
    if (userId) params.user_id = userId;
    if (timeframe) params.timeframe = timeframe;
    const response = await api.get('/api/personalization/insights', { params });
    return response.data;
  },

  getAudienceInsights: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/personalization/audience-insights', { params });
    return response.data;
  },

  getContentInsights: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/personalization/content-insights', { params });
    return response.data;
  },

  getPerformancePredictions: async (userId?: string, scenario?: any) => {
    const params = userId ? { user_id: userId } : {};
    const requestData = scenario ? { scenario } : {};
    const response = await api.post('/api/personalization/predictions', requestData, { params });
    return response.data;
  },

  // Content Templates
  getContentTemplates: async (category?: string, industry?: string) => {
    const params: any = {};
    if (category) params.category = category;
    if (industry) params.industry = industry;
    const response = await api.get('/api/personalization/content-templates', { params });
    return response.data;
  },

  getContentTemplate: async (templateId: string) => {
    const response = await api.get(`/api/personalization/content-templates/${templateId}`);
    return response.data;
  },

  generateContentFromTemplate: async (templateId: string, personalizationData: any) => {
    const response = await api.post(`/api/personalization/content-templates/${templateId}/generate`, personalizationData);
    return response.data;
  },

  customizeTemplate: async (templateId: string, customizations: any) => {
    const response = await api.post(`/api/personalization/content-templates/${templateId}/customize`, customizations);
    return response.data;
  },

  // Learning Analytics
  getLearningInsights: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/personalization/learning-insights', { params });
    return response.data;
  },

  getPerformancePatterns: async (userId?: string, patternType?: string) => {
    const params: any = {};
    if (userId) params.user_id = userId;
    if (patternType) params.pattern_type = patternType;
    const response = await api.get('/api/personalization/performance-patterns', { params });
    return response.data;
  },

  getOptimizationOpportunities: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/personalization/optimization-opportunities', { params });
    return response.data;
  },

  // Personalized Campaign Creation
  // Video Strategy Generation (User Input Based)
  generateVideoStrategy: async (strategyRequest: {
    user_id: string;
    campaign_brief: string;
    business_description: string;
    target_audience_description: string;
    unique_value_proposition: string;
    preferred_style?: string;
    aspect_ratios?: string[];
  }) => {
    const response = await api.post('/api/personalization/video-strategy', strategyRequest);
    return response.data;
  },

  // Image Strategy Generation (User Input Based)
  generateImageStrategy: async (strategyRequest: {
    user_id: string;
    campaign_brief: string;
    business_description: string;
    target_audience_description: string;
    unique_value_proposition: string;
    preferred_style?: string;
    image_format?: string;
  }) => {
    const response = await api.post('/api/personalization/image-strategy', strategyRequest);
    return response.data;
  },

  createPersonalizedCampaign: async (campaignData: any) => {
    const response = await api.post('/api/personalization/campaigns/create', campaignData);
    return response.data;
  },

  optimizeExistingCampaign: async (campaignId: string, optimizationPreferences?: any) => {
    const response = await api.post(`/api/personalization/campaigns/${campaignId}/optimize`, optimizationPreferences);
    return response.data;
  },

  // Audience Segmentation
  getAudienceSegments: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/personalization/audience-segments', { params });
    return response.data;
  },

  createAudienceSegment: async (segmentData: any) => {
    const response = await api.post('/api/personalization/audience-segments', segmentData);
    return response.data;
  },

  updateAudienceSegment: async (segmentId: string, updates: any) => {
    const response = await api.put(`/api/personalization/audience-segments/${segmentId}`, updates);
    return response.data;
  },

  deleteAudienceSegment: async (segmentId: string) => {
    const response = await api.delete(`/api/personalization/audience-segments/${segmentId}`);
    return response.data;
  },

  // Performance Analytics
  getPersonalizationPerformance: async (userId?: string, timeframe?: string) => {
    const params: any = {};
    if (userId) params.user_id = userId;
    if (timeframe) params.timeframe = timeframe;
    const response = await api.get('/api/personalization/performance', { params });
    return response.data;
  },

  comparePersonalizationImpact: async (userId?: string, campaignIds?: string[]) => {
    const params: any = {};
    if (userId) params.user_id = userId;
    if (campaignIds?.length) params.campaign_ids = campaignIds.join(',');
    const response = await api.get('/api/personalization/performance/comparison', { params });
    return response.data;
  },
};

// Subscription Management
export const subscriptionService = {
  upgradeSubscription: async (targetTier: string, billingCycle: string) => {
    const response = await api.post('/api/v1/subscription/upgrade', {
      target_tier: targetTier,
      billing_cycle: billingCycle
    });
    return response.data;
  },

  getCurrentSubscription: async () => {
    const response = await api.get('/api/v1/subscription/current');
    return response.data;
  },

  cancelSubscription: async () => {
    const response = await api.post('/api/v1/subscription/cancel');
    return response.data;
  },

  getBillingHistory: async () => {
    const response = await api.get('/api/v1/subscription/billing-history');
    return response.data;
  },

  updatePaymentMethod: async (paymentData: any) => {
    const response = await api.put('/api/v1/subscription/payment-method', paymentData);
    return response.data;
  }
};

// Privacy and Data Management
export const privacyService = {
  getPrivacyPolicy: async () => {
    const response = await api.get('/api/v1/privacy/privacy-policy');
    return response.data;
  },

  updateConsent: async (consentData: any) => {
    const response = await api.post('/api/v1/privacy/consent', consentData);
    return response.data;
  },

  getConsentStatus: async () => {
    const response = await api.get('/api/v1/privacy/consent/status');
    return response.data;
  },

  requestDataDeletion: async (deletionRequest: any) => {
    const response = await api.post('/api/v1/privacy/data-deletion', deletionRequest);
    return response.data;
  },

  getDataRequests: async () => {
    const response = await api.get('/api/v1/privacy/data-requests');
    return response.data;
  },

  deleteAccount: async () => {
    const response = await api.delete('/api/v1/privacy/account');
    return response.data;
  },

  getComplianceStatus: async () => {
    const response = await api.get('/api/v1/privacy/compliance-status');
    return response.data;
  }
};

// Note: ML Prediction services moved to dedicated mlPredictionService.ts

// Utility functions
export const healthService = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  getApiInfo: async () => {
    const response = await api.get('/');
    return response.data;
  },
};

// File download helper
export const downloadFile = async (url: string, filename?: string) => {
  try {
    const response = await api.get(url, { responseType: 'blob' });
    
    // Create blob link to download
    const urlBlob = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = urlBlob;
    link.setAttribute('download', filename || 'download');
    
    // Append to html link element page
    document.body.appendChild(link);
    
    // Start download
    link.click();
    
    // Clean up and remove the link
    link.parentNode?.removeChild(link);
    window.URL.revokeObjectURL(urlBlob);
    
    return true;
  } catch (error) {
    console.error('Download failed:', error);
    return false;
  }
};

// Error handling helper
export const handleApiError = (error: any) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return { message: data.detail || 'Bad request', type: 'error' };
      case 401:
        return { message: 'Unauthorized access', type: 'error' };
      case 403:
        return { message: 'Access forbidden', type: 'error' };
      case 404:
        return { message: 'Resource not found', type: 'error' };
      case 429:
        return { message: 'Too many requests. Please try again later.', type: 'warning' };
      case 500:
        return { message: 'Server error. Please try again later.', type: 'error' };
      default:
        return { message: data.detail || 'An error occurred', type: 'error' };
    }
  } else if (error.request) {
    // The request was made but no response was received
    return { message: 'No response from server. Please check your connection.', type: 'error' };
  } else {
    // Something happened in setting up the request that triggered an Error
    return { message: 'Request failed. Please try again.', type: 'error' };
  }
};

export default api;