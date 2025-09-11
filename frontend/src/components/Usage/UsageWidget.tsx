import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, ChevronDown, Zap, Camera, DollarSign } from 'lucide-react';
import { UsageSummary, SubscriptionTier } from '../../types';
import { SubscriptionService } from '../../services/subscriptionService';
import SubscriptionUpgrade from '../Subscription/SubscriptionUpgrade';

interface UsageWidgetProps {
  variant?: 'compact' | 'expanded';
  showUpgradeButton?: boolean;
  className?: string;
}

const UsageWidget: React.FC<UsageWidgetProps> = ({
  variant = 'compact',
  showUpgradeButton = true,
  className = ''
}) => {
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const summary = await SubscriptionService.getUsageSummary();
        setUsageSummary(summary);
      } catch (error) {
        console.error('Error fetching usage:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsage();
  }, []);

  if (isLoading) {
    return (
      <div className={`animate-pulse bg-gray-200 rounded-lg h-16 ${className}`} />
    );
  }

  if (!usageSummary) {
    return null;
  }

  const metrics = [
    {
      name: 'Campaigns',
      icon: <TrendingUp className="h-4 w-4" />,
      current: usageSummary.usage.campaigns,
      limit: usageSummary.limits.campaigns,
      percentage: usageSummary.usage_percentages.campaigns,
      color: 'blue'
    },
    {
      name: 'AI Gen',
      icon: <Zap className="h-4 w-4" />,
      current: usageSummary.usage.ai_generations,
      limit: usageSummary.limits.ai_generations,
      percentage: usageSummary.usage_percentages.ai_generations,
      color: 'purple'
    },
    {
      name: 'Ad Spend',
      icon: <DollarSign className="h-4 w-4" />,
      current: usageSummary.usage.ad_spend,
      limit: usageSummary.limits.ad_spend,
      percentage: usageSummary.usage_percentages.ad_spend,
      color: 'green',
      isMonetary: true
    }
  ];

  const maxUsage = Math.max(...metrics.map(m => m.percentage));
  const criticalMetrics = metrics.filter(m => m.percentage >= 90);
  const hasHighUsage = maxUsage >= 75;

  const getStatusColor = () => {
    if (maxUsage >= 95) return 'text-red-600';
    if (maxUsage >= 90) return 'text-orange-600';
    if (maxUsage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 95) return 'bg-red-500';
    if (percentage >= 90) return 'bg-orange-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const formatValue = (value: number, isMonetary = false) => {
    if (isMonetary) {
      return SubscriptionService.formatCurrency(value);
    }
    return value.toLocaleString();
  };

  const getSuggestedTier = (): SubscriptionTier => {
    if (usageSummary.current_tier === 'basic') return 'professional';
    if (usageSummary.current_tier === 'professional') return 'business';
    return 'business';
  };

  if (variant === 'compact') {
    return (
      <>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`bg-white rounded-lg shadow-sm border border-gray-200 p-3 cursor-pointer hover:shadow-md transition-shadow ${className}`}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {hasHighUsage && <AlertTriangle className="h-4 w-4 text-orange-500" />}
              <span className="text-sm font-medium text-gray-900">
                Usage: {Math.round(maxUsage)}%
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`text-xs font-medium ${getStatusColor()}`}>
                {usageSummary.current_tier.charAt(0).toUpperCase() + usageSummary.current_tier.slice(1)}
              </span>
              <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
            </div>
          </div>

          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              transition={{ duration: 0.2 }}
              className="mt-3 space-y-2 overflow-hidden"
            >
              {metrics.map((metric) => (
                <div key={metric.name} className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <div className={`text-gray-500`}>
                      {metric.icon}
                    </div>
                    <span className="text-gray-700">{metric.name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-600">
                      {formatValue(metric.current, metric.isMonetary)} / {formatValue(metric.limit, metric.isMonetary)}
                    </span>
                    <div className="w-12 bg-gray-200 rounded-full h-1">
                      <div
                        className={`h-1 rounded-full ${getProgressColor(metric.percentage)}`}
                        style={{ width: `${Math.min(metric.percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}

              {showUpgradeButton && hasHighUsage && (
                <div className="pt-2 border-t">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowUpgrade(true);
                    }}
                    className="w-full text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    Upgrade Plan
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </motion.div>

        {/* Upgrade Modal */}
        <SubscriptionUpgrade
          isOpen={showUpgrade}
          onClose={() => setShowUpgrade(false)}
          currentTier={usageSummary.current_tier}
          suggestedTier={getSuggestedTier()}
          usageSummary={usageSummary}
          onUpgradeComplete={() => setShowUpgrade(false)}
        />
      </>
    );
  }

  // Expanded variant
  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Current Usage</h3>
          <span className={`text-sm font-medium px-2 py-1 rounded-full ${
            hasHighUsage ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'
          }`}>
            {usageSummary.current_tier.charAt(0).toUpperCase() + usageSummary.current_tier.slice(1)} Plan
          </span>
        </div>

        <div className="space-y-3">
          {metrics.map((metric, index) => (
            <div key={metric.name} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="text-gray-500">
                    {metric.icon}
                  </div>
                  <span className="font-medium text-gray-900">{metric.name}</span>
                </div>
                <span className="text-gray-600">
                  {formatValue(metric.current, metric.isMonetary)} / {formatValue(metric.limit, metric.isMonetary)}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(metric.percentage, 100)}%` }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className={`h-2 rounded-full ${getProgressColor(metric.percentage)}`}
                  />
                </div>
                <span className={`text-xs font-medium w-12 text-right ${
                  metric.percentage >= 90 ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {metric.percentage.toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {criticalMetrics.length > 0 && (
          <div className="mt-4 p-3 bg-orange-50 rounded-lg">
            <div className="flex items-start space-x-2">
              <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-orange-900">
                  High Usage Alert
                </p>
                <p className="text-xs text-orange-700 mt-1">
                  {criticalMetrics.length > 1 
                    ? `${criticalMetrics.length} metrics are near their limits`
                    : `${criticalMetrics[0].name} is near its limit`
                  }
                </p>
              </div>
            </div>
          </div>
        )}

        {showUpgradeButton && hasHighUsage && (
          <div className="mt-4 pt-4 border-t">
            <button
              onClick={() => setShowUpgrade(true)}
              className="w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upgrade to {getSuggestedTier().charAt(0).toUpperCase() + getSuggestedTier().slice(1)}
            </button>
          </div>
        )}

        <div className="mt-3 text-xs text-gray-500 text-center">
          Resets in {usageSummary.days_until_reset} days
        </div>
      </motion.div>

      {/* Upgrade Modal */}
      <SubscriptionUpgrade
        isOpen={showUpgrade}
        onClose={() => setShowUpgrade(false)}
        currentTier={usageSummary.current_tier}
        suggestedTier={getSuggestedTier()}
        usageSummary={usageSummary}
        onUpgradeComplete={() => setShowUpgrade(false)}
      />
    </>
  );
};

export default UsageWidget;