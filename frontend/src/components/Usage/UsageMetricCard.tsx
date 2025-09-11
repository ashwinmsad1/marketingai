import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Camera, DollarSign, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { SubscriptionService } from '../../services/subscriptionService';

interface UsageMetricCardProps {
  title: string;
  current: number;
  limit: number;
  percentage: number;
  icon: 'campaigns' | 'ai' | 'budget';
  color: 'blue' | 'purple' | 'green';
  isMonetary?: boolean;
}

const UsageMetricCard: React.FC<UsageMetricCardProps> = ({
  title,
  current,
  limit,
  percentage,
  icon,
  color,
  isMonetary = false
}) => {
  const getIcon = () => {
    switch (icon) {
      case 'campaigns':
        return <TrendingUp className="h-6 w-6" />;
      case 'ai':
        return <Zap className="h-6 w-6" />;
      case 'budget':
        return <DollarSign className="h-6 w-6" />;
      default:
        return <TrendingUp className="h-6 w-6" />;
    }
  };

  const getColorClasses = () => {
    switch (color) {
      case 'blue':
        return {
          iconBg: 'bg-blue-100',
          iconText: 'text-blue-600',
          progressBg: 'bg-blue-500',
          textAccent: 'text-blue-600'
        };
      case 'purple':
        return {
          iconBg: 'bg-purple-100',
          iconText: 'text-purple-600',
          progressBg: 'bg-purple-500',
          textAccent: 'text-purple-600'
        };
      case 'green':
        return {
          iconBg: 'bg-green-100',
          iconText: 'text-green-600',
          progressBg: 'bg-green-500',
          textAccent: 'text-green-600'
        };
      default:
        return {
          iconBg: 'bg-gray-100',
          iconText: 'text-gray-600',
          progressBg: 'bg-gray-500',
          textAccent: 'text-gray-600'
        };
    }
  };

  const colorClasses = getColorClasses();
  const usageStatus = SubscriptionService.getUsageStatus(percentage);

  const getStatusIcon = () => {
    if (usageStatus.severity === 'critical' || usageStatus.severity === 'high') {
      return <AlertTriangle className="h-4 w-4 text-red-500" />;
    }
    return <CheckCircle className="h-4 w-4 text-green-500" />;
  };

  const getStatusColor = () => {
    switch (usageStatus.severity) {
      case 'critical':
        return 'text-red-600';
      case 'high':
        return 'text-orange-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-blue-600';
      default:
        return 'text-green-600';
    }
  };

  const getProgressBarColor = () => {
    if (percentage >= 95) return 'bg-red-500';
    if (percentage >= 90) return 'bg-orange-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return colorClasses.progressBg;
  };

  const formatValue = (value: number) => {
    if (isMonetary) {
      return SubscriptionService.formatCurrency(value);
    }
    return value.toLocaleString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 transition-shadow hover:shadow-md"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${colorClasses.iconBg}`}>
            <div className={colorClasses.iconText}>
              {getIcon()}
            </div>
          </div>
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        </div>
        {getStatusIcon()}
      </div>

      {/* Usage Numbers */}
      <div className="mb-4">
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-bold text-gray-900">
            {formatValue(current)}
          </span>
          <span className="text-gray-500">/ {formatValue(limit)}</span>
        </div>
        <div className={`flex items-center space-x-2 mt-1 ${getStatusColor()}`}>
          <span className="text-sm font-medium">
            {percentage.toFixed(1)}% used
          </span>
          <span className="text-xs">• {usageStatus.message}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Usage</span>
          <span>{percentage >= 100 ? 'Limit exceeded' : `${(limit - current).toLocaleString()} remaining`}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(percentage, 100)}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-2 rounded-full ${getProgressBarColor()}`}
          />
        </div>
      </div>

      {/* Additional Info */}
      <div className="text-xs text-gray-500">
        {percentage >= 100 ? (
          <span className="text-red-600 font-medium">
            Upgrade required to continue using this feature
          </span>
        ) : percentage >= 90 ? (
          <span className="text-orange-600 font-medium">
            Consider upgrading soon to avoid interruption
          </span>
        ) : (
          <span>
            Resets on the 1st of each month
          </span>
        )}
      </div>
    </motion.div>
  );
};

export default UsageMetricCard;