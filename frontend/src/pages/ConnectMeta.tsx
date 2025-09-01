import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Facebook, 
  Instagram, 
  ArrowRight, 
  Shield, 
  Check, 
  AlertCircle,
  ExternalLink,
  Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { metaService } from '../services/api';
import toast from 'react-hot-toast';

const ConnectMeta: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'intro' | 'connecting' | 'callback' | 'success' | 'error'>('intro');
  const [connectedAccounts, setConnectedAccounts] = useState<any[]>([]);
  const [error, setError] = useState<string>('');

  // Handle OAuth callback
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setStep('error');
      setError('User cancelled Meta connection or permission denied');
      return;
    }

    if (code && state) {
      handleOAuthCallback(code, state);
    }
  }, [searchParams]);

  const handleOAuthCallback = async (code: string, state: string) => {
    setStep('callback');
    setLoading(true);

    try {
      const response = await metaService.handleOAuthCallback(code, state);
      
      if (response.data.success) {
        setConnectedAccounts(response.data.accounts);
        setStep('success');
        toast.success(response.data.message);
      } else {
        throw new Error(response.data.message || 'Failed to connect Meta account');
      }
    } catch (error: any) {
      console.error('OAuth callback failed:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to connect Meta account');
      setStep('error');
      toast.error('Failed to connect Meta account');
    } finally {
      setLoading(false);
    }
  };

  const startConnection = async () => {
    if (!user) {
      toast.error('Please log in first');
      navigate('/login');
      return;
    }

    setLoading(true);
    setStep('connecting');

    try {
      const response = await metaService.startConnection();
      
      if (response.data.oauth_url) {
        // Store state in localStorage for verification
        localStorage.setItem('meta_oauth_state', response.data.state);
        
        // Redirect to Meta OAuth
        window.location.href = response.data.oauth_url;
      } else {
        throw new Error('Failed to get OAuth URL');
      }
    } catch (error: any) {
      console.error('Failed to start Meta connection:', error);
      setError(error.response?.data?.detail || 'Failed to start Meta connection');
      setStep('error');
      toast.error('Failed to start Meta connection');
    } finally {
      setLoading(false);
    }
  };

  const permissions = [
    {
      icon: Facebook,
      title: 'Facebook Ad Management',
      description: 'Create and manage Facebook ad campaigns',
      permission: 'ads_management'
    },
    {
      icon: Instagram,
      title: 'Instagram Business',
      description: 'Post content and manage Instagram business account',
      permission: 'instagram_content_publish'
    },
    {
      icon: Shield,
      title: 'Analytics Access',
      description: 'Read campaign performance and insights data',
      permission: 'read_insights'
    },
    {
      icon: Check,
      title: 'Page Management',
      description: 'Manage and post to connected Facebook pages',
      permission: 'pages_manage_posts'
    }
  ];

  if (step === 'callback') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center"
        >
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto mb-6"></div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Connecting Your Meta Account...
          </h2>
          <p className="text-gray-600">
            Please wait while we set up your Facebook and Instagram integration.
          </p>
        </motion.div>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8"
        >
          {/* Success Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4"
            >
              <Check className="w-10 h-10 text-green-600" />
            </motion.div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Meta Account Connected!
            </h1>
            <p className="text-gray-600 text-lg">
              Successfully connected {connectedAccounts.length} account{connectedAccounts.length !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Connected Accounts */}
          <div className="space-y-4 mb-8">
            {connectedAccounts.map((account, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-center p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3 flex-1">
                  <Facebook className="w-8 h-8 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">{account.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>Ad Account: {account.ad_account_id}</span>
                      <span>Currency: {account.currency}</span>
                    </div>
                  </div>
                </div>
                
                {account.instagram_connected && (
                  <div className="flex items-center text-sm text-purple-600">
                    <Instagram className="w-4 h-4 mr-1" />
                    Instagram Connected
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Next Steps */}
          <div className="bg-blue-50 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-blue-900 mb-3">What's Next?</h3>
            <ul className="space-y-2 text-blue-800">
              <li className="flex items-center">
                <ArrowRight className="w-4 h-4 mr-2" />
                Create your first AI-powered campaign
              </li>
              <li className="flex items-center">
                <ArrowRight className="w-4 h-4 mr-2" />
                Generate stunning images and videos
              </li>
              <li className="flex items-center">
                <ArrowRight className="w-4 h-4 mr-2" />
                Launch campaigns across Facebook and Instagram
              </li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => navigate('/create-campaign')}
              className="flex-1 btn-primary flex items-center justify-center"
            >
              <ArrowRight className="w-5 h-5 mr-2" />
              Create First Campaign
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="flex-1 btn-secondary"
            >
              Go to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  if (step === 'error') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-gray-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center"
        >
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Connection Failed
          </h2>
          <p className="text-gray-600 mb-6">
            {error || 'Failed to connect your Meta account. Please try again.'}
          </p>
          <div className="space-y-3">
            <button
              onClick={() => {
                setStep('intro');
                setError('');
              }}
              className="w-full btn-primary"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full btn-secondary"
            >
              Return to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl w-full bg-white rounded-2xl shadow-xl p-8"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-center space-x-4 mb-6"
          >
            <div className="p-4 bg-blue-100 rounded-full">
              <Facebook className="w-8 h-8 text-blue-600" />
            </div>
            <div className="p-2">
              <ArrowRight className="w-6 h-6 text-gray-400" />
            </div>
            <div className="p-4 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full">
              <Instagram className="w-8 h-8 text-purple-600" />
            </div>
          </motion.div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Connect Your Meta Business Account
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Link your Facebook and Instagram business accounts to start creating 
            AI-powered marketing campaigns that drive real results.
          </p>
        </div>

        {/* Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {/* Left Column - What We'll Access */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6">
              What We'll Access
            </h3>
            <div className="space-y-4">
              {permissions.map((permission, index) => (
                <motion.div
                  key={permission.permission}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-shrink-0 p-2 bg-white rounded-lg">
                    <permission.icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{permission.title}</h4>
                    <p className="text-sm text-gray-600">{permission.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Right Column - Benefits */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6">
              What You'll Get
            </h3>
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Check className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Automated Campaign Creation</h4>
                  <p className="text-sm text-gray-600">AI creates and optimizes campaigns across Facebook and Instagram automatically.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Check className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Real-Time Performance Tracking</h4>
                  <p className="text-sm text-gray-600">Monitor ROI, conversions, and engagement with detailed analytics.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Check className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">AI-Generated Content</h4>
                  <p className="text-sm text-gray-600">Create stunning images and videos optimized for your audience.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start space-x-3">
            <Shield className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">Secure Connection</h4>
              <p className="text-blue-800 text-sm">
                Your account credentials are encrypted and stored securely. We only use the minimum 
                permissions required to create and manage your marketing campaigns. You can disconnect 
                at any time from your account settings.
              </p>
            </div>
          </div>
        </div>

        {/* Connect Button */}
        <div className="text-center">
          <motion.button
            onClick={startConnection}
            disabled={loading}
            whileHover={{ scale: loading ? 1 : 1.02 }}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className={`inline-flex items-center px-8 py-4 rounded-lg font-semibold text-lg transition-all ${
              loading
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-6 h-6 mr-3 animate-spin" />
                Connecting...
              </>
            ) : (
              <>
                <Facebook className="w-6 h-6 mr-3" />
                Connect Meta Account
                <ExternalLink className="w-5 h-5 ml-2" />
              </>
            )}
          </motion.button>

          <p className="text-sm text-gray-500 mt-4">
            You'll be redirected to Facebook to authorize the connection
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default ConnectMeta;