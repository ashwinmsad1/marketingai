import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Facebook, 
  Instagram, 
  Plus, 
  Settings, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw, 
  Trash2,
  ExternalLink,
  Calendar,
  DollarSign,
  Globe,
  Clock
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { metaService } from '../services/api';
import toast from 'react-hot-toast';

interface MetaAccount {
  id: string;
  ad_account_id: string;
  account_name: string;
  currency: string;
  timezone: string;
  facebook_page_id?: string;
  instagram_business_id?: string;
  is_active: boolean;
  created_at: string;
  last_sync?: string;
}

const MetaAccounts: React.FC = () => {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<MetaAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string>('');

  useEffect(() => {
    if (user) {
      loadAccounts();
    }
  }, [user]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await metaService.getConnectedAccounts();
      setAccounts(response.data.accounts);
    } catch (error: any) {
      console.error('Failed to load Meta accounts:', error);
      toast.error('Failed to load Meta accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshToken = async (accountId: string) => {
    try {
      setActionLoading(accountId);
      await metaService.refreshToken(accountId);
      toast.success('Token refreshed successfully');
      await loadAccounts(); // Reload to get updated data
    } catch (error: any) {
      console.error('Failed to refresh token:', error);
      toast.error(error.response?.data?.detail || 'Failed to refresh token');
    } finally {
      setActionLoading('');
    }
  };

  const handleDisconnectAccount = async (accountId: string, accountName: string) => {
    if (!confirm(`Are you sure you want to disconnect "${accountName}"? This will stop all campaigns using this account.`)) {
      return;
    }

    try {
      setActionLoading(accountId);
      await metaService.disconnectAccount(accountId);
      toast.success('Account disconnected successfully');
      await loadAccounts();
    } catch (error: any) {
      console.error('Failed to disconnect account:', error);
      toast.error(error.response?.data?.detail || 'Failed to disconnect account');
    } finally {
      setActionLoading('');
    }
  };

  const getAccountStatus = (account: MetaAccount) => {
    if (!account.is_active) {
      return { 
        status: 'inactive', 
        color: 'red', 
        icon: AlertTriangle, 
        text: 'Inactive' 
      };
    }
    
    // Check if token might be expired (simplified check)
    const lastSync = account.last_sync ? new Date(account.last_sync) : null;
    const daysSinceSync = lastSync ? Math.floor((Date.now() - lastSync.getTime()) / (1000 * 60 * 60 * 24)) : null;
    
    if (daysSinceSync && daysSinceSync > 30) {
      return { 
        status: 'warning', 
        color: 'yellow', 
        icon: AlertTriangle, 
        text: 'Token may need refresh' 
      };
    }
    
    return { 
      status: 'active', 
      color: 'green', 
      icon: CheckCircle, 
      text: 'Active' 
    };
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-64 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Meta Accounts</h1>
            <p className="text-gray-600 mt-2">
              Manage your connected Facebook and Instagram business accounts
            </p>
          </div>
          
          <motion.a
            href="/meta/connect"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="w-5 h-5 mr-2" />
            Connect New Account
          </motion.a>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <Facebook className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Accounts</p>
                <p className="text-2xl font-bold text-gray-900">{accounts.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Active Accounts</p>
                <p className="text-2xl font-bold text-gray-900">
                  {accounts.filter(acc => acc.is_active).length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-full">
                <Instagram className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Instagram Connected</p>
                <p className="text-2xl font-bold text-gray-900">
                  {accounts.filter(acc => acc.instagram_business_id).length}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Accounts List */}
        {accounts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg p-12 text-center shadow-sm border border-gray-200"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-6">
              <Facebook className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              No Meta Accounts Connected
            </h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Connect your Facebook and Instagram business accounts to start creating 
              AI-powered marketing campaigns.
            </p>
            <a
              href="/meta/connect"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              <Plus className="w-5 h-5 mr-2" />
              Connect Your First Account
            </a>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AnimatePresence>
              {accounts.map((account, index) => {
                const status = getAccountStatus(account);
                const StatusIcon = status.icon;
                
                return (
                  <motion.div
                    key={account.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
                  >
                    {/* Account Header */}
                    <div className="p-6 border-b border-gray-100">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4">
                          <div className="p-3 bg-blue-100 rounded-full">
                            <Facebook className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {account.account_name}
                            </h3>
                            <p className="text-sm text-gray-500">
                              Account ID: {account.ad_account_id}
                            </p>
                            <div className="flex items-center mt-2">
                              <StatusIcon className={`w-4 h-4 mr-2 text-${status.color}-500`} />
                              <span className={`text-sm text-${status.color}-600 font-medium`}>
                                {status.text}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleRefreshToken(account.id)}
                            disabled={actionLoading === account.id}
                            className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Refresh Token"
                          >
                            <RefreshCw className={`w-5 h-5 ${
                              actionLoading === account.id ? 'animate-spin' : ''
                            }`} />
                          </button>
                          <button
                            onClick={() => handleDisconnectAccount(account.id, account.account_name)}
                            disabled={actionLoading === account.id}
                            className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                            title="Disconnect Account"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Account Details */}
                    <div className="p-6">
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-600">Currency: {account.currency}</span>
                        </div>
                        <div className="flex items-center">
                          <Globe className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-600">Timezone: {account.timezone}</span>
                        </div>
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-600">
                            Connected: {formatDate(account.created_at)}
                          </span>
                        </div>
                        {account.last_sync && (
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-600">
                              Synced: {formatDate(account.last_sync)}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Connected Services */}
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium text-gray-700">Connected Services</h4>
                        
                        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center">
                            <Facebook className="w-5 h-5 text-blue-600 mr-3" />
                            <span className="text-sm font-medium text-blue-900">Facebook Ads</span>
                          </div>
                          <CheckCircle className="w-5 h-5 text-blue-600" />
                        </div>

                        {account.facebook_page_id && (
                          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                            <div className="flex items-center">
                              <Facebook className="w-5 h-5 text-blue-600 mr-3" />
                              <span className="text-sm font-medium text-blue-900">Facebook Page</span>
                            </div>
                            <CheckCircle className="w-5 h-5 text-blue-600" />
                          </div>
                        )}

                        {account.instagram_business_id ? (
                          <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                            <div className="flex items-center">
                              <Instagram className="w-5 h-5 text-purple-600 mr-3" />
                              <span className="text-sm font-medium text-purple-900">Instagram Business</span>
                            </div>
                            <CheckCircle className="w-5 h-5 text-purple-600" />
                          </div>
                        ) : (
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center">
                              <Instagram className="w-5 h-5 text-gray-400 mr-3" />
                              <span className="text-sm text-gray-600">Instagram Business</span>
                            </div>
                            <span className="text-xs text-gray-500">Not Connected</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Account Actions */}
                    <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          Use this account in campaign creation
                        </span>
                        <a
                          href={`/create-campaign?account=${account.id}`}
                          className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Create Campaign
                          <ExternalLink className="w-4 h-4 ml-1" />
                        </a>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {/* Help Section */}
        {accounts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6"
          >
            <div className="flex items-start space-x-3">
              <Settings className="w-6 h-6 text-blue-600 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-2">Account Management Tips</h4>
                <ul className="text-blue-800 text-sm space-y-1">
                  <li>• Refresh tokens if you see warning status or campaign failures</li>
                  <li>• Connect Instagram Business accounts for cross-platform campaigns</li>
                  <li>• Each account can be used for multiple campaigns simultaneously</li>
                  <li>• Disconnecting an account will pause all associated campaigns</li>
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default MetaAccounts;