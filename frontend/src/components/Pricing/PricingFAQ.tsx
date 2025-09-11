import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
}

const PricingFAQ: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs: FAQItem[] = [
    {
      question: "What happens when I reach my usage limits?",
      answer: "When you approach your limits (at 75%, 90%, and 95%), you'll receive notifications to upgrade. Once you hit 100%, you'll need to upgrade to continue using the service for that billing cycle."
    },
    {
      question: "Can I change my plan anytime?",
      answer: "Yes! You can upgrade your plan instantly. When upgrading, you'll be charged the prorated difference for the current billing cycle. Downgrades take effect at the next billing cycle."
    },
    {
      question: "What payment methods do you accept?",
      answer: "We accept all major credit cards (Visa, MasterCard, American Express), UPI payments, and bank transfers for Indian businesses. All payments are processed securely through our payment partners."
    },
    {
      question: "Is there a setup fee or contract?",
      answer: "No setup fees! No long-term contracts required. You can cancel anytime and only pay for what you use. Annual plans offer significant savings with the flexibility to cancel."
    },
    {
      question: "How does AI generation counting work?",
      answer: "Each AI-generated image or video counts as one generation. This includes campaign creatives, social media posts, and any content created through our AI tools. Regenerating or creating variations also counts towards your limit."
    },
    {
      question: "What is Ad Spend Monitoring?",
      answer: "This is the total amount of advertising budget our platform can monitor and optimize across all your Meta (Facebook/Instagram) campaigns. It's not an additional cost - it's the limit on ad spend we'll track for optimization."
    },
    {
      question: "Do you offer refunds?",
      answer: "We offer a 30-day money-back guarantee for first-time subscribers. If you're not satisfied within the first 30 days, we'll provide a full refund, no questions asked."
    },
    {
      question: "Can I get a custom plan for enterprise needs?",
      answer: "Absolutely! If you have specific requirements that don't fit our standard plans, contact our sales team. We offer custom enterprise solutions with dedicated support, custom integrations, and volume discounts."
    },
    {
      question: "How does billing work for annual plans?",
      answer: "Annual plans are billed upfront for the entire year and offer significant savings (up to 17% off). Your usage limits reset monthly, but your billing is annual. You can upgrade during the year with prorated pricing."
    },
    {
      question: "What happens to my data if I cancel?",
      answer: "Your data remains accessible for 90 days after cancellation. You can export your campaigns, analytics, and generated content during this period. After 90 days, data is permanently deleted as per our privacy policy."
    }
  ];

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="bg-gray-50 py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-gray-600">
            Everything you need to know about our pricing and plans
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="bg-white rounded-lg shadow-sm overflow-hidden"
            >
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors"
              >
                <span className="text-lg font-medium text-gray-900">
                  {faq.question}
                </span>
                {openIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              <AnimatePresence>
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-4">
                      <p className="text-gray-600 leading-relaxed">
                        {faq.answer}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Contact Support */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            Still have questions? We're here to help!
          </p>
          <div className="space-y-2 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
            <button className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
              Contact Sales
            </button>
            <button className="w-full sm:w-auto border border-gray-300 hover:border-gray-400 text-gray-700 px-6 py-3 rounded-lg font-medium transition-colors">
              Email Support
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingFAQ;