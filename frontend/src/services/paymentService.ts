/**
 * Payment Service for Frontend
 * Provides TypeScript interfaces and API calls for payment and subscription features
 */

import api from './api';

// Types for Payment and Subscriptions
export interface PaymentConfig {
  razorpay_enabled: boolean;
  upi_enabled: boolean;
  supported_methods: string[];
  currency: string;
  min_amount: number;
  max_amount: number;
  subscription_tiers: {
    starter: { monthly_price: number; features: string[] };
    professional: { monthly_price: number; features: string[] };
    enterprise: { monthly_price: number; features: string[] };
  };
}

export interface SubscriptionRequest {
  tier: 'starter' | 'professional' | 'enterprise';
  billing_cycle: 'monthly' | 'yearly';
  payment_method: 'upi' | 'razorpay' | 'card';
  coupon_code?: string;
}

export interface PaymentOrderRequest {
  amount: number;
  currency: string;
  order_type: 'subscription' | 'one_time';
  subscription_tier?: string;
  billing_cycle?: string;
  description?: string;
}

export interface PaymentOrderResponse {
  success: boolean;
  order_id: string;
  payment_url?: string;
  razorpay_order_id?: string;
  upi_intent?: string;
  amount: number;
  currency: string;
  expires_at: string;
}

export interface SubscriptionResponse {
  success: boolean;
  subscription_id: string;
  tier: string;
  status: string;
  billing_cycle: string;
  current_period_start: string;
  current_period_end: string;
  next_billing_date: string;
  amount: number;
  currency: string;
}

export interface BillingHistoryItem {
  invoice_id: string;
  date: string;
  amount: number;
  currency: string;
  status: string;
  description: string;
  payment_method: string;
  download_url?: string;
}

export interface PaymentMethodRequest {
  payment_method: 'upi' | 'card' | 'razorpay';
  upi_id?: string;
  card_details?: {
    last_four: string;
    brand: string;
    exp_month: number;
    exp_year: number;
  };
  is_default?: boolean;
}

export interface PaymentStatusResponse {
  order_id: string;
  status: 'pending' | 'paid' | 'failed' | 'cancelled';
  payment_method?: string;
  transaction_id?: string;
  amount: number;
  currency: string;
  paid_at?: string;
  failure_reason?: string;
}

/**
 * Payment and Subscription API Service
 */
export const paymentService = {
  
  /**
   * Get payment configuration and available options
   */
  getPaymentConfig: async (): Promise<PaymentConfig> => {
    const response = await api.get('/api/v1/payment/config');
    return response.data;
  },

  /**
   * Create a new subscription
   */
  createSubscription: async (subscriptionData: SubscriptionRequest): Promise<SubscriptionResponse> => {
    const response = await api.post('/api/v1/payment/create-subscription', subscriptionData);
    return response.data;
  },

  /**
   * Create a payment order for subscription or one-time payment
   */
  createPaymentOrder: async (orderData: PaymentOrderRequest): Promise<PaymentOrderResponse> => {
    const response = await api.post('/api/v1/payment/create-payment-order', orderData);
    return response.data;
  },

  /**
   * Activate subscription after successful payment
   */
  activateSubscription: async (data: {
    order_id: string;
    payment_id: string;
    signature?: string;
  }): Promise<SubscriptionResponse> => {
    const response = await api.post('/api/v1/payment/activate-subscription', data);
    return response.data;
  },

  /**
   * Get current active subscription
   */
  getCurrentSubscription: async (): Promise<SubscriptionResponse> => {
    const response = await api.get('/api/v1/payment/subscriptions/current');
    return response.data;
  },

  /**
   * Cancel active subscription
   */
  cancelSubscription: async (data: {
    reason?: string;
    feedback?: string;
    cancel_at_period_end?: boolean;
  }): Promise<{ success: boolean; message: string; cancelled_at: string }> => {
    const response = await api.post('/api/v1/payment/subscriptions/cancel', data);
    return response.data;
  },

  /**
   * Get billing history
   */
  getBillingHistory: async (options?: {
    page?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<{
    invoices: BillingHistoryItem[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  }> => {
    const response = await api.get('/api/v1/payment/billing/history', {
      params: options
    });
    return response.data;
  },

  /**
   * Update payment method
   */
  updatePaymentMethod: async (paymentMethodData: PaymentMethodRequest): Promise<{
    success: boolean;
    message: string;
    payment_method_id: string;
  }> => {
    const response = await api.post('/api/v1/payment/update-payment-method', paymentMethodData);
    return response.data;
  },

  /**
   * Get payment status by order ID
   */
  getPaymentStatus: async (orderId: string): Promise<PaymentStatusResponse> => {
    const response = await api.get(`/api/v1/payment/status/${orderId}`);
    return response.data;
  },

  /**
   * Handle webhook (usually called by payment provider)
   * Note: This is primarily for server-to-server communication
   */
  handleWebhook: async (webhookData: any): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/api/v1/payment/webhook', webhookData);
    return response.data;
  }

};

/**
 * Utility functions for payment operations
 */
export const paymentUtils = {
  
  /**
   * Format currency amount for display
   */
  formatAmount: (amount: number, currency: string = 'INR'): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  },

  /**
   * Get subscription tier display name
   */
  getTierDisplayName: (tier: string): string => {
    const names: Record<string, string> = {
      'starter': 'Starter Plan',
      'professional': 'Professional Plan',
      'enterprise': 'Enterprise Plan'
    };
    return names[tier] || tier;
  },

  /**
   * Get subscription status color for UI
   */
  getStatusColor: (status: string): string => {
    const colors: Record<string, string> = {
      'active': 'green',
      'cancelled': 'red',
      'expired': 'orange',
      'trial': 'blue',
      'pending': 'yellow'
    };
    return colors[status] || 'gray';
  },

  /**
   * Calculate days remaining in subscription
   */
  getDaysRemaining: (endDate: string): number => {
    const end = new Date(endDate);
    const now = new Date();
    const diffTime = end.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  },

  /**
   * Validate UPI ID format
   */
  validateUpiId: (upiId: string): boolean => {
    const upiRegex = /^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$/;
    return upiRegex.test(upiId);
  },

  /**
   * Get payment method icon name
   */
  getPaymentMethodIcon: (method: string): string => {
    const icons: Record<string, string> = {
      'upi': 'phone',
      'card': 'credit-card',
      'razorpay': 'wallet',
      'bank_transfer': 'bank'
    };
    return icons[method] || 'payment';
  },

  /**
   * Check if subscription needs renewal
   */
  needsRenewal: (subscription: SubscriptionResponse): boolean => {
    if (subscription.status !== 'active') return false;
    
    const endDate = new Date(subscription.current_period_end);
    const now = new Date();
    const daysLeft = paymentUtils.getDaysRemaining(subscription.current_period_end);
    
    // Notify if less than 7 days remaining
    return daysLeft <= 7;
  },

  /**
   * Calculate monthly vs yearly savings
   */
  calculateYearlySavings: (monthlyPrice: number, yearlyPrice: number): {
    savings: number;
    percentage: number;
  } => {
    const yearlyMonthly = yearlyPrice / 12;
    const savings = (monthlyPrice * 12) - yearlyPrice;
    const percentage = (savings / (monthlyPrice * 12)) * 100;
    
    return {
      savings: Math.round(savings),
      percentage: Math.round(percentage)
    };
  }

};

export default paymentService;