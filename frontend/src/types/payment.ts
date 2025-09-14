/**
 * Payment and subscription TypeScript type definitions
 */

export interface PaymentOrder {
  id: string;
  amount: number;
  currency: string;
  status: 'created' | 'attempted' | 'paid' | 'failed' | 'cancelled';
  receipt: string;
  created_at: string;
  notes?: Record<string, string>;
}

export interface UPIPaymentData {
  order: PaymentOrder;
  payment_url?: string;
  upi_deep_link: string;
  qr_code_url?: string;
}

export interface PaymentConfig {
  merchant_name: string;
  merchant_upi_id: string;
  supported_apps: string[];
  max_amount: number;
  min_amount: number;
  currency: string;
  environment: 'production' | 'sandbox';
}

export interface PaymentSuccessData {
  payment_id: string;
  order_id: string;
  subscription_id: string;
  amount: number;
  status: 'succeeded';
  payment_method?: string;
  processed_at?: string;
}

export interface PaymentStatus {
  status: 'pending' | 'succeeded' | 'failed' | 'cancelled';
  payment_id?: string;
  order_id: string;
  error_message?: string;
  processed_at?: string;
  failure_reason?: string;
}

export interface SubscriptionDetails {
  subscription_id: string;
  tier: 'basic' | 'professional' | 'business';
  status: 'active' | 'trial' | 'past_due' | 'canceled' | 'incomplete';
  monthly_price: number;
  currency: string;
  is_trial: boolean;
  trial_end: string | null;
  trial_days_remaining: number | null;
  next_billing_date: string | null;
  created_at: string;
  updated_at: string;
  limits: {
    campaigns: number | 'unlimited';
    ai_generations: number | 'unlimited';
    api_calls: number | 'unlimited';
    analytics_retention_days: number;
  };
  usage: {
    campaigns: { used: number; limit: number | 'unlimited'; percentage: number };
    ai_generations: { used: number; limit: number | 'unlimited'; percentage: number };
    api_calls: { used: number; limit: number | 'unlimited'; percentage: number };
  };
  features: string[];
}

export interface BillingItem {
  id: string;
  type: 'payment' | 'invoice';
  amount: number;
  currency: string;
  description?: string;
  status: 'succeeded' | 'failed' | 'pending' | 'disputed';
  provider?: 'upi' | 'card' | 'netbanking' | 'wallet';
  created_at: string;
  processed_at?: string;
  invoice_number?: string;
  period_start?: string;
  period_end?: string;
  due_date?: string;
  paid_at?: string;
  payment_method_details?: {
    upi?: {
      vpa: string;
    };
    card?: {
      last4: string;
      brand: string;
    };
  };
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  description: string;
  features: string[];
  icon: React.ReactNode;
  popular?: boolean;
  tier: 'basic' | 'professional' | 'business';
}

export interface CreateSubscriptionRequest {
  tier: 'basic' | 'professional' | 'business';
  plan_id: string;
  monthly_price: number;
  start_trial: boolean;
  payment_method_types?: string[];
}

export interface CreateSubscriptionResponse {
  subscription_id: string;
  tier: string;
  status: string;
  trial_started: boolean;
  trial_end?: string;
  next_billing_date?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaymentPollingOptions {
  maxAttempts?: number;
  initialDelay?: number;
  maxDelay?: number;
  timeout?: number;
}

export interface ValidatedPaymentData {
  payment_id: string;
  order_id: string;
  signature?: string;
  subscription_id: string;
}

// Error types
export class PaymentError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'PaymentError';
  }
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public value?: any
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string = 'Authentication required') {
    super(message);
    this.name = 'AuthenticationError';
  }
}