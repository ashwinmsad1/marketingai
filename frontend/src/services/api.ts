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

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Check if this is an email verification error
      const errorDetail = error.response?.data?.detail;
      if (typeof errorDetail === 'object' && errorDetail?.error_code === 'EMAIL_NOT_VERIFIED') {
        // Redirect to email verification page with context
        window.location.href = '/verify-email';
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
    const response = await api.post('/api/auth/login', { email, password });
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
    const response = await api.post('/api/auth/register', userData);
    return response;
  },

  refreshToken: async (refreshToken: string) => {
    const response = await api.post('/api/auth/refresh', { refresh_token: refreshToken });
    return response;
  },

  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response;
  },

  updateProfile: async (userData: any) => {
    const response = await api.put('/api/auth/me', userData);
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
    type: string;
    prompt: string;
    caption?: string;
    style?: string;
    industry?: string;
    business_details?: Record<string, any>;
    competitor_url?: string;
    competitor_name?: string;
    user_id?: string;
  }) => {
    const response = await api.post('/api/campaigns', campaignData);
    return response.data;
  },

  getCampaigns: async (userId: string = 'default_user', limit: number = 50) => {
    const response = await api.get('/api/campaigns', {
      params: { user_id: userId, limit }
    });
    return response.data;
  },

  getCampaign: async (campaignId: string) => {
    const response = await api.get(`/api/campaigns/${campaignId}`);
    return response.data;
  },

  deleteCampaign: async (campaignId: string) => {
    const response = await api.delete(`/api/campaigns/${campaignId}`);
    return response.data;
  },

  updateCampaignStatus: async (campaignId: string, status: string) => {
    const response = await api.patch(`/api/campaigns/${campaignId}`, { status });
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
    const response = await api.post('/api/media/images/generate', imageData);
    return response.data;
  },

  generateVideo: async (videoData: {
    prompt: string;
    style?: string;
    duration?: number;
    aspect_ratio?: string;
    motion?: string;
    music_style?: string;
    text_overlay?: boolean;
    brand_colors?: string;
  }) => {
    const response = await api.post('/api/media/videos/generate', videoData);
    return response.data;
  },

  getMedia: async (userId: string = 'default_user', mediaType?: string) => {
    const response = await api.get('/api/media', {
      params: { user_id: userId, media_type: mediaType }
    });
    return response.data;
  },

  uploadMedia: async (file: File, mediaType: 'image' | 'video') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', mediaType);

    const response = await api.post('/api/media/upload', formData, {
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

// Industry Templates
export const templateService = {
  getIndustryTemplates: async () => {
    const response = await api.get('/api/templates/industries');
    return response.data;
  },

  getIndustryTemplate: async (industry: string) => {
    const response = await api.get(`/api/templates/industries/${industry}`);
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

  createViralCampaign: async (topicId: string, userId: string, industry?: string) => {
    const response = await api.post('/api/viral/create', {
      topic_id: topicId,
      user_id: userId,
      industry
    });
    return response.data;
  },
};

// Competitor Analysis
export const competitorService = {
  analyzeCompetitor: async (url: string, contentType: string = 'webpage') => {
    const response = await api.post('/api/competitors/analyze', {
      url,
      content_type: contentType
    });
    return response.data;
  },

  generateCompetitiveCampaign: async (competitorContentId: string, userId: string) => {
    const response = await api.post('/api/competitors/generate-campaign', {
      competitor_content_id: competitorContentId,
      user_id: userId
    });
    return response.data;
  },
};

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