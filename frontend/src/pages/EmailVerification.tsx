import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api';
import toast from 'react-hot-toast';
import { Button } from '../design-system';

const EmailVerification: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, refreshToken } = useAuth();
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<'pending' | 'success' | 'error'>('pending');
  const [countdown, setCountdown] = useState(0);
  const [verificationDetails, setVerificationDetails] = useState({
    is_verified: false,
    email: '',
    requires_verification: true
  });

  // Handle email verification from URL token
  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      handleVerificationFromToken(token);
    }
  }, [searchParams]);

  // Get verification status on component mount
  useEffect(() => {
    if (user) {
      fetchVerificationStatus();
    }
  }, [user]);

  const handleVerificationFromToken = async (token: string) => {
    setIsVerifying(true);
    try {
      const response = await authService.verifyEmail(token);
      setVerificationStatus('success');
      toast.success(response.data.message || 'Email verified successfully!');
      
      // Refresh user data
      await refreshToken();
      
      // Redirect to dashboard after a delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error: any) {
      setVerificationStatus('error');
      const errorMessage = error.response?.data?.detail || 'Email verification failed';
      toast.error(errorMessage);
    } finally {
      setIsVerifying(false);
    }
  };

  const fetchVerificationStatus = async () => {
    try {
      const response = await authService.getVerificationStatus();
      setVerificationDetails(response.data);
    } catch (error) {
      console.error('Failed to fetch verification status:', error);
    }
  };

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

  const renderVerificationContent = () => {
    const token = searchParams.get('token');
    
    if (token) {
      // Token-based verification flow
      if (isVerifying) {
        return (
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifying your email...</h2>
            <p className="text-gray-600">Please wait while we verify your email address.</p>
          </div>
        );
      }

      if (verificationStatus === 'success') {
        return (
          <div className="text-center">
            <div className="text-green-500 text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Email Verified!</h2>
            <p className="text-gray-600 mb-4">
              Your email has been successfully verified. You can now access all platform features.
            </p>
            <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
          </div>
        );
      }

      if (verificationStatus === 'error') {
        return (
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h2>
            <p className="text-gray-600 mb-4">
              The verification link is invalid or has expired. Please try requesting a new one.
            </p>
            <Button
              onClick={handleResendVerification}
              disabled={isResending || countdown > 0}
              className="bg-blue-600 text-white hover:bg-blue-700"
            >
              {isResending ? 'Sending...' : countdown > 0 ? `Wait ${countdown}s` : 'Resend Verification Email'}
            </Button>
          </div>
        );
      }
    }

    // Regular verification prompt for logged-in users
    if (user && !user.is_verified) {
      return (
        <div className="text-center">
          <div className="text-yellow-500 text-6xl mb-4">📧</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Verify Your Email</h2>
          <p className="text-gray-600 mb-4">
            We've sent a verification email to <strong>{user.email}</strong>
          </p>
          <p className="text-gray-600 mb-6">
            Please check your inbox and click the verification link to access all platform features.
          </p>
          
          <div className="space-y-4">
            <Button
              onClick={handleResendVerification}
              disabled={isResending || countdown > 0}
              className="bg-blue-600 text-white hover:bg-blue-700 w-full"
            >
              {isResending ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sending...
                </div>
              ) : countdown > 0 ? (
                `Resend in ${countdown}s`
              ) : (
                'Resend Verification Email'
              )}
            </Button>
            
            <div className="text-sm text-gray-500">
              <p>Didn't receive the email? Check your spam folder or</p>
              <button 
                onClick={() => navigate('/dashboard')}
                className="text-blue-600 hover:underline"
              >
                continue with limited access
              </button>
            </div>
          </div>
        </div>
      );
    }

    // Already verified
    if (user && user.is_verified) {
      return (
        <div className="text-center">
          <div className="text-green-500 text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Email Already Verified</h2>
          <p className="text-gray-600 mb-4">
            Your email address is already verified. You have access to all platform features.
          </p>
          <Button
            onClick={() => navigate('/dashboard')}
            className="bg-green-600 text-white hover:bg-green-700"
          >
            Go to Dashboard
          </Button>
        </div>
      );
    }

    // Not logged in
    return (
      <div className="text-center">
        <div className="text-blue-500 text-6xl mb-4">🔐</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Please Log In</h2>
        <p className="text-gray-600 mb-4">
          You need to be logged in to verify your email address.
        </p>
        <Button
          onClick={() => navigate('/login')}
          className="bg-blue-600 text-white hover:bg-blue-700"
        >
          Log In
        </Button>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          {renderVerificationContent()}
        </div>
        
        {/* Help section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Need Help?</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• Check your spam/junk folder for the verification email</p>
            <p>• Make sure you're checking the correct email address</p>
            <p>• Verification links expire in 24 hours</p>
            <p>• Contact support if you continue having issues</p>
          </div>
          <div className="mt-4">
            <a
              href="mailto:support@aimarketing.com"
              className="text-blue-600 hover:underline text-sm"
            >
              Contact Support
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerification;