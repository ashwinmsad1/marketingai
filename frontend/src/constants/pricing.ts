import { PricingTier, SubscriptionTier } from '../types';

export const PRICING_TIERS: Record<SubscriptionTier, PricingTier> = {
  basic: {
    name: "Basic",
    price_monthly: 2999,
    price_annual: 29990,
    campaigns_limit: 5,
    ai_generations_limit: 150,
    ad_spend_monitoring_limit: 25000,
    support_level: "email",
    features: [
      "ai_campaign_creation",
      "meta_ads_automation", 
      "basic_analytics",
      "budget_monitoring",
      "email_support"
    ]
  },
  professional: {
    name: "Professional", 
    price_monthly: 7999,
    price_annual: 79990,
    campaigns_limit: 20,
    ai_generations_limit: 500,
    ad_spend_monitoring_limit: 100000,
    support_level: "email_priority",
    features: [
      "ai_campaign_creation",
      "meta_ads_automation",
      "enhanced_analytics", 
      "advanced_budget_monitoring",
      "priority_email_support",
      "performance_tracking"
    ]
  },
  business: {
    name: "Business",
    price_monthly: 19999,
    price_annual: 199990,
    campaigns_limit: 50,
    ai_generations_limit: 1200,
    ad_spend_monitoring_limit: 500000,
    support_level: "email_premium",
    features: [
      "ai_campaign_creation",
      "meta_ads_automation",
      "full_analytics_suite",
      "comprehensive_budget_monitoring", 
      "premium_email_support",
      "advanced_performance_tracking",
      "data_export",
      "custom_reporting"
    ]
  }
};

export const FEATURE_LABELS: Record<string, string> = {
  ai_campaign_creation: "AI Campaign Creation",
  meta_ads_automation: "Meta Ads Automation",
  basic_analytics: "Basic Analytics",
  enhanced_analytics: "Enhanced Analytics", 
  full_analytics_suite: "Full Analytics Suite",
  budget_monitoring: "Budget Monitoring",
  advanced_budget_monitoring: "Advanced Budget Monitoring",
  comprehensive_budget_monitoring: "Comprehensive Budget Monitoring",
  email_support: "Email Support",
  priority_email_support: "Priority Email Support",
  premium_email_support: "Premium Email Support",
  performance_tracking: "Performance Tracking",
  advanced_performance_tracking: "Advanced Performance Tracking",
  data_export: "Data Export",
  custom_reporting: "Custom Reporting"
};

export const TIER_COLORS: Record<SubscriptionTier, { primary: string; secondary: string; accent: string }> = {
  basic: {
    primary: "from-blue-500 to-blue-600",
    secondary: "bg-blue-50 border-blue-200",
    accent: "text-blue-600"
  },
  professional: {
    primary: "from-purple-500 to-purple-600",
    secondary: "bg-purple-50 border-purple-200",
    accent: "text-purple-600"
  },
  business: {
    primary: "from-gold-500 to-gold-600",
    secondary: "bg-yellow-50 border-yellow-200",
    accent: "text-yellow-600"
  }
};

export const TIER_BADGES: Record<SubscriptionTier, string> = {
  basic: "Most Popular",
  professional: "Best Value",
  business: "Premium"
};

export function formatCurrency(amount: number): string {
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

export function calculateAnnualSavings(monthlyPrice: number, annualPrice: number): number {
  return (monthlyPrice * 12) - annualPrice;
}

export function calculateSavingsPercentage(monthlyPrice: number, annualPrice: number): number {
  const totalMonthly = monthlyPrice * 12;
  const savings = totalMonthly - annualPrice;
  return Math.round((savings / totalMonthly) * 100);
}

export function getTierUpgradePath(currentTier: SubscriptionTier): SubscriptionTier | null {
  const upgradePath: Record<SubscriptionTier, SubscriptionTier | null> = {
    basic: 'professional',
    professional: 'business',
    business: null
  };
  return upgradePath[currentTier];
}

export function compareTiers(tier1: SubscriptionTier, tier2: SubscriptionTier) {
  const config1 = PRICING_TIERS[tier1];
  const config2 = PRICING_TIERS[tier2];
  
  return {
    tier1,
    tier2,
    differences: {
      campaigns: {
        tier1: config1.campaigns_limit,
        tier2: config2.campaigns_limit,
        increase: config2.campaigns_limit - config1.campaigns_limit
      },
      ai_generations: {
        tier1: config1.ai_generations_limit,
        tier2: config2.ai_generations_limit,
        increase: config2.ai_generations_limit - config1.ai_generations_limit
      },
      ad_spend: {
        tier1: config1.ad_spend_monitoring_limit,
        tier2: config2.ad_spend_monitoring_limit,
        increase: config2.ad_spend_monitoring_limit - config1.ad_spend_monitoring_limit
      }
    },
    pricing: {
      monthly_difference: config2.price_monthly - config1.price_monthly,
      annual_difference: config2.price_annual - config1.price_annual
    },
    new_features: config2.features.filter(f => !config1.features.includes(f))
  };
}