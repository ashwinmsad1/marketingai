import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { personalizationService } from '../services/api';
import { 
  PersonalizationInsights, 
  CampaignRecommendation, 
  OptimizationOpportunity,
  MetaUserProfile,
  PersonalizationAskResponse
} from '../types';
import { Button, Card, Input } from '../design-system';
import {
  Brain,
  TrendingUp,
  Users,
  Target,
  Palette,
  Zap,
  MessageCircle,
  Send,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  BarChart3,
  DollarSign,
  Settings,
  ArrowRight,
  Star,
  Clock
} from 'lucide-react';

const PersonalizationDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [insights, setInsights] = useState<PersonalizationInsights | null>(null);
  const [recommendations, setRecommendations] = useState<CampaignRecommendation[]>([]);
  const [optimizationOpportunities, setOptimizationOpportunities] = useState<OptimizationOpportunity[]>([]);
  const [userProfile, setUserProfile] = useState<MetaUserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiResponse, setAiResponse] = useState<PersonalizationAskResponse | null>(null);
  const [isAsking, setIsAsking] = useState(false);
  const [showAiChat, setShowAiChat] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d');

  useEffect(() => {
    loadDashboardData();
  }, [selectedTimeframe]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load all dashboard data in parallel
      const [
        profileData,
        insightsData,
        recommendationsData,
        opportunitiesData
      ] = await Promise.all([
        personalizationService.getProfile(),
        personalizationService.getInsights(undefined, selectedTimeframe),
        personalizationService.getRecommendations(),
        personalizationService.getOptimizationOpportunities()
      ]);

      setUserProfile(profileData);
      setInsights(insightsData);
      setRecommendations(recommendationsData);
      setOptimizationOpportunities(opportunitiesData);
    } catch (error: any) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAIQuestion = async () => {
    if (!aiQuestion.trim()) return;

    setIsAsking(true);
    try {
      const response = await personalizationService.askPersonalizationQuestion(aiQuestion, {
        profile_id: userProfile?.user_id,
        timeframe: selectedTimeframe
      });
      setAiResponse(response);
      setAiQuestion('');
    } catch (error: any) {
      console.error('Error asking AI question:', error);
      toast.error('Failed to get AI response');
    } finally {
      setIsAsking(false);
    }
  };

  const applyRecommendation = async (recommendationId: string) => {
    try {
      await personalizationService.applyRecommendation(recommendationId);
      toast.success('Recommendation applied successfully!');
      await loadDashboardData(); // Reload data
    } catch (error: any) {
      console.error('Error applying recommendation:', error);
      toast.error('Failed to apply recommendation');
    }
  };

  const dismissRecommendation = async (recommendationId: string) => {
    try {
      await personalizationService.dismissRecommendation(recommendationId);
      setRecommendations(recommendations.filter(r => r.recommendation_id !== recommendationId));
      toast.success('Recommendation dismissed');
    } catch (error: any) {
      console.error('Error dismissing recommendation:', error);
      toast.error('Failed to dismiss recommendation');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-100 border-green-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'medium': return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'hard': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default: return <Zap className="w-4 h-4 text-gray-600" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Brain className="w-8 h-8 text-blue-600 mr-3" />
            Personalization Dashboard
          </h1>
          <p className="text-gray-600">AI-powered insights and recommendations for your campaigns</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          
          <Button
            onClick={() => setShowAiChat(true)}
            className="flex items-center space-x-2"
          >
            <MessageCircle className="w-4 h-4" />
            <span>Ask AI</span>
          </Button>
        </div>
      </div>

      {/* Profile Status */}
      {userProfile && (
        <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{userProfile.business_name}</h3>
                <p className="text-sm text-gray-600">{userProfile.industry} • {userProfile.business_type}</p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/personalization/profile')}
              className="flex items-center space-x-2"
            >
              <Settings className="w-4 h-4" />
              <span>Update Profile</span>
            </Button>
          </div>
        </Card>
      )}

      {/* Performance Summary */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Personalized Campaigns</p>
                <p className="text-2xl font-bold text-blue-600">{insights.performance_summary.personalized_campaigns}</p>
              </div>
              <Target className="w-8 h-8 text-blue-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Average Lift</p>
                <p className="text-2xl font-bold text-green-600">+{insights.performance_summary.average_lift}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Additional Revenue</p>
                <p className="text-2xl font-bold text-purple-600">${insights.performance_summary.total_additional_revenue.toLocaleString()}</p>
              </div>
              <DollarSign className="w-8 h-8 text-purple-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Top Segments</p>
                <p className="text-2xl font-bold text-orange-600">{insights.performance_summary.best_performing_segments.length}</p>
              </div>
              <Users className="w-8 h-8 text-orange-600" />
            </div>
          </Card>
        </div>
      )}

      {/* High Priority Recommendations */}
      {recommendations.length > 0 && (
        <Card className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
              Priority Recommendations
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/personalization/recommendations')}
            >
              View All
            </Button>
          </div>

          <div className="space-y-4">
            {recommendations.slice(0, 3).map((rec) => (
              <div key={rec.recommendation_id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                        {rec.priority.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500">{rec.type.replace('_', ' ')}</span>
                      {getDifficultyIcon(rec.implementation.difficulty)}
                    </div>
                    
                    <h4 className="font-medium text-gray-900 mb-1">{rec.title}</h4>
                    <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                    
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="w-3 h-3 text-green-600" />
                        <span className="text-green-600">+{rec.predicted_impact.estimated_change}% {rec.predicted_impact.metric}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Star className="w-3 h-3 text-yellow-600" />
                        <span className="text-gray-600">{rec.predicted_impact.confidence}% confidence</span>
                      </div>
                      <div className="text-gray-600">
                        {rec.implementation.time_required}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <Button
                      size="sm"
                      onClick={() => applyRecommendation(rec.recommendation_id)}
                      className="flex items-center space-x-1"
                    >
                      <CheckCircle className="w-3 h-3" />
                      <span>Apply</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => dismissRecommendation(rec.recommendation_id)}
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Create Strategy</h3>
          </div>
          <p className="text-gray-600 mb-4">Generate personalized campaign strategies based on your profile</p>
          <Button
            onClick={() => navigate('/personalization/strategy-wizard')}
            className="w-full flex items-center justify-center space-x-2"
          >
            <span>Start Wizard</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">A/B Testing</h3>
          </div>
          <p className="text-gray-600 mb-4">Create and monitor A/B tests to optimize performance</p>
          <Button
            onClick={() => navigate('/personalization/ab-testing')}
            className="w-full flex items-center justify-center space-x-2"
          >
            <span>Manage Tests</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Palette className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Content Templates</h3>
          </div>
          <p className="text-gray-600 mb-4">Browse personalized content templates for your industry</p>
          <Button
            onClick={() => navigate('/personalization/templates')}
            className="w-full flex items-center justify-center space-x-2"
          >
            <span>Browse Templates</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Card>
      </div>

      {/* Insights Overview */}
      {insights && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Audience Insights */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 text-blue-600 mr-2" />
              Top Audience Segments
            </h3>
            <div className="space-y-3">
              {insights.audience_insights.top_segments.slice(0, 3).map((segment, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">{segment.segment_name}</h4>
                    <p className="text-sm text-gray-600">
                      {segment.size.toLocaleString()} users • {(segment.engagement_rate * 100).toFixed(1)}% engagement
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">{(segment.conversion_rate * 100).toFixed(2)}%</div>
                    <div className="text-xs text-gray-500">CVR</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Content Performance */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Palette className="w-5 h-5 text-purple-600 mr-2" />
              Content Insights
            </h3>
            <div className="space-y-3">
              {insights.content_insights.top_performing_themes.slice(0, 3).map((theme, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">{theme}</h4>
                    <p className="text-sm text-gray-600">High-performing content theme</p>
                  </div>
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
              ))}
            </div>
            
            {insights.content_insights.trending_topics.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-medium text-gray-900 mb-2">Trending Topics</h4>
                <div className="flex flex-wrap gap-2">
                  {insights.content_insights.trending_topics.slice(0, 5).map((topic, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Optimization Opportunities */}
      {optimizationOpportunities.length > 0 && (
        <Card className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Zap className="w-5 h-5 text-yellow-600 mr-2" />
              Optimization Opportunities
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/personalization/optimization')}
            >
              View All
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {optimizationOpportunities.slice(0, 4).map((opportunity) => (
              <div key={opportunity.opportunity_id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{opportunity.title}</h4>
                  <span className={`px-2 py-1 text-xs rounded ${
                    opportunity.implementation_difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                    opportunity.implementation_difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {opportunity.implementation_difficulty}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{opportunity.description}</p>
                
                <div className="flex items-center justify-between">
                  <div className="text-sm">
                    <span className="text-green-600 font-medium">
                      +{opportunity.potential_impact.estimated_improvement}% {opportunity.potential_impact.metric}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    Priority: {opportunity.priority_score}/10
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* AI Chat Modal */}
      <AnimatePresence>
        {showAiChat && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <Card className="w-full max-w-2xl p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-900 flex items-center">
                  <Brain className="w-6 h-6 text-blue-600 mr-2" />
                  Ask Personalization AI
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAiChat(false)}
                >
                  Close
                </Button>
              </div>

              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Input
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    placeholder="Ask anything about your personalization strategy..."
                    onKeyDown={(e) => e.key === 'Enter' && handleAIQuestion()}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleAIQuestion}
                    disabled={isAsking || !aiQuestion.trim()}
                    className="flex items-center space-x-2"
                  >
                    {isAsking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </Button>
                </div>

                {aiResponse && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-blue-50 p-4 rounded-lg"
                  >
                    <div className="flex items-start space-x-2">
                      <Brain className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-gray-900 mb-3">{aiResponse.answer}</p>
                        
                        {aiResponse.recommendations && aiResponse.recommendations.length > 0 && (
                          <div className="mb-3">
                            <h4 className="font-medium text-gray-900 mb-2">Recommendations:</h4>
                            <ul className="space-y-1">
                              {aiResponse.recommendations.map((rec, index) => (
                                <li key={index} className="text-sm text-gray-700 flex items-start space-x-1">
                                  <CheckCircle className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" />
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {aiResponse.suggested_actions && aiResponse.suggested_actions.length > 0 && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Suggested Actions:</h4>
                            <div className="space-y-2">
                              {aiResponse.suggested_actions.map((action, index) => (
                                <Button
                                  key={index}
                                  variant="outline"
                                  size="sm"
                                  className="mr-2"
                                >
                                  {action}
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="text-xs text-gray-500 mt-3">
                          Confidence: {aiResponse.confidence}%
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PersonalizationDashboard;