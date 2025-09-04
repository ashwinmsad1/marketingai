import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { setNavigationHandler } from './services/api';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
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
import Subscription from './pages/Subscription';
import BillingHistory from './pages/BillingHistory';
import EmailVerification from './pages/EmailVerification';
import DemoNavigation from './components/DemoNavigation';
import { AppLayout } from './design-system';

// Personalization Pages
import ProfileSetup from './pages/ProfileSetup';
import PersonalizationDashboard from './pages/PersonalizationDashboard';
import CampaignStrategyWizard from './pages/CampaignStrategyWizard';
import ABTestingDashboard from './pages/ABTestingDashboard';
import ContentTemplatesManager from './pages/ContentTemplatesManager';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime in v5)
    },
  },
});

// Inner component to access useNavigate
const AppContent: React.FC = () => {
  const navigate = useNavigate();

  // Set up navigation handler for API service
  useEffect(() => {
    setNavigationHandler((path: string) => {
      navigate(path);
    });

    // Cleanup function to remove navigation handler
    return () => {
      setNavigationHandler(() => {});
    };
  }, [navigate]);

  const handleMediaCreated = (url: string, type: 'image' | 'video', prompt: string) => {
    console.log('Media created:', { url, type, prompt });
  };

  return (
    <ErrorBoundary showDetails={true}>
      <AuthProvider>
        <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-email" element={<EmailVerification />} />
            
            {/* Protected Routes - wrapped in AppLayout */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Dashboard user={{ name: 'Demo User', subscription_tier: 'free' }} />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/create-campaign" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <ErrorBoundary>
                    <AppLayout>
                      <CreateCampaign />
                    </AppLayout>
                  </ErrorBoundary>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/campaigns" 
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <CampaignsList 
                      campaigns={[]}
                      onViewCampaign={() => {}}
                      onEditCampaign={() => {}}
                      onToggleCampaign={() => {}}
                      onDeleteCampaign={() => {}}
                    />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/analytics" 
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Analytics />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/media-creation" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <AppLayout>
                    <MediaCreation onMediaCreated={handleMediaCreated} />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/meta/connect" 
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ConnectMeta />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/meta/callback" 
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ConnectMeta />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/meta/accounts" 
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <MetaAccounts />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/subscription" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <Subscription />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/billing/history" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <BillingHistory />
                </ProtectedRoute>
              } 
            />
            
            {/* Personalization Routes */}
            <Route 
              path="/personalization/profile" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <AppLayout>
                    <ProfileSetup />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/personalization/dashboard" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <AppLayout>
                    <PersonalizationDashboard />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/personalization/strategy-wizard" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <AppLayout>
                    <CampaignStrategyWizard />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/personalization/ab-testing" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <AppLayout>
                    <ABTestingDashboard />
                  </AppLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/personalization/templates" 
              element={
                <ProtectedRoute requiresVerification={true}>
                  <AppLayout>
                    <ContentTemplatesManager />
                  </AppLayout>
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
      </ErrorBoundary>
  );
};

const AppWithAuth: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContent />
        
        {/* React Query Devtools - only in development */}
        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
      </Router>
    </QueryClientProvider>
  );
};

export default AppWithAuth;