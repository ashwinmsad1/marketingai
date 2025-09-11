import React from 'react';
import { motion } from 'framer-motion';
import { X, AlertTriangle, TrendingUp, Crown } from 'lucide-react';
import { SubscriptionTier } from '../../types';
import toast from 'react-hot-toast';

interface UsageNotificationProps {
  type: 'warning' | 'critical' | 'upgrade_suggestion';
  metric: string;
  percentage: number;
  currentTier: SubscriptionTier;
  onUpgrade?: () => void;
  onDismiss?: () => void;
}

const UsageNotification: React.FC<UsageNotificationProps> = ({
  type,
  metric,
  percentage,
  currentTier,
  onUpgrade,
  onDismiss
}) => {
  const getIcon = () => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'upgrade_suggestion':
        return <Crown className="h-5 w-5 text-purple-600" />;
      default:
        return <TrendingUp className="h-5 w-5 text-blue-600" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-800'
        };
      case 'critical':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800'
        };
      case 'upgrade_suggestion':
        return {
          bg: 'bg-purple-50',
          border: 'border-purple-200',
          text: 'text-purple-800'
        };
      default:
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          text: 'text-blue-800'
        };
    }
  };

  const getMessage = () => {
    const metricName = metric.replace('_', ' ').toLowerCase();
    
    switch (type) {
      case 'warning':
        return `Your ${metricName} usage is at ${percentage.toFixed(0)}%. Consider upgrading soon.`;
      case 'critical':
        return `Critical: ${metricName} usage at ${percentage.toFixed(0)}%. Upgrade now to avoid interruption.`;
      case 'upgrade_suggestion':
        return `Unlock more ${metricName} capacity with a higher tier plan.`;
      default:
        return `${metricName} usage update: ${percentage.toFixed(0)}%`;
    }
  };

  const getUpgradeTier = (): SubscriptionTier => {
    if (currentTier === 'basic') return 'professional';
    if (currentTier === 'professional') return 'business';
    return 'business';
  };

  const styles = getStyles();

  return (
    <motion.div
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className={`
        max-w-sm w-full rounded-lg shadow-lg border pointer-events-auto
        ${styles.bg} ${styles.border}
      `}
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          <div className="ml-3 w-0 flex-1">
            <p className={`text-sm font-medium ${styles.text}`}>
              Usage Alert
            </p>
            <p className={`mt-1 text-sm ${styles.text} opacity-90`}>
              {getMessage()}
            </p>
            <div className="mt-3 flex space-x-2">
              {(type === 'critical' || type === 'upgrade_suggestion') && onUpgrade && (
                <button
                  onClick={onUpgrade}
                  className={`
                    text-xs px-3 py-1 rounded-md font-medium transition-colors
                    ${type === 'critical' 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'bg-purple-600 hover:bg-purple-700 text-white'
                    }
                  `}
                >
                  Upgrade to {getUpgradeTier().charAt(0).toUpperCase() + getUpgradeTier().slice(1)}
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="text-xs text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Dismiss
                </button>
              )}
            </div>
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              onClick={onDismiss}
              className={`
                rounded-md inline-flex text-gray-400 hover:text-gray-500 
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
              `}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// Toast notification functions
export const showUsageWarning = (
  metric: string, 
  percentage: number, 
  currentTier: SubscriptionTier,
  onUpgrade?: () => void
) => {
  toast.custom((t) => (
    <UsageNotification
      type="warning"
      metric={metric}
      percentage={percentage}
      currentTier={currentTier}
      onUpgrade={onUpgrade}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 8000,
    position: 'top-right'
  });
};

export const showUsageCritical = (
  metric: string, 
  percentage: number, 
  currentTier: SubscriptionTier,
  onUpgrade?: () => void
) => {
  toast.custom((t) => (
    <UsageNotification
      type="critical"
      metric={metric}
      percentage={percentage}
      currentTier={currentTier}
      onUpgrade={onUpgrade}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 12000,
    position: 'top-right'
  });
};

export const showUpgradeSuggestion = (
  currentTier: SubscriptionTier,
  onUpgrade?: () => void
) => {
  toast.custom((t) => (
    <UsageNotification
      type="upgrade_suggestion"
      metric="features"
      percentage={0}
      currentTier={currentTier}
      onUpgrade={onUpgrade}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 10000,
    position: 'top-right'
  });
};

export default UsageNotification;