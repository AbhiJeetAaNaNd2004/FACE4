import React, { useRef, useEffect, useState } from 'react';
import { Camera } from '../../types';

interface LiveCameraFeedProps {
  camera: Camera;
  className?: string;
  onError?: (error: string) => void;
  showControls?: boolean;
}

export const LiveCameraFeed: React.FC<LiveCameraFeedProps> = ({
  camera,
  className = '',
  onError,
  showControls = true
}) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [streamUrl, setStreamUrl] = useState<string>('');

  useEffect(() => {
    // Get authentication token
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Authentication required');
      onError?.('Authentication required');
      return;
    }

    // Create stream URL with authentication using the new endpoint
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const url = `${baseUrl}/stream/feed?${camera.id ? `camera_id=${camera.id}&` : ''}auth=${token}`;
    setStreamUrl(url);
    setIsLoading(false);
  }, [camera.id, onError]);

  const handleImageLoad = () => {
    setIsLoading(false);
    setError(null);
  };

  const handleImageError = () => {
    setIsLoading(false);
    const errorMsg = `Failed to load stream from camera ${camera.name}`;
    setError(errorMsg);
    onError?.(errorMsg);
  };

  const refreshStream = () => {
    setIsLoading(true);
    setError(null);
    if (imgRef.current) {
      // Force refresh by updating src with timestamp
      const token = localStorage.getItem('access_token');
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const url = `${baseUrl}/stream/feed?${camera.id ? `camera_id=${camera.id}&` : ''}auth=${token}&t=${Date.now()}`;
      imgRef.current.src = url;
    }
  };

  if (error) {
    return (
      <div className={`bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center ${className}`}>
        <div className="text-red-600 mb-4">
          <svg className="mx-auto h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p className="text-sm font-medium">{error}</p>
        </div>
        {showControls && (
          <button
            onClick={refreshStream}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`relative bg-black rounded-lg overflow-hidden ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading camera feed...</p>
          </div>
        </div>
      )}
      
      <img
        ref={imgRef}
        src={streamUrl}
        alt={`Live feed from ${camera.name}`}
        className="w-full h-full object-cover"
        onLoad={handleImageLoad}
        onError={handleImageError}
        style={{ minHeight: '200px' }}
      />
      
      {/* Camera info overlay */}
      <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
        {camera.name} (ID: {camera.id})
      </div>
      
      {/* Connection status indicator */}
      <div className="absolute top-2 right-2">
        <div className={`w-3 h-3 rounded-full ${!error && !isLoading ? 'bg-green-500' : 'bg-red-500'}`} />
      </div>

      {/* Controls */}
      {showControls && !error && (
        <div className="absolute bottom-2 right-2 flex space-x-2">
          <button
            onClick={refreshStream}
            className="bg-black bg-opacity-75 text-white p-2 rounded hover:bg-opacity-90 transition-opacity"
            title="Refresh stream"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};