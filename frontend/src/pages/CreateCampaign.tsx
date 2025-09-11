import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Zap,
  TrendingUp,
  ArrowRight,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
  Factory,
  Flame,
  Brain,
  Users,
  BarChart3,
  Star,
  Eye,
  Lightbulb
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { personalizationService, campaignService } from '../services/api';
import { MetaUserProfile, CampaignRecommendation, CampaignStrategy } from '../types';

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
  const location = useLocation();
  const [step, setStep] = useState(1);
  const [selectedType, setSelectedType] = useState<string>('');
  const [isCreating, setIsCreating] = useState(false);
  const [userProfile, setUserProfile] = useState<MetaUserProfile | null>(null);
  const [aiRecommendations, setAiRecommendations] = useState<CampaignRecommendation[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<CampaignStrategy | null>(null);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [showPersonalizationOptions, setShowPersonalizationOptions] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    prompt: '',
    caption: '',
    style: '',
    aspectRatio: '16:9',
    imageFormat: 'social_media',
    businessDescription: '',
    targetAudience: '',
    campaignGoal: '',
    selectedMetaAccount: '',
    budget: {
      daily: 50,
      total: 500
    },
    targeting: {
      age_min: 18,
      age_max: 65,
      interests: [] as string[],
      locations: [] as string[]
    },
    platforms: {
      facebook: true,
      instagram: true
    },
    userContext: {
      business_description: '',
      target_audience_description: '',
      unique_value_proposition: ''
    }
  });


  // Load data from navigation state (from strategy wizard or templates)
  useEffect(() => {
    if (location.state) {
      const { strategy, generatedContent } = location.state as any;
      if (strategy) {
        setSelectedStrategy(strategy);
        setSelectedType('personalized');
        setStep(2);
      }
      if (generatedContent) {
        // Handle content from templates
        setFormData(prev => ({
          ...prev,
          prompt: generatedContent.headline || '',
          caption: generatedContent.description || ''
        }));
        setSelectedType('personalized');
        setStep(2);
      }
    }
    
    loadPersonalizationData();
  }, [location.state]);

  const loadPersonalizationData = async () => {
    try {
      const [profile, recommendations] = await Promise.all([
        personalizationService.getProfile().catch(() => null),
        personalizationService.getRecommendations().catch(() => [])
      ]);
      
      setUserProfile(profile);
      setAiRecommendations(recommendations || []);
    } catch (error) {
      console.error('Error loading personalization data:', error);
    }
  };

  const campaignTypes: CampaignType[] = [
    {
      id: 'personalized',
      name: 'AI Personalized',
      description: 'Campaigns tailored to your business profile and audience',
      icon: <Brain className="w-8 h-8" />,
      color: 'bg-indigo-100 text-indigo-600',
      features: ['Profile-based targeting', 'AI recommendations', 'Performance optimization'],
      estimatedTime: '3-5 minutes',
      estimatedROI: '500-900%'
    },
    {
      id: 'quick',
      name: 'Quick Campaign',
      description: 'AI-generated content ready in a few minutes',
      icon: <Zap className="w-8 h-8" />,
      color: 'bg-blue-100 text-blue-600',
      features: ['AI content creation', 'Auto-posting', 'Basic targeting'],
      estimatedTime: '2-3 minutes',
      estimatedROI: '200-400%'
    },
    {
      id: 'custom',
      name: 'Custom Campaign',
      description: 'Create campaigns based on your specific business needs',
      icon: <Factory className="w-8 h-8" />,
      color: 'bg-purple-100 text-purple-600',
      features: ['Custom targeting', 'Tailored messaging', 'Personalized content'],
      estimatedTime: '3-5 minutes',
      estimatedROI: '300-500%'
    },
    {
      id: 'viral',
      name: 'Viral Trends',
      description: 'Capitalize on trending topics for maximum reach',
      icon: <Flame className="w-8 h-8" />,
      color: 'bg-orange-100 text-orange-600',
      features: ['Trend detection', 'Viral optimization', 'Peak timing'],
      estimatedTime: '3-5 minutes',
      estimatedROI: '400-800%'
    },
    {
      id: 'video',
      name: 'AI Video Ads',
      description: 'Generate professional video advertisements using AI',
      icon: <Eye className="w-8 h-8" />,
      color: 'bg-green-100 text-green-600',
      features: ['AI video generation', 'Multiple formats', 'Professional quality'],
      estimatedTime: '2 minutes',
      estimatedROI: '350-700%'
    }
  ];

  // Removed industries array - now using user input approach

  const handleTypeSelect = (typeId: string) => {
    setSelectedType(typeId);
    setFormData({ ...formData, type: typeId });
    setStep(2);
  };

  const loadAIRecommendations = async () => {
    if (!userProfile) return;
    
    setIsLoadingRecommendations(true);
    try {
      const recommendations = await personalizationService.getRecommendations(userProfile.user_id);
      setAiRecommendations(recommendations.filter((r: any) => r.type === 'new_campaign').slice(0, 3));
    } catch (error) {
      console.error('Error loading AI recommendations:', error);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const applyRecommendation = (recommendation: CampaignRecommendation) => {
    setFormData(prev => ({
      ...prev,
      type: 'personalized',
      prompt: recommendation.title,
      caption: recommendation.description,
      ...recommendation.campaign_config
    }));
    setSelectedType('personalized');
    setStep(2);
  };

  const handleCreateCampaign = async () => {
    setIsCreating(true);
    
    try {
      // Validate custom campaign fields
      if (selectedType === 'custom') {
        if (!formData.businessDescription || !formData.targetAudience || !formData.campaignGoal) {
          toast.error('Please fill in all custom campaign fields: business description, target audience, and campaign goal.');
          setIsCreating(false);
          return;
        }
      }
      
      // Validate required user context for personalized campaigns
      if (selectedType === 'video' || selectedType === 'personalized' || selectedType === 'viral' || selectedType === 'quick') {
        const { business_description, target_audience_description, unique_value_proposition } = formData.userContext;
        
        if (!business_description || !target_audience_description || !unique_value_proposition) {
          toast.error('Please fill in all campaign context fields for better personalization.');
          setIsCreating(false);
          return;
        }
      }

      // Validate platform selection - at least one platform must be selected
      if (!formData.platforms.facebook && !formData.platforms.instagram) {
        toast.error('Please select at least one platform (Facebook or Instagram) for your campaign.');
        setIsCreating(false);
        return;
      }

      const campaignData = {
        ...formData,
        user_id: userProfile?.user_id,
        strategy_id: selectedStrategy?.strategy_id
      };
      
      // For video campaigns, generate video strategy first
      if (selectedType === 'video' && userProfile?.user_id) {
        const videoStrategy = await personalizationService.generateVideoStrategy({
          user_id: userProfile.user_id,
          campaign_brief: formData.prompt,
          business_description: formData.userContext.business_description,
          target_audience_description: formData.userContext.target_audience_description,
          unique_value_proposition: formData.userContext.unique_value_proposition,
          preferred_style: formData.style,
          aspect_ratios: [formData.aspectRatio]
        });
        
        // Include video strategy in campaign data
        (campaignData as any).video_strategy = videoStrategy;
      }
      
      // For image campaigns (quick, personalized), generate image strategy first
      if ((selectedType === 'quick' || selectedType === 'personalized') && userProfile?.user_id) {
        const imageStrategy = await personalizationService.generateImageStrategy({
          user_id: userProfile.user_id,
          campaign_brief: formData.prompt,
          business_description: formData.userContext.business_description,
          target_audience_description: formData.userContext.target_audience_description,
          unique_value_proposition: formData.userContext.unique_value_proposition,
          preferred_style: formData.style || 'professional',
          image_format: formData.imageFormat || 'social_media'
        });
        
        // Include image strategy in campaign data
        (campaignData as any).image_strategy = imageStrategy;
      }
      
      const finalCampaignData = {
        ...campaignData,
        name: `${selectedType} Campaign - ${new Date().toLocaleDateString()}`,
        type: selectedType,
        // Include custom campaign fields for API
        ...(selectedType === 'custom' && {
          business_description: formData.businessDescription,
          target_audience: formData.targetAudience,
          campaign_goal: formData.campaignGoal
        })
      };

      if (selectedType === 'personalized' || selectedType === 'video' || selectedType === 'quick' || selectedType === 'custom') {
        await personalizationService.createPersonalizedCampaign(finalCampaignData);
      } else {
        await campaignService.createCampaign(finalCampaignData);
      }
      
      toast.success('Campaign created successfully!');
      setStep(4);
    } catch (error: any) {
      console.error('Error creating campaign:', error);
      toast.error(error.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
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

              <div className="space-y-6">
                {/* AI Recommendations Section */}
                {aiRecommendations.length > 0 && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                    <div className="flex items-center space-x-2 mb-4">
                      <Brain className="w-6 h-6 text-blue-600" />
                      <h3 className="text-lg font-semibold text-blue-900">AI Recommendations</h3>
                      <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded-full font-medium">
                        Personalized for you
                      </span>
                    </div>
                    <p className="text-blue-700 text-sm mb-4">
                      Based on your profile and performance data, here are campaigns we recommend:
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {aiRecommendations.slice(0, 3).map((rec) => (
                        <motion.div
                          key={rec.recommendation_id}
                          whileHover={{ scale: 1.02 }}
                          className="bg-white p-4 rounded-lg border border-blue-200 cursor-pointer"
                          onClick={() => applyRecommendation(rec)}
                        >
                          <div className="flex items-center space-x-2 mb-2">
                            <Star className="w-4 h-4 text-yellow-500" />
                            <span className={`px-2 py-1 text-xs rounded ${
                              rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                              rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {rec.priority.toUpperCase()}
                            </span>
                          </div>
                          <h4 className="font-medium text-gray-900 mb-1 text-sm">{rec.title}</h4>
                          <p className="text-gray-600 text-xs mb-3 line-clamp-2">{rec.description}</p>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-green-600 font-medium">
                              +{rec.predicted_impact.estimated_change}% {rec.predicted_impact.metric}
                            </span>
                            <span className="text-blue-600">
                              {rec.predicted_impact.confidence}% confidence
                            </span>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Campaign Types Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {campaignTypes.map((type) => {
                    const isRecommended = type.id === 'personalized' && userProfile;
                    return (
                      <motion.div
                        key={type.id}
                        whileHover={{ scale: 1.02, y: -4 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleTypeSelect(type.id)}
                        className={`card-hover cursor-pointer relative ${
                          isRecommended ? 'ring-2 ring-indigo-300' : ''
                        }`}
                      >
                        {isRecommended && (
                          <div className="absolute -top-2 -right-2 bg-indigo-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                            Recommended
                          </div>
                        )}
                        
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
                        
                        <button className={`btn-primary w-full ${
                          isRecommended ? 'bg-indigo-600 hover:bg-indigo-700' : ''
                        }`}>
                          Select {type.name}
                        </button>
                      </motion.div>
                    );
                  })}
                </div>
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
                  {/* Profile-based Pre-fill for Personalized Campaigns */}
                  {selectedType === 'personalized' && userProfile && (
                    <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                      <div className="flex items-center space-x-2 mb-3">
                        <Users className="w-5 h-5 text-indigo-600" />
                        <h3 className="font-semibold text-indigo-900">Using Your Business Profile</h3>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-indigo-700 font-medium">Business:</span>
                          <span className="text-indigo-600 ml-2">{userProfile.business_name}</span>
                        </div>
                        <div>
                          <span className="text-indigo-700 font-medium">Industry:</span>
                          <span className="text-indigo-600 ml-2">{userProfile.industry}</span>
                        </div>
                        <div className="md:col-span-2">
                          <span className="text-indigo-700 font-medium">Target Audience:</span>
                          <span className="text-indigo-600 ml-2">{userProfile.target_audience.slice(0, 100)}...</span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setShowPersonalizationOptions(!showPersonalizationOptions)}
                        className="mt-3 text-indigo-600 text-sm hover:text-indigo-800 flex items-center space-x-1"
                      >
                        <Eye className="w-4 h-4" />
                        <span>{showPersonalizationOptions ? 'Hide' : 'Show'} Personalization Options</span>
                      </button>
                    </div>
                  )}

                  {/* Strategy Preview */}
                  {selectedStrategy && (
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <div className="flex items-center space-x-2 mb-3">
                        <BarChart3 className="w-5 h-5 text-green-600" />
                        <h3 className="font-semibold text-green-900">Using Strategy: {selectedStrategy.strategy_type}</h3>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-green-700">
                        <div>Expected CTR: {(selectedStrategy.expected_performance.expected_ctr * 100).toFixed(2)}%</div>
                        <div>Estimated Reach: {selectedStrategy.expected_performance.estimated_reach.toLocaleString()}</div>
                      </div>
                    </div>
                  )}

                  {/* Personalization Options (expandable) */}
                  {selectedType === 'personalized' && showPersonalizationOptions && userProfile && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="border border-indigo-200 rounded-lg p-4 bg-indigo-50"
                    >
                      <h4 className="font-semibold text-indigo-900 mb-4">Personalization Settings</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-indigo-700 mb-1">Brand Voice</label>
                          <select className="w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                            <option value={userProfile.brand_voice}>{userProfile.brand_voice} (from profile)</option>
                            <option value="professional">Professional</option>
                            <option value="friendly">Friendly</option>
                            <option value="bold">Bold</option>
                            <option value="playful">Playful</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-indigo-700 mb-1">Primary Goal</label>
                          <select className="w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                            {userProfile.primary_goals.map(goal => (
                              <option key={goal} value={goal}>{goal}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-indigo-700 mb-1">Content Type Preference</label>
                          <select className="w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                            {userProfile.preferred_content_types?.map(type => (
                              <option key={type} value={type}>{type}</option>
                            )) || <option value="image">Image</option>}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-indigo-700 mb-1">Performance Priority</label>
                          <select className="w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                            {userProfile.performance_priorities?.map(priority => (
                              <option key={priority} value={priority}>{priority}</option>
                            )) || <option value="conversions">Conversions</option>}
                          </select>
                        </div>
                      </div>
                    </motion.div>
                  )}
                  {/* Business Information */}
                  {(selectedType === 'custom' || selectedType === 'personalized') && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      <div>
                        <label className="label">
                          Business Description
                          <span className="text-red-500">*</span>
                        </label>
                        <textarea
                          value={formData.businessDescription}
                          onChange={(e) => updateFormData({ businessDescription: e.target.value })}
                          className="input min-h-[80px]"
                          placeholder="Describe your business, products/services, and what makes you unique..."
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="label">
                          Target Audience
                          <span className="text-red-500">*</span>
                        </label>
                        <textarea
                          value={formData.targetAudience}
                          onChange={(e) => updateFormData({ targetAudience: e.target.value })}
                          className="input min-h-[60px]"
                          placeholder="Who are your ideal customers? (age group, interests, demographics...)"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="label">
                          Campaign Goal
                          <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={formData.campaignGoal}
                          onChange={(e) => updateFormData({ campaignGoal: e.target.value })}
                          className="input"
                          required
                        >
                          <option value="">Select campaign goal...</option>
                          <option value="brand_awareness">Brand Awareness</option>
                          <option value="lead_generation">Lead Generation</option>
                          <option value="website_traffic">Website Traffic</option>
                          <option value="sales_conversions">Sales & Conversions</option>
                          <option value="engagement">Social Media Engagement</option>
                          <option value="app_installs">App Installs</option>
                        </select>
                      </div>
                    </motion.div>
                  )}


                  {/* Campaign Prompt (for quick, viral, video, personalized, and custom) */}
                  {(selectedType === 'quick' || selectedType === 'viral' || selectedType === 'video' || selectedType === 'personalized' || selectedType === 'custom') && (
                    <div>
                      <label className="label">
                        Campaign Prompt
                        {selectedType === 'personalized' && userProfile && (
                          <span className="text-indigo-600 text-sm font-normal ml-2">
                            (AI will personalize based on your profile)
                          </span>
                        )}
                      </label>
                      <textarea
                        className="input-field h-24"
                        placeholder={selectedType === 'personalized' && userProfile 
                          ? `Describe your campaign. AI will personalize for ${userProfile.business_name} in ${userProfile.industry}...`
                          : "Describe what you want to promote..."
                        }
                        value={formData.prompt}
                        onChange={(e) => setFormData({...formData, prompt: e.target.value})}
                      />
                      {selectedType === 'personalized' && (
                        <button
                          type="button"
                          onClick={loadAIRecommendations}
                          disabled={isLoadingRecommendations}
                          className="mt-2 flex items-center space-x-2 text-indigo-600 hover:text-indigo-800 text-sm"
                        >
                          {isLoadingRecommendations ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Lightbulb className="w-4 h-4" />
                          )}
                          <span>Get AI Suggestions</span>
                        </button>
                      )}
                    </div>
                  )}

                  {/* Caption */}
                  <div>
                    <label className="label">
                      Caption (optional)
                      {selectedType === 'personalized' && userProfile && (
                        <span className="text-indigo-600 text-sm font-normal ml-2">
                          (Will match your brand voice: {userProfile.brand_voice})
                        </span>
                      )}
                    </label>
                    <textarea
                      className="input-field h-20"
                      placeholder={selectedType === 'personalized' && userProfile
                        ? `AI will create a ${userProfile.brand_voice.toLowerCase()} caption for ${userProfile.business_name}...`
                        : "Social media caption (AI will optimize if left blank)"
                      }
                      value={formData.caption}
                      onChange={(e) => setFormData({...formData, caption: e.target.value})}
                    />
                  </div>

                  {/* Video-specific options */}
                  {selectedType === 'video' && (
                    <div className="space-y-4 bg-green-50 p-4 rounded-lg border border-green-200">
                      <h4 className="font-medium text-green-800 flex items-center">
                        <Eye className="w-4 h-4 mr-2" />
                        Video Settings
                      </h4>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="label">Video Style</label>
                          <select
                            className="input-field"
                            value={formData.style || 'marketing commercial'}
                            onChange={(e) => setFormData({...formData, style: e.target.value})}
                          >
                            <option value="marketing commercial">Marketing Commercial</option>
                            <option value="cinematic">Cinematic</option>
                            <option value="luxury commercial">Luxury Commercial</option>
                            <option value="corporate">Corporate</option>
                            <option value="lifestyle">Lifestyle</option>
                            <option value="product showcase">Product Showcase</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="label">Aspect Ratio</label>
                          <select
                            className="input-field"
                            value={formData.aspectRatio || '16:9'}
                            onChange={(e) => setFormData({...formData, aspectRatio: e.target.value})}
                          >
                            <option value="16:9">16:9 (Landscape - Facebook)</option>
                            <option value="1:1">1:1 (Square - Instagram Feed)</option>
                            <option value="9:16">9:16 (Vertical - Instagram Stories)</option>
                          </select>
                        </div>
                      </div>
                      
                      <div className="text-sm text-green-700 bg-green-100 p-3 rounded-md">
                        <div className="flex items-start space-x-2">
                          <Clock className="w-4 h-4 mt-0.5" />
                          <div>
                            <p className="font-medium">Video Generation Info:</p>
                            <ul className="mt-1 space-y-1 text-xs">
                              <li>• Fixed 8-second duration (perfect for social media ads)</li>
                              <li>• High-quality AI generation using Google Veo 3.0</li>
                              <li>• Professional commercial-grade output</li>
                              <li>• Auto-posted to selected social platforms</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Image-specific options */}
                  {(selectedType === 'quick' || selectedType === 'personalized') && (
                    <div className="space-y-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <h4 className="font-medium text-blue-800 flex items-center">
                        <Sparkles className="w-4 h-4 mr-2" />
                        Image Settings
                      </h4>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="label">Image Style</label>
                          <select
                            className="input-field"
                            value={formData.style || 'professional'}
                            onChange={(e) => setFormData({...formData, style: e.target.value})}
                          >
                            <option value="professional">Professional</option>
                            <option value="modern">Modern</option>
                            <option value="creative">Creative</option>
                            <option value="minimalist">Minimalist</option>
                            <option value="vibrant">Vibrant</option>
                            <option value="corporate">Corporate</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="label">Image Format</label>
                          <select
                            className="input-field"
                            value={formData.imageFormat || 'social_media'}
                            onChange={(e) => setFormData({...formData, imageFormat: e.target.value})}
                          >
                            <option value="social_media">Social Media (1:1, 16:9)</option>
                            <option value="instagram_story">Instagram Stories (9:16)</option>
                            <option value="facebook_cover">Facebook Cover (16:9)</option>
                            <option value="poster">Print Poster (2:3, 3:4)</option>
                            <option value="banner">Web Banner (5:1)</option>
                          </select>
                        </div>
                      </div>
                      
                      <div className="text-sm text-blue-700 bg-blue-100 p-3 rounded-md">
                        <div className="flex items-start space-x-2">
                          <Clock className="w-4 h-4 mt-0.5" />
                          <div>
                            <p className="font-medium">Image Generation Info:</p>
                            <ul className="mt-1 space-y-1 text-xs">
                              <li>• High-resolution AI-generated images (1024x1024+)</li>
                              <li>• Professional quality optimized for your industry</li>
                              <li>• Platform-specific formatting and dimensions</li>
                              <li>• Generated in 1-2 minutes</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* User Context Fields for Better Personalization */}
                  {(selectedType === 'video' || selectedType === 'personalized' || selectedType === 'viral' || selectedType === 'quick') && (
                    <div className="space-y-4 border-t pt-6">
                      <div className="flex items-center space-x-2 mb-4">
                        <Users className="w-5 h-5 text-indigo-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Campaign Context</h3>
                        <span className="text-sm text-gray-500">(Better results with more details)</span>
                      </div>
                      
                      <div>
                        <label className="label">What does your business do? *</label>
                        <textarea
                          className="input-field h-20"
                          placeholder="e.g., We run a boutique fitness studio specializing in HIIT workouts for busy professionals. We focus on 30-minute sessions that deliver maximum results."
                          value={formData.userContext.business_description}
                          onChange={(e) => setFormData({
                            ...formData,
                            userContext: {...formData.userContext, business_description: e.target.value}
                          })}
                        />
                      </div>
                      
                      <div>
                        <label className="label">Who is your target audience? *</label>
                        <textarea
                          className="input-field h-20"
                          placeholder="e.g., Working professionals aged 25-40 in Mumbai and Pune, earning 8-25 LPA, who struggle to find time for fitness but value health and efficiency."
                          value={formData.userContext.target_audience_description}
                          onChange={(e) => setFormData({
                            ...formData,
                            userContext: {...formData.userContext, target_audience_description: e.target.value}
                          })}
                        />
                      </div>
                      
                      <div>
                        <label className="label">What makes you unique? *</label>
                        <textarea
                          className="input-field h-20"
                          placeholder="e.g., Only fitness studio in the area with 30-minute scientifically proven HIIT programs. Results guaranteed in 6 weeks or money back. Personal trainers with 10+ years experience."
                          value={formData.userContext.unique_value_proposition}
                          onChange={(e) => setFormData({
                            ...formData,
                            userContext: {...formData.userContext, unique_value_proposition: e.target.value}
                          })}
                        />
                      </div>
                      
                      <div className="text-sm text-blue-700 bg-blue-50 p-3 rounded-md">
                        <div className="flex items-start space-x-2">
                          <Lightbulb className="w-4 h-4 mt-0.5" />
                          <div>
                            <p className="font-medium">💡 Pro Tip:</p>
                            <p className="mt-1">The more specific you are, the better our AI can create personalized content that resonates with your exact audience and highlights what makes you special.</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Platform Selection */}
                  <div className="space-y-4 border-t pt-6">
                    <div className="flex items-center space-x-2 mb-4">
                      <BarChart3 className="w-5 h-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-gray-900">Platform Selection</h3>
                      <span className="text-sm text-gray-500">(At least one platform required)</span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-blue-50 transition-colors">
                        <input
                          type="checkbox"
                          id="facebook"
                          checked={formData.platforms.facebook}
                          onChange={(e) => setFormData({
                            ...formData,
                            platforms: { ...formData.platforms, facebook: e.target.checked }
                          })}
                          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="facebook" className="flex items-center space-x-2 text-sm font-medium text-gray-900 cursor-pointer">
                          <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
                            <span className="text-white text-xs font-bold">f</span>
                          </div>
                          <span>Facebook Feed & Stories</span>
                        </label>
                      </div>
                      
                      <div className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-pink-50 transition-colors">
                        <input
                          type="checkbox"
                          id="instagram"
                          checked={formData.platforms.instagram}
                          onChange={(e) => setFormData({
                            ...formData,
                            platforms: { ...formData.platforms, instagram: e.target.checked }
                          })}
                          className="w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500"
                        />
                        <label htmlFor="instagram" className="flex items-center space-x-2 text-sm font-medium text-gray-900 cursor-pointer">
                          <div className="w-6 h-6 bg-gradient-to-r from-pink-500 to-purple-600 rounded flex items-center justify-center">
                            <span className="text-white text-xs font-bold">📸</span>
                          </div>
                          <span>Instagram Feed & Stories</span>
                        </label>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
                      <p><strong>✓ Recommendation:</strong> Enable both platforms for maximum reach and engagement. Our AI will optimize content for each platform automatically.</p>
                    </div>
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
                      <h3 className="font-semibold mb-2">Business Description</h3>
                      <p className="text-gray-600">{formData.businessDescription || 'Not specified'}</p>
                    </div>
                    {(formData.businessDetails.business_name || userProfile?.business_name) && (
                      <div>
                        <h3 className="font-semibold mb-2">Business</h3>
                        <p className="text-gray-600">{formData.businessDetails.business_name || userProfile?.business_name}</p>
                      </div>
                    )}
                    {formData.prompt && (
                      <div className="md:col-span-2">
                        <h3 className="font-semibold mb-2">Prompt</h3>
                        <p className="text-gray-600">{formData.prompt}</p>
                      </div>
                    )}
                    {selectedType === 'personalized' && userProfile && (
                      <div className="md:col-span-2">
                        <h3 className="font-semibold mb-2">Personalization Features</h3>
                        <div className="flex flex-wrap gap-2">
                          <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded">Profile-based targeting</span>
                          <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded">Brand voice: {userProfile.brand_voice}</span>
                          <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded">Industry: {userProfile.industry}</span>
                          {selectedStrategy && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">AI Strategy Applied</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className={`${selectedType === 'personalized' ? 'bg-indigo-50 border-indigo-200' : 'bg-blue-50 border-blue-200'} rounded-lg p-6 mb-8 border`}>
                  <div className="flex items-start">
                    <AlertCircle className={`w-5 h-5 ${selectedType === 'personalized' ? 'text-indigo-600' : 'text-blue-600'} mt-1 mr-3`} />
                    <div>
                      <h3 className={`font-semibold ${selectedType === 'personalized' ? 'text-indigo-900' : 'text-blue-900'} mb-2`}>
                        {selectedType === 'personalized' ? 'AI Personalization Guarantee' : 'Performance Guarantee'}
                      </h3>
                      <p className={`${selectedType === 'personalized' ? 'text-indigo-800' : 'text-blue-800'} text-sm`}>
                        {selectedType === 'personalized' 
                          ? 'This personalized campaign uses AI to optimize for your specific business profile and goals. Expected performance improvement of 40-60% over standard campaigns.'
                          : 'This campaign is backed by our performance guarantee. If it doesn\'t meet our performance standards, we\'ll optimize it automatically.'
                        }
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
                        {selectedType === 'personalized' ? 'Creating Personalized Campaign...' : 'Creating Campaign...'}
                      </>
                    ) : (
                      <>
                        {selectedType === 'personalized' ? <Brain className="mr-2 w-4 h-4" /> : <Sparkles className="mr-2 w-4 h-4" />}
                        {selectedType === 'personalized' ? 'Create Personalized Campaign' : 'Create Campaign'}
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