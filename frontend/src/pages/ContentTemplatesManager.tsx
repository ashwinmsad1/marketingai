import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { personalizationService } from '../services/api';
import { ContentTemplate, MetaUserProfile } from '../types';
import { Button, Card, Input } from '../design-system';
import {
  Palette,
  Image,
  Video,
  Layers,
  Search,
  Star,
  Eye,
  Wand2,
  Settings,
  Grid,
  Clock,
  Users,
  TrendingUp,
  Loader2,
  Play,
  Edit3,
  Copy,
  Heart
} from 'lucide-react';

interface TemplatePreviewData {
  [key: string]: string | number;
}

const ContentTemplatesManager: React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<ContentTemplate[]>([]);
  const [userProfile, setUserProfile] = useState<MetaUserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showCustomization, setShowCustomization] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewData, setPreviewData] = useState<TemplatePreviewData>({});

  const {
    register,
    handleSubmit,
    setValue
  } = useForm();

  const categories = [
    { id: 'all', name: 'All Templates', icon: Grid },
    { id: 'awareness', name: 'Brand Awareness', icon: Users },
    { id: 'conversion', name: 'Conversion', icon: TrendingUp },
    { id: 'engagement', name: 'Engagement', icon: Heart },
    { id: 'product', name: 'Product Launch', icon: Star },
    { id: 'seasonal', name: 'Seasonal', icon: Clock },
  ];

  const contentTypes = [
    { id: 'image', name: 'Image', icon: Image, color: 'text-blue-600' },
    { id: 'video', name: 'Video', icon: Video, color: 'text-purple-600' },
    { id: 'carousel', name: 'Carousel', icon: Layers, color: 'text-green-600' },
    { id: 'story', name: 'Story', icon: Play, color: 'text-orange-600' },
  ];

  useEffect(() => {
    loadTemplatesAndProfile();
  }, [selectedCategory]);

  const loadTemplatesAndProfile = async () => {
    try {
      setIsLoading(true);
      
      const [templatesData, profileData] = await Promise.all([
        personalizationService.getContentTemplates(
          selectedCategory === 'all' ? undefined : selectedCategory
        ),
        personalizationService.getProfile()
      ]);

      setTemplates(templatesData);
      setUserProfile(profileData);
    } catch (error: any) {
      console.error('Error loading templates:', error);
      toast.error('Failed to load templates');
    } finally {
      setIsLoading(false);
    }
  };

  const generateContentFromTemplate = async (templateId: string, customizations: any) => {
    setIsGenerating(true);
    try {
      const result = await personalizationService.generateContentFromTemplate(templateId, customizations);
      toast.success('Content generated successfully!');
      
      // Navigate to campaign creation with generated content
      navigate('/campaigns/create', { 
        state: { 
          generatedContent: result,
          templateUsed: selectedTemplate 
        } 
      });
    } catch (error: any) {
      console.error('Error generating content:', error);
      toast.error('Failed to generate content');
    } finally {
      setIsGenerating(false);
      setShowCustomization(false);
    }
  };

  const previewTemplate = async (template: ContentTemplate) => {
    setSelectedTemplate(template);
    
    // Populate preview data with user profile values
    const preview: TemplatePreviewData = {};
    if (userProfile) {
      template.personalization_variables.forEach(variable => {
        switch (variable.variable_name) {
          case 'business_name':
            preview[variable.variable_name] = userProfile.business_name;
            break;
          case 'target_audience':
            preview[variable.variable_name] = userProfile.target_audience;
            break;
          case 'unique_value_proposition':
            preview[variable.variable_name] = userProfile.unique_value_proposition;
            break;
          case 'brand_colors':
            preview[variable.variable_name] = userProfile.brand_colors || '#007bff';
            break;
          default:
            preview[variable.variable_name] = variable.default_value || 'Sample Text';
        }
      });
    }
    
    setPreviewData(preview);
    setShowPreview(true);
  };

  const customizeTemplate = (template: ContentTemplate) => {
    setSelectedTemplate(template);
    
    // Set form values based on user profile
    if (userProfile) {
      template.personalization_variables.forEach(variable => {
        let value = variable.default_value;
        
        switch (variable.variable_name) {
          case 'business_name':
            value = userProfile.business_name;
            break;
          case 'target_audience':
            value = userProfile.target_audience;
            break;
          case 'unique_value_proposition':
            value = userProfile.unique_value_proposition;
            break;
          case 'brand_colors':
            value = userProfile.brand_colors || '#007bff';
            break;
        }
        
        setValue(variable.variable_name, value);
      });
    }
    
    setShowCustomization(true);
  };

  const getContentTypeIcon = (contentType: string) => {
    const type = contentTypes.find(t => t.id === contentType);
    const IconComponent = type?.icon || Image;
    return <IconComponent className={`w-4 h-4 ${type?.color || 'text-gray-600'}`} />;
  };

  const getPerformanceColor = (ctr: number) => {
    if (ctr >= 3) return 'text-green-600 bg-green-100';
    if (ctr >= 2) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.industry.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const renderTemplatePreview = () => {
    if (!selectedTemplate) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900 flex items-center">
              <Eye className="w-6 h-6 text-blue-600 mr-2" />
              Template Preview: {selectedTemplate.name}
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowPreview(false)}
            >
              Close
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Template Info */}
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Template Information</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Category:</span>
                    <span className="capitalize">{selectedTemplate.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Industry:</span>
                    <span>{selectedTemplate.industry}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Content Type:</span>
                    <div className="flex items-center space-x-1">
                      {getContentTypeIcon(selectedTemplate.content_type)}
                      <span className="capitalize">{selectedTemplate.content_type}</span>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Usage Count:</span>
                    <span>{selectedTemplate.performance_data.usage_count}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Performance Metrics</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">
                      {(selectedTemplate.performance_data.average_ctr * 100).toFixed(2)}%
                    </div>
                    <div className="text-xs text-gray-600">Avg. CTR</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">
                      {(selectedTemplate.performance_data.average_conversion_rate * 100).toFixed(2)}%
                    </div>
                    <div className="text-xs text-gray-600">Avg. CVR</div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Personalization Variables</h4>
                <div className="space-y-2">
                  {selectedTemplate.personalization_variables.map((variable, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded text-sm">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{variable.variable_name}</span>
                        <span className="text-xs text-gray-500 capitalize">{variable.variable_type}</span>
                      </div>
                      <div className="text-gray-600 text-xs">{variable.description}</div>
                      <div className="text-blue-600 text-xs mt-1">
                        Preview: {previewData[variable.variable_name] || variable.default_value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Visual Preview */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Visual Preview</h4>
              <div className="aspect-square bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg p-6 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">
                    {selectedTemplate.content_type === 'image' && '📸'}
                    {selectedTemplate.content_type === 'video' && '🎥'}
                    {selectedTemplate.content_type === 'carousel' && '📱'}
                    {selectedTemplate.content_type === 'story' && '📖'}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {previewData.business_name || 'Your Business Name'}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {previewData.unique_value_proposition || selectedTemplate.description}
                  </p>
                  <Button size="sm">Call to Action</Button>
                </div>
              </div>
              
              <div className="mt-4 flex space-x-2">
                <Button
                  onClick={() => customizeTemplate(selectedTemplate)}
                  className="flex-1 flex items-center justify-center space-x-2"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Customize</span>
                </Button>
                <Button
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Copy className="w-4 h-4" />
                  <span>Duplicate</span>
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    );
  };

  const renderCustomizationModal = () => {
    if (!selectedTemplate) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <Card className="w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900 flex items-center">
              <Settings className="w-6 h-6 text-purple-600 mr-2" />
              Customize Template: {selectedTemplate.name}
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCustomization(false)}
            >
              Cancel
            </Button>
          </div>

          <form onSubmit={handleSubmit((data) => generateContentFromTemplate(selectedTemplate.template_id, data))}>
            <div className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Template Information</h4>
                <p className="text-blue-800 text-sm">{selectedTemplate.description}</p>
                <div className="mt-2 flex items-center space-x-4 text-sm">
                  <span className="text-blue-700">Category: {selectedTemplate.category}</span>
                  <span className="text-blue-700">Industry: {selectedTemplate.industry}</span>
                  <div className="flex items-center space-x-1">
                    {getContentTypeIcon(selectedTemplate.content_type)}
                    <span className="text-blue-700 capitalize">{selectedTemplate.content_type}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Personalization Variables</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedTemplate.personalization_variables.map((variable, index) => (
                    <div key={index}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {variable.variable_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        {variable.description && (
                          <span className="text-gray-500 font-normal"> - {variable.description}</span>
                        )}
                      </label>
                      
                      {variable.variable_type === 'text' && (
                        <Input
                          {...register(variable.variable_name)}
                          placeholder={variable.default_value}
                        />
                      )}
                      
                      {variable.variable_type === 'color' && (
                        <input
                          type="color"
                          {...register(variable.variable_name)}
                          className="w-full h-10 rounded border border-gray-300"
                        />
                      )}
                      
                      {variable.variable_type === 'number' && (
                        <Input
                          type="number"
                          {...register(variable.variable_name)}
                          placeholder={variable.default_value}
                        />
                      )}
                      
                      {variable.possible_values && variable.possible_values.length > 0 && (
                        <select
                          {...register(variable.variable_name)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select {variable.variable_name}</option>
                          {variable.possible_values.map(value => (
                            <option key={value} value={value}>{value}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Additional Customizations</h4>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Campaign Objective
                    </label>
                    <select
                      {...register('campaign_objective')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="awareness">Brand Awareness</option>
                      <option value="traffic">Traffic</option>
                      <option value="engagement">Engagement</option>
                      <option value="conversions">Conversions</option>
                      <option value="sales">Sales</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Target Audience Notes
                    </label>
                    <textarea
                      {...register('audience_notes')}
                      placeholder="Any specific targeting preferences for this content..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Creative Style
                    </label>
                    <select
                      {...register('creative_style')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="professional">Professional</option>
                      <option value="casual">Casual</option>
                      <option value="playful">Playful</option>
                      <option value="elegant">Elegant</option>
                      <option value="bold">Bold</option>
                      <option value="minimalist">Minimalist</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCustomization(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isGenerating}
                  className="flex items-center space-x-2"
                >
                  {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                  <span>Generate Content</span>
                </Button>
              </div>
            </div>
          </form>
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
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Palette className="w-8 h-8 text-purple-600 mr-3" />
            Content Templates
          </h1>
          <p className="text-gray-600">Personalized content templates for your industry and goals</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Templates</p>
              <p className="text-2xl font-bold text-gray-900">{templates.length}</p>
            </div>
            <Grid className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Your Industry</p>
              <p className="text-2xl font-bold text-purple-600">
                {templates.filter(t => t.industry === userProfile?.industry).length}
              </p>
            </div>
            <Users className="w-8 h-8 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Performance</p>
              <p className="text-2xl font-bold text-green-600">
                {templates.filter(t => t.performance_data.average_ctr > 0.03).length}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recently Added</p>
              <p className="text-2xl font-bold text-orange-600">
                {templates.filter(t => {
                  const weekAgo = new Date();
                  weekAgo.setDate(weekAgo.getDate() - 7);
                  return new Date(t.created_at) > weekAgo;
                }).length}
              </p>
            </div>
            <Clock className="w-8 h-8 text-orange-600" />
          </div>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <Input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search templates..."
              className="pl-10"
            />
          </div>
        </div>
        
        <div className="flex space-x-2">
          {categories.map((category) => {
            const IconComponent = category.icon;
            return (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
                className="flex items-center space-x-1"
              >
                <IconComponent className="w-4 h-4" />
                <span>{category.name}</span>
              </Button>
            );
          })}
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <Card key={template.template_id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2">
                {getContentTypeIcon(template.content_type)}
                <h3 className="font-semibold text-gray-900">{template.name}</h3>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getPerformanceColor(template.performance_data.average_ctr * 100)}`}>
                {(template.performance_data.average_ctr * 100).toFixed(1)}% CTR
              </span>
            </div>

            <p className="text-gray-600 text-sm mb-4 line-clamp-2">{template.description}</p>

            <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
              <span className="capitalize">{template.category}</span>
              <span>•</span>
              <span>{template.industry}</span>
              <span>•</span>
              <span>{template.performance_data.usage_count} uses</span>
            </div>

            <div className="space-y-2 mb-4">
              <div className="text-xs text-gray-500">Variables:</div>
              <div className="flex flex-wrap gap-1">
                {template.personalization_variables.slice(0, 3).map((variable, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {variable.variable_name}
                  </span>
                ))}
                {template.personalization_variables.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                    +{template.personalization_variables.length - 3} more
                  </span>
                )}
              </div>
            </div>

            <div className="flex space-x-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => previewTemplate(template)}
                className="flex-1 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3 h-3" />
                <span>Preview</span>
              </Button>
              <Button
                size="sm"
                onClick={() => customizeTemplate(template)}
                className="flex-1 flex items-center justify-center space-x-1"
              >
                <Wand2 className="w-3 h-3" />
                <span>Use Template</span>
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <Card className="p-12 text-center">
          <Palette className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm
              ? `No templates match "${searchTerm}" in the ${selectedCategory === 'all' ? 'all categories' : selectedCategory} category`
              : `No templates found in the ${selectedCategory === 'all' ? 'all categories' : selectedCategory} category`
            }
          </p>
          <div className="flex justify-center space-x-2">
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
              }}
            >
              Clear Filters
            </Button>
          </div>
        </Card>
      )}

      {/* Modals */}
      <AnimatePresence>
        {showPreview && renderTemplatePreview()}
        {showCustomization && renderCustomizationModal()}
      </AnimatePresence>
    </div>
  );
};

export default ContentTemplatesManager;