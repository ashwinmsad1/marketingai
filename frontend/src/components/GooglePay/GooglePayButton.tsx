import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

interface GooglePayButtonProps {
  amount: number;
  onPaymentSuccess: (paymentData: google.payments.api.PaymentData) => void;
  onPaymentError: (error: any) => void;
  disabled?: boolean;
  className?: string;
}

declare global {
  namespace google {
    namespace payments {
      namespace api {
        interface PaymentData {
          apiVersion: number;
          apiVersionMinor: number;
          paymentMethodData: {
            description: string;
            info: {
              cardDetails: string;
              cardNetwork: string;
            };
            tokenizationData: {
              type: string;
              token: string;
            };
            type: string;
          };
        }

        interface PaymentDataRequest {
          apiVersion: number;
          apiVersionMinor: number;
          allowedPaymentMethods: any[];
          transactionInfo: {
            totalPriceStatus: string;
            totalPrice: string;
            currencyCode: string;
          };
          merchantInfo: {
            merchantName: string;
            merchantId: string;
          };
        }

        interface PaymentsClient {
          isReadyToPay(request: any): Promise<{ result: boolean }>;
          createButton(options: any): HTMLElement;
          loadPaymentData(request: PaymentDataRequest): Promise<PaymentData>;
        }

        function PaymentsClient(options: any): PaymentsClient;
      }
    }
  }
}

const GooglePayButton: React.FC<GooglePayButtonProps> = ({
  amount,
  onPaymentSuccess,
  onPaymentError,
  disabled = false,
  className = ''
}) => {
  const [isGooglePayReady, setIsGooglePayReady] = useState(false);
  const [paymentsClient, setPaymentsClient] = useState<google.payments.api.PaymentsClient | null>(null);
  const [paymentConfig, setPaymentConfig] = useState<any>(null);

  useEffect(() => {
    const initializeGooglePay = async () => {
      try {
        // Load Google Pay API
        if (!window.google?.payments?.api) {
          const script = document.createElement('script');
          script.src = 'https://pay.google.com/gp/p/js/pay.js';
          script.async = true;
          script.onload = () => initializeGooglePay();
          document.head.appendChild(script);
          return;
        }

        // Get payment configuration from backend
        const response = await fetch('/api/payments/config');
        const config = await response.json();
        
        if (!config.success) {
          throw new Error('Failed to load payment configuration');
        }

        setPaymentConfig(config.data);

        // Initialize Google Pay client
        const client = new (google.payments.api.PaymentsClient as any)({
          environment: config.data.google_pay.environment
        });

        // Check if Google Pay is ready
        const readyToPayRequest = {
          apiVersion: config.data.google_pay.apiVersion,
          apiVersionMinor: config.data.google_pay.apiVersionMinor,
          allowedPaymentMethods: config.data.google_pay.allowedPaymentMethods
        };

        const readyToPay = await client.isReadyToPay(readyToPayRequest);
        
        if (readyToPay.result) {
          setPaymentsClient(client);
          setIsGooglePayReady(true);
        }
      } catch (error) {
        console.error('Google Pay initialization error:', error);
        onPaymentError?.(error);
      }
    };

    initializeGooglePay();
  }, [onPaymentError]);

  const handleGooglePayClick = async () => {
    if (!paymentsClient || !paymentConfig) {
      toast.error('Google Pay not ready');
      return;
    }

    try {
      const paymentDataRequest: google.payments.api.PaymentDataRequest = {
        apiVersion: paymentConfig.google_pay.apiVersion,
        apiVersionMinor: paymentConfig.google_pay.apiVersionMinor,
        allowedPaymentMethods: paymentConfig.google_pay.allowedPaymentMethods,
        transactionInfo: {
          totalPriceStatus: 'FINAL',
          totalPrice: amount.toString(),
          currencyCode: 'USD'
        },
        merchantInfo: paymentConfig.google_pay.merchantInfo
      };

      const paymentData = await paymentsClient.loadPaymentData(paymentDataRequest);
      onPaymentSuccess(paymentData);
    } catch (error) {
      console.error('Google Pay payment error:', error);
      onPaymentError?.(error);
    }
  };

  if (!isGooglePayReady) {
    return (
      <button
        disabled
        className={`w-full bg-gray-300 text-gray-500 px-6 py-3 rounded-lg font-medium ${className}`}
      >
        Loading Google Pay...
      </button>
    );
  }

  return (
    <button
      onClick={handleGooglePayClick}
      disabled={disabled}
      className={`w-full bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      <svg
        className="w-5 h-5"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
      </svg>
      <span>Pay with Google Pay</span>
    </button>
  );
};

export default GooglePayButton;