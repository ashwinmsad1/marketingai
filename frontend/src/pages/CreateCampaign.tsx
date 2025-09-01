import React, { useState } from 'react';
import {
  Zap,
  TrendingUp,
  Target,
  Wand2,
  ArrowRight,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
  Camera,
  Video,
  Factory,
  Flame
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CampaignType {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  features: string[];
  estimatedTime: string;
  estimatedROI: string;
}

const CreateCampaign: React.FC = () => {
  const [step, setStep] = useState(1);
  const [selectedType, setSelectedType] = useState<string>('');
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    prompt: '',
    caption: '',
    industry: '',
    businessDetails: {
      business_name: '',
      signature_product: '',
      location: '',
      phone: ''
    },
    competitorUrl: '',
    competitorName: ''
  });

  const campaignTypes: CampaignType[] = [
    {
      id: 'quick',
      name: 'Quick Campaign',
      description: 'AI-generated content ready in 60 seconds',
      icon: <Zap className="w-8 h-8" />,
      color: 'bg-blue-100 text-blue-600',
      features: ['AI content creation', 'Auto-posting', 'Basic targeting'],
      estimatedTime: '60 seconds',
      estimatedROI: '200-400%'
    },
    {
      id: 'industry_optimized',
      name: 'Industry Template',
      description: 'Optimized campaigns for your specific industry',
      icon: <Factory className="w-8 h-8" />,
      color: 'bg-purple-100 text-purple-600',
      features: ['Industry templates', 'Conversion optimization', 'Best practices'],
      estimatedTime: '2 minutes',
      estimatedROI: '300-500%'
    },
    {
      id: 'viral',
      name: 'Viral Trends',
      description: 'Capitalize on trending topics for maximum reach',
      icon: <Flame className="w-8 h-8" />,
      color: 'bg-orange-100 text-orange-600',
      features: ['Trend detection', 'Viral optimization', 'Peak timing'],
      estimatedTime: '90 seconds',
      estimatedROI: '400-800%'
    },
    {
      id: 'competitor_beating',
      name: 'Beat Competitors',
      description: 'Analyze competitors and create superior campaigns',
      icon: <Target className="w-8 h-8" />,
      color: 'bg-red-100 text-red-600',
      features: ['Competitor analysis', 'Performance improvement', 'Market advantage'],
      estimatedTime: '3 minutes',
      estimatedROI: '350-600%'
    }
  ];

  const industries = [
    'Restaurant/Food', 'Real Estate', 'Fitness/Health', 'Beauty/Cosmetics',
    'Fashion/Retail', 'Automotive', 'Education', 'Healthcare',
    'Technology/SaaS', 'Professional Services', 'E-commerce', 'Other'
  ];

  const handleTypeSelect = (typeId: string) => {
    setSelectedType(typeId);
    setFormData({ ...formData, type: typeId });
    setStep(2);
  };

  const handleCreateCampaign = async () => {
    setIsCreating(true);
    
    // Simulate campaign creation
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setIsCreating(false);
    setStep(4); // Success step
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold">Create New Campaign</h1>
            <div className="flex items-center space-x-2">
              {[1, 2, 3, 4].map((num) => (
                <div
                  key={num}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    num < step 
                      ? 'bg-green-500 text-white' 
                      : num === step 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {num < step ? <CheckCircle className="w-4 h-4" /> : num}
                </div>
              ))}
            </div>
          </div>
          <div className="h-2 bg-gray-200 rounded-full">
            <div 
              className="h-2 bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${(step - 1) * 33.33}%` }}
            />
          </div>
        </div>

        <AnimatePresence mode="wait">
          {/* Step 1: Campaign Type Selection */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold mb-4">Choose Your Campaign Type</h2>
                <p className="text-gray-600">Select the type of campaign that best fits your goals</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {campaignTypes.map((type) => (
                  <motion.div
                    key={type.id}
                    whileHover={{ scale: 1.02, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleTypeSelect(type.id)}
                    className="card-hover cursor-pointer"
                  >
                    <div className={`w-16 h-16 ${type.color} rounded-xl flex items-center justify-center mb-6`}>
                      {type.icon}
                    </div>
                    
                    <h3 className="text-xl font-bold mb-2">{type.name}</h3>
                    <p className="text-gray-600 mb-4">{type.description}</p>
                    
                    <div className="space-y-2 mb-6">
                      {type.features.map((feature, index) => (
                        <div key={index} className="flex items-center text-sm text-gray-700">
                          <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                          {feature}
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex justify-between items-center text-sm text-gray-600 mb-4">
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {type.estimatedTime}
                      </div>
                      <div className="flex items-center">
                        <TrendingUp className="w-4 h-4 mr-1" />
                        {type.estimatedROI} ROI
                      </div>
                    </div>
                    
                    <button className="btn-primary w-full">
                      Select {type.name}
                    </button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Step 2: Campaign Details */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="card">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold mb-4">Campaign Details</h2>
                  <p className="text-gray-600">Tell us about your campaign to generate the best results</p>
                </div>

                <div className="space-y-6">
                  {/* Industry Selection (for industry_optimized type) */}
                  {selectedType === 'industry_optimized' && (
                    <div>
                      <label className="label">Industry</label>
                      <select 
                        className="input-field"
                        value={formData.industry}
                        onChange={(e) => setFormData({...formData, industry: e.target.value})}
                      >
                        <option value="">Select your industry</option>
                        {industries.map(industry => (
                          <option key={industry} value={industry.toLowerCase()}>
                            {industry}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Business Details (for industry_optimized) */}
                  {selectedType === 'industry_optimized' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="label">Business Name</label>
                        <input
                          type="text"
                          className="input-field"
                          placeholder="Your business name"
                          value={formData.businessDetails.business_name}
                          onChange={(e) => setFormData({
                            ...formData,
                            businessDetails: {...formData.businessDetails, business_name: e.target.value}
                          })}
                        />
                      </div>
                      <div>
                        <label className="label">Signature Product/Service</label>
                        <input
                          type="text"
                          className="input-field"
                          placeholder="What you're known for"
                          value={formData.businessDetails.signature_product}
                          onChange={(e) => setFormData({
                            ...formData,
                            businessDetails: {...formData.businessDetails, signature_product: e.target.value}
                          })}
                        />
                      </div>
                      <div>
                        <label className="label">Location</label>
                        <input
                          type="text"
                          className="input-field"
                          placeholder="City, State"
                          value={formData.businessDetails.location}
                          onChange={(e) => setFormData({
                            ...formData,
                            businessDetails: {...formData.businessDetails, location: e.target.value}
                          })}
                        />
                      </div>
                      <div>
                        <label className="label">Phone (optional)</label>
                        <input
                          type="text"
                          className="input-field"
                          placeholder="(555) 123-4567"
                          value={formData.businessDetails.phone}
                          onChange={(e) => setFormData({
                            ...formData,
                            businessDetails: {...formData.businessDetails, phone: e.target.value}
                          })}
                        />
                      </div>
                    </div>
                  )}

                  {/* Competitor Details (for competitor_beating) */}
                  {selectedType === 'competitor_beating' && (
                    <div className="space-y-4">
                      <div>
                        <label className="label">Competitor Name</label>
                        <input
                          type="text"
                          className="input-field"
                          placeholder="Name of competitor to analyze"
                          value={formData.competitorName}
                          onChange={(e) => setFormData({...formData, competitorName: e.target.value})}
                        />
                      </div>
                      <div>
                        <label className="label">Competitor Content URL</label>
                        <input
                          type="url"
                          className="input-field"
                          placeholder="https://facebook.com/competitor-post"
                          value={formData.competitorUrl}
                          onChange={(e) => setFormData({...formData, competitorUrl: e.target.value})}
                        />
                      </div>
                    </div>
                  )}

                  {/* Campaign Prompt (for quick and viral) */}
                  {(selectedType === 'quick' || selectedType === 'viral') && (
                    <div>
                      <label className="label">Campaign Prompt</label>
                      <textarea
                        className="input-field h-24"
                        placeholder="Describe what you want to promote..."
                        value={formData.prompt}
                        onChange={(e) => setFormData({...formData, prompt: e.target.value})}
                      />
                    </div>
                  )}

                  {/* Caption */}
                  <div>
                    <label className="label">Caption (optional)</label>
                    <textarea
                      className="input-field h-20"
                      placeholder="Social media caption (AI will optimize if left blank)"
                      value={formData.caption}
                      onChange={(e) => setFormData({...formData, caption: e.target.value})}
                    />
                  </div>

                  <div className="flex justify-between">
                    <button 
                      onClick={() => setStep(1)}
                      className="btn-secondary"
                    >
                      Back
                    </button>
                    <button 
                      onClick={() => setStep(3)}
                      className="btn-primary flex items-center"
                    >
                      Review Campaign
                      <ArrowRight className="ml-2 w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 3: Review & Create */}
          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="card">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold mb-4">Review Your Campaign</h2>
                  <p className="text-gray-600">Double-check your details before creating</p>
                </div>

                <div className="bg-gray-50 rounded-lg p-6 mb-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold mb-2">Campaign Type</h3>
                      <p className="text-gray-600 capitalize">{selectedType.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Industry</h3>
                      <p className="text-gray-600 capitalize">{formData.industry || 'General'}</p>
                    </div>
                    {formData.businessDetails.business_name && (
                      <div>
                        <h3 className="font-semibold mb-2">Business</h3>
                        <p className="text-gray-600">{formData.businessDetails.business_name}</p>
                      </div>
                    )}
                    {formData.prompt && (
                      <div className="md:col-span-2">
                        <h3 className="font-semibold mb-2">Prompt</h3>
                        <p className="text-gray-600">{formData.prompt}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-blue-50 rounded-lg p-6 mb-8">
                  <div className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-blue-600 mt-1 mr-3" />
                    <div>
                      <h3 className="font-semibold text-blue-900 mb-2">Performance Guarantee</h3>
                      <p className="text-blue-800 text-sm">
                        This campaign is backed by our performance guarantee. If it doesn't meet our 
                        performance standards, we'll optimize it automatically or provide a refund.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-between">
                  <button 
                    onClick={() => setStep(2)}
                    className="btn-secondary"
                  >
                    Back
                  </button>
                  <button 
                    onClick={handleCreateCampaign}
                    disabled={isCreating}
                    className="btn-success flex items-center"
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                        Creating Campaign...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 w-4 h-4" />
                        Create Campaign
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 4: Success */}
          {step === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <div className="card">
                <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-12 h-12 text-green-600" />
                </div>
                
                <h2 className="text-3xl font-bold mb-4">Campaign Created Successfully! 🎉</h2>
                <p className="text-xl text-gray-600 mb-8">
                  Your AI-powered campaign is now live and working to generate results
                </p>
                
                <div className="bg-gray-50 rounded-lg p-6 mb-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                    <div>
                      <div className="text-2xl font-bold text-blue-600 mb-2">Campaign #1247</div>
                      <div className="text-sm text-gray-600">Campaign ID</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-600 mb-2">Live</div>
                      <div className="text-sm text-gray-600">Status</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600 mb-2">2-24 hrs</div>
                      <div className="text-sm text-gray-600">First Results</div>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button 
                    onClick={() => {setStep(1); setFormData({} as any); setSelectedType('');}}
                    className="btn-secondary"
                  >
                    Create Another Campaign
                  </button>
                  <button className="btn-primary">
                    View Campaign Dashboard
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default CreateCampaign;