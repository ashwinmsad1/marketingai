import React from 'react';
import { motion } from 'framer-motion';

interface UsageProgressBarProps {
  current: number;
  limit: number;
  percentage: number;
  label?: string;
  showValues?: boolean;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
  animate?: boolean;
  className?: string;
  isMonetary?: boolean;
}

const UsageProgressBar: React.FC<UsageProgressBarProps> = ({
  current,
  limit,
  percentage,
  label,
  showValues = true,
  showPercentage = true,
  size = 'md',
  animate = true,
  className = '',
  isMonetary = false
}) => {
  const getBarHeight = () => {
    switch (size) {
      case 'sm':
        return 'h-1';
      case 'md':
        return 'h-2';
      case 'lg':
        return 'h-3';
      default:
        return 'h-2';
    }
  };

  const getBarColor = () => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 95) return 'bg-red-500';
    if (percentage >= 90) return 'bg-orange-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm':
        return 'text-xs';
      case 'md':
        return 'text-sm';
      case 'lg':
        return 'text-base';
      default:
        return 'text-sm';
    }
  };

  const formatValue = (value: number) => {
    if (isMonetary) {
      if (value >= 100000) {
        const lakhs = value / 100000;
        return `₹${lakhs.toFixed(1)}L`;
      } else if (value >= 1000) {
        const thousands = value / 1000;
        return `₹${thousands.toFixed(0)}K`;
      } else {
        return `₹${value.toLocaleString()}`;
      }
    }
    return value.toLocaleString();
  };

  const getStatusText = () => {
    if (percentage >= 100) return 'Limit exceeded';
    if (percentage >= 95) return 'Near limit';
    if (percentage >= 90) return 'High usage';
    if (percentage >= 75) return 'Moderate usage';
    return 'Normal usage';
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Header */}
      {(label || showValues || showPercentage) && (
        <div className={`flex items-center justify-between ${getTextSize()}`}>
          {label && (
            <span className="font-medium text-gray-900">{label}</span>
          )}
          <div className="flex items-center space-x-2">
            {showValues && (
              <span className="text-gray-600">
                {formatValue(current)} / {formatValue(limit)}
              </span>
            )}
            {showPercentage && (
              <span className={`font-medium ${
                percentage >= 90 ? 'text-red-600' : 
                percentage >= 75 ? 'text-yellow-600' : 'text-gray-600'
              }`}>
                {percentage.toFixed(1)}%
              </span>
            )}
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className={`w-full bg-gray-200 rounded-full ${getBarHeight()}`}>
        <motion.div
          initial={animate ? { width: 0 } : { width: `${Math.min(percentage, 100)}%` }}
          animate={{ width: `${Math.min(percentage, 100)}%` }}
          transition={animate ? { duration: 0.8, ease: 'easeOut' } : { duration: 0 }}
          className={`${getBarHeight()} rounded-full ${getBarColor()}`}
        />
      </div>

      {/* Status Text */}
      <div className={`flex items-center justify-between ${getTextSize()}`}>
        <span className={`${
          percentage >= 90 ? 'text-red-600' : 
          percentage >= 75 ? 'text-yellow-600' : 'text-gray-500'
        }`}>
          {getStatusText()}
        </span>
        {limit > current && (
          <span className="text-gray-500">
            {formatValue(limit - current)} remaining
          </span>
        )}
      </div>

      {/* Threshold Indicators */}
      {size !== 'sm' && (
        <div className="relative">
          <div className="absolute top-0 left-3/4 w-0.5 h-1 bg-yellow-400 opacity-50" 
               title="75% threshold" />
          <div className="absolute top-0 right-1/10 w-0.5 h-1 bg-red-400 opacity-50"
               title="90% threshold" />
        </div>
      )}
    </div>
  );
};

export default UsageProgressBar;