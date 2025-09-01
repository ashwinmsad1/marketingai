import React from 'react';
import { motion } from 'framer-motion';
import { Facebook, Instagram, AlertTriangle, CheckCircle, ExternalLink } from 'lucide-react';

interface MetaAccount {
  id: string;
  ad_account_id: string;
  account_name: string;
  currency: string;
  timezone: string;
  facebook_page_id?: string;
  instagram_business_id?: string;
  is_active: boolean;
}

interface MetaAccountSelectorProps {
  accounts: MetaAccount[];
  selectedAccountId: string;
  onAccountSelect: (accountId: string) => void;
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

const MetaAccountSelector: React.FC<MetaAccountSelectorProps> = ({
  accounts,
  selectedAccountId,
  onAccountSelect,
  loading = false,
  error,
  onRetry
}) => {
  if (loading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Select Meta Account</h3>
        <div className="animate-pulse">
          <div className="h-20 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Select Meta Account</h3>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-red-800 mb-2">
            Failed to Load Meta Accounts
          </h4>
          <p className="text-red-700 mb-4">{error}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    );
  }

  if (accounts.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Meta Account Required</h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-yellow-800 mb-2">
            No Meta Accounts Connected
          </h4>
          <p className="text-yellow-700 mb-4">
            You need to connect a Facebook/Instagram business account to create campaigns.
          </p>
          <a
            href="/meta/connect"
            className="inline-flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            Connect Meta Account
            <ExternalLink className="w-4 h-4 ml-2" />
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Select Meta Account</h3>
      <p className="text-gray-600 text-sm">
        Choose which Facebook/Instagram account to use for this campaign
      </p>

      <div className="space-y-3">
        {accounts.map((account) => (
          <motion.div
            key={account.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className={`relative p-4 border rounded-lg cursor-pointer transition-all ${
              selectedAccountId === account.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            } ${!account.is_active ? 'opacity-60' : ''}`}
            onClick={() => account.is_active && onAccountSelect(account.id)}
          >
            {/* Selection Indicator */}
            {selectedAccountId === account.id && (
              <div className="absolute top-3 right-3">
                <CheckCircle className="w-5 h-5 text-blue-600" />
              </div>
            )}

            <div className="flex items-start space-x-4">
              {/* Account Icon */}
              <div className="flex-shrink-0 p-2 bg-blue-100 rounded-lg">
                <Facebook className="w-6 h-6 text-blue-600" />
              </div>

              {/* Account Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900 truncate">
                      {account.account_name}
                    </h4>
                    <p className="text-sm text-gray-500 truncate">
                      Account ID: {account.ad_account_id}
                    </p>
                  </div>
                  
                  {/* Status Badge */}
                  <div className="flex-shrink-0 ml-2">
                    {account.is_active ? (
                      <div className="flex flex-col space-y-1">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Active
                        </span>
                        {!account.facebook_page_id && !account.instagram_business_id && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            Limited
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        Inactive
                      </span>
                    )}
                  </div>
                </div>

                {/* Account Meta Info */}
                <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                  <span>💰 {account.currency}</span>
                  <span>🕐 {account.timezone}</span>
                </div>

                {/* Connected Services */}
                <div className="mt-3 flex items-center space-x-4">
                  {/* Facebook */}
                  <div className="flex items-center text-xs text-blue-600">
                    <Facebook className="w-3 h-3 mr-1" />
                    Facebook Ads
                  </div>

                  {/* Facebook Page */}
                  {account.facebook_page_id && (
                    <div className="flex items-center text-xs text-blue-600">
                      <Facebook className="w-3 h-3 mr-1" />
                      Page Connected
                    </div>
                  )}

                  {/* Instagram */}
                  {account.instagram_business_id ? (
                    <div className="flex items-center text-xs text-purple-600">
                      <Instagram className="w-3 h-3 mr-1" />
                      Instagram
                    </div>
                  ) : (
                    <div className="flex items-center text-xs text-gray-400">
                      <Instagram className="w-3 h-3 mr-1" />
                      No Instagram
                    </div>
                  )}
                </div>

                {!account.is_active && (
                  <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-600">
                    <p className="font-medium">Account Inactive</p>
                    <p>This account may have expired permissions or been disconnected. Please refresh your connection in Meta Accounts or reconnect.</p>
                  </div>
                )}
                
                {account.is_active && !account.facebook_page_id && !account.instagram_business_id && (
                  <div className="mt-2 p-2 bg-yellow-50 rounded text-xs text-yellow-600">
                    <p className="font-medium">Limited Functionality</p>
                    <p>Connect a Facebook Page or Instagram Business account for full campaign capabilities.</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Help Text */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <p className="font-medium text-gray-700 mb-1">💡 Tip:</p>
        <p>
          Each account can run multiple campaigns simultaneously. Instagram campaigns 
          require a connected Instagram Business account.
        </p>
      </div>
    </div>
  );
};

export default MetaAccountSelector;