import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CreateCampaign from './pages/CreateCampaign';
import CampaignsList from './pages/CampaignsList';
import Analytics from './pages/Analytics';
import MediaCreation from './pages/MediaCreation';
import ConnectMeta from './pages/ConnectMeta';
import MetaAccounts from './pages/MetaAccounts';
import DemoNavigation from './components/DemoNavigation';

const AppWithAuth: React.FC = () => {
  const handleMediaCreated = (url: string, type: 'image' | 'video', prompt: string) => {
    console.log('Media created:', { url, type, prompt });
  };

  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard user={{ name: 'Demo User', subscription_tier: 'free' }} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/create-campaign" 
            element={
              <ProtectedRoute>
                <CreateCampaign />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/campaigns" 
            element={
              <ProtectedRoute>
                <CampaignsList 
                  campaigns={[]}
                  onViewCampaign={() => {}}
                  onEditCampaign={() => {}}
                  onToggleCampaign={() => {}}
                  onDeleteCampaign={() => {}}
                />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute>
                <Analytics user={{ name: 'Demo User', subscription_tier: 'free' }} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/media-creation" 
            element={
              <ProtectedRoute>
                <MediaCreation onMediaCreated={handleMediaCreated} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/meta/connect" 
            element={
              <ProtectedRoute>
                <ConnectMeta />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/meta/callback" 
            element={
              <ProtectedRoute>
                <ConnectMeta />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/meta/accounts" 
            element={
              <ProtectedRoute>
                <MetaAccounts />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirect unknown routes to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>

        {/* Demo Navigation - only show in development */}
        {import.meta.env.DEV && <DemoNavigation />}

        {/* Toast notifications */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </AuthProvider>
    </Router>
  );
};

export default AppWithAuth;