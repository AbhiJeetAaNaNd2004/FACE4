import React, { useState, useEffect } from 'react';
import { Camera } from '../../types';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { apiService } from '../../services/api';

interface CameraSettingsModalProps {
  camera: Camera | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (cameraId: number, settings: CameraSettings) => Promise<void>;
}

interface CameraSettings {
  camera_name?: string;
  resolution_width?: number;
  resolution_height?: number;
  fps?: number;
  location_description?: string;
  is_active?: boolean;
}

interface Resolution {
  width: number;
  height: number;
  name: string;
  aspect_ratio: string;
}

export const CameraSettingsModal: React.FC<CameraSettingsModalProps> = ({
  camera,
  isOpen,
  onClose,
  onSave
}) => {
  const [settings, setSettings] = useState<CameraSettings>({});
  const [supportedResolutions, setSupportedResolutions] = useState<Resolution[]>([]);
  const [customResolution, setCustomResolution] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Initialize settings when camera changes
  useEffect(() => {
    if (camera) {
      setSettings({
        camera_name: camera.name,
        resolution_width: camera.resolution_width || 1920,
        resolution_height: camera.resolution_height || 1080,
        fps: camera.fps || 30,
        location_description: camera.location_description || '',
        is_active: camera.is_active
      });
      setError(null);
      setValidationErrors({});
      
      // Load supported resolutions
      loadSupportedResolutions(camera.id);
    }
  }, [camera]);

  const loadSupportedResolutions = async (cameraId: number) => {
    try {
      const response = await apiService.getSupportedResolutions(cameraId);
      if (response.success) {
        setSupportedResolutions(response.data.supported_resolutions);
      }
    } catch (error) {
      console.error('Failed to load supported resolutions:', error);
      // Use default resolutions if API call fails
      setSupportedResolutions([
        { width: 640, height: 480, name: "VGA", aspect_ratio: "4:3" },
        { width: 1280, height: 720, name: "HD 720p", aspect_ratio: "16:9" },
        { width: 1920, height: 1080, name: "Full HD 1080p", aspect_ratio: "16:9" },
        { width: 2560, height: 1440, name: "QHD 1440p", aspect_ratio: "16:9" },
        { width: 3840, height: 2160, name: "4K UHD", aspect_ratio: "16:9" }
      ]);
    }
  };

  const validateSettings = (): boolean => {
    const errors: Record<string, string> = {};

    if (!settings.camera_name?.trim()) {
      errors.camera_name = 'Camera name is required';
    } else if (settings.camera_name.length < 2) {
      errors.camera_name = 'Camera name must be at least 2 characters';
    }

    if (!settings.resolution_width || settings.resolution_width < 320 || settings.resolution_width > 4096) {
      errors.resolution_width = 'Width must be between 320 and 4096 pixels';
    }

    if (!settings.resolution_height || settings.resolution_height < 240 || settings.resolution_height > 2160) {
      errors.resolution_height = 'Height must be between 240 and 2160 pixels';
    }

    if (!settings.fps || settings.fps < 1 || settings.fps > 120) {
      errors.fps = 'FPS must be between 1 and 120';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!camera || !validateSettings()) return;

    try {
      setLoading(true);
      setError(null);
      
      await onSave(camera.id, settings);
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.message || 'Failed to update camera settings');
    } finally {
      setLoading(false);
    }
  };

  const handleResolutionChange = (resolution: Resolution) => {
    setSettings(prev => ({
      ...prev,
      resolution_width: resolution.width,
      resolution_height: resolution.height
    }));
    setCustomResolution(false);
  };

  const handleCustomResolutionToggle = () => {
    setCustomResolution(!customResolution);
  };

  const currentResolution = supportedResolutions.find(
    r => r.width === settings.resolution_width && r.height === settings.resolution_height
  );

  const fpsOptions = [5, 10, 15, 20, 24, 25, 30, 60];

  if (!camera) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Camera Settings - ${camera.name}`}
      size="md"
    >
      <div className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Camera Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Camera Name *
          </label>
          <Input
            type="text"
            value={settings.camera_name || ''}
            onChange={(e) => setSettings(prev => ({ ...prev, camera_name: e.target.value }))}
            placeholder="Enter camera name"
            error={validationErrors.camera_name}
          />
          <p className="text-xs text-gray-500 mt-1">
            This name will be displayed throughout the system
          </p>
        </div>

        {/* Location Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location Description
          </label>
          <Input
            type="text"
            value={settings.location_description || ''}
            onChange={(e) => setSettings(prev => ({ ...prev, location_description: e.target.value }))}
            placeholder="e.g., Main Entrance, Office Floor 2"
          />
          <p className="text-xs text-gray-500 mt-1">
            Describe where this camera is physically located
          </p>
        </div>

        {/* Resolution Settings */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resolution
          </label>
          
          {!customResolution ? (
            <div className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {supportedResolutions.map((resolution) => (
                  <button
                    key={`${resolution.width}x${resolution.height}`}
                    onClick={() => handleResolutionChange(resolution)}
                    className={`p-3 text-left border rounded-lg transition-colors ${
                      currentResolution?.width === resolution.width && currentResolution?.height === resolution.height
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium">{resolution.name}</div>
                    <div className="text-sm text-gray-500">
                      {resolution.width} × {resolution.height} ({resolution.aspect_ratio})
                    </div>
                  </button>
                ))}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleCustomResolutionToggle}
                className="mt-2"
              >
                Set Custom Resolution
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Width (px)
                  </label>
                  <Input
                    type="number"
                    value={settings.resolution_width || ''}
                    onChange={(e) => setSettings(prev => ({ 
                      ...prev, 
                      resolution_width: parseInt(e.target.value) || 0 
                    }))}
                    min={320}
                    max={4096}
                    error={validationErrors.resolution_width}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Height (px)
                  </label>
                  <Input
                    type="number"
                    value={settings.resolution_height || ''}
                    onChange={(e) => setSettings(prev => ({ 
                      ...prev, 
                      resolution_height: parseInt(e.target.value) || 0 
                    }))}
                    min={240}
                    max={2160}
                    error={validationErrors.resolution_height}
                  />
                </div>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleCustomResolutionToggle}
              >
                Choose from Presets
              </Button>
            </div>
          )}
        </div>

        {/* FPS Settings */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Frame Rate (FPS) *
          </label>
          <div className="grid grid-cols-4 gap-2 mb-3">
            {fpsOptions.map((fps) => (
              <button
                key={fps}
                onClick={() => setSettings(prev => ({ ...prev, fps }))}
                className={`p-2 text-center border rounded transition-colors ${
                  settings.fps === fps
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {fps} FPS
              </button>
            ))}
          </div>
          
          <div className="flex items-center space-x-2">
            <Input
              type="number"
              value={settings.fps || ''}
              onChange={(e) => setSettings(prev => ({ 
                ...prev, 
                fps: parseInt(e.target.value) || 0 
              }))}
              min={1}
              max={120}
              placeholder="Custom FPS"
              className="w-32"
              error={validationErrors.fps}
            />
            <span className="text-sm text-gray-500">fps</span>
          </div>
          
          <p className="text-xs text-gray-500 mt-1">
            Higher FPS provides smoother video but uses more processing power
          </p>
        </div>

        {/* Camera Status */}
        <div>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.is_active || false}
              onChange={(e) => setSettings(prev => ({ ...prev, is_active: e.target.checked }))}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span className="text-sm font-medium text-gray-700">
              Camera Active
            </span>
          </label>
          <p className="text-xs text-gray-500 mt-1 ml-7">
            Inactive cameras will not be used for face detection
          </p>
        </div>

        {/* Current Settings Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Current Settings Summary</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-gray-600">Resolution:</div>
            <div className="font-medium">{settings.resolution_width} × {settings.resolution_height}</div>
            <div className="text-gray-600">Frame Rate:</div>
            <div className="font-medium">{settings.fps} FPS</div>
            <div className="text-gray-600">Status:</div>
            <div className={`font-medium ${settings.is_active ? 'text-green-600' : 'text-red-600'}`}>
              {settings.is_active ? 'Active' : 'Inactive'}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            loading={loading}
            disabled={loading}
          >
            Save Settings
          </Button>
        </div>
      </div>
    </Modal>
  );
};