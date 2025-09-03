/**
 * Payment status polling utilities for secure payment verification
 */

import { getAuthHeaders } from './auth';

export interface PaymentStatus {
  status: 'pending' | 'succeeded' | 'failed' | 'cancelled';
  payment_id?: string;
  order_id: string;
  error_message?: string;
}

/**
 * Poll payment status with exponential backoff and timeout
 */
export class PaymentStatusPoller {
  private orderId: string;
  private maxAttempts: number;
  private initialDelay: number;
  private maxDelay: number;
  private timeout: number;
  private abortController: AbortController;
  private pollTimer: number | null = null;

  constructor(orderId: string, options: {
    maxAttempts?: number;
    initialDelay?: number;
    maxDelay?: number;
    timeout?: number;
  } = {}) {
    this.orderId = orderId;
    this.maxAttempts = options.maxAttempts ?? 60; // 5 minutes with 5s intervals
    this.initialDelay = options.initialDelay ?? 5000; // 5 seconds
    this.maxDelay = options.maxDelay ?? 30000; // 30 seconds max
    this.timeout = options.timeout ?? 300000; // 5 minutes total
    this.abortController = new AbortController();
  }

  /**
   * Start polling for payment status
   */
  public async pollStatus(): Promise<PaymentStatus> {
    return new Promise((resolve, reject) => {
      let attempt = 0;
      let delay = this.initialDelay;

      // Set overall timeout
      const timeoutTimer = setTimeout(() => {
        this.cleanup();
        reject(new Error('Payment verification timeout'));
      }, this.timeout);

      const poll = async () => {
        try {
          if (this.abortController.signal.aborted) {
            clearTimeout(timeoutTimer);
            reject(new Error('Payment verification cancelled'));
            return;
          }

          attempt++;
          const status = await this.checkPaymentStatus();

          // If payment is complete (success or failure), resolve
          if (status.status === 'succeeded' || status.status === 'failed' || status.status === 'cancelled') {
            clearTimeout(timeoutTimer);
            this.cleanup();
            resolve(status);
            return;
          }

          // If payment is still pending and we haven't exceeded max attempts
          if (status.status === 'pending' && attempt < this.maxAttempts) {
            // Schedule next poll with exponential backoff
            const nextDelay = Math.min(delay * 1.5, this.maxDelay);
            this.pollTimer = setTimeout(poll, delay);
            delay = nextDelay;
          } else {
            // Max attempts reached or unknown status
            clearTimeout(timeoutTimer);
            this.cleanup();
            reject(new Error('Payment verification failed - maximum attempts exceeded'));
          }
        } catch (error) {
          // If this is the last attempt or a critical error, fail
          if (attempt >= this.maxAttempts) {
            clearTimeout(timeoutTimer);
            this.cleanup();
            reject(error);
          } else {
            // Otherwise, retry after delay
            this.pollTimer = setTimeout(poll, delay);
            delay = Math.min(delay * 1.5, this.maxDelay);
          }
        }
      };

      // Start polling
      poll();
    });
  }

  /**
   * Check payment status via API
   */
  private async checkPaymentStatus(): Promise<PaymentStatus> {
    try {
      const headers = getAuthHeaders();
      
      const response = await fetch(`/api/payments/status/${this.orderId}`, {
        method: 'GET',
        headers,
        signal: this.abortController.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Failed to check payment status');
      }

      return {
        status: result.data.status,
        payment_id: result.data.payment_id,
        order_id: this.orderId,
        error_message: result.data.error_message
      };
    } catch (error: any) {
      // Network or parsing errors
      console.error('Payment status check failed:', error);
      throw new Error(`Payment status check failed: ${error.message}`);
    }
  }

  /**
   * Cancel polling
   */
  public cancel(): void {
    this.abortController.abort();
    this.cleanup();
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    if (this.pollTimer) {
      clearTimeout(this.pollTimer);
      this.pollTimer = null;
    }
  }
}

/**
 * Simplified function to poll payment status
 */
export const pollPaymentStatus = async (
  orderId: string,
  options?: {
    maxAttempts?: number;
    initialDelay?: number;
    maxDelay?: number;
    timeout?: number;
  }
): Promise<PaymentStatus> => {
  const poller = new PaymentStatusPoller(orderId, options);
  return poller.pollStatus();
};