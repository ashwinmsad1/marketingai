import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  DollarSign,
  Target,
  Zap,
  ArrowUp,
  Play,
  Pause,
  MoreVertical,
  Eye,
  CreditCard,
  Brain,
  Lightbulb,
  BarChart3,
  Star,
  ChevronRight,
  Palette,
  TestTube
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { personalizationService } from '../services/api';
import { PersonalizationInsights, MetaUserProfile, CampaignRecommendation } from '../types';
import { CardSkeleton } from '../components/LoadingStates';
import {
  Card,
  CardHeader,
  CardContent,
  CardTitle,
  CardDescription,
  Button,
  IconButton,
} from '../design-system';
import EmailVerificationBanner from '../components/EmailVerificationBanner';

interface DashboardProps {
  user: {
    name: string;
    subscription_tier: string;
  };
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [personalizationInsights, setPersonalizationInsights] = useState<PersonalizationInsights | null>(null);
  const [userProfile, setUserProfile] = useState<MetaUserProfile | null>(null);
  const [recommendations, setRecommendations] = useState<CampaignRecommendation[]>([]);
  const [isLoadingPersonalization, setIsLoadingPersonalization] = useState(true);
  const [showPersonalizationPrompt, setShowPersonalizationPrompt] = useState(false);
  const navigate = useNavigate();

  // Load personalization data
  useEffect(() => {
    let isMounted = true; // Flag to prevent state updates after unmount

    const loadPersonalizationData = async () => {
      try {
        if (isMounted) {
          setIsLoadingPersonalization(true);
        }
        
        const [profileData, insightsData, recommendationsData] = await Promise.all([
          personalizationService.getProfile().catch(() => null),
          personalizationService.getInsights(undefined, selectedPeriod).catch(() => null),
          personalizationService.getRecommendations().catch(() => [])
        ]);
        
        if (isMounted) {
          setUserProfile(profileData);
          setPersonalizationInsights(insightsData);
          setRecommendations(recommendationsData.slice(0, 3));
          
          // Show personalization prompt if no profile exists
          if (!profileData) {
            setShowPersonalizationPrompt(true);
          }
        }
      } catch (error) {
        console.error('Error loading personalization data:', error);
      } finally {
        if (isMounted) {
          setIsLoadingPersonalization(false);
        }
      }
    };

    loadPersonalizationData();

    // Cleanup function
    return () => {
      isMounted = false;
    };
  }, [selectedPeriod]);

  // Mock data - would come from API
  const dashboardData = {
    success_summary: {
      total_campaigns: 12,
      total_revenue: 15750.50,
      overall_roi: 485.5,
      guarantee_success_rate: 92.3
    },
    recent_campaigns: [
      {
        campaign_id: '1',
        name: 'Restaurant Summer Special',
        type: 'industry_optimized',
        status: 'active',
        spend: 250,
        revenue: 1850,
        roi: 640,
        ctr: 3.2,
        created_at: '2025-01-01',
        performance_status: 'excellent'
      },
      {
        campaign_id: '2', 
        name: 'Fitness Challenge Viral',
        type: 'viral',
        status: 'active',
        spend: 180,
        revenue: 920,
        roi: 411,
        ctr: 2.8,
        created_at: '2024-12-28',
        performance_status: 'good'
      },
      {
        campaign_id: '3',
        name: 'Fashion Trend Analysis',
        type: 'viral',
        status: 'active',
        spend: 320,
        revenue: 1200,
        roi: 275,
        ctr: 2.1,
        created_at: '2024-12-25',
        performance_status: 'good'
      }
    ]
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'badge-success';
      case 'paused': return 'badge-warning';
      case 'completed': return 'badge-primary';
      default: return 'badge-danger';
    }
  };

  const getPerformanceColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-600';
      case 'good': return 'text-blue-600';
      case 'poor': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getCampaignTypeIcon = (type: string) => {
    switch (type) {
      case 'personalized': return '🧠';
      case 'viral': return '🔥';
      case 'industry_optimized': return '🏭';
      default: return '🎨';
    }
  };

  return (
    <div className="space-y-6">
      {/* Email Verification Banner */}
      <EmailVerificationBanner className="mb-4" />
      
      {/* Personalization Setup Prompt */}
      <AnimatePresence>
        {showPersonalizationPrompt && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-xl mb-6"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-white/20 p-3 rounded-lg">
                  <Brain className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-1">Unlock AI Personalization</h3>
                  <p className="text-indigo-100">
                    Set up your business profile to get personalized campaigns with 40-60% better performance
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Button
                  variant="outline"
                  className="border-white/30 text-white hover:bg-white/10"
                  onClick={() => setShowPersonalizationPrompt(false)}
                >
                  Later
                </Button>
                <Button
                  className="bg-white text-indigo-600 hover:bg-gray-50"
                  onClick={() => navigate('/personalization/profile')}
                >
                  Set Up Profile
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user.name}! 👋
            </h1>
            <p className="text-gray-600 mt-2">
              Here's how your AI marketing campaigns are performing
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select 
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="h-10 px-4 text-sm border border-gray-300 bg-white focus:border-blue-500 focus:ring-blue-500 rounded-md w-32"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
            <div className="flex items-center space-x-2">
              {userProfile && (
                <Button
                  variant="outline"
                  leftIcon={<Brain className="w-4 h-4" />}
                  onClick={() => navigate('/personalization/dashboard')}
                >
                  Personalization
                </Button>
              )}
              <Button
                leftIcon={<Zap className="w-4 h-4" />}
                onClick={() => navigate('/create-campaign')}
              >
                New Campaign
              </Button>
            </div>
          </div>
        </div>
        
        {/* Subscription Tier Badge */}
        <button
          onClick={() => navigate('/subscription')}
          className="inline-flex items-center bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-4 py-2 rounded-full transition-all duration-200 hover:shadow-lg"
        >
          <CreditCard className="w-4 h-4 mr-2" />
          <span className="text-sm font-medium capitalize">{user.subscription_tier} Plan</span>
        </button>
      </motion.div>

      {/* Personalization Metrics (if available) */}
      {personalizationInsights && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.05 }}
          className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-xl border border-indigo-200 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="bg-indigo-100 p-2 rounded-lg">
                <Brain className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold text-indigo-900">AI Personalization Impact</h3>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="border-indigo-200 text-indigo-600 hover:bg-indigo-50"
              onClick={() => navigate('/personalization/dashboard')}
            >
              View Details
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {personalizationInsights.performance_summary.personalized_campaigns}
              </div>
              <div className="text-sm text-indigo-700">Personalized Campaigns</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                +{personalizationInsights.performance_summary.average_lift}%
              </div>
              <div className="text-sm text-indigo-700">Average Lift</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                ${personalizationInsights.performance_summary.total_additional_revenue.toLocaleString()}
              </div>
              <div className="text-sm text-indigo-700">Additional Revenue</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {personalizationInsights.performance_summary.best_performing_segments.length}
              </div>
              <div className="text-sm text-indigo-700">Top Segments</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Key Metrics Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <div className="flex items-center text-green-600 text-sm font-medium">
                <ArrowUp className="w-4 h-4 mr-1" />
                +24.5%
              </div>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                ${dashboardData.success_summary.total_revenue.toLocaleString()}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div className="flex items-center text-blue-600 text-sm font-medium">
                <ArrowUp className="w-4 h-4 mr-1" />
                +67.2%
              </div>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Overall ROI</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.success_summary.overall_roi.toFixed(1)}%
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
              <div className="flex items-center text-purple-600 text-sm font-medium">
                <ArrowUp className="w-4 h-4 mr-1" />
                +12.8%
              </div>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Active Campaigns</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.success_summary.total_campaigns}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="bg-orange-100 p-3 rounded-lg">
                <Zap className="w-6 h-6 text-orange-600" />
              </div>
              <div className="flex items-center text-orange-600 text-sm font-medium">
                <ArrowUp className="w-4 h-4 mr-1" />
                +8.4%
              </div>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.success_summary.guarantee_success_rate.toFixed(1)}%
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* AI Recommendations */}
      {recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Lightbulb className="w-5 h-5 text-yellow-600" />
                  <CardTitle>AI Recommendations</CardTitle>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-blue-600 hover:text-blue-700"
                  onClick={() => navigate('/personalization/dashboard')}
                >
                  View All
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
              <CardDescription>
                Personalized recommendations to improve your campaigns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recommendations.map((rec, index) => (
                  <motion.div
                    key={rec.recommendation_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200"
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${
                        rec.priority === 'high' ? 'bg-red-100 text-red-600' :
                        rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                        'bg-green-100 text-green-600'
                      }`}>
                        <Star className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">{rec.title}</h4>
                        <p className="text-sm text-gray-600 mb-2">{rec.description.slice(0, 100)}...</p>
                        <div className="flex items-center space-x-4 text-xs">
                          <span className="text-green-600 font-medium">
                            +{rec.predicted_impact.estimated_change}% {rec.predicted_impact.metric}
                          </span>
                          <span className="text-blue-600">
                            {rec.predicted_impact.confidence}% confidence
                          </span>
                          <span className={`px-2 py-1 rounded ${
                            rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                            rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {rec.priority.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        onClick={() => {
                          // Apply recommendation logic would go here
                          toast.success('Recommendation applied!');
                        }}
                      >
                        Apply
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Recent Campaigns */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Campaigns</CardTitle>
              <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData.recent_campaigns.map((campaign, index) => (
                <motion.div
                  key={campaign.campaign_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                <div className="flex items-center space-x-4">
                  <div className="text-2xl">
                    {getCampaignTypeIcon(campaign.type)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={getStatusColor(campaign.status)}>
                        {campaign.status}
                      </span>
                      <span className="text-gray-400">•</span>
                      <span className="text-sm text-gray-600">
                        {new Date(campaign.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Spend</p>
                    <p className="font-semibold">${campaign.spend}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Revenue</p>
                    <p className="font-semibold text-green-600">${campaign.revenue}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">ROI</p>
                    <p className={`font-semibold ${getPerformanceColor(campaign.performance_status)}`}>
                      {campaign.roi}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">CTR</p>
                    <p className="font-semibold">{campaign.ctr}%</p>
                  </div>

                  <div className="flex items-center space-x-2">
                    {campaign.status === 'active' ? (
                      <IconButton
                        icon={<Pause className="w-4 h-4" />}
                        aria-label="Pause campaign"
                        variant="ghost"
                        size="sm"
                        className="text-gray-400 hover:text-orange-600"
                      />
                    ) : (
                      <IconButton
                        icon={<Play className="w-4 h-4" />}
                        aria-label="Resume campaign"
                        variant="ghost"
                        size="sm"
                        className="text-gray-400 hover:text-green-600"
                      />
                    )}
                    <IconButton
                      icon={<Eye className="w-4 h-4" />}
                      aria-label="View campaign details"
                      variant="ghost"
                      size="sm"
                      className="text-gray-400 hover:text-blue-600"
                    />
                    <IconButton
                      icon={<MoreVertical className="w-4 h-4" />}
                      aria-label="More actions"
                      variant="ghost"
                      size="sm"
                      className="text-gray-400 hover:text-gray-600"
                    />
                  </div>
                </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {isLoadingPersonalization ? (
          <CardSkeleton />
        ) : userProfile ? (
          <Card hoverable className="text-center" onClick={() => navigate('/create-campaign')}>
            <CardContent>
              <div className="bg-indigo-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-indigo-600" />
              </div>
              <CardTitle as="h3" className="text-base mb-2">AI Personalized</CardTitle>
              <CardDescription className="mb-4">Campaigns tailored for {userProfile.business_name}</CardDescription>
              <Button width="full">Create Campaign</Button>
            </CardContent>
          </Card>
        ) : (
          <Card hoverable className="text-center" onClick={() => navigate('/create-campaign')}>
            <CardContent>
              <div className="bg-blue-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <CardTitle as="h3" className="text-base mb-2">Quick Campaign</CardTitle>
              <CardDescription className="mb-4">Create campaign in minutes</CardDescription>
              <Button width="full">Start Now</Button>
            </CardContent>
          </Card>
        )}

        <Card hoverable className="text-center" onClick={() => navigate('/personalization/strategy-wizard')}>
          <CardContent>
            <div className="bg-purple-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-8 h-8 text-purple-600" />
            </div>
            <CardTitle as="h3" className="text-base mb-2">Strategy Wizard</CardTitle>
            <CardDescription className="mb-4">AI-powered campaign strategies</CardDescription>
            <Button variant="secondary" width="full">Start Wizard</Button>
          </CardContent>
        </Card>

        <Card hoverable className="text-center" onClick={() => navigate('/personalization/ab-testing')}>
          <CardContent>
            <div className="bg-red-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <TestTube className="w-8 h-8 text-red-600" />
            </div>
            <CardTitle as="h3" className="text-base mb-2">A/B Testing</CardTitle>
            <CardDescription className="mb-4">Test & optimize campaigns</CardDescription>
            <Button variant="secondary" width="full">Create Test</Button>
          </CardContent>
        </Card>

        <Card hoverable className="text-center" onClick={() => navigate('/personalization/templates')}>
          <CardContent>
            <div className="bg-green-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Palette className="w-8 h-8 text-green-600" />
            </div>
            <CardTitle as="h3" className="text-base mb-2">Templates</CardTitle>
            <CardDescription className="mb-4">Personalized content templates</CardDescription>
            <Button variant="secondary" width="full">Browse Templates</Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Dashboard;