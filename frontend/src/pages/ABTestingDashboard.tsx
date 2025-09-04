import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { personalizationService } from '../services/api';
import { ABTest, ABTestRequest } from '../types';
import { Button, Card, Input } from '../design-system';
import {
  Plus,
  Play,
  Pause,
  StopCircle,
  BarChart3,
  TrendingUp,
  Clock,
  Users,
  Target,
  CheckCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Filter,
  Download,
  Loader2,
  Lightbulb,
  Zap
} from 'lucide-react';

const ABTestingDashboard: React.FC = () => {
  const [tests, setTests] = useState<ABTest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isCreating, setIsCreating] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid }
  } = useForm<ABTestRequest>({
    mode: 'onChange',
    defaultValues: {
      test_type: 'content',
      traffic_split: 50,
      confidence_level: 95,
      sample_size: 1000,
      duration_days: 14
    }
  });

  // Load A/B tests on component mount
  useEffect(() => {
    loadABTests();
  }, []);

  const loadABTests = async () => {
    try {
      const response = await personalizationService.getABTests();
      setTests(response);
    } catch (error) {
      console.error('Error loading A/B tests:', error);
      toast.error('Failed to load A/B tests');
    } finally {
      setIsLoading(false);
    }
  };

  const createABTest = async (data: ABTestRequest) => {
    setIsCreating(true);
    try {
      const newTest = await personalizationService.createABTest(data);
      setTests([newTest, ...tests]);
      setShowCreateForm(false);
      reset();
      toast.success('A/B test created successfully!');
    } catch (error: any) {
      console.error('Error creating A/B test:', error);
      toast.error(error.response?.data?.detail || 'Failed to create A/B test');
    } finally {
      setIsCreating(false);
    }
  };

  const startTest = async (testId: string) => {
    try {
      await personalizationService.startABTest(testId);
      await loadABTests(); // Reload to get updated status
      toast.success('A/B test started successfully!');
    } catch (error: any) {
      console.error('Error starting test:', error);
      toast.error(error.response?.data?.detail || 'Failed to start test');
    }
  };

  const pauseTest = async (testId: string) => {
    try {
      await personalizationService.pauseABTest(testId);
      await loadABTests();
      toast.success('A/B test paused successfully!');
    } catch (error: any) {
      console.error('Error pausing test:', error);
      toast.error(error.response?.data?.detail || 'Failed to pause test');
    }
  };

  const completeTest = async (testId: string) => {
    try {
      await personalizationService.completeABTest(testId);
      await loadABTests();
      toast.success('A/B test completed successfully!');
    } catch (error: any) {
      console.error('Error completing test:', error);
      toast.error(error.response?.data?.detail || 'Failed to complete test');
    }
  };

  const deleteTest = async (testId: string) => {
    if (!confirm('Are you sure you want to delete this A/B test?')) return;
    
    try {
      await personalizationService.deleteABTest(testId);
      setTests(tests.filter(test => test.test_id !== testId));
      toast.success('A/B test deleted successfully!');
    } catch (error: any) {
      console.error('Error deleting test:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete test');
    }
  };

  const viewTestResults = async (test: ABTest) => {
    if (test.status === 'completed' && !test.results) {
      try {
        const results = await personalizationService.getABTestResults(test.test_id);
        test.results = results;
      } catch (error) {
        console.error('Error loading test results:', error);
        toast.error('Failed to load test results');
        return;
      }
    }
    
    setSelectedTest(test);
    setShowResults(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      case 'draft': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTestTypeIcon = (type: string) => {
    switch (type) {
      case 'content': return Target;
      case 'audience': return Users;
      case 'creative': return Lightbulb;
      case 'timing': return Clock;
      default: return Zap;
    }
  };

  const filteredTests = tests.filter(test => 
    filterStatus === 'all' || test.status === filterStatus
  );

  const renderCreateForm = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-gray-900">Create New A/B Test</h3>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setShowCreateForm(false)}
          >
            Cancel
          </Button>
        </div>

        <form onSubmit={handleSubmit(createABTest)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Campaign Name *
              </label>
              <Input
                {...register('campaign_name', { required: 'Campaign name is required' })}
                placeholder="Enter campaign name"
                errorText={errors.campaign_name?.message}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Test Type *
              </label>
              <select
                {...register('test_type', { required: 'Test type is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="content">Content Test</option>
                <option value="audience">Audience Test</option>
                <option value="creative">Creative Test</option>
                <option value="timing">Timing Test</option>
              </select>
            </div>
          </div>

          {/* Variant A */}
          <div className="border rounded-lg p-4 bg-blue-50">
            <h4 className="font-semibold text-blue-900 mb-3">Variant A (Control)</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <Input
                  {...register('variant_a.name', { required: 'Variant A name is required' })}
                  placeholder="Control version"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  {...register('variant_a.description')}
                  placeholder="Describe this variant"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Headline</label>
                <Input
                  {...register('variant_a.content.headline')}
                  placeholder="Enter headline for variant A"
                />
              </div>
            </div>
          </div>

          {/* Variant B */}
          <div className="border rounded-lg p-4 bg-green-50">
            <h4 className="font-semibold text-green-900 mb-3">Variant B (Test)</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <Input
                  {...register('variant_b.name', { required: 'Variant B name is required' })}
                  placeholder="Test version"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  {...register('variant_b.description')}
                  placeholder="Describe this variant"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Headline</label>
                <Input
                  {...register('variant_b.content.headline')}
                  placeholder="Enter headline for variant B"
                />
              </div>
            </div>
          </div>

          {/* Test Settings */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Traffic Split (% to A)
              </label>
              <Input
                type="number"
                min="10"
                max="90"
                {...register('traffic_split', { 
                  required: 'Traffic split is required',
                  min: 10,
                  max: 90
                })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sample Size
              </label>
              <Input
                type="number"
                min="100"
                {...register('sample_size', { required: 'Sample size is required' })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (days)
              </label>
              <Input
                type="number"
                min="1"
                max="90"
                {...register('duration_days', { required: 'Duration is required' })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confidence Level
            </label>
            <select
              {...register('confidence_level')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="90">90%</option>
              <option value="95">95%</option>
              <option value="99">99%</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isCreating || !isValid}
              className="flex items-center space-x-2"
            >
              {isCreating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              <span>Create Test</span>
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );

  const renderTestResults = () => {
    if (!selectedTest || !selectedTest.results) return null;

    const results = selectedTest.results;
    const variantA = selectedTest.variant_a;
    const variantB = selectedTest.variant_b;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900">Test Results: {selectedTest.campaign_name}</h3>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowResults(false)}
            >
              Close
            </Button>
          </div>

          {/* Results Summary */}
          <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900 mb-2">
                Winner: {results.winner === 'A' ? variantA.name : results.winner === 'B' ? variantB.name : 'Inconclusive'}
              </div>
              <div className="text-lg text-gray-600 mb-4">{results.summary}</div>
              <div className="flex justify-center space-x-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{results.confidence}%</div>
                  <div className="text-sm text-gray-600">Confidence</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">+{results.lift}%</div>
                  <div className="text-sm text-gray-600">Improvement</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{results.significance}%</div>
                  <div className="text-sm text-gray-600">Significance</div>
                </div>
              </div>
            </div>
          </div>

          {/* Variant Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Variant A Results */}
            <Card className={`p-4 border-2 ${results.winner === 'A' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                {results.winner === 'A' && <CheckCircle className="w-5 h-5 text-green-600 mr-2" />}
                Variant A: {variantA.name}
              </h4>
              {variantA.metrics && (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Impressions:</span>
                    <span className="font-medium">{variantA.metrics.impressions.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Clicks:</span>
                    <span className="font-medium">{variantA.metrics.clicks.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CTR:</span>
                    <span className="font-medium">{(variantA.metrics.ctr * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Conversions:</span>
                    <span className="font-medium">{variantA.metrics.conversions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Conversion Rate:</span>
                    <span className="font-medium">{(variantA.metrics.conversion_rate * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cost per Conversion:</span>
                    <span className="font-medium">${variantA.metrics.cost_per_conversion.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </Card>

            {/* Variant B Results */}
            <Card className={`p-4 border-2 ${results.winner === 'B' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                {results.winner === 'B' && <CheckCircle className="w-5 h-5 text-green-600 mr-2" />}
                Variant B: {variantB.name}
              </h4>
              {variantB.metrics && (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Impressions:</span>
                    <span className="font-medium">{variantB.metrics.impressions.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Clicks:</span>
                    <span className="font-medium">{variantB.metrics.clicks.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CTR:</span>
                    <span className="font-medium">{(variantB.metrics.ctr * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Conversions:</span>
                    <span className="font-medium">{variantB.metrics.conversions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Conversion Rate:</span>
                    <span className="font-medium">{(variantB.metrics.conversion_rate * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cost per Conversion:</span>
                    <span className="font-medium">${variantB.metrics.cost_per_conversion.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </Card>
          </div>

          {/* Recommendations */}
          {results.recommendations.length > 0 && (
            <Card className="p-4">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
                Recommendations
              </h4>
              <ul className="space-y-2">
                {results.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </Card>
      </motion.div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">A/B Testing Dashboard</h1>
          <p className="text-gray-600">Create, monitor, and analyze your A/B tests</p>
        </div>
        <Button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create A/B Test</span>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Tests</p>
              <p className="text-2xl font-bold text-gray-900">{tests.length}</p>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="text-2xl font-bold text-green-600">{tests.filter(t => t.status === 'running').length}</p>
            </div>
            <Play className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-blue-600">{tests.filter(t => t.status === 'completed').length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Drafts</p>
              <p className="text-2xl font-bold text-gray-600">{tests.filter(t => t.status === 'draft').length}</p>
            </div>
            <Edit className="w-8 h-8 text-gray-600" />
          </div>
        </Card>
      </div>

      {/* Filter and Actions */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Tests</option>
            <option value="draft">Drafts</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="paused">Paused</option>
          </select>
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Download className="w-4 h-4" />
          <span>Export Data</span>
        </Button>
      </div>

      {/* A/B Tests List */}
      <div className="grid grid-cols-1 gap-6">
        {filteredTests.map((test) => {
          const TestTypeIcon = getTestTypeIcon(test.test_type);
          return (
            <Card key={test.test_id} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <TestTypeIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{test.campaign_name}</h3>
                    <p className="text-gray-600">
                      {test.test_type.charAt(0).toUpperCase() + test.test_type.slice(1)} Test
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(test.status)}`}>
                    {test.status.charAt(0).toUpperCase() + test.status.slice(1)}
                  </span>
                  
                  <div className="flex items-center space-x-2">
                    {test.status === 'draft' && (
                      <Button
                        size="sm"
                        onClick={() => startTest(test.test_id)}
                        className="flex items-center space-x-1"
                      >
                        <Play className="w-3 h-3" />
                        <span>Start</span>
                      </Button>
                    )}
                    
                    {test.status === 'running' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => pauseTest(test.test_id)}
                          className="flex items-center space-x-1"
                        >
                          <Pause className="w-3 h-3" />
                          <span>Pause</span>
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => completeTest(test.test_id)}
                          className="flex items-center space-x-1"
                        >
                          <StopCircle className="w-3 h-3" />
                          <span>Complete</span>
                        </Button>
                      </>
                    )}
                    
                    {test.status === 'completed' && (
                      <Button
                        size="sm"
                        onClick={() => viewTestResults(test)}
                        className="flex items-center space-x-1"
                      >
                        <Eye className="w-3 h-3" />
                        <span>View Results</span>
                      </Button>
                    )}
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteTest(test.test_id)}
                      className="text-red-600 hover:text-red-700 flex items-center space-x-1"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Users className="w-4 h-4" />
                  <span>Sample Size: {test.sample_size.toLocaleString()}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>Duration: {test.end_date ? 
                    Math.ceil((new Date(test.end_date).getTime() - new Date(test.start_date || '').getTime()) / (1000 * 60 * 60 * 24)) 
                    : '—'} days</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Target className="w-4 h-4" />
                  <span>Split: {test.traffic_split}% / {100 - test.traffic_split}%</span>
                </div>
              </div>

              {test.status === 'completed' && test.statistical_significance && (
                <div className="mt-4 p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    {test.winner === 'A' || test.winner === 'B' ? (
                      <TrendingUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-yellow-600" />
                    )}
                    <span className="text-sm font-medium text-gray-900">
                      {test.winner === 'A' || test.winner === 'B' 
                        ? `Winner: Variant ${test.winner}` 
                        : 'Inconclusive Results'}
                    </span>
                    <span className="text-sm text-gray-600">
                      ({test.statistical_significance}% confidence)
                    </span>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {filteredTests.length === 0 && (
        <Card className="p-12 text-center">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No A/B tests found</h3>
          <p className="text-gray-600 mb-4">
            {filterStatus === 'all' 
              ? "Create your first A/B test to start optimizing your campaigns"
              : `No tests with status "${filterStatus}" found`
            }
          </p>
          <Button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create A/B Test</span>
          </Button>
        </Card>
      )}

      {/* Modals */}
      <AnimatePresence>
        {showCreateForm && renderCreateForm()}
        {showResults && renderTestResults()}
      </AnimatePresence>
    </div>
  );
};

export default ABTestingDashboard;