import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Calendar, TrendingUp, AlertCircle } from 'lucide-react';
import { UsageSummary, SubscriptionTier } from '../../types';
import { SubscriptionService } from '../../services/subscriptionService';
import UsageMetricCard from './UsageMetricCard';
import UsageChart from './UsageChart';
import UsageAlert from '../Subscription/UsageAlert';
import SubscriptionStatus from '../Subscription/SubscriptionStatus';
import { LoadingSpinner } from '../LoadingStates';
import toast from 'react-hot-toast';

interface UsageDashboardProps {
  className?: string;
}

const UsageDashboard: React.FC<UsageDashboardProps> = ({ className = '' }) => {
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  const fetchUsageSummary = async (showRefreshIndicator = false) => {
    if (showRefreshIndicator) setIsRefreshing(true);
    
    try {
      const summary = await SubscriptionService.getUsageSummary();
      setUsageSummary(summary);
    } catch (error) {
      console.error('Error fetching usage summary:', error);
      toast.error('Failed to load usage data. Please try again.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchUsageSummary();
  }, []);

  const handleRefresh = () => {
    fetchUsageSummary(true);
  };

  const handleDismissAlert = (alertId: string) => {
    setDismissedAlerts(prev => new Set([...prev, alertId]));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!usageSummary) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to load usage data</h3>
        <p className="text-gray-500 mb-4">Please check your connection and try again.</p>
        <button
          onClick={() => fetchUsageSummary()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  const activeAlerts = usageSummary.warnings.filter(
    warning => !dismissedAlerts.has(`${warning.metric}-${warning.percentage}`)
  );

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Usage Dashboard</h2>
          <p className="text-gray-600">
            Track your subscription usage and limits
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-5 w-5 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Usage Alerts */}
      {activeAlerts.length > 0 && (
        <div className="space-y-3">
          {activeAlerts.map((warning, index) => (
            <UsageAlert
              key={`${warning.metric}-${warning.percentage}`}
              warning={warning}
              currentTier={usageSummary.current_tier}
              onDismiss={() => handleDismissAlert(`${warning.metric}-${warning.percentage}`)}
            />
          ))}
        </div>
      )}

      {/* Subscription Status */}
      <SubscriptionStatus
        currentTier={usageSummary.current_tier}
        nextBillingDate={usageSummary.next_reset_date}
        billingCycle="monthly" // This would come from user data
      />

      {/* Usage Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UsageMetricCard
          title="Campaigns"
          current={usageSummary.usage.campaigns}
          limit={usageSummary.limits.campaigns}
          percentage={usageSummary.usage_percentages.campaigns}
          icon="campaigns"
          color="blue"
        />
        <UsageMetricCard
          title="AI Generations"
          current={usageSummary.usage.ai_generations}
          limit={usageSummary.limits.ai_generations}
          percentage={usageSummary.usage_percentages.ai_generations}
          icon="ai"
          color="purple"
        />
        <UsageMetricCard
          title="Ad Spend Monitoring"
          current={usageSummary.usage.ad_spend}
          limit={usageSummary.limits.ad_spend}
          percentage={usageSummary.usage_percentages.ad_spend}
          icon="budget"
          color="green"
          isMonetary={true}
        />
      </div>

      {/* Usage Chart */}
      <UsageChart usageSummary={usageSummary} />

      {/* Reset Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-50 rounded-lg p-6"
      >
        <div className="flex items-center space-x-3 mb-4">
          <Calendar className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Billing Cycle Information</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-1">Current billing period</p>
            <p className="font-medium text-gray-900">
              {new Date(usageSummary.usage.billing_cycle_start).toLocaleDateString()} - {' '}
              {new Date(usageSummary.usage.billing_cycle_end).toLocaleDateString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Next reset</p>
            <p className="font-medium text-gray-900">
              {new Date(usageSummary.next_reset_date).toLocaleDateString()}
              <span className="text-sm text-gray-500 ml-2">
                (in {usageSummary.days_until_reset} days)
              </span>
            </p>
          </div>
        </div>

        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start space-x-3">
            <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900 mb-1">Usage Tips</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Your usage limits reset on the 1st of each month</li>
                <li>• Upgrade anytime to get immediate access to higher limits</li>
                <li>• Monitor your usage regularly to avoid service interruptions</li>
                <li>• Annual plans offer better value and the same monthly resets</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default UsageDashboard;