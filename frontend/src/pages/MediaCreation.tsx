import React, { useState } from 'react';
import { Image, Video, Sparkles, Target, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ImageGenerator from '../components/MediaCreation/ImageGenerator';
import VideoGenerator from '../components/MediaCreation/VideoGenerator';

interface MediaCreationProps {
  onMediaCreated?: (mediaUrl: string, type: 'image' | 'video', prompt: string) => void;
}

const MediaCreation: React.FC<MediaCreationProps> = ({ onMediaCreated }) => {
  const [activeTab, setActiveTab] = useState<'images' | 'videos'>('images');
  const [createdMedia, setCreatedMedia] = useState<Array<{
    url: string;
    type: 'image' | 'video';
    prompt: string;
    createdAt: Date;
  }>>([]);

  const handleMediaGenerated = (mediaUrl: string, type: 'image' | 'video', prompt: string) => {
    const newMedia = {
      url: mediaUrl,
      type,
      prompt,
      createdAt: new Date()
    };
    setCreatedMedia(prev => [newMedia, ...prev]);
    
    if (onMediaCreated) {
      onMediaCreated(mediaUrl, type, prompt);
    }
  };

  const tabs = [
    { 
      id: 'images' as const, 
      name: 'AI Images & Posters', 
      icon: Image, 
      count: createdMedia.filter(m => m.type === 'image').length,
      description: 'Generate stunning visuals for your campaigns'
    },
    { 
      id: 'videos' as const, 
      name: 'AI Marketing Videos', 
      icon: Video, 
      count: createdMedia.filter(m => m.type === 'video').length,
      description: 'Create engaging video content with AI'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-full mb-6">
            <Sparkles className="w-5 h-5 mr-2" />
            <span className="font-medium">AI-Powered Creative Studio</span>
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Create Marketing Content in Seconds
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform your ideas into professional images, posters, and videos using 
            advanced AI. No design experience required.
          </p>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="card text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Image className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {createdMedia.filter(m => m.type === 'image').length}
            </h3>
            <p className="text-gray-600">Images Generated</p>
          </div>

          <div className="card text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Video className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {createdMedia.filter(m => m.type === 'video').length}
            </h3>
            <p className="text-gray-600">Videos Created</p>
          </div>

          <div className="card text-center">
            <div className="bg-green-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Target className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {createdMedia.length}
            </h3>
            <p className="text-gray-600">Total Assets</p>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 py-4 px-6 text-center border-b-2 font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-2">
                    <tab.icon className="w-5 h-5" />
                    <span className="font-semibold">{tab.name}</span>
                    {tab.count > 0 && (
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        activeTab === tab.id 
                          ? 'bg-blue-100 text-blue-600' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {tab.count}
                      </span>
                    )}
                  </div>
                  <p className="text-xs mt-1 text-gray-500">{tab.description}</p>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            <AnimatePresence mode="wait">
              {activeTab === 'images' && (
                <motion.div
                  key="images"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ImageGenerator
                    onImageGenerated={(url, prompt) => handleMediaGenerated(url, 'image', prompt)}
                  />
                </motion.div>
              )}

              {activeTab === 'videos' && (
                <motion.div
                  key="videos"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <VideoGenerator
                    onVideoGenerated={(url, prompt) => handleMediaGenerated(url, 'video', prompt)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Recent Creations */}
        {createdMedia.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
                Your Recent Creations
              </h3>
              <span className="text-sm text-gray-500">
                {createdMedia.length} total assets created
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {createdMedia.slice(0, 8).map((media, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow group"
                >
                  <div className="aspect-video relative">
                    {media.type === 'image' ? (
                      <img
                        src={media.url}
                        alt="Generated content"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <video
                        src={media.url}
                        className="w-full h-full object-cover"
                        muted
                      />
                    )}
                    <div className="absolute top-2 left-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        media.type === 'image' 
                          ? 'bg-blue-100 text-blue-700' 
                          : 'bg-purple-100 text-purple-700'
                      }`}>
                        {media.type === 'image' ? '🖼️ Image' : '🎥 Video'}
                      </span>
                    </div>
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all" />
                  </div>
                  <div className="p-3">
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {media.prompt}
                    </p>
                    <p className="text-xs text-gray-500">
                      Created {media.createdAt.toLocaleDateString()}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>

            {createdMedia.length > 8 && (
              <div className="text-center mt-6">
                <button className="btn-secondary">
                  View All Creations ({createdMedia.length})
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Getting Started Guide */}
        {createdMedia.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card text-center py-12"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full mb-6">
              <Sparkles className="w-10 h-10 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Create Amazing Content?
            </h3>
            <p className="text-gray-600 max-w-md mx-auto mb-8">
              Start by choosing whether you want to create images or videos, 
              then describe your vision and let our AI bring it to life.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => setActiveTab('images')}
                className="btn-primary flex items-center justify-center"
              >
                <Image className="w-5 h-5 mr-2" />
                Create Images
              </button>
              <button
                onClick={() => setActiveTab('videos')}
                className="btn-secondary flex items-center justify-center"
              >
                <Video className="w-5 h-5 mr-2" />
                Create Videos
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default MediaCreation;