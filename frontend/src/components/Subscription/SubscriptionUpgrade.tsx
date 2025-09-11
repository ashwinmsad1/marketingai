import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, ArrowRight, AlertTriangle, Crown, Zap, TrendingUp } from 'lucide-react';
import { SubscriptionTier, UsageSummary, SubscriptionUpgradeInfo } from '../../types';
import { SubscriptionService } from '../../services/subscriptionService';
import { formatCurrency } from '../../constants/pricing';
import toast from 'react-hot-toast';

interface SubscriptionUpgradeProps {
  isOpen: boolean;
  onClose: () => void;
  currentTier: SubscriptionTier;
  suggestedTier: SubscriptionTier;
  usageSummary?: UsageSummary;
  onUpgradeComplete?: () => void;
}

const SubscriptionUpgrade: React.FC<SubscriptionUpgradeProps> = ({
  isOpen,
  onClose,
  currentTier,
  suggestedTier,
  usageSummary,
  onUpgradeComplete
}) => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [isUpgrading, setIsUpgrading] = useState(false);
  const [upgradeInfo, setUpgradeInfo] = useState<SubscriptionUpgradeInfo | null>(null);

  useEffect(() => {
    if (isOpen) {
      const info = SubscriptionService.getUpgradeInfo(
        currentTier,
        suggestedTier,
        usageSummary?.usage_percentages
      );
      setUpgradeInfo(info);
    }
  }, [isOpen, currentTier, suggestedTier, usageSummary]);

  const handleUpgrade = async () => {
    setIsUpgrading(true);
    try {
      const result = await SubscriptionService.upgradeSubscription(suggestedTier, billingCycle);
      
      if (result.success && result.upgrade_url) {
        // In a real implementation, redirect to payment processor
        window.open(result.upgrade_url, '_blank');
        toast.success('Redirecting to payment page...');
        if (onUpgradeComplete) {
          onUpgradeComplete();
        }
        onClose();
      } else {
        toast.error(result.error || 'Upgrade failed. Please try again.');
      }
    } catch (error) {
      toast.error('Network error. Please check your connection and try again.');
    } finally {
      setIsUpgrading(false);
    }
  };

  const getTierIcon = (tier: SubscriptionTier) => {
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

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (!upgradeInfo) return null;

  const targetTierConfig = SubscriptionService.getPricingTiers()[suggestedTier];
  const currentPrice = billingCycle === 'monthly' ? targetTierConfig.price_monthly : targetTierConfig.price_annual;
  const monthlyPrice = billingCycle === 'annual' ? Math.round(targetTierConfig.price_annual / 12) : targetTierConfig.price_monthly;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            {/* Background overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
              onClick={onClose}
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg bg-gradient-to-r ${getTierColor(suggestedTier)} text-white`}>
                    {getTierIcon(suggestedTier)}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Upgrade to {targetTierConfig.name}
                  </h3>
                </div>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-500 focus:outline-none"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Urgency Alert */}
              {upgradeInfo.upgrade_urgency !== 'none' && (
                <div className={`mb-6 p-4 rounded-lg border ${getUrgencyColor(upgradeInfo.upgrade_urgency)}`}>
                  <div className="flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2" />
                    <span className="font-medium">
                      {upgradeInfo.upgrade_urgency === 'critical' && 'Immediate Action Required'}
                      {upgradeInfo.upgrade_urgency === 'high' && 'Upgrade Recommended Soon'}
                      {upgradeInfo.upgrade_urgency === 'medium' && 'Consider Upgrading'}
                      {upgradeInfo.upgrade_urgency === 'low' && 'Upgrade Available'}
                    </span>
                  </div>
                  <p className="mt-1 text-sm">
                    You're approaching your usage limits. Upgrade now to avoid service interruption.
                  </p>
                </div>
              )}

              {/* Pricing */}
              <div className="mb-6 text-center">
                <div className="mb-4">
                  <div className="flex items-center justify-center space-x-4 mb-4">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        value="monthly"
                        checked={billingCycle === 'monthly'}
                        onChange={(e) => setBillingCycle(e.target.value as 'monthly')}
                        className="mr-2"
                      />
                      Monthly
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        value="annual"
                        checked={billingCycle === 'annual'}
                        onChange={(e) => setBillingCycle(e.target.value as 'annual')}
                        className="mr-2"
                      />
                      Annual
                      <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                        Save 17%
                      </span>
                    </label>
                  </div>
                  
                  <div className="text-3xl font-bold text-gray-900">
                    {formatCurrency(monthlyPrice)}
                    <span className="text-lg font-normal text-gray-500">/month</span>
                  </div>
                  
                  {billingCycle === 'annual' && (
                    <div className="text-sm text-gray-500 mt-1">
                      {formatCurrency(currentPrice)} billed annually
                    </div>
                  )}
                </div>
              </div>

              {/* Benefits */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">What you'll get:</h4>
                <ul className="space-y-2">
                  {upgradeInfo.benefits.slice(0, 5).map((benefit, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Cost Information */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">
                  <div className="flex justify-between mb-2">
                    <span>Monthly cost difference:</span>
                    <span className="font-medium">+{formatCurrency(upgradeInfo.cost_difference.monthly)}</span>
                  </div>
                  {billingCycle === 'annual' && (
                    <div className="flex justify-between">
                      <span>Annual savings:</span>
                      <span className="font-medium text-green-600">
                        {formatCurrency(upgradeInfo.cost_difference.annual_savings)}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Maybe Later
                </button>
                <button
                  onClick={handleUpgrade}
                  disabled={isUpgrading}
                  className={`flex-1 px-4 py-2 bg-gradient-to-r ${getTierColor(suggestedTier)} text-white rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center`}
                >
                  {isUpgrading ? (
                    <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      Upgrade Now
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </>
                  )}
                </button>
              </div>

              {/* Footer */}
              <p className="text-xs text-gray-500 text-center mt-4">
                No setup fees • Cancel anytime • 30-day money-back guarantee
              </p>
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default SubscriptionUpgrade;