import React, { useState } from 'react';
import {
  Search,
  Filter,
  MoreVertical,
  Play,
  Pause,
  Eye,
  Edit,
  Trash2,
  TrendingUp,
  DollarSign,
  Users,
  Target
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Campaign } from '../types';

interface CampaignsListProps {
  campaigns: Campaign[];
  onViewCampaign: (campaignId: string) => void;
  onEditCampaign: (campaignId: string) => void;
  onToggleCampaign: (campaignId: string) => void;
  onDeleteCampaign: (campaignId: string) => void;
}

const CampaignsList: React.FC<CampaignsListProps> = ({
  campaigns,
  onViewCampaign,
  onEditCampaign,
  onToggleCampaign,
  onDeleteCampaign
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([]);

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || campaign.status === filterStatus;
    const matchesType = filterType === 'all' || campaign.type === filterType;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'badge-success';
      case 'paused': return 'badge-warning';
      case 'completed': return 'badge-primary';
      default: return 'badge-danger';
    }
  };

  const getPerformanceColor = (status?: string) => {
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
      case 'image': return '🖼️';
      case 'video': return '🎥';
      default: return '🎨';
    }
  };

  const handleSelectAll = () => {
    if (selectedCampaigns.length === filteredCampaigns.length) {
      setSelectedCampaigns([]);
    } else {
      setSelectedCampaigns(filteredCampaigns.map(c => c.campaign_id));
    }
  };

  const handleSelectCampaign = (campaignId: string) => {
    setSelectedCampaigns(prev => 
      prev.includes(campaignId)
        ? prev.filter(id => id !== campaignId)
        : [...prev, campaignId]
    );
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
              <h1 className="text-3xl font-bold text-gray-900">My Campaigns</h1>
              <p className="text-gray-600 mt-2">Manage and monitor your AI-generated marketing campaigns</p>
            </div>
            <button className="btn-primary">
              <Target className="w-4 h-4 mr-2" />
              New Campaign
            </button>
          </div>

          {/* Filters and Search */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search campaigns..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 input-field"
              />
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input-field"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input-field"
            >
              <option value="all">All Types</option>
              <option value="viral">Viral</option>
              <option value="industry_optimized">Industry Optimized</option>
              <option value="competitor_beating">Competitor Beating</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
            </select>

            <button className="btn-secondary flex items-center justify-center">
              <Filter className="w-4 h-4 mr-2" />
              More Filters
            </button>
          </div>
        </motion.div>

        {/* Campaign Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">{campaigns.length}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">
                  {campaigns.filter(c => c.status === 'active').length}
                </p>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <Play className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Spend</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${campaigns.reduce((sum, c) => sum + (c.spend || 0), 0).toLocaleString()}
                </p>
              </div>
              <div className="bg-orange-100 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg. ROI</p>
                <p className="text-2xl font-bold text-green-600">
                  {campaigns.length > 0 
                    ? Math.round(campaigns.reduce((sum, c) => sum + (c.roi || 0), 0) / campaigns.length)
                    : 0}%
                </p>
              </div>
              <div className="bg-purple-100 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Campaigns Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Campaign Performance</h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleSelectAll}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                {selectedCampaigns.length === filteredCampaigns.length ? 'Deselect All' : 'Select All'}
              </button>
              {selectedCampaigns.length > 0 && (
                <button className="btn-danger text-sm">
                  Delete Selected ({selectedCampaigns.length})
                </button>
              )}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Spend
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ROI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCampaigns.map((campaign) => (
                  <tr key={campaign.campaign_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedCampaigns.includes(campaign.campaign_id)}
                          onChange={() => handleSelectCampaign(campaign.campaign_id)}
                          className="mr-4 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <div className="flex items-center">
                          <div className="text-2xl mr-3">
                            {getCampaignTypeIcon(campaign.type)}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">{campaign.name}</div>
                            <div className="text-sm text-gray-500">
                              Created {new Date(campaign.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900 capitalize">
                        {campaign.type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={getStatusColor(campaign.status)}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm">
                        <div className={`font-medium ${getPerformanceColor(campaign.performance_status)}`}>
                          {campaign.performance_status || 'N/A'}
                        </div>
                        <div className="text-gray-500">
                          CTR: {campaign.ctr?.toFixed(1) || 'N/A'}%
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${campaign.spend?.toLocaleString() || '0'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${getPerformanceColor(campaign.performance_status)}`}>
                        {campaign.roi?.toFixed(0) || '0'}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        {campaign.status === 'active' ? (
                          <button
                            onClick={() => onToggleCampaign(campaign.campaign_id)}
                            className="p-1 text-orange-600 hover:text-orange-800"
                            title="Pause"
                          >
                            <Pause className="w-4 h-4" />
                          </button>
                        ) : (
                          <button
                            onClick={() => onToggleCampaign(campaign.campaign_id)}
                            className="p-1 text-green-600 hover:text-green-800"
                            title="Resume"
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => onViewCampaign(campaign.campaign_id)}
                          className="p-1 text-blue-600 hover:text-blue-800"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onEditCampaign(campaign.campaign_id)}
                          className="p-1 text-gray-600 hover:text-gray-800"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDeleteCampaign(campaign.campaign_id)}
                          className="p-1 text-red-600 hover:text-red-800"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredCampaigns.length === 0 && (
            <div className="text-center py-12">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns found</h3>
              <p className="text-gray-500 mb-4">
                {searchTerm || filterStatus !== 'all' || filterType !== 'all' 
                  ? 'Try adjusting your filters or search terms'
                  : 'Create your first AI-powered marketing campaign'
                }
              </p>
              <button className="btn-primary">
                <Target className="w-4 h-4 mr-2" />
                Create Campaign
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default CampaignsList;