import { 
  SubscriptionTier, 
  UsageSummary, 
  TierComparisonData, 
  SubscriptionUpgradeInfo,
  PricingTier,
  APIResponse 
} from '../types';
import { PRICING_TIERS } from '../constants/pricing';
import api from './api';

export class SubscriptionService {
  /**
   * Get current user's usage summary and tier information
   */
  static async getUsageSummary(): Promise<UsageSummary> {
    try {
      const response = await api.get<APIResponse<UsageSummary>>('/api/v1/campaigns/usage-status');
      if (response.data.success && response.data.data) {
        return response.data.data;
      }
      throw new Error('Failed to fetch usage summary');
    } catch (error) {
      console.error('Error fetching usage summary:', error);
      throw error;
    }
  }

  /**
   * Get pricing tier configuration
   */
  static getPricingTiers(): Record<SubscriptionTier, PricingTier> {
    return PRICING_TIERS;
  }

  /**
   * Compare two subscription tiers
   */
  static compareTiers(currentTier: SubscriptionTier, targetTier: SubscriptionTier): TierComparisonData {
    const current = PRICING_TIERS[currentTier];
    const target = PRICING_TIERS[targetTier];

    return {
      tier1: currentTier,
      tier2: targetTier,
      differences: {
        campaigns: {
          tier1: current.campaigns_limit,
          tier2: target.campaigns_limit,
          increase: target.campaigns_limit - current.campaigns_limit
        },
        ai_generations: {
          tier1: current.ai_generations_limit,
          tier2: target.ai_generations_limit,
          increase: target.ai_generations_limit - current.ai_generations_limit
        },
        ad_spend: {
          tier1: current.ad_spend_monitoring_limit,
          tier2: target.ad_spend_monitoring_limit,
          increase: target.ad_spend_monitoring_limit - current.ad_spend_monitoring_limit
        }
      },
      pricing: {
        monthly_difference: target.price_monthly - current.price_monthly,
        annual_difference: target.price_annual - current.price_annual
      },
      new_features: target.features.filter(f => !current.features.includes(f))
    };
  }

  /**
   * Get upgrade information for a user
   */
  static getUpgradeInfo(
    currentTier: SubscriptionTier, 
    suggestedTier: SubscriptionTier,
    usagePercentages?: { campaigns: number; ai_generations: number; ad_spend: number }
  ): SubscriptionUpgradeInfo {
    const comparison = this.compareTiers(currentTier, suggestedTier);
    const target = PRICING_TIERS[suggestedTier];
    
    // Calculate upgrade urgency based on usage
    let urgency: 'none' | 'low' | 'medium' | 'high' | 'critical' = 'low';
    if (usagePercentages) {
      const maxUsage = Math.max(...Object.values(usagePercentages));
      if (maxUsage >= 100) urgency = 'critical';
      else if (maxUsage >= 95) urgency = 'high';
      else if (maxUsage >= 85) urgency = 'medium';
      else if (maxUsage >= 70) urgency = 'low';
      else urgency = 'none';
    }

    // Generate benefits list
    const benefits = [
      `${comparison.differences.campaigns.increase} more campaigns per month`,
      `${comparison.differences.ai_generations.increase} more AI generations`,
      `₹${(comparison.differences.ad_spend.increase / 1000).toFixed(0)}K more ad spend monitoring`,
      ...comparison.new_features.map(f => this.getFeatureBenefit(f))
    ].filter(Boolean);

    return {
      current_tier: currentTier,
      suggested_tier: suggestedTier,
      benefits,
      cost_difference: {
        monthly: comparison.pricing.monthly_difference,
        annual: comparison.pricing.annual_difference,
        annual_savings: (target.price_monthly * 12) - target.price_annual
      },
      upgrade_urgency: urgency
    };
  }

  /**
   * Get human-readable benefit for a feature
   */
  private static getFeatureBenefit(feature: string): string {
    const benefitMap: Record<string, string> = {
      enhanced_analytics: 'Enhanced analytics with deeper insights',
      full_analytics_suite: 'Complete analytics suite with custom reports',
      advanced_budget_monitoring: 'Advanced budget monitoring and alerts',
      comprehensive_budget_monitoring: 'Comprehensive budget monitoring with forecasting',
      priority_email_support: 'Priority email support with faster response',
      premium_email_support: 'Premium email support with dedicated account manager',
      performance_tracking: 'Performance tracking and optimization recommendations',
      advanced_performance_tracking: 'Advanced performance tracking with AI insights',
      data_export: 'Data export capabilities for external analysis',
      custom_reporting: 'Custom reporting with automated scheduling'
    };
    return benefitMap[feature] || feature.replace(/_/g, ' ');
  }

  /**
   * Initiate subscription upgrade
   */
  static async upgradeSubscription(
    targetTier: SubscriptionTier, 
    billingCycle: 'monthly' | 'annual'
  ): Promise<{ success: boolean; upgrade_url?: string; error?: string }> {
    try {
      const response = await api.post<APIResponse<{ upgrade_url: string }>>('/api/v1/subscription/upgrade', {
        target_tier: targetTier,
        billing_cycle: billingCycle
      });

      if (response.data.success && response.data.data) {
        return {
          success: true,
          upgrade_url: response.data.data.upgrade_url
        };
      }
      
      return {
        success: false,
        error: response.data.message || 'Upgrade failed'
      };
    } catch (error: any) {
      console.error('Error upgrading subscription:', error);
      return {
        success: false,
        error: error.response?.data?.message || 'Network error during upgrade'
      };
    }
  }

  /**
   * Calculate usage percentage
   */
  static calculateUsagePercentage(current: number, limit: number): number {
    if (limit <= 0) return 0;
    return Math.min((current / limit) * 100, 100);
  }

  /**
   * Get usage status color and message
   */
  static getUsageStatus(percentage: number): {
    status: string;
    color: string;
    message: string;
    severity: string;
  } {
    if (percentage >= 100) {
      return {
        status: 'exceeded',
        color: 'red',
        message: 'Limit exceeded',
        severity: 'critical'
      };
    } else if (percentage >= 95) {
      return {
        status: 'critical',
        color: 'red',
        message: 'Near limit - action required',
        severity: 'high'
      };
    } else if (percentage >= 90) {
      return {
        status: 'warning',
        color: 'orange',
        message: 'Approaching limit',
        severity: 'medium'
      };
    } else if (percentage >= 75) {
      return {
        status: 'caution',
        color: 'yellow',
        message: 'Moderate usage',
        severity: 'low'
      };
    } else {
      return {
        status: 'normal',
        color: 'green',
        message: 'Usage within normal range',
        severity: 'none'
      };
    }
  }

  /**
   * Format currency for Indian market
   */
  static formatCurrency(amount: number): string {
    if (amount >= 100000) {
      const lakhs = amount / 100000;
      return `₹${lakhs.toFixed(1)}L`;
    } else if (amount >= 1000) {
      const thousands = amount / 1000;
      return `₹${thousands.toFixed(0)}K`;
    } else {
      return `₹${amount.toLocaleString()}`;
    }
  }

  /**
   * Get next billing date
   */
  static getNextBillingDate(resetDate: string): Date {
    return new Date(resetDate);
  }

  /**
   * Get days until reset
   */
  static getDaysUntilReset(resetDate: string): number {
    const now = new Date();
    const reset = new Date(resetDate);
    const diffTime = reset.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  /**
   * Check if user should see upgrade prompt
   */
  static shouldShowUpgradePrompt(usagePercentages: { campaigns: number; ai_generations: number; ad_spend: number }): boolean {
    const maxUsage = Math.max(...Object.values(usagePercentages));
    return maxUsage >= 75; // Show upgrade prompt at 75% usage
  }

  /**
   * Get recommended tier based on usage patterns
   */
  static getRecommendedTier(
    projectedUsage: { campaigns: number; ai_generations: number; ad_spend: number }
  ): SubscriptionTier {
    const tiers: SubscriptionTier[] = ['basic', 'professional', 'business'];
    
    for (const tier of tiers) {
      const limits = PRICING_TIERS[tier];
      if (
        projectedUsage.campaigns <= limits.campaigns_limit &&
        projectedUsage.ai_generations <= limits.ai_generations_limit &&
        projectedUsage.ad_spend <= limits.ad_spend_monitoring_limit
      ) {
        return tier;
      }
    }
    
    return 'business'; // Default to highest tier if none fit
  }
}

export default SubscriptionService;