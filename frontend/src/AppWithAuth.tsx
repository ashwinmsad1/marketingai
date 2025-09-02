import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
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
import Subscription from './pages/Subscription';
import BillingHistory from './pages/BillingHistory';
import EmailVerification from './pages/EmailVerification';
import DemoNavigation from './components/DemoNavigation';
import { AppLayout } from './design-system';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime in v5)
    },
  },
});

const AppWithAuth: React.FC = () => {
  const handleMediaCreated = (url: string, type: 'image' | 'video', prompt: string) => {
    console.log('Media created:', { url, type, prompt });
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
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
                  <AppLayout>
                    <CreateCampaign />
                  </AppLayout>
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
      
      {/* React Query Devtools - only in development */}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
};

export default AppWithAuth;