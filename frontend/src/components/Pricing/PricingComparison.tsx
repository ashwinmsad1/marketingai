import React from 'react';
import { Check, X } from 'lucide-react';
import { PRICING_TIERS, FEATURE_LABELS, formatCurrency } from '../../constants/pricing';
import { SubscriptionTier } from '../../types';

const PricingComparison: React.FC = () => {
  const tiers = Object.keys(PRICING_TIERS) as SubscriptionTier[];
  
  const comparisonFeatures = [
    {
      category: 'Core Features',
      features: [
        { key: 'ai_campaign_creation', label: 'AI Campaign Creation', basic: true, professional: true, business: true },
        { key: 'meta_ads_automation', label: 'Meta Ads Automation', basic: true, professional: true, business: true },
        { key: 'budget_monitoring', label: 'Budget Monitoring', basic: 'Basic', professional: 'Advanced', business: 'Comprehensive' },
        { key: 'email_support', label: 'Email Support', basic: 'Standard', professional: 'Priority', business: 'Premium' },
      ]
    },
    {
      category: 'Analytics & Reporting',
      features: [
        { key: 'basic_analytics', label: 'Basic Analytics', basic: true, professional: false, business: false },
        { key: 'enhanced_analytics', label: 'Enhanced Analytics', basic: false, professional: true, business: true },
        { key: 'full_analytics_suite', label: 'Full Analytics Suite', basic: false, professional: false, business: true },
        { key: 'performance_tracking', label: 'Performance Tracking', basic: false, professional: true, business: true },
        { key: 'advanced_performance_tracking', label: 'Advanced Performance Tracking', basic: false, professional: false, business: true },
        { key: 'data_export', label: 'Data Export', basic: false, professional: false, business: true },
        { key: 'custom_reporting', label: 'Custom Reporting', basic: false, professional: false, business: true },
      ]
    },
    {
      category: 'Usage Limits',
      features: [
        { key: 'campaigns_limit', label: 'Campaigns per Month', basic: '5', professional: '20', business: '50' },
        { key: 'ai_generations_limit', label: 'AI Generations per Month', basic: '150', professional: '500', business: '1,200' },
        { key: 'ad_spend_monitoring_limit', label: 'Ad Spend Monitoring', basic: '₹25K', professional: '₹1L', business: '₹5L' },
      ]
    },
    {
      category: 'Support & Services',
      features: [
        { key: 'response_time', label: 'Support Response Time', basic: '24-48 hours', professional: '12-24 hours', business: '2-6 hours' },
        { key: 'dedicated_support', label: 'Dedicated Account Manager', basic: false, professional: false, business: true },
        { key: 'setup_assistance', label: 'Setup Assistance', basic: 'Self-service', professional: 'Email guidance', business: 'Live assistance' },
        { key: 'training', label: 'Training & Onboarding', basic: 'Documentation', professional: 'Video tutorials', business: 'Live training' },
      ]
    }
  ];

  const renderFeatureValue = (value: string | boolean, tier: SubscriptionTier) => {
    if (typeof value === 'boolean') {
      return value ? (
        <Check className="h-5 w-5 text-green-500 mx-auto" />
      ) : (
        <X className="h-5 w-5 text-gray-300 mx-auto" />
      );
    }
    
    const colorMap = {
      basic: 'text-blue-600',
      professional: 'text-purple-600',
      business: 'text-yellow-600'
    };
    
    return (
      <span className={`text-sm font-medium ${colorMap[tier]}`}>
        {value}
      </span>
    );
  };

  return (
    <div className="bg-white py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Detailed Feature Comparison
          </h2>
          <p className="text-lg text-gray-600">
            Compare all features across our subscription tiers
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            {/* Table Header */}
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-4 px-6 text-lg font-semibold text-gray-900">
                  Features
                </th>
                {tiers.map((tier) => (
                  <th key={tier} className="text-center py-4 px-6">
                    <div className="space-y-2">
                      <div className="text-lg font-bold text-gray-900 capitalize">
                        {PRICING_TIERS[tier].name}
                      </div>
                      <div className="text-2xl font-bold text-gray-900">
                        {formatCurrency(Math.round(PRICING_TIERS[tier].price_annual / 12))}
                        <span className="text-sm font-normal text-gray-500">/month</span>
                      </div>
                      <div className="text-sm text-gray-500">
                        billed annually
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>

            {/* Table Body */}
            <tbody>
              {comparisonFeatures.map((category, categoryIndex) => (
                <React.Fragment key={category.category}>
                  {/* Category Header */}
                  <tr className="bg-gray-50">
                    <td colSpan={4} className="py-3 px-6 text-sm font-semibold text-gray-900 uppercase tracking-wider">
                      {category.category}
                    </td>
                  </tr>
                  
                  {/* Features in Category */}
                  {category.features.map((feature, featureIndex) => (
                    <tr key={feature.key} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-6 text-gray-700">
                        {feature.label}
                      </td>
                      <td className="py-4 px-6 text-center">
                        {renderFeatureValue(feature.basic, 'basic')}
                      </td>
                      <td className="py-4 px-6 text-center">
                        {renderFeatureValue(feature.professional, 'professional')}
                      </td>
                      <td className="py-4 px-6 text-center">
                        {renderFeatureValue(feature.business, 'business')}
                      </td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Additional Info */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Perfect for Startups</h3>
            <p className="text-blue-700">
              Basic plan is ideal for small businesses and startups looking to get started with AI marketing.
            </p>
          </div>
          <div className="text-center p-6 bg-purple-50 rounded-lg">
            <h3 className="text-lg font-semibold text-purple-900 mb-2">Scale Your Growth</h3>
            <p className="text-purple-700">
              Professional plan offers the perfect balance of features and value for growing businesses.
            </p>
          </div>
          <div className="text-center p-6 bg-yellow-50 rounded-lg">
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">Enterprise Ready</h3>
            <p className="text-yellow-700">
              Business plan provides enterprise-grade features for large-scale marketing operations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingComparison;