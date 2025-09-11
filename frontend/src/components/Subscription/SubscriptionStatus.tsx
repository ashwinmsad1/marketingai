import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Crown, Zap, TrendingUp, Settings, Calendar, ArrowUp } from 'lucide-react';
import { SubscriptionTier } from '../../types';
import { PRICING_TIERS, formatCurrency } from '../../constants/pricing';
import { SubscriptionService } from '../../services/subscriptionService';
import SubscriptionUpgrade from './SubscriptionUpgrade';

interface SubscriptionStatusProps {
  currentTier: SubscriptionTier;
  nextBillingDate?: string;
  billingCycle?: 'monthly' | 'annual';
  onManageSubscription?: () => void;
}

const SubscriptionStatus: React.FC<SubscriptionStatusProps> = ({
  currentTier,
  nextBillingDate,
  billingCycle = 'monthly',
  onManageSubscription
}) => {
  const [showUpgrade, setShowUpgrade] = useState(false);

  const tierConfig = PRICING_TIERS[currentTier];
  const currentPrice = billingCycle === 'monthly' ? tierConfig.price_monthly : tierConfig.price_annual;
  const monthlyPrice = billingCycle === 'annual' ? Math.round(tierConfig.price_annual / 12) : tierConfig.price_monthly;

  const getTierIcon = (tier: SubscriptionTier) => {
    switch (tier) {
      case 'basic':
        return <Zap className="h-5 w-5" />;
      case 'professional':
        return <TrendingUp className="h-5 w-5" />;
      case 'business':
        return <Crown className="h-5 w-5" />;
      default:
        return <Zap className="h-5 w-5" />;
    }
  };

  const getTierColor = (tier: SubscriptionTier) => {
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

  const getUpgradeTarget = (): SubscriptionTier | null => {
    if (currentTier === 'basic') return 'professional';
    if (currentTier === 'professional') return 'business';
    return null;
  };

  const upgradeTarget = getUpgradeTarget();

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg bg-gradient-to-r ${getTierColor(currentTier)} text-white`}>
              {getTierIcon(currentTier)}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {tierConfig.name} Plan
              </h3>
              <p className="text-sm text-gray-500">
                {formatCurrency(monthlyPrice)}/month
                {billingCycle === 'annual' && (
                  <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                    Annual
                  </span>
                )}
              </p>
            </div>
          </div>
          
          <button
            onClick={onManageSubscription}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Settings className="h-5 w-5" />
          </button>
        </div>

        {/* Current Plan Features */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-700">Campaigns per month</span>
            <span className="font-semibold text-gray-900">{tierConfig.campaigns_limit}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-700">AI Generations</span>
            <span className="font-semibold text-gray-900">{tierConfig.ai_generations_limit.toLocaleString()}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-700">Ad Spend Monitoring</span>
            <span className="font-semibold text-gray-900">{formatCurrency(tierConfig.ad_spend_monitoring_limit)}</span>
          </div>
        </div>

        {/* Billing Information */}
        {nextBillingDate && (
          <div className="flex items-center space-x-2 mb-6 p-3 bg-blue-50 rounded-lg">
            <Calendar className="h-4 w-4 text-blue-600" />
            <span className="text-sm text-blue-700">
              Next billing: {new Date(nextBillingDate).toLocaleDateString()}
            </span>
          </div>
        )}

        {/* Upgrade Option */}
        {upgradeTarget && (
          <div className="border-t pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Want more features?</h4>
                <p className="text-sm text-gray-500">
                  Upgrade to {PRICING_TIERS[upgradeTarget].name} for better limits and features
                </p>
              </div>
              <button
                onClick={() => setShowUpgrade(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all duration-200"
              >
                <ArrowUp className="h-4 w-4" />
                <span>Upgrade</span>
              </button>
            </div>
          </div>
        )}
      </motion.div>

      {/* Upgrade Modal */}
      {upgradeTarget && (
        <SubscriptionUpgrade
          isOpen={showUpgrade}
          onClose={() => setShowUpgrade(false)}
          currentTier={currentTier}
          suggestedTier={upgradeTarget}
          onUpgradeComplete={() => setShowUpgrade(false)}
        />
      )}
    </>
  );
};

export default SubscriptionStatus;