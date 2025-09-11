/**
 * Privacy Service for Frontend
 * Provides TypeScript interfaces and API calls for GDPR/CCPA compliance features
 */

import api from './api';

// Types for Privacy and Compliance
export interface ConsentRequest {
  consent_type: 'marketing' | 'analytics' | 'functional' | 'advertising' | 'data_processing';
  consented: boolean;
  consent_text: string;
  ip_address?: string;
  user_agent?: string;
}

export interface ConsentStatus {
  consent_id: string;
  consent_type: string;
  consented: boolean;
  consent_date: string;
  consent_text: string;
  ip_address?: string;
  user_agent?: string;
  updated_at: string;
}

export interface DataDeletionRequest {
  deletion_type: 'full_account' | 'specific_data' | 'campaign_data' | 'analytics_data';
  reason: string;
  data_types?: string[];
  confirm_deletion: boolean;
}

export interface DataDeletionResponse {
  success: boolean;
  request_id: string;
  deletion_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  estimated_completion: string;
  data_types_affected: string[];
  message: string;
}

export interface DataRequest {
  request_id: string;
  request_type: 'deletion' | 'export' | 'rectification';
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  requested_at: string;
  completed_at?: string;
  data_types: string[];
  description: string;
  estimated_completion?: string;
  download_url?: string;
}

export interface PrivacyPolicy {
  version: string;
  effective_date: string;
  last_updated: string;
  content: {
    data_collection: string;
    data_usage: string;
    data_sharing: string;
    data_retention: string;
    user_rights: string;
    contact_info: string;
  };
  changes_summary?: string[];
}

export interface ComplianceStatus {
  gdpr_compliant: boolean;
  ccpa_compliant: boolean;
  data_retention_policy: {
    user_data: number; // days
    campaign_data: number;
    analytics_data: number;
    logs: number;
  };
  consent_status: {
    marketing: boolean;
    analytics: boolean;
    functional: boolean;
    advertising: boolean;
    data_processing: boolean;
  };
  data_processing_purposes: string[];
  legal_basis: string;
  data_controller: {
    name: string;
    contact: string;
    dpo_contact?: string;
  };
  user_rights: string[];
  pending_requests: number;
}

export interface AccountDeletionRequest {
  confirmation_text: string;
  deletion_reason: string;
  feedback?: string;
  data_export_requested?: boolean;
}

export interface AccountDeletionResponse {
  success: boolean;
  deletion_id: string;
  scheduled_deletion_date: string;
  grace_period_days: number;
  data_export_available: boolean;
  export_download_url?: string;
  cancellation_deadline: string;
  message: string;
}

/**
 * Privacy and GDPR Compliance API Service
 */
export const privacyService = {
  
  /**
   * Record user consent for specific data processing
   */
  recordConsent: async (consentData: ConsentRequest): Promise<{
    success: boolean;
    consent_id: string;
    recorded_at: string;
    message: string;
  }> => {
    const response = await api.post('/api/v1/privacy/consent', consentData);
    return response.data;
  },

  /**
   * Get current consent status for all consent types
   */
  getConsentStatus: async (): Promise<{
    success: boolean;
    consents: ConsentStatus[];
    last_updated: string;
  }> => {
    const response = await api.get('/api/v1/privacy/consent/status');
    return response.data;
  },

  /**
   * Request data deletion (GDPR Article 17 - Right to be Forgotten)
   */
  requestDataDeletion: async (deletionRequest: DataDeletionRequest): Promise<DataDeletionResponse> => {
    const response = await api.post('/api/v1/privacy/data-deletion', deletionRequest);
    return response.data;
  },

  /**
   * Get all data requests (deletion, export, etc.)
   */
  getDataRequests: async (options?: {
    request_type?: 'deletion' | 'export' | 'rectification';
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<{
    requests: DataRequest[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  }> => {
    const response = await api.get('/api/v1/privacy/data-requests', {
      params: options
    });
    return response.data;
  },

  /**
   * Get current privacy policy
   */
  getPrivacyPolicy: async (): Promise<PrivacyPolicy> => {
    const response = await api.get('/api/v1/privacy/privacy-policy');
    return response.data;
  },

  /**
   * Request complete account deletion
   */
  deleteAccount: async (deletionData: AccountDeletionRequest): Promise<AccountDeletionResponse> => {
    const response = await api.delete('/api/v1/privacy/account', {
      data: deletionData
    });
    return response.data;
  },

  /**
   * Get comprehensive compliance status
   */
  getComplianceStatus: async (): Promise<ComplianceStatus> => {
    const response = await api.get('/api/v1/privacy/compliance-status');
    return response.data;
  },

  /**
   * Request data export (GDPR Article 20 - Data Portability)
   */
  requestDataExport: async (exportRequest: {
    data_types?: string[];
    format: 'json' | 'csv' | 'xml';
    include_metadata?: boolean;
  }): Promise<{
    success: boolean;
    export_id: string;
    estimated_completion: string;
    message: string;
  }> => {
    const response = await api.post('/api/v1/privacy/data-export', exportRequest);
    return response.data;
  },

  /**
   * Update consent preferences
   */
  updateConsent: async (consentId: string, updates: {
    consented: boolean;
    consent_text: string;
  }): Promise<{
    success: boolean;
    consent_id: string;
    updated_at: string;
    message: string;
  }> => {
    const response = await api.put(`/api/v1/privacy/consent/${consentId}`, updates);
    return response.data;
  },

  /**
   * Cancel a pending data request
   */
  cancelDataRequest: async (requestId: string): Promise<{
    success: boolean;
    request_id: string;
    cancelled_at: string;
    message: string;
  }> => {
    const response = await api.delete(`/api/v1/privacy/data-requests/${requestId}`);
    return response.data;
  }

};

/**
 * Utility functions for privacy operations
 */
export const privacyUtils = {
  
  /**
   * Get consent type display name
   */
  getConsentTypeDisplayName: (consentType: string): string => {
    const names: Record<string, string> = {
      'marketing': 'Marketing Communications',
      'analytics': 'Usage Analytics',
      'functional': 'Functional Cookies',
      'advertising': 'Personalized Advertising',
      'data_processing': 'Data Processing for Service'
    };
    return names[consentType] || consentType;
  },

  /**
   * Get consent type description
   */
  getConsentTypeDescription: (consentType: string): string => {
    const descriptions: Record<string, string> = {
      'marketing': 'Receive marketing emails, promotional content, and product updates',
      'analytics': 'Allow us to collect usage data to improve our services',
      'functional': 'Enable essential website functionality and user preferences',
      'advertising': 'Show you personalized ads based on your interests and behavior',
      'data_processing': 'Process your data to provide and improve our core services'
    };
    return descriptions[consentType] || 'Data processing for this purpose';
  },

  /**
   * Get data request status color for UI
   */
  getRequestStatusColor: (status: string): string => {
    const colors: Record<string, string> = {
      'pending': 'yellow',
      'processing': 'blue',
      'completed': 'green',
      'failed': 'red',
      'cancelled': 'gray'
    };
    return colors[status] || 'gray';
  },

  /**
   * Get data request status display name
   */
  getRequestStatusDisplayName: (status: string): string => {
    const names: Record<string, string> = {
      'pending': 'Pending Review',
      'processing': 'In Progress',
      'completed': 'Completed',
      'failed': 'Failed',
      'cancelled': 'Cancelled'
    };
    return names[status] || status;
  },

  /**
   * Calculate estimated completion time
   */
  getEstimatedCompletionDisplay: (estimatedCompletion: string): string => {
    const completion = new Date(estimatedCompletion);
    const now = new Date();
    const diffTime = completion.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 0) return 'Processing...';
    if (diffDays === 1) return '1 day remaining';
    if (diffDays <= 7) return `${diffDays} days remaining`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks remaining`;
    return `${Math.ceil(diffDays / 30)} months remaining`;
  },

  /**
   * Check if user has given all required consents
   */
  hasRequiredConsents: (consents: ConsentStatus[]): boolean => {
    const requiredConsents = ['functional', 'data_processing'];
    const givenConsents = consents
      .filter(c => c.consented)
      .map(c => c.consent_type);
    
    return requiredConsents.every(required => 
      givenConsents.includes(required)
    );
  },

  /**
   * Get missing required consents
   */
  getMissingRequiredConsents: (consents: ConsentStatus[]): string[] => {
    const requiredConsents = ['functional', 'data_processing'];
    const givenConsents = consents
      .filter(c => c.consented)
      .map(c => c.consent_type);
    
    return requiredConsents.filter(required => 
      !givenConsents.includes(required)
    );
  },

  /**
   * Format data types for display
   */
  formatDataTypes: (dataTypes: string[]): string => {
    const formatted = dataTypes.map(type => {
      const typeNames: Record<string, string> = {
        'user_profile': 'Profile Information',
        'campaign_data': 'Campaign Data',
        'analytics_data': 'Usage Analytics',
        'billing_data': 'Billing Information',
        'communication_logs': 'Communication History',
        'device_data': 'Device Information',
        'location_data': 'Location Data'
      };
      return typeNames[type] || type;
    });
    
    if (formatted.length <= 2) {
      return formatted.join(' and ');
    }
    
    return formatted.slice(0, -1).join(', ') + ', and ' + formatted[formatted.length - 1];
  },

  /**
   * Validate deletion confirmation text
   */
  validateDeletionConfirmation: (confirmationText: string): boolean => {
    const expectedText = 'DELETE MY ACCOUNT';
    return confirmationText.trim().toUpperCase() === expectedText;
  },

  /**
   * Check if request is within grace period for cancellation
   */
  isWithinGracePeriod: (requestDate: string, gracePeriodDays: number): boolean => {
    const request = new Date(requestDate);
    const now = new Date();
    const gracePeriodMs = gracePeriodDays * 24 * 60 * 60 * 1000;
    const deadline = new Date(request.getTime() + gracePeriodMs);
    
    return now < deadline;
  }

};

export default privacyService;