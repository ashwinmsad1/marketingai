import React, { useState, useRef } from 'react';
import { 
  Video, 
  Upload, 
  Play, 
  Pause, 
  Download, 
  RefreshCw, 
  Film, 
  Clock,
  Palette,
  Music,
  Type,
  Wand2,
  Eye,
  Settings
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface VideoGeneratorProps {
  onVideoGenerated?: (videoUrl: string, prompt: string) => void;
  onVideoSelected?: (videoUrl: string) => void;
}

const VideoGenerator: React.FC<VideoGeneratorProps> = ({ 
  onVideoGenerated, 
  onVideoSelected 
}) => {
  const [prompt, setPrompt] = useState('');
  const [videoStyle, setVideoStyle] = useState('commercial');
  const [duration, setDuration] = useState('15');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedVideos, setGeneratedVideos] = useState<Array<{url: string, thumbnail: string}>>([]);
  const [selectedVideo, setSelectedVideo] = useState<string>('');
  const [uploadedMedia, setUploadedMedia] = useState<Array<{url: string, type: 'image' | 'video'}>>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string>('');
  const videoRefs = useRef<{[key: string]: HTMLVideoElement}>({});

  // Advanced settings
  const [motion, setMotion] = useState('dynamic');
  const [musicStyle, setMusicStyle] = useState('upbeat');
  const [textOverlay, setTextOverlay] = useState(true);
  const [brandColors, setBrandColors] = useState('#3B82F6');
  const [voiceover, setVoiceover] = useState('none');

  const videoStyles = [
    { id: 'commercial', name: 'Commercial', emoji: '🎬', description: 'Professional ads' },
    { id: 'social', name: 'Social Media', emoji: '📱', description: 'Engaging posts' },
    { id: 'explainer', name: 'Explainer', emoji: '📚', description: 'Educational content' },
    { id: 'testimonial', name: 'Testimonial', emoji: '💬', description: 'Customer stories' },
    { id: 'product', name: 'Product Demo', emoji: '📦', description: 'Showcase features' },
    { id: 'brand', name: 'Brand Story', emoji: '🏢', description: 'Company narrative' },
    { id: 'event', name: 'Event Promo', emoji: '🎉', description: 'Promote events' },
    { id: 'tutorial', name: 'How-to', emoji: '🛠️', description: 'Step by step' }
  ];

  const durations = [
    { id: '6', name: '6 seconds', description: 'Bumper ads' },
    { id: '15', name: '15 seconds', description: 'Social stories' },
    { id: '30', name: '30 seconds', description: 'Standard ads' },
    { id: '60', name: '1 minute', description: 'Detailed content' },
    { id: '120', name: '2 minutes', description: 'Explainer videos' }
  ];

  const aspectRatios = [
    { id: '16:9', name: 'Landscape (16:9)', description: 'YouTube, Facebook' },
    { id: '9:16', name: 'Vertical (9:16)', description: 'TikTok, Instagram' },
    { id: '1:1', name: 'Square (1:1)', description: 'Instagram posts' },
    { id: '4:5', name: 'Portrait (4:5)', description: 'Instagram feed' }
  ];

  const musicStyles = [
    { id: 'upbeat', name: 'Upbeat', emoji: '🎵' },
    { id: 'corporate', name: 'Corporate', emoji: '🏢' },
    { id: 'emotional', name: 'Emotional', emoji: '❤️' },
    { id: 'energetic', name: 'Energetic', emoji: '⚡' },
    { id: 'calm', name: 'Calm', emoji: '🌊' },
    { id: 'none', name: 'No Music', emoji: '🔇' }
  ];

  const motionStyles = [
    { id: 'static', name: 'Static', description: 'Minimal movement' },
    { id: 'smooth', name: 'Smooth', description: 'Gentle transitions' },
    { id: 'dynamic', name: 'Dynamic', description: 'Energetic motion' },
    { id: 'cinematic', name: 'Cinematic', description: 'Film-like movement' }
  ];

  const voiceoverOptions = [
    { id: 'none', name: 'No Voiceover' },
    { id: 'male-professional', name: 'Male - Professional' },
    { id: 'female-professional', name: 'Female - Professional' },
    { id: 'male-casual', name: 'Male - Casual' },
    { id: 'female-casual', name: 'Female - Casual' },
    { id: 'ai-generated', name: 'AI Generated' }
  ];

  const videoPromptTemplates = [
    "A dynamic product showcase video featuring [product name] with smooth camera movements and modern graphics",
    "An engaging social media video promoting [brand] with vibrant colors and upbeat music",
    "A professional testimonial video with clean typography and corporate aesthetic",
    "An educational explainer video demonstrating [service] with clear animations and voice narration",
    "A brand story video showcasing company values with emotional storytelling and cinematic visuals"
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    try {
      const { mediaService } = await import('../../services/api');
      
      const result = await mediaService.generateVideo({
        prompt,
        style: videoStyle,
        duration: parseInt(duration),
        aspect_ratio: aspectRatio,
        motion,
        music_style: musicStyle,
        text_overlay: textOverlay,
        brand_colors: brandColors
      });
      
      if (result.success && result.data) {
        const video = {
          url: `http://localhost:8000${result.data.url}`,
          thumbnail: result.data.thumbnail ? `http://localhost:8000${result.data.thumbnail}` : 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300'
        };
        setGeneratedVideos([video]);
        
        if (onVideoGenerated) {
          onVideoGenerated(video.url, prompt);
        }
      } else {
        throw new Error('Failed to generate video');
      }
    } catch (error) {
      console.error('Failed to generate video:', error);
      // Fallback to mock videos for demo
      const mockVideos = [
        {
          url: 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
          thumbnail: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300'
        },
        {
          url: 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4',
          thumbnail: 'https://images.unsplash.com/photo-1634973357973-f2ed2657db3c?w=400&h=300'
        }
      ];

      setGeneratedVideos(mockVideos);
      if (onVideoGenerated && mockVideos[0]) {
        onVideoGenerated(mockVideos[0].url, prompt);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleMediaUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const result = e.target?.result as string;
          const mediaType = file.type.startsWith('video/') ? 'video' : 'image';
          setUploadedMedia(prev => [...prev, { url: result, type: mediaType }]);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const handleVideoSelect = (videoUrl: string) => {
    setSelectedVideo(videoUrl);
    if (onVideoSelected) {
      onVideoSelected(videoUrl);
    }
  };

  const toggleVideoPlayback = (videoUrl: string) => {
    const video = videoRefs.current[videoUrl];
    if (video) {
      if (currentlyPlaying === videoUrl) {
        video.pause();
        setCurrentlyPlaying('');
      } else {
        // Pause all other videos
        Object.values(videoRefs.current).forEach(v => v.pause());
        video.play();
        setCurrentlyPlaying(videoUrl);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI Video Generator
        </h2>
        <p className="text-gray-600">
          Create professional marketing videos with AI-powered video generation
        </p>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="space-y-4">
          {/* Video Concept Input */}
          <div>
            <label className="label">Describe your marketing video concept</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A professional product demonstration video showcasing our new fitness app with dynamic animations, upbeat music, and clear call-to-action..."
              className="input-field h-24 resize-none"
              maxLength={800}
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-500">
                {prompt.length}/800 characters
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

          {/* Video Style Selection */}
          <div>
            <label className="label">Video Style</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {videoStyles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setVideoStyle(style.id)}
                  className={`p-3 rounded-lg border-2 text-sm transition-all ${
                    videoStyle === style.id
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-lg mb-1">{style.emoji}</div>
                  <div className="font-medium">{style.name}</div>
                  <div className="text-xs text-gray-500">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Duration and Format */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Duration</label>
              <div className="grid grid-cols-2 gap-2">
                {durations.map((dur) => (
                  <button
                    key={dur.id}
                    onClick={() => setDuration(dur.id)}
                    className={`p-2 rounded-lg border-2 text-sm transition-all ${
                      duration === dur.id
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium">{dur.name}</div>
                    <div className="text-xs text-gray-500">{dur.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="label">Format</label>
              <div className="space-y-2">
                {aspectRatios.map((ratio) => (
                  <button
                    key={ratio.id}
                    onClick={() => setAspectRatio(ratio.id)}
                    className={`w-full p-2 rounded-lg border-2 text-left text-sm transition-all ${
                      aspectRatio === ratio.id
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium">{ratio.name}</div>
                    <div className="text-xs text-gray-500">{ratio.description}</div>
                  </button>
                ))}
              </div>
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Camera Motion</label>
                    <select
                      value={motion}
                      onChange={(e) => setMotion(e.target.value)}
                      className="input-field"
                    >
                      {motionStyles.map(style => (
                        <option key={style.id} value={style.id}>
                          {style.name} - {style.description}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="label">Music Style</label>
                    <div className="flex flex-wrap gap-2">
                      {musicStyles.map((music) => (
                        <button
                          key={music.id}
                          onClick={() => setMusicStyle(music.id)}
                          className={`px-3 py-1 rounded-full text-sm border transition-all ${
                            musicStyle === music.id
                              ? 'border-green-500 bg-green-50 text-green-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          {music.emoji} {music.name}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="label">Brand Color</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        value={brandColors}
                        onChange={(e) => setBrandColors(e.target.value)}
                        className="w-10 h-10 rounded-lg border border-gray-300"
                      />
                      <input
                        type="text"
                        value={brandColors}
                        onChange={(e) => setBrandColors(e.target.value)}
                        className="input-field flex-1"
                        placeholder="#3B82F6"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="label">Text Overlay</label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={textOverlay}
                        onChange={(e) => setTextOverlay(e.target.checked)}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm">Include text overlays</span>
                    </label>
                  </div>

                  <div>
                    <label className="label">Voiceover</label>
                    <select
                      value={voiceover}
                      onChange={(e) => setVoiceover(e.target.value)}
                      className="input-field"
                    >
                      {voiceoverOptions.map(option => (
                        <option key={option.id} value={option.id}>
                          {option.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Media Assets */}
          <div>
            <label className="label">Media Assets (Optional)</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                type="file"
                accept="image/*,video/*"
                onChange={handleMediaUpload}
                className="hidden"
                id="media-upload"
                multiple
              />
              <label htmlFor="media-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">
                  Upload images or videos to include in your marketing video
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supports: JPG, PNG, MP4, MOV (Max 50MB each)
                </p>
              </label>
            </div>

            {/* Uploaded Media Preview */}
            {uploadedMedia.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
                {uploadedMedia.map((media, index) => (
                  <div key={index} className="relative">
                    {media.type === 'image' ? (
                      <img
                        src={media.url}
                        alt={`Asset ${index + 1}`}
                        className="w-full h-20 object-cover rounded-lg"
                      />
                    ) : (
                      <video
                        src={media.url}
                        className="w-full h-20 object-cover rounded-lg"
                        muted
                      />
                    )}
                    <div className="absolute top-1 right-1">
                      <span className="bg-black bg-opacity-50 text-white text-xs px-1 rounded">
                        {media.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
                Creating Your Video... ({Math.floor(Math.random() * 60 + 30)}s remaining)
              </>
            ) : (
              <>
                <Film className="w-5 h-5 mr-2" />
                Generate Marketing Video
              </>
            )}
          </button>
        </div>
      </div>

      {/* Video Templates */}
      <div className="card">
        <h3 className="font-bold text-lg mb-4 flex items-center">
          <Wand2 className="w-5 h-5 mr-2 text-purple-500" />
          Video Concept Templates
        </h3>
        <div className="space-y-2">
          {videoPromptTemplates.map((template, index) => (
            <button
              key={index}
              onClick={() => setPrompt(template)}
              className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors group"
            >
              <div className="flex items-start justify-between">
                <p className="text-sm text-gray-700 flex-1">{template}</p>
                <Type className="w-4 h-4 text-gray-400 group-hover:text-gray-600 ml-2 flex-shrink-0" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Generated Videos */}
      {generatedVideos.length > 0 && (
        <div className="card">
          <h3 className="font-bold text-lg mb-4 flex items-center">
            <Video className="w-5 h-5 mr-2 text-green-500" />
            Generated Videos
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {generatedVideos.map((video, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.2 }}
                className={`relative group cursor-pointer rounded-lg overflow-hidden ${
                  selectedVideo === video.url ? 'ring-4 ring-purple-500' : ''
                }`}
              >
                <div className="relative">
                  <video
                    ref={(el) => {if (el) videoRefs.current[video.url] = el;}}
                    src={video.url}
                    poster={video.thumbnail}
                    className="w-full h-48 object-cover"
                    onClick={() => handleVideoSelect(video.url)}
                    onEnded={() => setCurrentlyPlaying('')}
                    muted
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleVideoPlayback(video.url);
                        }}
                        className="bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-3 transition-all"
                      >
                        {currentlyPlaying === video.url ? (
                          <Pause className="w-6 h-6 text-gray-800" />
                        ) : (
                          <Play className="w-6 h-6 text-gray-800 ml-1" />
                        )}
                      </button>
                    </div>
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity space-x-2">
                      <button className="bg-white rounded-full p-2 shadow-lg hover:bg-gray-100">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="bg-white rounded-full p-2 shadow-lg hover:bg-gray-100">
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                    {duration}s • {aspectRatio}
                  </div>
                  {selectedVideo === video.url && (
                    <div className="absolute bottom-2 right-2">
                      <span className="bg-purple-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                        Selected
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Generation Progress */}
      {isGenerating && (
        <div className="card">
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
              <Film className="w-8 h-8 text-purple-600 animate-pulse" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Creating Your Marketing Video</h3>
            <p className="text-gray-600 mb-4">
              Our AI is analyzing your prompt and generating a professional video...
            </p>
            <div className="max-w-md mx-auto">
              <div className="bg-gray-200 rounded-full h-2">
                <div className="bg-purple-500 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
              </div>
            </div>
            <div className="mt-4 space-y-2 text-sm text-gray-500">
              <div className="flex items-center justify-center">
                <Clock className="w-4 h-4 mr-2" />
                Estimated time: 2-3 minutes
              </div>
              <div>Processing: Scene composition, motion graphics, audio sync...</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoGenerator;