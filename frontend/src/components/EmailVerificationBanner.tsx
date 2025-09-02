import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

interface EmailVerificationBannerProps {
  showOnVerified?: boolean;
  className?: string;
}

const EmailVerificationBanner: React.FC<EmailVerificationBannerProps> = ({
  showOnVerified = false,
  className = ''
}) => {
  const { user } = useAuth();
  const [isResending, setIsResending] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [countdown, setCountdown] = useState(0);

  // Don't show banner if dismissed or user is not logged in
  if (dismissed || !user) return null;

  // Show verified state if requested
  if (user.is_verified && showOnVerified) {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="text-green-500 text-xl">✅</div>
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-green-800">
              Email verified! You have access to all platform features.
            </p>
          </div>
          <div className="ml-auto pl-3">
            <button
              onClick={() => setDismissed(true)}
              className="text-green-400 hover:text-green-600"
              aria-label="Dismiss"
            >
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Don't show banner if user is already verified (unless specifically requested)
  if (user.is_verified && !showOnVerified) return null;

  const handleResendVerification = async () => {
    setIsResending(true);
    try {
      const response = await authService.resendVerificationEmail();
      toast.success(response.data.message || 'Verification email sent!');
      
      // Start countdown
      setCountdown(60);
      const interval = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to send verification email';
      toast.error(errorMessage);
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <div className="text-yellow-400 text-xl">⚠️</div>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">
            Email Verification Required
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            <p>
              Please verify your email address ({user.email}) to access all platform features including 
              campaign creation and AI content generation.
            </p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={handleResendVerification}
              disabled={isResending || countdown > 0}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-800 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isResending ? (
                <>
                  <div className="animate-spin rounded-full h-3 w-3 border-b border-yellow-800 mr-1"></div>
                  Sending...
                </>
              ) : countdown > 0 ? (
                `Resend in ${countdown}s`
              ) : (
                'Resend Email'
              )}
            </button>
            <a
              href="/verify-email"
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-800 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
            >
              Verification Help
            </a>
          </div>
        </div>
        <div className="ml-auto pl-3">
          <button
            onClick={() => setDismissed(true)}
            className="text-yellow-400 hover:text-yellow-600"
            aria-label="Dismiss"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationBanner;