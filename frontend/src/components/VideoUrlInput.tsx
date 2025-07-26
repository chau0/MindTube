'use client';

import { useState } from 'react';
import { Play, AlertCircle } from 'lucide-react';
import { useProcessingStore } from '@/lib/store';
import { utils } from '@/lib/api';
import toast from 'react-hot-toast';

export function VideoUrlInput() {
  const [url, setUrl] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const { startProcessing, isProcessing, settings } = useProcessingStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      toast.error('Please enter a YouTube URL');
      return;
    }

    if (!utils.isValidYouTubeUrl(url)) {
      toast.error('Please enter a valid YouTube URL');
      return;
    }

    setIsValidating(true);

    try {
      await startProcessing({
        url: url.trim(),
        enable_asr: settings.enableAsr,
        language: settings.preferredLanguage,
      });
      
      // Clear the input after successful submission
      setUrl('');
    } catch (error) {
      // Error is already handled in the store and shown via toast
    } finally {
      setIsValidating(false);
    }
  };

  const isLoading = isValidating || isProcessing;

  return (
    <div className="card">
      <div className="card-body">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 mb-2">
              YouTube Video URL
            </label>
            <div className="relative">
              <input
                id="youtube-url"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="input-primary pr-12"
                disabled={isLoading}
                autoComplete="url"
              />
              {url && !utils.isValidYouTubeUrl(url) && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                </div>
              )}
            </div>
            {url && !utils.isValidYouTubeUrl(url) && (
              <p className="mt-1 text-sm text-red-600">
                Please enter a valid YouTube URL
              </p>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Supports videos up to {settings.maxDurationMinutes} minutes
            </div>
            <button
              type="submit"
              disabled={isLoading || !url || !utils.isValidYouTubeUrl(url)}
              className="btn-primary"
            >
              {isLoading ? (
                <>
                  <div className="spinner w-4 h-4 mr-2" />
                  {isValidating ? 'Validating...' : 'Processing...'}
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Summarize Video
                </>
              )}
            </button>
          </div>
        </form>

        {/* Example URLs */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-3">Try these examples:</p>
          <div className="space-y-2">
            {[
              'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
              'https://youtu.be/dQw4w9WgXcQ',
            ].map((exampleUrl, index) => (
              <button
                key={index}
                onClick={() => setUrl(exampleUrl)}
                disabled={isLoading}
                className="text-sm text-primary-600 hover:text-primary-700 block truncate max-w-full text-left"
              >
                {exampleUrl}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}