import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { personalizationService } from '../services/api';
import { 
  CampaignStrategy, 
  CampaignStrategyRequest, 
  MetaUserProfile
} from '../types';
import { Button, Card } from '../design-system';
import { 
  Loader2, 
  Wand2, 
  Target, 
  DollarSign, 
  Users, 
  Palette,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Lightbulb,
  BarChart3
} from 'lucide-react';

interface CampaignStrategyWizardProps {
  profileId?: string;
  onStrategyCreated?: (strategy: CampaignStrategy) => void;
}

const CampaignStrategyWizard: React.FC<CampaignStrategyWizardProps> = ({
  profileId,
  onStrategyCreated
}) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [userProfile, setUserProfile] = useState<MetaUserProfile | null>(null);
  const [generatedStrategy, setGeneratedStrategy] = useState<CampaignStrategy | null>(null);
  const totalSteps = 4;

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    getValues,
    formState: { errors, isValid }
  } = useForm<CampaignStrategyRequest>({
    mode: 'onChange',
    defaultValues: {
      strategy_type: 'conversion',
      budget_range: '$1,000-$2,500/month',
      duration_days: 30,
      specific_goals: [],
      content_preferences: []
    }
  });

  const watchedStrategyType = watch('strategy_type');
  const watchedBudgetRange = watch('budget_range');

  // Load user profile on component mount
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profile = await personalizationService.getProfile(profileId);
        setUserProfile(profile);
        setValue('profile_id', profile.user_id);
      } catch (error) {
        console.error('Error loading profile:', error);
        toast.error('Failed to load user profile');
      }
    };

    loadProfile();
  }, [profileId, setValue]);

  // Strategy type options with descriptions
  const strategyTypes = [
    {
      value: 'awareness',
      label: 'Brand Awareness',
      description: 'Increase brand recognition and reach new audiences',
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      value: 'conversion',
      label: 'Conversions',
      description: 'Drive sales, leads, and specific actions',
      icon: Target,
      color: 'bg-green-500'
    },
    {
      value: 'engagement',
      label: 'Engagement',
      description: 'Boost likes, comments, shares, and interactions',
      icon: TrendingUp,
      color: 'bg-purple-500'
    },
    {
      value: 'retention',
      label: 'Customer Retention',
      description: 'Re-engage existing customers and increase loyalty',
      icon: CheckCircle,
      color: 'bg-orange-500'
    }
  ];

  const budgetRanges = [
    '$500-$1,000/month',
    '$1,000-$2,500/month',
    '$2,500-$5,000/month',
    '$5,000-$10,000/month',
    '$10,000-$25,000/month',
    '$25,000+/month'
  ];

  const durationOptions = [
    { value: 7, label: '1 Week - Quick Test' },
    { value: 14, label: '2 Weeks - Short Campaign' },
    { value: 30, label: '1 Month - Standard' },
    { value: 60, label: '2 Months - Extended' },
    { value: 90, label: '3 Months - Long-term' },
  ];

  const getSpecificGoalsForStrategy = (strategyType: string) => {
    const goalsByStrategy: Record<string, string[]> = {
      awareness: [
        'Increase brand recognition',
        'Reach new demographics',
        'Build brand association',
        'Expand market presence'
      ],
      conversion: [
        'Increase online sales',
        'Generate qualified leads',
        'Drive app downloads',
        'Boost subscription sign-ups',
        'Increase store visits'
      ],
      engagement: [
        'Increase social media followers',
        'Boost post engagement',
        'Grow email list',
        'Increase video views',
        'Build community'
      ],
      retention: [
        'Re-engage inactive customers',
        'Increase customer lifetime value',
        'Drive repeat purchases',
        'Reduce churn rate',
        'Upsell existing customers'
      ]
    };

    return goalsByStrategy[strategyType] || [];
  };

  const getContentPreferences = () => [
    'High-quality product images',
    'Lifestyle photography',
    'Video demonstrations',
    'Customer testimonials',
    'Behind-the-scenes content',
    'Educational content',
    'User-generated content',
    'Animated graphics',
    'Infographics',
    'Live videos'
  ];

  const handleArrayFieldChange = (
    fieldName: 'specific_goals' | 'content_preferences',
    value: string,
    checked: boolean
  ) => {
    const currentValues = getValues(fieldName) || [];
    if (checked) {
      setValue(fieldName, [...currentValues, value]);
    } else {
      setValue(fieldName, currentValues.filter(item => item !== value));
    }
  };

  const generateStrategy = async (formData: CampaignStrategyRequest) => {
    setIsGenerating(true);
    try {
      const strategy = await personalizationService.generateCampaignStrategy(formData);
      setGeneratedStrategy(strategy);
      setCurrentStep(4);
      toast.success('Campaign strategy generated successfully!');
      
      if (onStrategyCreated) {
        onStrategyCreated(strategy);
      }
    } catch (error: any) {
      console.error('Error generating strategy:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate campaign strategy');
    } finally {
      setIsGenerating(false);
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderProgressBar = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Campaign Strategy Wizard</h2>
        <div className="text-sm text-gray-600">
          Step {currentStep} of {totalSteps}
        </div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <motion.div
          className="bg-blue-600 h-2 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${(currentStep / totalSteps) * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
    </div>
  );

  const renderStep1 = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <Wand2 className="w-16 h-16 text-blue-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Choose Your Campaign Objective</h3>
        <p className="text-gray-600">Select the primary goal for your Meta advertising campaign</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {strategyTypes.map((strategy) => {
          const IconComponent = strategy.icon;
          return (
            <motion.div
              key={strategy.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <label className={`block p-6 border-2 rounded-lg cursor-pointer transition-all ${
                watchedStrategyType === strategy.value 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}>
                <input
                  type="radio"
                  value={strategy.value}
                  {...register('strategy_type', { required: 'Please select a campaign objective' })}
                  className="sr-only"
                />
                <div className="flex items-start space-x-4">
                  <div className={`${strategy.color} p-3 rounded-lg`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{strategy.label}</h4>
                    <p className="text-gray-600 mt-1">{strategy.description}</p>
                  </div>
                </div>
              </label>
            </motion.div>
          );
        })}
      </div>
      {errors.strategy_type && (
        <p className="text-red-500 text-sm text-center">{errors.strategy_type.message}</p>
      )}
    </motion.div>
  );

  const renderStep2 = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <DollarSign className="w-16 h-16 text-green-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Budget & Duration</h3>
        <p className="text-gray-600">Set your campaign budget and duration preferences</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Monthly Budget Range
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {budgetRanges.map(range => (
              <label key={range} className={`block p-4 border-2 rounded-lg cursor-pointer transition-all ${
                watchedBudgetRange === range 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}>
                <input
                  type="radio"
                  value={range}
                  {...register('budget_range', { required: 'Please select a budget range' })}
                  className="sr-only"
                />
                <span className="text-sm font-medium">{range}</span>
              </label>
            ))}
          </div>
          {errors.budget_range && (
            <p className="text-red-500 text-sm mt-1">{errors.budget_range.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Campaign Duration
          </label>
          <select
            {...register('duration_days', { required: 'Please select campaign duration' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select duration</option>
            {durationOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          {errors.duration_days && (
            <p className="text-red-500 text-sm mt-1">{errors.duration_days.message}</p>
          )}
        </div>

        {userProfile && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Based on Your Profile:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Industry: {userProfile.industry}</li>
              <li>• Business Type: {userProfile.business_type}</li>
              <li>• Target Audience: {userProfile.target_audience.slice(0, 100)}...</li>
            </ul>
          </div>
        )}
      </div>
    </motion.div>
  );

  const renderStep3 = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <Target className="w-16 h-16 text-purple-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Specific Goals & Preferences</h3>
        <p className="text-gray-600">Define your specific objectives and content preferences</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Specific Goals for {strategyTypes.find(s => s.value === watchedStrategyType)?.label}
          </label>
          <div className="space-y-2">
            {getSpecificGoalsForStrategy(watchedStrategyType).map(goal => (
              <label key={goal} className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50">
                <input
                  type="checkbox"
                  value={goal}
                  onChange={(e) => handleArrayFieldChange('specific_goals', goal, e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{goal}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Content Preferences (Select all that apply)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {getContentPreferences().map(preference => (
              <label key={preference} className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50">
                <input
                  type="checkbox"
                  value={preference}
                  onChange={(e) => handleArrayFieldChange('content_preferences', preference, e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{preference}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Audience Preferences (Optional)
          </label>
          <textarea
            {...register('target_audience_preferences')}
            placeholder="Any specific audience targeting preferences for your campaign?"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>
      </div>
    </motion.div>
  );

  const renderStrategyResults = () => {
    if (!generatedStrategy) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        <div className="text-center mb-8">
          <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Your Personalized Campaign Strategy</h3>
          <p className="text-gray-600">AI-generated strategy based on your profile and goals</p>
          <div className="inline-flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium mt-2">
            <TrendingUp className="w-4 h-4 mr-1" />
            Confidence Score: {Math.round(generatedStrategy.confidence_score * 100)}%
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Campaign Overview */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
              Campaign Overview
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Objective:</span>
                <span className="font-medium">{generatedStrategy.meta_campaign_objective}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Strategy Type:</span>
                <span className="font-medium capitalize">{generatedStrategy.strategy_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Daily Budget:</span>
                <span className="font-medium">${generatedStrategy.budget_allocation.daily_budget}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Estimated Reach:</span>
                <span className="font-medium">{generatedStrategy.expected_performance.estimated_reach.toLocaleString()}</span>
              </div>
            </div>
          </Card>

          {/* Expected Performance */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
              Expected Performance
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Expected CTR:</span>
                <span className="font-medium">{(generatedStrategy.expected_performance.expected_ctr * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Conversion Rate:</span>
                <span className="font-medium">{(generatedStrategy.expected_performance.expected_conversion_rate * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cost per Result:</span>
                <span className="font-medium">${generatedStrategy.expected_performance.estimated_cost_per_result.toFixed(2)}</span>
              </div>
            </div>
          </Card>

          {/* Audience Segments */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-purple-600" />
              Audience Segments
            </h4>
            <div className="space-y-3">
              {generatedStrategy.audience_segments.map((segment) => (
                <div key={segment.segment_id} className="border rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium">{segment.name}</h5>
                    <span className="text-sm text-gray-500">{segment.recommended_budget_percentage}% budget</span>
                  </div>
                  <p className="text-sm text-gray-600">{segment.description}</p>
                  <div className="mt-2 text-xs text-gray-500">
                    Est. Size: {segment.estimated_size.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Content Themes */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Palette className="w-5 h-5 mr-2 text-orange-600" />
              Content Themes
            </h4>
            <div className="space-y-3">
              {generatedStrategy.content_themes.map((theme) => (
                <div key={theme.theme_id} className="border rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium">{theme.name}</h5>
                    <div className="flex items-center text-sm text-green-600">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      {(theme.performance_prediction * 100).toFixed(0)}%
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">{theme.description}</p>
                  <div className="mt-2">
                    <div className="flex flex-wrap gap-1">
                      {theme.content_pillars.slice(0, 3).map(pillar => (
                        <span key={pillar} className="px-2 py-1 bg-gray-100 text-xs rounded">
                          {pillar}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Creative Recommendations */}
        {generatedStrategy.creative_recommendations.length > 0 && (
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
              Creative Recommendations
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {generatedStrategy.creative_recommendations.map((rec, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium capitalize">{rec.creative_type}</h5>
                    <span className="text-sm text-blue-600">{(rec.predicted_performance_score * 100).toFixed(0)}% score</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    {rec.content_suggestions.headline_options.length > 0 && (
                      <div>
                        <span className="font-medium">Headlines:</span>
                        <ul className="text-gray-600 ml-2">
                          {rec.content_suggestions.headline_options.slice(0, 2).map((headline, idx) => (
                            <li key={idx}>• {headline}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        <div className="flex justify-center space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/campaigns/create', { 
              state: { strategy: generatedStrategy } 
            })}
          >
            Create Campaign from Strategy
          </Button>
          <Button
            type="button"
            onClick={() => {
              navigate('/personalization/dashboard');
            }}
          >
            Go to Dashboard
          </Button>
        </div>
      </motion.div>
    );
  };

  const renderStepNavigation = () => {
    if (currentStep === 4) return null; // No navigation on results step

    return (
      <div className="flex justify-between items-center mt-8 pt-6 border-t">
        <div>
          {currentStep > 1 && (
            <Button
              type="button"
              variant="outline"
              onClick={prevStep}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Previous</span>
            </Button>
          )}
        </div>

        <div>
          {currentStep < 3 ? (
            <Button
              type="button"
              onClick={nextStep}
              className="flex items-center space-x-2"
            >
              <span>Next</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              disabled={isGenerating || !isValid}
              className="flex items-center space-x-2"
            >
              {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
              <span>Generate Strategy</span>
            </Button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="p-8">
          <form onSubmit={handleSubmit(generateStrategy)}>
            {renderProgressBar()}
            
            <div className="min-h-[600px]">
              <AnimatePresence mode="wait">
                {currentStep === 1 && renderStep1()}
                {currentStep === 2 && renderStep2()}
                {currentStep === 3 && renderStep3()}
                {currentStep === 4 && renderStrategyResults()}
              </AnimatePresence>
            </div>

            {renderStepNavigation()}
          </form>
        </Card>
      </div>
    </div>
  );
};

export default CampaignStrategyWizard;