import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Calendar } from 'lucide-react';
import { UsageSummary } from '../../types';
import { SubscriptionService } from '../../services/subscriptionService';

interface UsageChartProps {
  usageSummary: UsageSummary;
}

const UsageChart: React.FC<UsageChartProps> = ({ usageSummary }) => {
  const metrics = [
    {
      name: 'Campaigns',
      current: usageSummary.usage.campaigns,
      limit: usageSummary.limits.campaigns,
      percentage: usageSummary.usage_percentages.campaigns,
      color: 'bg-blue-500'
    },
    {
      name: 'AI Generations',
      current: usageSummary.usage.ai_generations,
      limit: usageSummary.limits.ai_generations,
      percentage: usageSummary.usage_percentages.ai_generations,
      color: 'bg-purple-500'
    },
    {
      name: 'Ad Spend',
      current: usageSummary.usage.ad_spend,
      limit: usageSummary.limits.ad_spend,
      percentage: usageSummary.usage_percentages.ad_spend,
      color: 'bg-green-500',
      isMonetary: true
    }
  ];

  const maxPercentage = Math.max(...metrics.map(m => m.percentage));
  const chartHeight = 200;

  const getBarColor = (percentage: number, defaultColor: string) => {
    if (percentage >= 95) return 'bg-red-500';
    if (percentage >= 90) return 'bg-orange-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return defaultColor;
  };

  const formatValue = (value: number, isMonetary = false) => {
    if (isMonetary) {
      return SubscriptionService.formatCurrency(value);
    }
    return value.toLocaleString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-gray-100">
            <BarChart3 className="h-5 w-5 text-gray-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">Usage Overview</h3>
            <p className="text-sm text-gray-500">Current billing period usage</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Calendar className="h-4 w-4" />
          <span>{usageSummary.days_until_reset} days until reset</span>
        </div>
      </div>

      {/* Chart */}
      <div className="space-y-6">
        {metrics.map((metric, index) => (
          <div key={metric.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${metric.color}`} />
                <span className="font-medium text-gray-900">{metric.name}</span>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {formatValue(metric.current, metric.isMonetary)} / {formatValue(metric.limit, metric.isMonetary)}
                </div>
                <div className="text-xs text-gray-500">
                  {metric.percentage.toFixed(1)}% used
                </div>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="relative">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(metric.percentage, 100)}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1, ease: 'easeOut' }}
                  className={`h-3 rounded-full ${getBarColor(metric.percentage, metric.color)}`}
                />
              </div>
              
              {/* Threshold markers */}
              <div className="absolute top-0 left-3/4 w-0.5 h-3 bg-yellow-400 opacity-50" />
              <div className="absolute top-0 right-1/10 w-0.5 h-3 bg-red-400 opacity-50" />
            </div>
          </div>
        ))}
      </div>

      {/* Chart Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-6 text-xs text-gray-500">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-yellow-400 rounded-full" />
            <span>75% threshold</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-400 rounded-full" />
            <span>90% threshold</span>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">
            {Math.round(metrics.reduce((sum, m) => sum + m.percentage, 0) / metrics.length)}%
          </div>
          <div className="text-sm text-gray-500">Average Usage</div>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">
            {metrics.filter(m => m.percentage >= 75).length}
          </div>
          <div className="text-sm text-gray-500">High Usage Metrics</div>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">
            {usageSummary.days_until_reset}
          </div>
          <div className="text-sm text-gray-500">Days Until Reset</div>
        </div>
      </div>

      {/* Usage Insights */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-start space-x-3">
          <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">Usage Insights</h4>
            <div className="text-sm text-blue-700 space-y-1">
              {maxPercentage >= 90 && (
                <p>• High usage detected - consider upgrading before limits are reached</p>
              )}
              {maxPercentage < 50 && (
                <p>• You're using less than 50% of your limits - great efficiency!</p>
              )}
              <p>• Your current {usageSummary.current_tier} plan resets on the 1st of each month</p>
              {usageSummary.days_until_reset <= 7 && (
                <p>• Your usage will reset in {usageSummary.days_until_reset} days</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default UsageChart;