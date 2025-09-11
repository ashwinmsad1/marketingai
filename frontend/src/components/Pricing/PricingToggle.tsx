import React from 'react';
import { motion } from 'framer-motion';

interface PricingToggleProps {
  billingCycle: 'monthly' | 'annual';
  onToggle: (cycle: 'monthly' | 'annual') => void;
  savings: number;
}

const PricingToggle: React.FC<PricingToggleProps> = ({
  billingCycle,
  onToggle,
  savings
}) => {
  return (
    <div className="flex items-center justify-center space-x-4">
      <span className={`text-lg font-medium ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
        Monthly
      </span>
      
      <div className="relative">
        <motion.button
          onClick={() => onToggle(billingCycle === 'monthly' ? 'annual' : 'monthly')}
          className="relative inline-flex h-8 w-16 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          animate={{
            backgroundColor: billingCycle === 'annual' ? '#3B82F6' : '#E5E7EB'
          }}
          transition={{ duration: 0.2 }}
        >
          <motion.span
            className="inline-block h-6 w-6 rounded-full bg-white shadow-lg transform transition-transform"
            animate={{
              translateX: billingCycle === 'annual' ? '32px' : '4px'
            }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
          />
        </motion.button>
      </div>
      
      <div className="flex items-center space-x-2">
        <span className={`text-lg font-medium ${billingCycle === 'annual' ? 'text-gray-900' : 'text-gray-500'}`}>
          Annual
        </span>
        {savings > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
          >
            Save {savings}%
          </motion.span>
        )}
      </div>
    </div>
  );
};

export default PricingToggle;