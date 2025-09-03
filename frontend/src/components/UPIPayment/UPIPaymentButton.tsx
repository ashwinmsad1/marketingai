import React, { useEffect, useState, useCallback, useRef } from 'react';
import { QrCode, Smartphone, CreditCard, ArrowRight, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { getAuthHeaders } from '../../utils/auth';
import { isValidSubscriptionId, isValidPaymentAmount, validatePaymentData } from '../../utils/validation';
import { PaymentStatusPoller } from '../../utils/paymentPolling';
import { 
  UPIPaymentData, 
  PaymentSuccessData, 
  PaymentError
} from '../../types/payment';

interface UPIPaymentButtonProps {
  amount: number;
  subscriptionId: string;
  onPaymentSuccess: (paymentData: PaymentSuccessData) => void;
  onPaymentError: (error: PaymentError) => void;
  disabled?: boolean;
  className?: string;
}


const UPIPaymentButton: React.FC<UPIPaymentButtonProps> = ({
  amount,
  subscriptionId,
  onPaymentSuccess,
  onPaymentError,
  disabled = false,
  className = ''
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [paymentOrder, setPaymentOrder] = useState<UPIPaymentData | null>(null);
  const [showPaymentOptions, setShowPaymentOptions] = useState(false);
  const [isPollingPayment, setIsPollingPayment] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<string>('idle');
  const paymentPollerRef = useRef<PaymentStatusPoller | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      cleanup();
    };
  }, []);

  // Input validation on props change
  useEffect(() => {
    if (!isValidSubscriptionId(subscriptionId)) {
      console.error('Invalid subscription ID provided');
      onPaymentError(new Error('Invalid subscription ID'));
    }
    
    if (!isValidPaymentAmount(amount)) {
      console.error('Invalid payment amount provided');
      onPaymentError(new Error('Invalid payment amount'));
    }
  }, [subscriptionId, amount, onPaymentError]);

  const cleanup = useCallback(() => {
    if (paymentPollerRef.current) {
      paymentPollerRef.current.cancel();
      paymentPollerRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);


  const createPaymentOrder = async () => {
    // Validate inputs before API call
    if (!isValidSubscriptionId(subscriptionId)) {
      const error = new Error('Invalid subscription ID');
      onPaymentError(error);
      return;
    }
    
    if (!isValidPaymentAmount(amount)) {
      const error = new Error('Invalid payment amount');
      onPaymentError(error);
      return;
    }

    try {
      setIsLoading(true);
      abortControllerRef.current = new AbortController();
      
      const headers = getAuthHeaders();
      const response = await fetch('/api/payments/create-payment-order', {
        method: 'POST',
        headers,
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          subscription_id: subscriptionId,
          amount: amount
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        setPaymentOrder(result.data);
        setShowPaymentOptions(true);
        setPaymentStatus('order_created');
        toast.success('Payment order created successfully!');
      } else {
        throw new Error(result.error || 'Failed to create payment order');
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Payment order error:', error);
        const errorMessage = error.message || 'Failed to create payment order';
        toast.error(errorMessage);
        onPaymentError(new Error(errorMessage));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleUPIAppPayment = async (appName: string, _upiId?: string) => {
    if (!paymentOrder) {
      onPaymentError(new Error('No payment order available'));
      return;
    }

    const upiLink = paymentOrder.upi_deep_link;
    
    // Validate UPI link before opening
    if (!upiLink || typeof upiLink !== 'string') {
      onPaymentError(new Error('Invalid UPI payment link'));
      return;
    }
    
    try {
      // Open UPI app
      const opened = window.open(upiLink, '_blank');
      if (!opened) {
        throw new Error('Failed to open UPI app. Please check if popup blocker is disabled.');
      }
      
      toast.success(`Opening ${appName}...`);
      setPaymentStatus('payment_initiated');
      
      // Start polling for payment status
      await startPaymentStatusPolling(paymentOrder.order.id);
      
    } catch (error: any) {
      console.error('UPI payment error:', error);
      onPaymentError(new Error(error.message || 'Failed to initiate UPI payment'));
    }
  };

  const startPaymentStatusPolling = async (orderId: string) => {
    try {
      setIsPollingPayment(true);
      setPaymentStatus('checking_payment');
      
      // Create payment status poller
      paymentPollerRef.current = new PaymentStatusPoller(orderId, {
        maxAttempts: 60, // Poll for 5 minutes
        initialDelay: 5000, // Start with 5 second intervals
        maxDelay: 30000, // Max 30 seconds between polls
        timeout: 300000 // 5 minute total timeout
      });
      
      const paymentStatus = await paymentPollerRef.current.pollStatus();
      
      if (paymentStatus.status === 'succeeded') {
        await verifyAndActivatePayment({
          payment_id: paymentStatus.payment_id,
          order_id: paymentStatus.order_id,
          subscription_id: subscriptionId
        });
      } else if (paymentStatus.status === 'failed') {
        throw new Error(paymentStatus.error_message || 'Payment failed');
      } else if (paymentStatus.status === 'cancelled') {
        throw new Error('Payment was cancelled');
      } else {
        throw new Error('Payment verification timeout');
      }
      
    } catch (error: any) {
      console.error('Payment polling error:', error);
      setPaymentStatus('failed');
      onPaymentError(new Error(error.message || 'Payment verification failed'));
    } finally {
      setIsPollingPayment(false);
      paymentPollerRef.current = null;
    }
  };

  const verifyAndActivatePayment = async (paymentData: any) => {
    // Validate payment data
    const validatedData = validatePaymentData(paymentData);
    if (!validatedData) {
      throw new Error('Invalid payment data received');
    }

    try {
      abortControllerRef.current = new AbortController();
      const headers = getAuthHeaders();
      
      const response = await fetch('/api/payments/activate-subscription', {
        method: 'POST',
        headers,
        signal: abortControllerRef.current.signal,
        body: JSON.stringify(validatedData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setPaymentStatus('completed');
        const successData: PaymentSuccessData = {
          payment_id: validatedData.payment_id,
          order_id: validatedData.order_id,
          subscription_id: validatedData.subscription_id,
          amount: amount,
          status: 'succeeded'
        };
        onPaymentSuccess(successData);
        setShowPaymentOptions(false);
        toast.success('Payment successful! Subscription activated.');
      } else {
        throw new Error(result.error || 'Payment verification failed');
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Payment verification error:', error);
        throw error;
      }
    }
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const upiApps = [
    { name: 'PhonePe', icon: '📱', color: 'bg-purple-600' },
    { name: 'Google Pay', icon: '💳', color: 'bg-blue-600' },
    { name: 'Paytm', icon: '💰', color: 'bg-indigo-600' },
    { name: 'BHIM', icon: '🏦', color: 'bg-green-600' },
    { name: 'Amazon Pay', icon: '🛒', color: 'bg-orange-600' },
    { name: 'WhatsApp Pay', icon: '💬', color: 'bg-green-500' }
  ];

  if (showPaymentOptions && paymentOrder) {
    return (
      <div className="w-full">
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Complete Payment</h3>
            <span className="text-xl font-bold text-green-600">
              {formatAmount(paymentOrder.order.amount)}
            </span>
          </div>
          
          <div className="mb-6">
            <p className="text-sm text-gray-600 mb-2">Order ID: {paymentOrder.order.receipt}</p>
            
            {isPollingPayment && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm text-blue-800 font-medium">
                    {paymentStatus === 'checking_payment' ? 'Verifying payment...' : 'Processing...'}
                  </span>
                </div>
                <p className="text-xs text-blue-600 mt-1">
                  Complete your payment in the UPI app. We'll automatically detect when it's done.
                </p>
              </div>
            )}
            
            {paymentStatus === 'payment_initiated' && !isPollingPayment && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm text-yellow-800 font-medium">
                    Complete payment in your UPI app
                  </span>
                </div>
                <p className="text-xs text-yellow-600 mt-1">
                  Return here after completing the payment. We'll verify it automatically.
                </p>
              </div>
            )}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-center mb-3">
                <QrCode className="w-8 h-8 text-gray-600" />
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-2">Scan QR code or choose your UPI app</p>
                <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-4 mb-4">
                  <div className="w-32 h-32 mx-auto bg-gray-100 rounded flex items-center justify-center">
                    <span className="text-xs text-gray-500">QR Code would appear here</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Choose UPI App</h4>
            <div className="grid grid-cols-3 gap-3">
              {upiApps.map((app) => (
                <button
                  key={app.name}
                  onClick={() => handleUPIAppPayment(app.name)}
                  disabled={isPollingPayment}
                  className={`${app.color} hover:opacity-90 text-white p-3 rounded-lg transition-all duration-200 flex flex-col items-center space-y-1 disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <span className="text-lg">{app.icon}</span>
                  <span className="text-xs font-medium">{app.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={() => {
                cleanup();
                setShowPaymentOptions(false);
                setPaymentStatus('idle');
              }}
              disabled={isPollingPayment}
              className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPollingPayment ? 'Processing...' : 'Cancel'}
            </button>
            <button
              onClick={() => window.open(paymentOrder.upi_deep_link, '_blank')}
              disabled={isPollingPayment}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Smartphone className="w-4 h-4" />
              <span>Open UPI App</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={createPaymentOrder}
      disabled={disabled || isLoading}
      className={`w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {isLoading ? (
        <>
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          <span>Creating Order...</span>
        </>
      ) : (
        <>
          <div className="flex items-center space-x-2">
            <CreditCard className="w-5 h-5" />
            <span>Pay with UPI</span>
            <span className="bg-white/20 px-2 py-1 rounded text-sm">
              {formatAmount(amount)}
            </span>
          </div>
          <ArrowRight className="w-4 h-4" />
        </>
      )}
    </button>
  );
};

export default UPIPaymentButton;