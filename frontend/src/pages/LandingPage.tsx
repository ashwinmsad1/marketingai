import React from 'react';
import { 
  Zap, 
  Target, 
  TrendingUp, 
  Shield, 
  ArrowRight, 
  Check, 
  Star,
  Play,
  Sparkles,
  Clock,
  DollarSign
} from 'lucide-react';
import { motion } from 'framer-motion';

const LandingPage: React.FC = () => {

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="gradient-hero text-white py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="inline-flex items-center bg-white/10 rounded-full px-6 py-2 mb-8">
              <Sparkles className="w-5 h-5 mr-2" />
              <span className="text-sm font-medium">From Idea to Profit in 60 Seconds</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              AI Marketing
              <br />
              <span className="text-yellow-300">Automation</span>
            </h1>
            
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed opacity-90">
              Turn any idea into viral content and profitable campaigns. 
              No design skills, no ad expertise needed. Just results.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-yellow-400 text-gray-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-colors flex items-center"
              >
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5" />
              </motion.button>
              
              <button 
                onClick={() => {}}
                className="bg-white/20 backdrop-blur-sm px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/30 transition-colors flex items-center"
              >
                <Play className="mr-2 w-5 h-5" />
                Watch Demo
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Clock className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold mb-2">60-Second Setup</h3>
                <p className="opacity-90">From idea to live campaign in under a minute</p>
              </div>
              
              <div className="text-center">
                <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold mb-2">300% ROI Guarantee</h3>
                <p className="opacity-90">We guarantee results or your money back</p>
              </div>
              
              <div className="text-center">
                <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Shield className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold mb-2">Performance Guarantees</h3>
                <p className="opacity-90">Auto-optimization ensures success</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Why Choose AI Marketing Automation?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Join thousands of businesses already using AI to 10x their marketing results
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-20">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h3 className="text-3xl font-bold mb-6">Traditional Marketing vs AI Automation</h3>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <div className="bg-red-100 rounded-full p-1 mr-4 mt-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Traditional Marketing</p>
                    <p className="text-gray-600">Weeks to create campaigns, expensive agencies, no guarantees</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="bg-green-100 rounded-full p-1 mr-4 mt-1">
                    <Check className="w-3 h-3 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">AI Automation</p>
                    <p className="text-gray-600">60-second campaigns, performance guarantees, 10x ROI</p>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-2">2x</div>
                  <div className="text-sm text-gray-600">More Leads</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">50%</div>
                  <div className="text-sm text-gray-600">Higher CTR</div>
                </div>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="bg-gradient-to-br from-blue-50 to-purple-50 p-8 rounded-2xl"
            >
              <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Check className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <h4 className="font-bold">Campaign Created</h4>
                    <p className="text-sm text-gray-600">AI-generated content ready</p>
                  </div>
                </div>
                <div className="h-2 bg-gray-200 rounded-full">
                  <div className="h-2 bg-green-500 rounded-full" style={{ width: '100%' }}></div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-bold">Live Results</h4>
                  <span className="badge-success">Active</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-2xl font-bold text-green-600">127</div>
                    <div className="text-sm text-gray-600">New Customers</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">485%</div>
                    <div className="text-sm text-gray-600">ROI</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6">Powerful Features That Deliver Results</h2>
            <p className="text-xl text-gray-600">Everything you need to dominate your market</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Zap className="w-8 h-8" />,
                title: "Industry Templates",
                description: "10+ vertical-specific templates optimized for maximum conversion",
                color: "bg-yellow-100 text-yellow-600"
              },
              {
                icon: <Target className="w-8 h-8" />,
                title: "Competitor Analysis",
                description: "AI analyzes competitors and creates better-performing versions",
                color: "bg-red-100 text-red-600"
              },
              {
                icon: <TrendingUp className="w-8 h-8" />,
                title: "Viral Trend Detection",
                description: "Automatically creates campaigns from trending topics",
                color: "bg-green-100 text-green-600"
              },
              {
                icon: <Shield className="w-8 h-8" />,
                title: "Performance Guarantees",
                description: "Auto-optimization ensures campaigns meet performance targets",
                color: "bg-blue-100 text-blue-600"
              },
              {
                icon: <DollarSign className="w-8 h-8" />,
                title: "ROI Tracking",
                description: "Track every lead and sale back to specific AI-generated content",
                color: "bg-purple-100 text-purple-600"
              },
              {
                icon: <Star className="w-8 h-8" />,
                title: "Success Dashboard",
                description: "Complete analytics showing exactly how much revenue each campaign generates",
                color: "bg-orange-100 text-orange-600"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className={`w-16 h-16 ${feature.color} rounded-xl flex items-center justify-center mb-6`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6">Simple, Value-Based Pricing</h2>
            <p className="text-xl text-gray-600">Pay based on the value you get, not hours worked</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: "Starter",
                price: "$49.99",
                promise: "Get 100 new leads per month",
                description: "Perfect for local businesses",
                features: [
                  "10 AI campaigns per month",
                  "Industry-specific templates", 
                  "Basic performance tracking",
                  "Email support",
                  "Performance guarantees"
                ]
              },
              {
                name: "Professional",
                price: "$149.99",
                promise: "Increase sales by 300%",
                description: "Ideal for growing businesses",
                features: [
                  "50 AI campaigns per month",
                  "A/B testing & optimization",
                  "Revenue attribution tracking",
                  "Competitor analysis",
                  "Priority support",
                  "Viral trend campaigns"
                ],
                popular: true
              },
              {
                name: "Enterprise",
                price: "$399.99",
                promise: "Scale to $1M+ attributed revenue",
                description: "For agencies & large brands",
                features: [
                  "Unlimited campaigns",
                  "White-label platform",
                  "Custom industry templates",
                  "Dedicated success manager",
                  "API access",
                  "Custom integrations"
                ]
              }
            ].map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`card relative ${plan.popular ? 'ring-2 ring-primary-500' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary-500 text-white px-4 py-2 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold mb-2">{plan.price}</div>
                  <div className="text-sm text-gray-600 mb-4">/month</div>
                  <div className="text-primary-600 font-semibold mb-4">{plan.promise}</div>
                  <p className="text-gray-600">{plan.description}</p>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-center">
                      <Check className="w-5 h-5 text-green-500 mr-3" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <button className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                  plan.popular 
                    ? 'btn-primary' 
                    : 'btn-secondary'
                }`}>
                  Start {plan.name}
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="gradient-hero text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to 10x Your Marketing Results?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of businesses using AI to generate more leads, sales, and revenue
            </p>
            <button className="bg-yellow-400 text-gray-900 px-12 py-4 rounded-lg font-bold text-xl hover:bg-yellow-300 transition-colors">
              Start Your Free Trial Today
            </button>
            <p className="text-sm mt-4 opacity-75">14-day free trial • No credit card required • Cancel anytime</p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;