import React, { useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  Target,
  Users,
  Calendar,
  Download,
  Filter,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';
import { motion } from 'framer-motion';

interface AnalyticsProps {
  user: {
    name: string;
    subscription_tier: string;
  };
}

const Analytics: React.FC<AnalyticsProps> = ({ user }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');

  // Mock analytics data
  const analyticsData = {
    overview: {
      total_revenue: 47820.50,
      total_spent: 8950.00,
      overall_roi: 434.2,
      total_conversions: 1247,
      avg_ctr: 3.8,
      top_performing_campaign: 'Restaurant Summer Special'
    },
    revenue_by_campaign: [
      { name: 'Restaurant Summer Special', revenue: 18500, spend: 2500, roi: 640 },
      { name: 'Fitness Challenge Viral', revenue: 12800, spend: 1800, roi: 611 },
      { name: 'E-commerce Flash Sale', revenue: 8900, spend: 1200, roi: 642 },
      { name: 'Local Service Push', revenue: 7620, spend: 3450, roi: 121 }
    ],
    performance_trends: [
      { date: '2025-01-01', revenue: 2400, spend: 400, conversions: 24 },
      { date: '2025-01-02', revenue: 1398, spend: 300, conversions: 18 },
      { date: '2025-01-03', revenue: 9800, spend: 800, conversions: 98 },
      { date: '2025-01-04', revenue: 3908, spend: 550, conversions: 42 },
      { date: '2025-01-05', revenue: 4800, spend: 600, conversions: 56 },
      { date: '2025-01-06', revenue: 3800, spend: 450, conversions: 48 },
      { date: '2025-01-07', revenue: 4300, spend: 500, conversions: 52 }
    ],
    industry_performance: [
      { industry: 'Restaurant', campaigns: 4, revenue: 18500, avg_roi: 640 },
      { industry: 'Fitness', campaigns: 3, revenue: 12800, avg_roi: 511 },
      { industry: 'E-commerce', campaigns: 2, revenue: 8900, avg_roi: 642 },
      { industry: 'Local Services', campaigns: 3, revenue: 7620, avg_roi: 221 }
    ],
    campaign_types: [
      { type: 'Industry Optimized', count: 8, revenue: 28400 },
      { type: 'Viral', count: 3, revenue: 12800 },
      { type: 'Competitor Beating', count: 1, revenue: 6620 }
    ]
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getROIColor = (roi: number) => {
    if (roi >= 500) return 'text-green-600';
    if (roi >= 300) return 'text-blue-600';
    if (roi >= 200) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p className="text-gray-600 mt-2">Deep insights into your campaign performance and ROI</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="input-field w-40"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              <button className="btn-secondary flex items-center">
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </button>
            </div>
          </div>
        </motion.div>

        {/* Key Metrics Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-green-600 text-sm font-medium">+24.5% vs last period</span>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(analyticsData.overview.total_revenue)}
              </p>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-blue-600 text-sm font-medium">+67.2% ROI</span>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Overall ROI</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData.overview.overall_roi.toFixed(1)}%
              </p>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-purple-600 text-sm font-medium">+12.8% conversions</span>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Conversions</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData.overview.total_conversions.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-orange-100 p-3 rounded-lg">
                <Target className="w-6 h-6 text-orange-600" />
              </div>
              <span className="text-orange-600 text-sm font-medium">+8.4% CTR</span>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Average CTR</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData.overview.avg_ctr.toFixed(1)}%
              </p>
            </div>
          </div>
        </motion.div>

        {/* Performance Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8"
        >
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-900">Revenue Trend</h3>
              <div className="flex items-center space-x-2">
                <select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="revenue">Revenue</option>
                  <option value="spend">Spend</option>
                  <option value="conversions">Conversions</option>
                </select>
                <LineChart className="w-5 h-5 text-gray-400" />
              </div>
            </div>
            
            {/* Simple chart representation */}
            <div className="h-64 bg-gradient-to-t from-blue-50 to-transparent rounded-lg flex items-end justify-between p-4">
              {analyticsData.performance_trends.map((trend, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div
                    className="bg-blue-500 rounded-t-lg w-8 min-h-4"
                    style={{
                      height: `${(trend[selectedMetric as keyof typeof trend] as number / 
                        Math.max(...analyticsData.performance_trends.map(t => t[selectedMetric as keyof typeof t] as number))) * 200}px`
                    }}
                  ></div>
                  <span className="text-xs text-gray-500 mt-2">
                    {new Date(trend.date).getDate()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-900">Campaign Types Performance</h3>
              <PieChart className="w-5 h-5 text-gray-400" />
            </div>
            
            <div className="space-y-4">
              {analyticsData.campaign_types.map((type, index) => {
                const percentage = (type.revenue / analyticsData.overview.total_revenue) * 100;
                return (
                  <div key={index}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-900">{type.type}</span>
                      <span className="text-sm text-gray-600">{formatCurrency(type.revenue)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between items-center mt-1">
                      <span className="text-xs text-gray-500">{type.count} campaigns</span>
                      <span className="text-xs text-gray-500">{percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Campaign Performance Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-900">Top Performing Campaigns</h3>
            <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
              View All Campaigns
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Revenue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Spend
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    ROI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analyticsData.revenue_by_campaign.map((campaign, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{campaign.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatCurrency(campaign.revenue)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatCurrency(campaign.spend)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${getROIColor(campaign.roi)}`}>
                        {campaign.roi.toFixed(0)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-full bg-gray-200 rounded-full h-2 mr-3" style={{ width: '60px' }}>
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${Math.min((campaign.roi / 1000) * 100, 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-500">Excellent</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Industry Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-900">Performance by Industry</h3>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {analyticsData.industry_performance.map((industry, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{industry.industry}</h4>
                  <span className="text-xs text-gray-500">{industry.campaigns} campaigns</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Revenue</span>
                    <span className="text-sm font-medium">{formatCurrency(industry.revenue)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg ROI</span>
                    <span className={`text-sm font-medium ${getROIColor(industry.avg_roi)}`}>
                      {industry.avg_roi.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Analytics;