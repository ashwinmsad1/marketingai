import React, { useState } from 'react';
import { Check, Star, Zap, Crown, AlertCircle } from 'lucide-react';
import UPIPaymentButton from '../UPIPayment/UPIPaymentButton';
import toast from 'react-hot-toast';
import { getAuthHeaders, isAuthenticated } from '../../utils/auth';
import { SubscriptionPlan } from '../../types/payment';

const plans: SubscriptionPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 799,
    description: 'Perfect for small businesses getting started',
    tier: 'starter',
    icon: <Star className="w-6 h-6" />,
    features: [
      'Basic AI content generation',
      '5 active campaigns',
      '100 AI generations/month',
      '1,000 API calls/month',
      '30-day analytics retention',
      'Email support',
      '30-day free trial'
    ]
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 1599,
    description: 'Advanced features for growing businesses',
    tier: 'professional',
    icon: <Zap className="w-6 h-6" />,
    popular: true,
    features: [
      'Advanced AI content generation',
      '25 active campaigns',
      '500 AI generations/month',
      '5,000 API calls/month',
      '90-day analytics retention',
      'Multi-platform automation',
      'A/B testing tools',
      'Priority support',
      '30-day free trial'
    ]
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 2999,
    description: 'Full-scale solution for large organizations',
    tier: 'enterprise',
    icon: <Crown className="w-6 h-6" />,
    features: [
      'Unlimited AI content generation',
      'Unlimited campaigns',
      'Unlimited API calls',
      '365-day analytics retention',
      'White-label platform access',
      'Custom integrations',
      'Dedicated account manager',
      'Team collaboration tools',
      '30-day free trial'
    ]
  }
];

interface SubscriptionPlansProps {
  onPlanSelect?: (plan: SubscriptionPlan) => void;
}

const SubscriptionPlans: React.FC<SubscriptionPlansProps> = ({ onPlanSelect }) => {
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [createdSubscription, setCreatedSubscription] = useState<string | null>(null);

  const handlePlanSelection = async (plan: SubscriptionPlan) => {
    if (!isAuthenticated()) {
      toast.error('Please log in to start your subscription');
      return;
    }

    try {
      setLoading(true);
      setSelectedPlan(plan);
      
      // Create subscription
      const subscriptionId = await createSubscription(plan);
      setCreatedSubscription(subscriptionId);
      
      onPlanSelect?.(plan);
    } catch (error: any) {
      console.error('Error selecting plan:', error);
      toast.error(error.message || 'Failed to create subscription');
      setSelectedPlan(null);
    } finally {
      setLoading(false);
    }
  };

  const createSubscription = async (plan: SubscriptionPlan): Promise<string> => {
    const headers = getAuthHeaders();
    
    const response = await fetch('/api/payments/create-subscription', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        tier: plan.tier,
        trial_days: 30
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.success && result.data) {
      return result.data.subscription_id;
    } else {
      throw new Error(result.error || 'Failed to create subscription');
    }
  };

  const handleUPIPaymentSuccess = async (_paymentData: any) => {
    if (!selectedPlan) return;

    try {
      setLoading(true);
      toast.success(`Successfully activated ${selectedPlan.name} plan!`);
      // Reload page to reflect subscription changes
      window.location.reload();
    } catch (error) {
      console.error('Payment activation error:', error);
      toast.error('Payment failed. Please try again.');
    } finally {
      setLoading(false);
      setSelectedPlan(null);
    }
  };

  const handleUPIPaymentError = (error: any) => {
    console.error('UPI payment error:', error);
    toast.error('Payment failed. Please try again.');
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Choose Your Plan
        </h2>
        <p className="text-lg text-gray-600">
          Start with a 30-day free trial. No payment required during trial.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`relative bg-white rounded-xl shadow-lg border-2 transition-all duration-200 ${
              plan.popular
                ? 'border-blue-500 ring-2 ring-blue-200'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <div className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </div>
              </div>
            )}

            <div className="p-6">
              <div className="flex items-center space-x-2 mb-4">
                <div className={`p-2 rounded-lg ${
                  plan.popular ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                }`}>
                  {plan.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
              </div>

              <div className="mb-4">
                <div className="flex items-baseline">
                  <span className="text-3xl font-bold text-gray-900">
                    ₹{plan.price.toLocaleString('en-IN')}
                  </span>
                  <span className="text-gray-500 ml-2">/month</span>
                </div>
                <p className="text-gray-600 mt-2">{plan.description}</p>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <div className="space-y-3">
                {selectedPlan?.id === plan.id && createdSubscription ? (
                  <UPIPaymentButton
                    amount={plan.price}
                    subscriptionId={createdSubscription}
                    onPaymentSuccess={handleUPIPaymentSuccess}
                    onPaymentError={handleUPIPaymentError}
                    disabled={loading}
                  />
                ) : (
                  <button
                    onClick={() => handlePlanSelection(plan)}
                    disabled={loading}
                    className={`w-full py-3 px-6 rounded-lg font-medium transition-colors ${
                      plan.popular
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {loading && selectedPlan?.id === plan.id ? 'Creating Subscription...' : 'Start Free Trial'}
                  </button>
                )}
                
                <p className="text-xs text-gray-500 text-center">
                  30-day free trial, then ₹{plan.price.toLocaleString('en-IN')}/month. Cancel anytime.
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 text-center">
        <div className="bg-gray-50 rounded-lg p-6">
          {!isAuthenticated() && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm text-blue-800 font-medium">
                  Sign up or log in to start your free trial
                </span>
              </div>
              <p className="text-xs text-blue-600 mt-1">
                Create an account to access all features with a 30-day free trial
              </p>
            </div>
          )}
          
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Why Choose Our Platform?
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-600">
            <div>
              <div className="font-medium text-gray-900 mb-2">Advanced AI Technology</div>
              <p>State-of-the-art AI models for content generation and optimization</p>
            </div>
            <div>
              <div className="font-medium text-gray-900 mb-2">Multi-Platform Support</div>
              <p>Seamless integration with Facebook, Instagram, and other major platforms</p>
            </div>
            <div>
              <div className="font-medium text-gray-900 mb-2">24/7 Support</div>
              <p>Expert support team available to help you succeed</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPlans;