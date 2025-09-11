import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, TrendingUp, Zap } from 'lucide-react';
import { SubscriptionTier, UsageWarning } from '../../types';
import { SubscriptionService } from '../../services/subscriptionService';
import SubscriptionUpgrade from './SubscriptionUpgrade';

interface UsageAlertProps {
  warning: UsageWarning;
  currentTier: SubscriptionTier;
  onDismiss: () => void;
  className?: string;
}

const UsageAlert: React.FC<UsageAlertProps> = ({
  warning,
  currentTier,
  onDismiss,
  className = ''
}) => {
  const [showUpgrade, setShowUpgrade] = useState(false);

  const getAlertIcon = () => {
    switch (warning.status.severity) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'medium':
        return <TrendingUp className="h-5 w-5 text-yellow-500" />;
      default:
        return <Zap className="h-5 w-5 text-blue-500" />;
    }
  };

  const getAlertColors = () => {
    switch (warning.status.severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'high':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getButtonColors = () => {
    switch (warning.status.severity) {
      case 'critical':
        return 'bg-red-600 hover:bg-red-700';
      case 'high':
        return 'bg-orange-600 hover:bg-orange-700';
      case 'medium':
        return 'bg-yellow-600 hover:bg-yellow-700';
      default:
        return 'bg-blue-600 hover:bg-blue-700';
    }
  };

  const getSuggestedTier = (): SubscriptionTier => {
    if (currentTier === 'basic') return 'professional';
    if (currentTier === 'professional') return 'business';
    return 'business';
  };

  const shouldShowUpgradeButton = () => {
    return warning.status.severity === 'critical' || warning.status.severity === 'high';
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`p-4 rounded-lg border ${getAlertColors()} ${className}`}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            {getAlertIcon()}
            <div className="flex-1">
              <h4 className="font-medium mb-1">
                {warning.metric_name} Usage Alert
              </h4>
              <p className="text-sm mb-2">{warning.message}</p>
              
              {/* Usage Progress Bar */}
              <div className="mb-3">
                <div className="flex justify-between text-xs mb-1">
                  <span>{warning.percentage.toFixed(1)}% used</span>
                  <span>100% limit</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${warning.percentage}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className={`h-2 rounded-full ${warning.status.color === 'red' ? 'bg-red-500' : 
                      warning.status.color === 'orange' ? 'bg-orange-500' :
                      warning.status.color === 'yellow' ? 'bg-yellow-500' : 'bg-blue-500'}`}
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                {shouldShowUpgradeButton() && (
                  <button
                    onClick={() => setShowUpgrade(true)}
                    className={`px-3 py-1 text-white text-sm rounded-md font-medium transition-colors ${getButtonColors()}`}
                  >
                    Upgrade Plan
                  </button>
                )}
                <button
                  onClick={onDismiss}
                  className="px-3 py-1 text-gray-600 text-sm rounded-md border border-gray-300 hover:bg-gray-50 transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
          
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-gray-500 focus:outline-none ml-2"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </motion.div>

      {/* Upgrade Modal */}
      <SubscriptionUpgrade
        isOpen={showUpgrade}
        onClose={() => setShowUpgrade(false)}
        currentTier={currentTier}
        suggestedTier={getSuggestedTier()}
        onUpgradeComplete={() => {
          setShowUpgrade(false);
          onDismiss();
        }}
      />
    </>
  );
};

export default UsageAlert;