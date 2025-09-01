import React, { useState } from 'react';
import { 
  Upload, 
  Image as ImageIcon, 
  Wand2, 
  Download, 
  RefreshCw, 
  Palette, 
  Sparkles,
  Eye,
  Copy,
  Settings
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ImageGeneratorProps {
  onImageGenerated?: (imageUrl: string, prompt: string) => void;
  onImageSelected?: (imageUrl: string) => void;
}

const ImageGenerator: React.FC<ImageGeneratorProps> = ({ 
  onImageGenerated, 
  onImageSelected 
}) => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('photorealistic');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<string[]>([]);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [uploadedImage, setUploadedImage] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Advanced settings
  const [quality, setQuality] = useState('high');
  const [creativity, setCreativity] = useState(50);
  const [iterations, setIterations] = useState(1);

  const styleOptions = [
    { id: 'photorealistic', name: 'Photorealistic', emoji: '📸' },
    { id: 'illustration', name: 'Illustration', emoji: '🎨' },
    { id: 'cartoon', name: 'Cartoon', emoji: '🎭' },
    { id: 'abstract', name: 'Abstract', emoji: '🌀' },
    { id: 'vintage', name: 'Vintage', emoji: '📼' },
    { id: 'minimalist', name: 'Minimalist', emoji: '⚪' },
    { id: 'cyberpunk', name: 'Cyberpunk', emoji: '🌃' },
    { id: 'watercolor', name: 'Watercolor', emoji: '🖌️' }
  ];

  const aspectRatios = [
    { id: '1:1', name: 'Square (1:1)', description: 'Perfect for social posts' },
    { id: '16:9', name: 'Landscape (16:9)', description: 'Great for banners' },
    { id: '9:16', name: 'Portrait (9:16)', description: 'Ideal for stories' },
    { id: '4:3', name: 'Standard (4:3)', description: 'Classic format' }
  ];

  const promptTemplates = [
    "A modern minimalist product advertisement featuring [product] with clean typography and premium lighting",
    "An energetic social media post showcasing [brand] with vibrant colors and dynamic composition",
    "A professional business poster with corporate aesthetic and sophisticated design elements",
    "A trendy Instagram story graphic with bold colors and engaging visual hierarchy",
    "A vintage-inspired marketing banner with retro styling and warm color palette"
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    try {
      const { mediaService } = await import('../../services/api');
      
      const result = await mediaService.generateImage({
        prompt,
        style,
        aspect_ratio: aspectRatio,
        quality,
        creativity,
        iterations
      });
      
      if (result.success && result.data.images) {
        const imageUrls = result.data.images.map((img: any) => 
          `http://localhost:8000${img.url}`
        );
        setGeneratedImages(imageUrls);
        
        if (onImageGenerated && imageUrls[0]) {
          onImageGenerated(imageUrls[0], prompt);
        }
      } else {
        throw new Error('Failed to generate images');
      }
    } catch (error) {
      console.error('Failed to generate image:', error);
      // Fallback to mock images for demo
      const mockImages = [
        'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=600',
        'https://images.unsplash.com/photo-1634973357973-f2ed2657db3c?w=800&h=600',
        'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&h=600'
      ].slice(0, iterations);

      setGeneratedImages(mockImages);
      if (onImageGenerated && mockImages[0]) {
        onImageGenerated(mockImages[0], prompt);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setUploadedImage(result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    setSelectedImage(imageUrl);
    if (onImageSelected) {
      onImageSelected(imageUrl);
    }
  };

  const copyPrompt = (template: string) => {
    setPrompt(template);
    navigator.clipboard.writeText(template);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI Image & Poster Generator
        </h2>
        <p className="text-gray-600">
          Create stunning marketing visuals with AI-powered image generation
        </p>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="space-y-4">
          {/* Prompt Input */}
          <div>
            <label className="label">Describe your marketing visual</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A professional marketing poster for a tech startup with modern design, blue and white colors, featuring innovative technology..."
              className="input-field h-24 resize-none"
              maxLength={500}
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-500">
                {prompt.length}/500 characters
              </span>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-xs text-blue-600 hover:text-blue-700 flex items-center"
              >
                <Settings className="w-3 h-3 mr-1" />
                Advanced Settings
              </button>
            </div>
          </div>

          {/* Style Selection */}
          <div>
            <label className="label">Visual Style</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {styleOptions.map((styleOption) => (
                <button
                  key={styleOption.id}
                  onClick={() => setStyle(styleOption.id)}
                  className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                    style === styleOption.id
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-lg mb-1">{styleOption.emoji}</div>
                  <div>{styleOption.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Aspect Ratio */}
          <div>
            <label className="label">Format & Size</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {aspectRatios.map((ratio) => (
                <button
                  key={ratio.id}
                  onClick={() => setAspectRatio(ratio.id)}
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    aspectRatio === ratio.id
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{ratio.name}</div>
                  <div className="text-xs text-gray-500">{ratio.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Advanced Settings */}
          <AnimatePresence>
            {showAdvanced && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-4 border-t pt-4"
              >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="label">Quality</label>
                    <select
                      value={quality}
                      onChange={(e) => setQuality(e.target.value)}
                      className="input-field"
                    >
                      <option value="standard">Standard</option>
                      <option value="high">High Quality</option>
                      <option value="ultra">Ultra HD</option>
                    </select>
                  </div>

                  <div>
                    <label className="label">Creativity Level: {creativity}%</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={creativity}
                      onChange={(e) => setCreativity(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div>
                    <label className="label">Variations</label>
                    <select
                      value={iterations}
                      onChange={(e) => setIterations(Number(e.target.value))}
                      className="input-field"
                    >
                      <option value={1}>1 image</option>
                      <option value={2}>2 images</option>
                      <option value={3}>3 images</option>
                      <option value={4}>4 images</option>
                    </select>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Reference Image */}
          <div>
            <label className="label">Reference Image (Optional)</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                {uploadedImage ? (
                  <img
                    src={uploadedImage}
                    alt="Uploaded reference"
                    className="mx-auto h-24 w-auto rounded-lg mb-2"
                  />
                ) : (
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                )}
                <p className="text-sm text-gray-600">
                  {uploadedImage ? 'Change reference image' : 'Upload reference image'}
                </p>
              </label>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className="btn-primary w-full py-4 text-lg font-semibold flex items-center justify-center"
          >
            {isGenerating ? (
              <>
                <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                Generating Amazing Visuals...
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5 mr-2" />
                Generate Marketing Visual
              </>
            )}
          </button>
        </div>
      </div>

      {/* Prompt Templates */}
      <div className="card">
        <h3 className="font-bold text-lg mb-4 flex items-center">
          <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
          Quick Start Templates
        </h3>
        <div className="space-y-2">
          {promptTemplates.map((template, index) => (
            <button
              key={index}
              onClick={() => copyPrompt(template)}
              className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors group"
            >
              <div className="flex items-start justify-between">
                <p className="text-sm text-gray-700 flex-1">{template}</p>
                <Copy className="w-4 h-4 text-gray-400 group-hover:text-gray-600 ml-2 flex-shrink-0" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Generated Images */}
      {generatedImages.length > 0 && (
        <div className="card">
          <h3 className="font-bold text-lg mb-4 flex items-center">
            <ImageIcon className="w-5 h-5 mr-2 text-green-500" />
            Generated Images
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {generatedImages.map((imageUrl, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`relative group cursor-pointer rounded-lg overflow-hidden ${
                  selectedImage === imageUrl ? 'ring-4 ring-blue-500' : ''
                }`}
              >
                <img
                  src={imageUrl}
                  alt={`Generated ${index + 1}`}
                  className="w-full h-48 object-cover"
                  onClick={() => handleImageSelect(imageUrl)}
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all">
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity space-x-2">
                    <button className="bg-white rounded-full p-2 shadow-lg hover:bg-gray-100">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="bg-white rounded-full p-2 shadow-lg hover:bg-gray-100">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {selectedImage === imageUrl && (
                  <div className="absolute bottom-2 left-2">
                    <span className="bg-blue-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                      Selected
                    </span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGenerator;