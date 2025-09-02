/**
 * Input validation and XSS protection utilities
 */

/**
 * Sanitize string input to prevent XSS
 */
export const sanitizeString = (input: string): string => {
  if (typeof input !== 'string') {
    return '';
  }
  
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

/**
 * Validate subscription ID format
 */
export const isValidSubscriptionId = (id: string): boolean => {
  if (!id || typeof id !== 'string') {
    return false;
  }
  
  // Subscription IDs should be alphanumeric with possible hyphens/underscores
  const subscriptionIdRegex = /^[a-zA-Z0-9_-]{1,50}$/;
  return subscriptionIdRegex.test(id);
};

/**
 * Validate payment amount
 */
export const isValidPaymentAmount = (amount: number): boolean => {
  if (typeof amount !== 'number' || isNaN(amount)) {
    return false;
  }
  
  // Amount should be positive and reasonable (0.01 to 100,000 INR)
  return amount >= 1 && amount <= 10000000; // in paisa (1 INR = 100 paisa)
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  if (!email || typeof email !== 'string') {
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 255;
};

/**
 * Validate payment order ID format
 */
export const isValidOrderId = (orderId: string): boolean => {
  if (!orderId || typeof orderId !== 'string') {
    return false;
  }
  
  // Order IDs should be alphanumeric with possible special chars but no spaces
  const orderIdRegex = /^[a-zA-Z0-9_-]{1,100}$/;
  return orderIdRegex.test(orderId);
};

/**
 * Validate UPI payment data structure
 */
export interface ValidatedPaymentData {
  payment_id: string;
  order_id: string;
  signature: string;
  subscription_id: string;
}

export const validatePaymentData = (data: any): ValidatedPaymentData | null => {
  if (!data || typeof data !== 'object') {
    return null;
  }
  
  const { payment_id, order_id, signature, subscription_id } = data;
  
  if (!isValidOrderId(payment_id) || 
      !isValidOrderId(order_id) || 
      !signature || 
      !isValidSubscriptionId(subscription_id)) {
    return null;
  }
  
  return {
    payment_id: sanitizeString(payment_id),
    order_id: sanitizeString(order_id),
    signature: sanitizeString(signature),
    subscription_id: sanitizeString(subscription_id)
  };
};

/**
 * Validate URL format
 */
export const isValidUrl = (url: string): boolean => {
  if (!url || typeof url !== 'string') {
    return false;
  }
  
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
};

/**
 * Clean object by removing undefined/null values and sanitizing strings
 */
export const cleanObject = (obj: Record<string, any>): Record<string, any> => {
  const cleaned: Record<string, any> = {};
  
  Object.keys(obj).forEach(key => {
    const value = obj[key];
    if (value !== null && value !== undefined) {
      if (typeof value === 'string') {
        cleaned[key] = sanitizeString(value);
      } else if (typeof value === 'object' && !Array.isArray(value)) {
        cleaned[key] = cleanObject(value);
      } else {
        cleaned[key] = value;
      }
    }
  });
  
  return cleaned;
};