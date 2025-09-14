import React, { useState } from 'react';
import { Check, Star, Zap, Crown, AlertCircle } from 'lucide-react';
import UPIPaymentButton from '../UPIPayment/UPIPaymentButton';
import toast from 'react-hot-toast';
import { getAuthHeaders, isAuthenticated } from '../../utils/auth';
import { SubscriptionPlan } from '../../types/payment';

const plans: SubscriptionPlan[] = [
  {
    id: 'basic',
    name: 'Basic',
    price: 2999,
    description: 'Perfect for small businesses getting started with AI marketing',
    tier: 'basic',
    icon: <Star className="w-6 h-6" />,
    features: [
      '5 Facebook/Instagram campaigns per month',
      '150 AI content generations per month',
      'Basic AI content generation (text + image)',
      'Facebook & Instagram posting',
      'Basic analytics (last 30 days)',
      'Budget monitoring up to ₹25,000',
      'Email support'
    ]
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 7999,
    description: 'Advanced features for growing businesses ready to scale',
    tier: 'professional',
    icon: <Zap className="w-6 h-6" />,
    popular: true,
    features: [
      '20 Facebook/Instagram campaigns per month',
      '500 AI content generations per month',
      'Advanced AI content generation (text + image + video thumbnails)',
      'Advanced Facebook & Instagram automation',
      'Enhanced analytics (90 days + performance tracking)',
      'Budget monitoring up to ₹1,00,000',
      'Priority email support',
      'Campaign templates library'
    ]
  },
  {
    id: 'business',
    name: 'Business',
    price: 19999,
    description: 'Complete automation solution for serious marketers',
    tier: 'business',
    icon: <Crown className="w-6 h-6" />,
    features: [
      '50 Facebook/Instagram campaigns per month',
      '1200 AI content generations per month',
      'Premium AI content generation (all formats + brand customization)',
      'Full Facebook & Instagram automation suite',
      'Full analytics suite (12 months + custom reporting)',
      'Budget monitoring up to ₹5,00,000',
      'Premium email support',
      'Data export and custom reporting',
      'Advanced performance tracking'
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
          Simplified pricing designed for your success. Choose the plan that fits your needs.
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
                    {loading && selectedPlan?.id === plan.id ? 'Creating Subscription...' : 'Get Started'}
                  </button>
                )}
                
                <p className="text-xs text-gray-500 text-center">
                  ₹{plan.price.toLocaleString('en-IN')}/month. Cancel anytime.
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
                  Sign up or log in to get started
                </span>
              </div>
              <p className="text-xs text-blue-600 mt-1">
                Create an account to access all features and start your subscription
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
              <div className="font-medium text-gray-900 mb-2">Facebook & Instagram Focus</div>
              <p>Specialized integration with Facebook and Instagram for optimal performance</p>
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