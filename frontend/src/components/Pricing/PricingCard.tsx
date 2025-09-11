import React from 'react';
import { Check, Crown, Zap, TrendingUp } from 'lucide-react';
import { PricingTier, SubscriptionTier } from '../../types';
import { FEATURE_LABELS, formatCurrency, calculateSavingsPercentage } from '../../constants/pricing';

interface PricingCardProps {
  tier: SubscriptionTier;
  config: PricingTier;
  billingCycle: 'monthly' | 'annual';
  isCurrentTier?: boolean;
  isPopular?: boolean;
  onUpgrade: () => void;
}

const PricingCard: React.FC<PricingCardProps> = ({
  tier,
  config,
  billingCycle,
  isCurrentTier = false,
  isPopular = false,
  onUpgrade
}) => {
  const price = billingCycle === 'monthly' ? config.price_monthly : config.price_annual;
  const monthlyPrice = billingCycle === 'annual' ? Math.round(config.price_annual / 12) : config.price_monthly;
  const savings = billingCycle === 'annual' ? calculateSavingsPercentage(config.price_monthly, config.price_annual) : 0;

  const getTierIcon = () => {
    switch (tier) {
      case 'basic':
        return <Zap className="h-6 w-6" />;
      case 'professional':
        return <TrendingUp className="h-6 w-6" />;
      case 'business':
        return <Crown className="h-6 w-6" />;
      default:
        return <Zap className="h-6 w-6" />;
    }
  };

  const getTierGradient = () => {
    switch (tier) {
      case 'basic':
        return 'from-blue-500 to-blue-600';
      case 'professional':
        return 'from-purple-500 to-purple-600';
      case 'business':
        return 'from-yellow-500 to-yellow-600';
      default:
        return 'from-blue-500 to-blue-600';
    }
  };

  const getBorderColor = () => {
    if (isCurrentTier) return 'border-green-500';
    if (isPopular) return 'border-blue-500';
    return 'border-gray-200';
  };

  const getButtonStyle = () => {
    if (isCurrentTier) {
      return 'bg-green-600 hover:bg-green-700 text-white';
    }
    if (tier === 'professional') {
      return 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white';
    }
    if (tier === 'business') {
      return 'bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-white';
    }
    return 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white';
  };

  return (
    <div className={`relative bg-white rounded-2xl shadow-lg border-2 ${getBorderColor()} overflow-hidden transition-all duration-300 hover:shadow-xl`}>
      {/* Popular Badge */}
      {isPopular && (
        <div className="absolute top-0 left-0 right-0">
          <div className={`bg-gradient-to-r ${getTierGradient()} text-white text-center py-2 px-4`}>
            <span className="text-sm font-medium">Most Popular</span>
          </div>
        </div>
      )}

      {/* Current Tier Badge */}
      {isCurrentTier && (
        <div className="absolute top-0 left-0 right-0">
          <div className="bg-green-600 text-white text-center py-2 px-4">
            <span className="text-sm font-medium">Current Plan</span>
          </div>
        </div>
      )}

      <div className={`p-8 ${isPopular || isCurrentTier ? 'pt-16' : ''}`}>
        {/* Header */}
        <div className="text-center mb-6">
          <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-r ${getTierGradient()} text-white mb-4`}>
            {getTierIcon()}
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">{config.name}</h3>
          
          {/* Pricing */}
          <div className="mb-4">
            <div className="flex items-baseline justify-center">
              <span className="text-4xl font-bold text-gray-900">
                {formatCurrency(monthlyPrice)}
              </span>
              <span className="text-gray-500 ml-1">/month</span>
            </div>
            {billingCycle === 'annual' && (
              <div className="text-sm text-gray-500 mt-1">
                Billed annually • {formatCurrency(price)} per year
              </div>
            )}
            {savings > 0 && (
              <div className="text-sm text-green-600 font-medium mt-1">
                Save {savings}% with annual billing
              </div>
            )}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-700">Campaigns per month</span>
            <span className="font-semibold text-gray-900">{config.campaigns_limit}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-700">AI Generations</span>
            <span className="font-semibold text-gray-900">{config.ai_generations_limit.toLocaleString()}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-700">Ad Spend Monitoring</span>
            <span className="font-semibold text-gray-900">{formatCurrency(config.ad_spend_monitoring_limit)}</span>
          </div>
        </div>

        {/* Features */}
        <div className="space-y-3 mb-8">
          <h4 className="font-semibold text-gray-900">Everything included:</h4>
          <ul className="space-y-2">
            {config.features.map((feature) => (
              <li key={feature} className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-gray-700 text-sm">
                  {FEATURE_LABELS[feature] || feature}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* CTA Button */}
        <button
          onClick={onUpgrade}
          disabled={isCurrentTier}
          className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 ${getButtonStyle()} ${
            isCurrentTier ? 'cursor-not-allowed opacity-75' : 'hover:shadow-lg transform hover:-translate-y-0.5'
          }`}
        >
          {isCurrentTier ? 'Current Plan' : `Get Started with ${config.name}`}
        </button>

        {/* Additional Info */}
        <p className="text-center text-sm text-gray-500 mt-4">
          No setup fees • Cancel anytime
        </p>
      </div>
    </div>
  );
};

export default PricingCard;