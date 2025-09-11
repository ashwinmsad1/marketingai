import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { personalizationService } from '../services/api';
import { MetaUserProfile, PersonalizationProfileRequest } from '../types';
import { Button, Card, Input } from '../design-system';
import { CheckCircle, ArrowRight, ArrowLeft, Save } from 'lucide-react';
import { ButtonWithLoading } from '../components/LoadingStates';

interface ProfileSetupProps {
  existingProfile?: MetaUserProfile;
  onComplete?: (profile: MetaUserProfile) => void;
  isOnboarding?: boolean;
}

const ProfileSetup: React.FC<ProfileSetupProps> = ({
  existingProfile,
  onComplete,
  isOnboarding = false
}) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const totalSteps = 4;

  const {
    register,
    handleSubmit,
    setValue,
    getValues,
    formState: { errors, isValid },
    trigger
  } = useForm<PersonalizationProfileRequest>({
    mode: 'onChange',
    defaultValues: existingProfile ? {
      business_name: existingProfile.business_name,
      industry: existingProfile.industry,
      business_type: existingProfile.business_type,
      target_audience: existingProfile.target_audience,
      primary_location: existingProfile.primary_location,
      budget_range: existingProfile.budget_range,
      signature_product_service: existingProfile.signature_product_service,
      unique_value_proposition: existingProfile.unique_value_proposition,
      brand_voice: existingProfile.brand_voice,
      primary_goals: existingProfile.primary_goals,
      peak_sales_times: existingProfile.peak_sales_times,
      customer_pain_points: existingProfile.customer_pain_points,
      preferred_content_types: existingProfile.preferred_content_types,
      brand_colors: existingProfile.brand_colors,
      brand_fonts: existingProfile.brand_fonts,
      seasonal_trends: existingProfile.seasonal_trends,
      marketing_channels: existingProfile.marketing_channels,
      content_calendar_preferences: existingProfile.content_calendar_preferences,
      performance_priorities: existingProfile.performance_priorities,
    } : {
      primary_goals: [],
      preferred_content_types: [],
      marketing_channels: [],
      performance_priorities: []
    }
  });


  // Industry options
  const industryOptions = [
    'E-commerce', 'SaaS/Technology', 'Healthcare', 'Financial Services', 
    'Real Estate', 'Fitness/Wellness', 'Food & Beverage', 'Fashion/Beauty',
    'Education', 'Professional Services', 'Home Services', 'Entertainment',
    'Travel/Hospitality', 'Non-profit', 'Manufacturing', 'Retail', 'Other'
  ];

  // Dynamic options based on selections
  const getBusinessTypeOptions = () => ['B2C', 'B2B', 'Both'];
  
  const getBudgetRangeOptions = () => [
    '₹5,000-₹10,000/month',     // Small local businesses
    '₹10,000-₹25,000/month',    // Growing SMEs  
    '₹25,000-₹50,000/month',    // Established SMEs
    '₹50,000-₹100,000/month',   // Mid-size businesses
    '₹100,000-₹250,000/month',  // Large businesses
    '₹250,000+/month'           // Enterprise level
  ];

  const getPrimaryGoalsOptions = () => [
    'Increase brand awareness', 'Generate leads', 'Drive sales', 'Boost engagement',
    'Build community', 'Launch new product', 'Increase market share', 'Customer retention',
    'Improve customer satisfaction', 'Expand to new markets'
  ];

  const getContentTypeOptions = () => [
    'Images/Photos', 'Videos', 'Stories', 'Reels/Short Videos', 'Carousels',
    'Live Videos', 'User-generated content', 'Behind-the-scenes', 'Educational content',
    'Product demonstrations', 'Customer testimonials', 'Industry insights'
  ];

  const getMarketingChannelOptions = () => [
    'Facebook Ads', 'Instagram Ads', 'Email Marketing',
    'Content Marketing', 'SEO', 'Influencer Marketing',
    'Print Advertising', 'Radio/TV'
  ];

  const getPerformancePriorityOptions = () => [
    'Cost per click (CPC)', 'Click-through rate (CTR)', 'Conversion rate',
    'Return on ad spend (ROAS)', 'Cost per acquisition (CPA)', 'Reach',
    'Engagement rate', 'Brand awareness lift', 'Video view rate', 'Lead quality'
  ];

  const getBrandVoiceOptions = () => [
    'Professional', 'Friendly', 'Authoritative', 'Playful', 'Inspirational',
    'Educational', 'Conversational', 'Bold', 'Caring', 'Innovative'
  ];

  // Step validation
  const validateStep = async (step: number): Promise<boolean> => {
    const fieldsToValidate: Record<number, string[]> = {
      1: ['business_name', 'industry', 'business_type', 'primary_location'],
      2: ['target_audience', 'signature_product_service', 'unique_value_proposition', 'budget_range'],
      3: ['brand_voice', 'primary_goals'],
      4: ['performance_priorities']
    };

    const fields = fieldsToValidate[step];
    if (!fields) return true;

    const result = await trigger(fields as any);
    return result;
  };

  const nextStep = async () => {
    const isStepValid = await validateStep(currentStep);
    if (isStepValid && currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleArrayFieldChange = (
    fieldName: 'primary_goals' | 'preferred_content_types' | 'marketing_channels' | 'performance_priorities',
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

  const onSubmit = async (data: PersonalizationProfileRequest) => {
    setIsLoading(true);
    try {
      let result;
      if (existingProfile) {
        result = await personalizationService.updateProfile(data, existingProfile.user_id);
        toast.success('Profile updated successfully!');
      } else {
        result = await personalizationService.createProfile(data);
        toast.success('Profile created successfully!');
      }

      if (onComplete) {
        onComplete(result);
      }

      if (isOnboarding) {
        navigate('/personalization/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (error: any) {
      console.error('Error saving profile:', error);
      toast.error(error.response?.data?.detail || 'Failed to save profile');
    } finally {
      setIsLoading(false);
    }
  };

  const saveProgress = async () => {
    setIsSaving(true);
    try {
      const data = getValues();
      await personalizationService.updateProfile(data);
      toast.success('Progress saved!');
    } catch (error) {
      toast.error('Failed to save progress');
    } finally {
      setIsSaving(false);
    }
  };

  const renderProgressBar = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          {isOnboarding ? 'Welcome! Let\'s set up your personalization profile' : 'Update Your Profile'}
        </h2>
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
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Business Basics</h3>
        <p className="text-gray-600">Tell us about your business to get started</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Business Name *
          </label>
          <Input
            {...register('business_name', { required: 'Business name is required' })}
            placeholder="Enter your business name"
            errorText={errors.business_name?.message}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Industry *
          </label>
          <select
            {...register('industry', { required: 'Industry is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select your industry</option>
            {industryOptions.map(industry => (
              <option key={industry} value={industry}>{industry}</option>
            ))}
          </select>
          {errors.industry && <p className="text-red-500 text-sm mt-1">{errors.industry.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Business Type *
          </label>
          <select
            {...register('business_type', { required: 'Business type is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select business type</option>
            {getBusinessTypeOptions().map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          {errors.business_type && <p className="text-red-500 text-sm mt-1">{errors.business_type.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Primary Location *
          </label>
          <Input
            {...register('primary_location', { required: 'Primary location is required' })}
            placeholder="e.g., New York, USA"
            errorText={errors.primary_location?.message}
          />
        </div>
      </div>
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
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Target Audience & Value</h3>
        <p className="text-gray-600">Help us understand your customers and what makes you unique</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Audience *
          </label>
          <textarea
            {...register('target_audience', { required: 'Target audience is required' })}
            placeholder="Describe your ideal customers (demographics, interests, behaviors)"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          {errors.target_audience && <p className="text-red-500 text-sm mt-1">{errors.target_audience.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Signature Product/Service *
          </label>
          <textarea
            {...register('signature_product_service', { required: 'Signature product/service is required' })}
            placeholder="What is your main product or service offering?"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
          />
          {errors.signature_product_service && <p className="text-red-500 text-sm mt-1">{errors.signature_product_service.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Unique Value Proposition *
          </label>
          <textarea
            {...register('unique_value_proposition', { required: 'Unique value proposition is required' })}
            placeholder="What makes your business unique and valuable to customers?"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          {errors.unique_value_proposition && <p className="text-red-500 text-sm mt-1">{errors.unique_value_proposition.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Marketing Budget *
          </label>
          <select
            {...register('budget_range', { required: 'Budget range is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select your monthly budget</option>
            {getBudgetRangeOptions().map(range => (
              <option key={range} value={range}>{range}</option>
            ))}
          </select>
          {errors.budget_range && <p className="text-red-500 text-sm mt-1">{errors.budget_range.message}</p>}
        </div>
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
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Brand & Goals</h3>
        <p className="text-gray-600">Define your brand personality and objectives</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Brand Voice *
          </label>
          <select
            {...register('brand_voice', { required: 'Brand voice is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select your brand voice</option>
            {getBrandVoiceOptions().map(voice => (
              <option key={voice} value={voice}>{voice}</option>
            ))}
          </select>
          {errors.brand_voice && <p className="text-red-500 text-sm mt-1">{errors.brand_voice.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Primary Goals * (Select all that apply)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {getPrimaryGoalsOptions().map(goal => (
              <label key={goal} className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50">
                <input
                  type="checkbox"
                  value={goal}
                  onChange={(e) => handleArrayFieldChange('primary_goals', goal, e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{goal}</span>
              </label>
            ))}
          </div>
          {errors.primary_goals && <p className="text-red-500 text-sm mt-1">Please select at least one goal</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Peak Sales Times
            </label>
            <Input
              {...register('peak_sales_times')}
              placeholder="e.g., Weekends, Holiday seasons"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Brand Colors
            </label>
            <Input
              {...register('brand_colors')}
              placeholder="e.g., #FF5733, Blue, Red"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Customer Pain Points
          </label>
          <textarea
            {...register('customer_pain_points')}
            placeholder="What problems do your customers face that you solve?"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
          />
        </div>
      </div>
    </motion.div>
  );

  const renderStep4 = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Preferences & Priorities</h3>
        <p className="text-gray-600">Final details to personalize your experience</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Content Types (Select all that apply)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {getContentTypeOptions().map(type => (
              <label key={type} className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50">
                <input
                  type="checkbox"
                  value={type}
                  onChange={(e) => handleArrayFieldChange('preferred_content_types', type, e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{type}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Current Marketing Channels
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {getMarketingChannelOptions().map(channel => (
              <label key={channel} className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50">
                <input
                  type="checkbox"
                  value={channel}
                  onChange={(e) => handleArrayFieldChange('marketing_channels', channel, e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{channel}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Performance Priorities * (Select top priorities)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {getPerformancePriorityOptions().map(priority => (
              <label key={priority} className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50">
                <input
                  type="checkbox"
                  value={priority}
                  onChange={(e) => handleArrayFieldChange('performance_priorities', priority, e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{priority}</span>
              </label>
            ))}
          </div>
          {errors.performance_priorities && <p className="text-red-500 text-sm mt-1">Please select at least one priority</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Seasonal Trends
            </label>
            <textarea
              {...register('seasonal_trends')}
              placeholder="How does seasonality affect your business?"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
          </div>

        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content Calendar Preferences
          </label>
          <Input
            {...register('content_calendar_preferences')}
            placeholder="e.g., 3 posts per week, focus on Tuesday and Thursday"
          />
        </div>
      </div>
    </motion.div>
  );

  const renderStepNavigation = () => (
    <div className="flex justify-between items-center mt-8 pt-6 border-t">
      <div className="flex items-center space-x-4">
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
        
        {!isOnboarding && (
          <ButtonWithLoading
            isLoading={isSaving}
            loadingText="Saving..."
            onClick={saveProgress}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            Save Progress
          </ButtonWithLoading>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {currentStep < totalSteps ? (
          <Button
            type="button"
            onClick={nextStep}
            className="flex items-center space-x-2"
          >
            <span>Next</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        ) : (
          <ButtonWithLoading
            isLoading={isLoading}
            loadingText={existingProfile ? 'Updating...' : 'Completing Setup...'}
            disabled={!isValid}
            className="flex items-center space-x-2"
            variant="primary"
            onClick={() => {}} // Will be handled by form submit
          >
            <CheckCircle className="w-4 h-4" />
            {existingProfile ? 'Update Profile' : 'Complete Setup'}
          </ButtonWithLoading>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="p-8">
          <form onSubmit={handleSubmit(onSubmit)}>
            {renderProgressBar()}
            
            <div className="min-h-[600px]">
              {currentStep === 1 && renderStep1()}
              {currentStep === 2 && renderStep2()}
              {currentStep === 3 && renderStep3()}
              {currentStep === 4 && renderStep4()}
            </div>

            {renderStepNavigation()}
          </form>
        </Card>
      </div>
    </div>
  );
};

export default ProfileSetup;