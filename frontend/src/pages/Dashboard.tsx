import React, { useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  Target,
  Zap,
  Calendar,
  ArrowUp,
  ArrowDown,
  Play,
  Pause,
  MoreVertical,
  Eye
} from 'lucide-react';
import { motion } from 'framer-motion';

interface DashboardProps {
  user: {
    name: string;
    subscription_tier: string;
  };
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');

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
        name: 'Competitor Analysis Fashion',
        type: 'competitor_beating',
        status: 'paused',
        spend: 320,
        revenue: 1200,
        roi: 275,
        ctr: 2.1,
        created_at: '2024-12-25',
        performance_status: 'poor'
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
      case 'viral': return '🔥';
      case 'industry_optimized': return '🏭';
      case 'competitor_beating': return '🥊';
      default: return '🎨';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
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
                className="input-field w-32"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
              <button className="btn-primary">
                <Zap className="w-4 h-4 mr-2" />
                New Campaign
              </button>
            </div>
          </div>
          
          {/* Subscription Tier Badge */}
          <div className="inline-flex items-center bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-full">
            <span className="text-sm font-medium capitalize">{user.subscription_tier} Plan</span>
          </div>
        </motion.div>

        {/* Key Metrics Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <div className="card">
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
          </div>

          <div className="card">
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
          </div>

          <div className="card">
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
          </div>

          <div className="card">
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
          </div>
        </motion.div>

        {/* Recent Campaigns */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Campaigns</h2>
            <button className="text-blue-600 hover:text-blue-700 font-medium">
              View All
            </button>
          </div>

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
                      <button className="p-2 text-gray-400 hover:text-orange-600 transition-colors">
                        <Pause className="w-4 h-4" />
                      </button>
                    ) : (
                      <button className="p-2 text-gray-400 hover:text-green-600 transition-colors">
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8"
        >
          <div className="card-hover text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Zap className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="font-semibold mb-2">Quick Campaign</h3>
            <p className="text-sm text-gray-600 mb-4">Create campaign in 60 seconds</p>
            <button className="btn-primary w-full">Start Now</button>
          </div>

          <div className="card-hover text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="font-semibold mb-2">Viral Trends</h3>
            <p className="text-sm text-gray-600 mb-4">Create from trending topics</p>
            <button className="btn-secondary w-full">Explore Trends</button>
          </div>

          <div className="card-hover text-center">
            <div className="bg-red-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Target className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="font-semibold mb-2">Beat Competitors</h3>
            <p className="text-sm text-gray-600 mb-4">Analyze & outperform rivals</p>
            <button className="btn-secondary w-full">Analyze Now</button>
          </div>

          <div className="card-hover text-center">
            <div className="bg-green-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="font-semibold mb-2">ROI Report</h3>
            <p className="text-sm text-gray-600 mb-4">Detailed success analytics</p>
            <button className="btn-secondary w-full">View Report</button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;