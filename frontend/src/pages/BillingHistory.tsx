import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Receipt, CreditCard, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { getAuthHeaders, isAuthenticated } from '../utils/auth';
import { sanitizeString } from '../utils/validation';
import { BillingItem } from '../types/payment';


const BillingHistory: React.FC = () => {
  const navigate = useNavigate();
  const [billingHistory, setBillingHistory] = useState<BillingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'payments' | 'invoices'>('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication before making API calls
    if (!isAuthenticated()) {
      toast.error('Please log in to view your billing history');
      navigate('/login');
      return;
    }
    
    fetchBillingHistory();
  }, [navigate]);

  const handleAuthError = useCallback(() => {
    toast.error('Session expired. Please log in again.');
    navigate('/login');
  }, [navigate]);

  const fetchBillingHistory = async () => {
    if (!isAuthenticated()) {
      handleAuthError();
      return;
    }

    try {
      setError(null);
      const headers = getAuthHeaders();
      
      const response = await fetch('/api/payments/billing/history', {
        headers
      });

      if (response.status === 401) {
        handleAuthError();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        // Sanitize billing history data
        const sanitizedHistory = (result.data || []).map((item: BillingItem) => ({
          ...item,
          id: sanitizeString(item.id || ''),
          description: sanitizeString(item.description || ''),
          status: sanitizeString(item.status || ''),
          provider: sanitizeString(item.provider || ''),
          invoice_number: sanitizeString(item.invoice_number || '')
        }));
        setBillingHistory(sanitizedHistory);
      } else {
        throw new Error(result.error || 'Failed to load billing history');
      }
    } catch (error: any) {
      console.error('Error fetching billing history:', error);
      const errorMessage = error.message || 'Failed to load billing history';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
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

  const formatAmount = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency.toUpperCase(),
      minimumFractionDigits: 0
    }).format(amount);
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'succeeded':
      case 'paid':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'succeeded':
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredHistory = billingHistory.filter(item => {
    if (filter === 'all') return true;
    return item.type === (filter === 'payments' ? 'payment' : 'invoice');
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading billing history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center">
                <button
                  onClick={() => navigate('/subscription')}
                  className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
                >
                  <ArrowLeft className="w-5 h-5 mr-2" />
                  Back to Subscription
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Billing History</h1>
              </div>
            </div>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-center">
          <div className="text-center bg-white p-8 rounded-lg shadow-lg max-w-md">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Billing History</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="space-y-2">
              <button
                onClick={fetchBillingHistory}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => navigate('/subscription')}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Back to Subscription
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/subscription')}
                className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Subscription
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Billing History</h1>
            </div>
            <button
              onClick={() => {
                toast.success('Export feature coming soon!');
              }}
              className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setFilter('all')}
                className={`py-3 px-6 font-medium text-sm border-b-2 ${
                  filter === 'all'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                All Transactions ({billingHistory.length})
              </button>
              <button
                onClick={() => setFilter('payments')}
                className={`py-3 px-6 font-medium text-sm border-b-2 ${
                  filter === 'payments'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Payments ({billingHistory.filter(item => item.type === 'payment').length})
              </button>
              <button
                onClick={() => setFilter('invoices')}
                className={`py-3 px-6 font-medium text-sm border-b-2 ${
                  filter === 'invoices'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Invoices ({billingHistory.filter(item => item.type === 'invoice').length})
              </button>
            </nav>
          </div>
        </div>

        {/* Billing History List */}
        {filteredHistory.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <Receipt className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No billing history</h3>
            <p className="text-gray-500">Your billing transactions will appear here once you start using our services.</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredHistory.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {item.type === 'payment' ? (
                            <CreditCard className="w-5 h-5 text-blue-500 mr-2" />
                          ) : (
                            <Receipt className="w-5 h-5 text-green-500 mr-2" />
                          )}
                          <span className="text-sm font-medium text-gray-900 capitalize">
                            {item.type}
                          </span>
                          {item.invoice_number && (
                            <span className="ml-2 text-xs text-gray-500">
                              #{item.invoice_number}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {item.description || `${item.type === 'payment' ? 'Payment' : 'Invoice'} transaction`}
                        </div>
                        {item.period_start && item.period_end && (
                          <div className="text-xs text-gray-500">
                            Service period: {formatDate(item.period_start)} - {formatDate(item.period_end)}
                          </div>
                        )}
                        {item.provider && (
                          <div className="text-xs text-gray-500 capitalize">
                            via {item.provider.replace('_', ' ').replace('upi', 'UPI')}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatAmount(item.amount, item.currency)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(item.status)}
                          <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                            {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div>{formatDate(item.created_at)}</div>
                        {item.processed_at && item.processed_at !== item.created_at && (
                          <div className="text-xs text-gray-400">
                            Processed: {formatDate(item.processed_at)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => toast.success('Receipt download coming soon!')}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Download
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BillingHistory;