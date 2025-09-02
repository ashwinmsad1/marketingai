import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CreditCard, Calendar, AlertCircle } from 'lucide-react';
import SubscriptionPlans from '../components/Subscription/SubscriptionPlans';
import toast from 'react-hot-toast';
import { getAuthHeaders, isAuthenticated } from '../utils/auth';
import { sanitizeString } from '../utils/validation';
import { SubscriptionDetails, ApiResponse } from '../types/payment';


const Subscription: React.FC = () => {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<SubscriptionDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPlans, setShowPlans] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication before making API calls
    if (!isAuthenticated()) {
      toast.error('Please log in to view your subscription');
      navigate('/login');
      return;
    }
    
    fetchCurrentSubscription();
  }, [navigate]);

  const handleAuthError = useCallback(() => {
    toast.error('Session expired. Please log in again.');
    navigate('/login');
  }, [navigate]);

  const fetchCurrentSubscription = async () => {
    if (!isAuthenticated()) {
      handleAuthError();
      return;
    }

    try {
      setError(null);
      const headers = getAuthHeaders();
      
      const response = await fetch('/api/payments/subscriptions/current', {
        headers
      });

      if (response.status === 401) {
        handleAuthError();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        // Sanitize subscription data
        const sanitizedData = {
          ...result.data,
          subscription_id: sanitizeString(result.data.subscription_id || ''),
          tier: sanitizeString(result.data.tier || ''),
          status: sanitizeString(result.data.status || '')
        };
        setSubscription(sanitizedData);
      } else {
        // No active subscription found
        setShowPlans(true);
      }
    } catch (error: any) {
      console.error('Error fetching subscription:', error);
      const errorMessage = error.message || 'Failed to load subscription details';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!subscription) {
      toast.error('No active subscription to cancel');
      return;
    }

    if (!isAuthenticated()) {
      handleAuthError();
      return;
    }

    const confirmed = window.confirm(
      'Are you sure you want to cancel your subscription? This action cannot be undone and you will lose access to premium features.'
    );
    
    if (!confirmed) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      
      const response = await fetch('/api/payments/subscriptions/cancel', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          subscription_id: subscription.subscription_id,
          reason: sanitizeString('User requested cancellation'),
          immediate: false
        })
      });

      if (response.status === 401) {
        handleAuthError();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        toast.success('Subscription canceled successfully');
        await fetchCurrentSubscription();
      } else {
        throw new Error(result.error || 'Failed to cancel subscription');
      }
    } catch (error: any) {
      console.error('Error canceling subscription:', error);
      const errorMessage = error.message || 'Failed to cancel subscription. Please try again.';
      toast.error(errorMessage);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'trial':
        return 'bg-blue-100 text-blue-800';
      case 'past_due':
        return 'bg-yellow-100 text-yellow-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading subscription details...</p>
        </div>
      </div>
    );
  }

  if (error && !showPlans) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Subscription</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-y-2">
            <button
              onClick={fetchCurrentSubscription}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showPlans || !subscription) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center py-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Dashboard
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Choose Your Plan</h1>
            </div>
          </div>
        </div>
        <SubscriptionPlans />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Dashboard
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Subscription Management</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Current Subscription Card */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Current Plan</h2>
                <p className="text-blue-100">
                  {subscription.tier.charAt(0).toUpperCase() + subscription.tier.slice(1)} Plan
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white">
                  ₹{subscription.monthly_price.toLocaleString('en-IN')}/month
                </div>
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(subscription.status)}`}>
                  {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                </span>
              </div>
            </div>
          </div>

          <div className="px-6 py-6">
            {/* Trial Information */}
            {subscription.is_trial && subscription.trial_days_remaining !== null && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-blue-600 mr-2" />
                  <div>
                    <h3 className="font-medium text-blue-900">Free Trial Active</h3>
                    <p className="text-blue-700">
                      {subscription.trial_days_remaining} days remaining in your 30-day free trial.
                      {subscription.trial_end && ` Trial ends on ${formatDate(subscription.trial_end)}.`}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Billing Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="flex items-center space-x-3">
                <CreditCard className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Payment Method</p>
                  <p className="text-sm text-gray-600">UPI</p>
                </div>
              </div>
              {subscription.next_billing_date && (
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Next Billing Date</p>
                    <p className="text-sm text-gray-600">{formatDate(subscription.next_billing_date)}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Usage Overview */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Usage This Month</h3>
              <div className="space-y-4">
                {/* Campaigns Usage */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Campaigns</span>
                    <span className="text-gray-900">
                      {subscription.usage.campaigns.used} / {subscription.usage.campaigns.limit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${Math.min(subscription.usage.campaigns.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* AI Generations Usage */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">AI Generations</span>
                    <span className="text-gray-900">
                      {subscription.usage.ai_generations.used} / {subscription.usage.ai_generations.limit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${Math.min(subscription.usage.ai_generations.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* API Calls Usage */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">API Calls</span>
                    <span className="text-gray-900">
                      {subscription.usage.api_calls.used} / {subscription.usage.api_calls.limit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${Math.min(subscription.usage.api_calls.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Plan Features */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Plan Features</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {subscription.features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-4">
              <button
                onClick={() => setShowPlans(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Upgrade Plan
              </button>
              <button
                onClick={() => navigate('/billing/history')}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors"
              >
                View Billing History
              </button>
              <button
                onClick={handleCancelSubscription}
                className="bg-red-100 hover:bg-red-200 text-red-700 px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Cancel Subscription
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscription;