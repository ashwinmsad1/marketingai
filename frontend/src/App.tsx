import React, { useState } from 'react';
import { motion } from 'framer-motion';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import CreateCampaign from './pages/CreateCampaign';
import CampaignsList from './pages/CampaignsList';
import Analytics from './pages/Analytics';
import MediaCreation from './pages/MediaCreation';
import Navbar from './components/Layout/Navbar';
import { User, Campaign } from './types';
import './index.css';

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Mock user data
  const mockUser: User = {
    id: '1',
    email: 'john.doe@example.com',
    name: 'John Doe',
    subscription_tier: 'professional',
    created_at: '2024-12-01',
    industry: 'Restaurant'
  };

  // Mock campaigns data
  const mockCampaigns: Campaign[] = [
    {
      campaign_id: '1',
      user_id: '1',
      name: 'Restaurant Summer Special',
      type: 'industry_optimized',
      status: 'active',
      created_at: '2025-01-01',
      updated_at: '2025-01-01',
      spend: 250,
      roi: 640,
      ctr: 3.2,
      performance_status: 'excellent'
    },
    {
      campaign_id: '2',
      user_id: '1',
      name: 'Fitness Challenge Viral',
      type: 'viral',
      status: 'active',
      created_at: '2024-12-28',
      updated_at: '2024-12-28',
      spend: 180,
      roi: 411,
      ctr: 2.8,
      performance_status: 'good'
    },
    {
      campaign_id: '3',
      user_id: '1',
      name: 'Competitor Analysis Fashion',
      type: 'competitor_beating',
      status: 'paused',
      created_at: '2024-12-25',
      updated_at: '2024-12-25',
      spend: 320,
      roi: 275,
      ctr: 2.1,
      performance_status: 'poor'
    }
  ];

  const handleNavigation = (page: string) => {
    setCurrentPage(page);
    if (page !== 'landing') {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  };

  const handleCampaignAction = (action: string, campaignId: string) => {
    console.log(`${action} campaign:`, campaignId);
    // In a real app, this would make API calls
  };

  const handleCreateCampaign = (campaignData: any) => {
    console.log('Creating campaign:', campaignData);
    // In a real app, this would make an API call
    // After successful creation, navigate to campaigns list
    setCurrentPage('campaigns');
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage />;
      
      case 'dashboard':
        return <Dashboard user={mockUser} />;
      
      case 'create-campaign':
        return <CreateCampaign onCreateCampaign={handleCreateCampaign} />;
      
      case 'campaigns':
        return (
          <CampaignsList
            campaigns={mockCampaigns}
            onViewCampaign={(id) => handleCampaignAction('view', id)}
            onEditCampaign={(id) => handleCampaignAction('edit', id)}
            onToggleCampaign={(id) => handleCampaignAction('toggle', id)}
            onDeleteCampaign={(id) => handleCampaignAction('delete', id)}
          />
        );
      
      case 'analytics':
        return <Analytics user={mockUser} />;
      
      case 'media-creation':
        return <MediaCreation onMediaCreated={(url, type, prompt) => console.log('Media created:', { url, type, prompt })} />;
      
      default:
        return <LandingPage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && currentPage !== 'landing' && (
        <Navbar
          user={mockUser}
          onNavigate={handleNavigation}
          currentPage={currentPage}
        />
      )}
      
      <motion.div
        key={currentPage}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {renderPage()}
      </motion.div>

      {/* Demo Navigation for Testing - Remove in production */}
      {currentPage === 'landing' && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1 }}
          className="fixed top-6 right-6 z-50"
        >
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-gray-200/50 p-5 min-w-56">
            {/* Header */}
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-100">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-semibold text-gray-800">Demo Mode</span>
              </div>
              <span className="text-lg">🚀</span>
            </div>
            
            {/* Navigation Buttons */}
            <div className="space-y-3">
              <motion.button
                whileHover={{ scale: 1.02, x: 2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigation('dashboard')}
                className="w-full flex items-center space-x-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-3 rounded-xl font-medium text-sm shadow-md hover:shadow-lg transition-all duration-200 group"
              >
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  📊
                </div>
                <span>Dashboard</span>
                <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">→</div>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, x: 2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigation('create-campaign')}
                className="w-full flex items-center space-x-3 bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-3 rounded-xl font-medium text-sm shadow-md hover:shadow-lg transition-all duration-200 group"
              >
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  ✨
                </div>
                <span>Create Campaign</span>
                <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">→</div>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, x: 2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigation('media-creation')}
                className="w-full flex items-center space-x-3 bg-gradient-to-r from-pink-500 to-rose-600 text-white px-4 py-3 rounded-xl font-medium text-sm shadow-md hover:shadow-lg transition-all duration-200 group"
              >
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  🎨
                </div>
                <span>Create Content</span>
                <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">→</div>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, x: 2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigation('campaigns')}
                className="w-full flex items-center space-x-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white px-4 py-3 rounded-xl font-medium text-sm shadow-md hover:shadow-lg transition-all duration-200 group"
              >
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  🎯
                </div>
                <span>My Campaigns</span>
                <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">→</div>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, x: 2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigation('analytics')}
                className="w-full flex items-center space-x-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white px-4 py-3 rounded-xl font-medium text-sm shadow-md hover:shadow-lg transition-all duration-200 group"
              >
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  📈
                </div>
                <span>Analytics</span>
                <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">→</div>
              </motion.button>
            </div>

            {/* Footer */}
            <div className="mt-4 pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-500 text-center">
                Experience the full platform
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default App;