import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, TrendingUp, Shield, Star } from 'lucide-react';
import { PRICING_TIERS, FEATURE_LABELS, TIER_COLORS, TIER_BADGES, formatCurrency, calculateSavingsPercentage } from '../constants/pricing';
import { SubscriptionTier } from '../types';
import PricingCard from '../components/Pricing/PricingCard';
import PricingToggle from '../components/Pricing/PricingToggle';
import PricingFAQ from '../components/Pricing/PricingFAQ';
import PricingComparison from '../components/Pricing/PricingComparison';

interface PricingPageProps {
  currentTier?: SubscriptionTier;
  onUpgrade?: (tier: SubscriptionTier, billingCycle: 'monthly' | 'annual') => void;
}

const PricingPage: React.FC<PricingPageProps> = ({ currentTier, onUpgrade }) => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [showComparison, setShowComparison] = useState(false);

  const handleUpgrade = (tier: SubscriptionTier) => {
    if (onUpgrade) {
      onUpgrade(tier, billingCycle);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      {/* Hero Section */}
      <div className="pt-16 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Choose Your{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Growth Plan
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Unlock the power of AI-driven marketing automation designed specifically for Indian businesses. 
              Scale your campaigns, generate stunning content, and grow your revenue with confidence.
            </p>
          </motion.div>

          {/* Value Propositions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto"
          >
            <div className="flex items-center justify-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Zap className="h-6 w-6 text-blue-600" />
              <span className="text-gray-700 font-medium">AI-Powered Campaigns</span>
            </div>
            <div className="flex items-center justify-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <TrendingUp className="h-6 w-6 text-green-600" />
              <span className="text-gray-700 font-medium">Guaranteed ROI</span>
            </div>
            <div className="flex items-center justify-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Shield className="h-6 w-6 text-purple-600" />
              <span className="text-gray-700 font-medium">Enterprise Security</span>
            </div>
          </motion.div>

          {/* Billing Toggle */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mb-12"
          >
            <PricingToggle
              billingCycle={billingCycle}
              onToggle={setBillingCycle}
              savings={calculateSavingsPercentage(PRICING_TIERS.basic.price_monthly, PRICING_TIERS.basic.price_annual)}
            />
          </motion.div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="px-4 sm:px-6 lg:px-8 pb-16">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {(Object.keys(PRICING_TIERS) as SubscriptionTier[]).map((tier, index) => (
              <motion.div
                key={tier}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
              >
                <PricingCard
                  tier={tier}
                  config={PRICING_TIERS[tier]}
                  billingCycle={billingCycle}
                  isCurrentTier={currentTier === tier}
                  isPopular={tier === 'basic'}
                  onUpgrade={() => handleUpgrade(tier)}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Comparison Toggle */}
      <div className="px-4 sm:px-6 lg:px-8 pb-8">
        <div className="max-w-7xl mx-auto text-center">
          <button
            onClick={() => setShowComparison(!showComparison)}
            className="inline-flex items-center px-6 py-3 border border-gray-300 shadow-sm text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {showComparison ? 'Hide' : 'Show'} Detailed Comparison
          </button>
        </div>
      </div>

      {/* Features Comparison Table */}
      {showComparison && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.5 }}
        >
          <PricingComparison />
        </motion.div>
      )}

      {/* Success Stories Section */}
      <div className="bg-gray-50 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Trusted by Growing Indian Businesses
            </h2>
            <p className="text-lg text-gray-600">
              Join thousands of businesses already scaling with our AI marketing platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                company: "TechStart Mumbai",
                industry: "SaaS",
                result: "300% ROI increase",
                quote: "The AI campaigns generated leads we never thought possible for our B2B SaaS."
              },
              {
                company: "Fashion Forward Delhi",
                industry: "E-commerce",
                result: "250% sales growth",
                quote: "Our Instagram campaigns now convert 5x better with AI-generated content."
              },
              {
                company: "Local Eats Bangalore",
                industry: "Food & Beverage",
                result: "150% customer acquisition",
                quote: "We went from 50 to 400 daily orders using targeted AI marketing campaigns."
              }
            ].map((story, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                className="bg-white p-6 rounded-lg shadow-sm"
              >
                <div className="flex items-center mb-4">
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                </div>
                <p className="text-gray-600 mb-4 italic">"{story.quote}"</p>
                <div className="border-t pt-4">
                  <p className="font-semibold text-gray-900">{story.company}</p>
                  <p className="text-sm text-gray-500">{story.industry} • {story.result}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <PricingFAQ />

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Scale Your Marketing?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of Indian businesses growing with AI-powered marketing automation
          </p>
          <div className="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
            <button
              onClick={() => handleUpgrade('basic')}
              className="w-full sm:w-auto bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold shadow-lg hover:bg-gray-50 transition-colors"
            >
              Start with Basic Plan
            </button>
            <button className="w-full sm:w-auto border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              Book a Demo
            </button>
          </div>
          <p className="text-sm text-blue-100 mt-4">
            No setup fees • Cancel anytime • 24/7 support
          </p>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;