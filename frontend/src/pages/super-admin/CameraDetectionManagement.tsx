import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { apiService } from '../../services/api';

// Simple notification system (replace with proper toast library if needed)
const notify = {
  success: (message: string) => {
    console.log('SUCCESS:', message);
    alert('✅ ' + message);
  },
  error: (message: string) => {
    console.error('ERROR:', message);
    alert('❌ ' + message);
  }
};

interface DetectedCamera {
  camera_id: number;
  name: string;
  type: string;
  source: string;
  resolution: string;
  resolution_width: number;
  resolution_height: number;
  fps: number;
  status: string;
  is_working: boolean;
  last_seen: string | null;
  ip_address: string | null;
  stream_url: string | null;
  is_configured_for_fts: boolean;
  fts_config?: {
    database_id: number;
    enabled: boolean;
    camera_name: string;
    location: string;
  } | null;
}

interface ConfiguredCamera {
  id: number;
  name: string;
  location: string;
  camera_type: string;
  source: string;
  resolution: string;
  fps: number;
  is_active: boolean;
  tripwires: Array<{
    id: number;
    name: string;
    position: number;
    direction: string;
    spacing: number;
  }>;
}

interface ConfigurationForm {
  camera_name: string;
  location: string;
  camera_type: 'entry' | 'exit' | 'monitoring';
  enabled: boolean;
  tripwires: Array<{
    name: string;
    position: number;
    direction: 'horizontal' | 'vertical';
    spacing: number;
  }>;
}

const CameraDetectionManagement: React.FC = () => {
  const [detectedCameras, setDetectedCameras] = useState<DetectedCamera[]>([]);
  const [configuredCameras, setConfiguredCameras] = useState<ConfiguredCamera[]>([]);
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<DetectedCamera | null>(null);
  const [stats, setStats] = useState({
    total_detected: 0,
    working_cameras: 0,
    configured_cameras: 0,
    available_for_configuration: 0
  });

  const [configForm, setConfigForm] = useState<ConfigurationForm>({
    camera_name: '',
    location: '',
    camera_type: 'monitoring',
    enabled: true,
    tripwires: [
      {
        name: 'Detection Zone',
        position: 0.5,
        direction: 'horizontal',
        spacing: 0.05
      }
    ]
  });

  useEffect(() => {
    loadDetectedCameras();
    loadConfiguredCameras();
  }, []);

  const loadDetectedCameras = async () => {
    try {
      const response = await apiService.getDetectedCameras();
      if (response.success) {
        setDetectedCameras(response.data.detected_cameras);
        setStats(prev => ({
          ...prev,
          total_detected: response.data.total_detected,
          working_cameras: response.data.working_cameras
        }));
      }
    } catch (error) {
      console.error('Failed to load detected cameras:', error);
    }
  };

  const loadConfiguredCameras = async () => {
    try {
      const response = await apiService.getFtsConfiguredCameras();
      if (response.success) {
        setConfiguredCameras(response.data.configured_cameras);
        setStats(prev => ({
          ...prev,
          configured_cameras: response.data.total_configured
        }));
      }
    } catch (error) {
      console.error('Failed to load configured cameras:', error);
    }
  };

  const runCameraDetection = async () => {
    setDetecting(true);
    try {
      const response = await apiService.detectAllCameras();
      if (response.success) {
        setDetectedCameras(response.data.detected_cameras);
        setStats({
          total_detected: response.data.total_detected,
          working_cameras: response.data.working_cameras,
          configured_cameras: response.data.configured_cameras,
          available_for_configuration: response.data.available_for_configuration
        });
        notify.success(`Camera detection completed! Found ${response.data.working_cameras} working cameras.`);
      }
          } catch (error: any) {
        notify.error('Failed to detect cameras: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDetecting(false);
    }
  };

  const openConfigurationModal = (camera: DetectedCamera) => {
    if (!camera.is_working) {
      notify.error('Cannot configure a non-working camera');
      return;
    }
    if (camera.is_configured_for_fts) {
      notify.error('Camera is already configured for FTS');
      return;
    }

    setSelectedCamera(camera);
    setConfigForm({
      camera_name: camera.name,
      location: '',
      camera_type: 'monitoring',
      enabled: true,
      tripwires: [
        {
          name: 'Detection Zone',
          position: 0.5,
          direction: 'horizontal',
          spacing: 0.05
        }
      ]
    });
    setShowConfigModal(true);
  };

  const configureCamera = async () => {
    if (!selectedCamera) return;

    setLoading(true);
    try {
      const configData = {
        detected_camera_id: selectedCamera.camera_id,
        camera_name: configForm.camera_name,
        location: configForm.location,
        camera_type: configForm.camera_type,
        enabled: configForm.enabled,
        tripwires: configForm.tripwires
      };

      const response = await apiService.configureCameraForFts(configData);
      if (response.success) {
        notify.success(`Camera "${configForm.camera_name}" configured successfully!`);
        setShowConfigModal(false);
        loadDetectedCameras();
        loadConfiguredCameras();
      }
    } catch (error: any) {
      notify.error('Failed to configure camera: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const removeFromFts = async (configuredCamera: ConfiguredCamera) => {
    if (!window.confirm(`Are you sure you want to remove "${configuredCamera.name}" from FTS configuration?`)) {
      return;
    }

    try {
      const response = await apiService.removeCameraFromFts(configuredCamera.id);
      if (response.success) {
        notify.success(`Camera "${configuredCamera.name}" removed from FTS configuration`);
        loadDetectedCameras();
        loadConfiguredCameras();
      }
    } catch (error: any) {
      notify.error('Failed to remove camera: ' + (error.response?.data?.detail || error.message));
    }
  };

  const addTripwire = () => {
    setConfigForm(prev => ({
      ...prev,
      tripwires: [
        ...prev.tripwires,
        {
          name: `Zone ${prev.tripwires.length + 1}`,
          position: 0.5,
          direction: 'horizontal',
          spacing: 0.05
        }
      ]
    }));
  };

  const removeTripwire = (index: number) => {
    setConfigForm(prev => ({
      ...prev,
      tripwires: prev.tripwires.filter((_, i) => i !== index)
    }));
  };

  const updateTripwire = (index: number, field: string, value: any) => {
    setConfigForm(prev => ({
      ...prev,
      tripwires: prev.tripwires.map((tw, i) => 
        i === index ? { ...tw, [field]: value } : tw
      )
    }));
  };

  const getCameraTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'usb': return 'bg-blue-100 text-blue-800';
      case 'built-in': return 'bg-green-100 text-green-800';
      case 'ip': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (isWorking: boolean, isConfigured: boolean) => {
    if (isConfigured) return 'bg-indigo-100 text-indigo-800';
    if (isWorking) return 'bg-green-100 text-green-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusText = (isWorking: boolean, isConfigured: boolean) => {
    if (isConfigured) return 'Configured for FTS';
    if (isWorking) return 'Available';
    return 'Not Working';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Camera Detection & Configuration</h1>
          <p className="text-gray-600 mt-2">
            Detect available cameras and configure them for Face Tracking System
          </p>
        </div>
        <Button 
          onClick={runCameraDetection} 
          disabled={detecting}
          className="flex items-center space-x-2"
        >
          {detecting && <LoadingSpinner size="sm" />}
          <span>{detecting ? 'Detecting...' : 'Detect Cameras'}</span>
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total_detected}</div>
              <div className="text-sm text-gray-600">Total Detected</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.working_cameras}</div>
              <div className="text-sm text-gray-600">Working Cameras</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">{stats.configured_cameras}</div>
              <div className="text-sm text-gray-600">Configured for FTS</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.available_for_configuration}</div>
              <div className="text-sm text-gray-600">Available to Configure</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detected Cameras */}
      <Card>
        <CardHeader>
          <CardTitle>Detected Cameras</CardTitle>
        </CardHeader>
        <CardContent>
          {detectedCameras.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No cameras detected. Click "Detect Cameras" to scan for available cameras.
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {detectedCameras.map((camera) => (
                <Card key={camera.camera_id} className="border">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{camera.name}</h3>
                        <p className="text-sm text-gray-600">Source: {camera.source}</p>
                      </div>
                      <div className="flex flex-col space-y-1">
                        <Badge className={getCameraTypeColor(camera.type)}>
                          {camera.type}
                        </Badge>
                        <Badge className={getStatusColor(camera.is_working, camera.is_configured_for_fts)}>
                          {getStatusText(camera.is_working, camera.is_configured_for_fts)}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resolution:</span>
                        <span>{camera.resolution}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">FPS:</span>
                        <span>{camera.fps}</span>
                      </div>
                      {camera.ip_address && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">IP Address:</span>
                          <span>{camera.ip_address}</span>
                        </div>
                      )}
                      {camera.last_seen && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Last Seen:</span>
                          <span>{new Date(camera.last_seen).toLocaleString()}</span>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 flex space-x-2">
                      {camera.is_working && !camera.is_configured_for_fts && (
                        <Button 
                          size="sm" 
                          onClick={() => openConfigurationModal(camera)}
                          className="flex-1"
                        >
                          Configure for FTS
                        </Button>
                      )}
                      {camera.is_configured_for_fts && camera.fts_config && (
                        <div className="flex-1 text-center py-2 px-3 bg-indigo-50 rounded-md">
                          <div className="text-sm font-medium text-indigo-800">
                            Configured as: {camera.fts_config.camera_name}
                          </div>
                          <div className="text-xs text-indigo-600">
                            Location: {camera.fts_config.location}
                          </div>
                        </div>
                      )}
                      {!camera.is_working && (
                        <div className="flex-1 text-center py-2 px-3 bg-red-50 rounded-md">
                          <div className="text-sm text-red-800">Camera not responding</div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configured Cameras for FTS */}
      <Card>
        <CardHeader>
          <CardTitle>Cameras Configured for FTS</CardTitle>
        </CardHeader>
        <CardContent>
          {configuredCameras.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No cameras configured for FTS yet. Configure cameras from the detected list above.
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {configuredCameras.map((camera) => (
                <Card key={camera.id} className="border">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{camera.name}</h3>
                        <p className="text-sm text-gray-600">{camera.location}</p>
                      </div>
                      <div className="flex flex-col space-y-1">
                        <Badge className={camera.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                          {camera.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        <Badge className="bg-blue-100 text-blue-800">
                          {camera.camera_type}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Source:</span>
                        <span>{camera.source}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resolution:</span>
                        <span>{camera.resolution}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tripwires:</span>
                        <span>{camera.tripwires.length}</span>
                      </div>
                    </div>

                    <div className="mt-4">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => removeFromFts(camera)}
                        className="w-full text-red-600 border-red-300 hover:bg-red-50"
                      >
                        Remove from FTS
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configuration Modal */}
      <Modal
        isOpen={showConfigModal}
        onClose={() => setShowConfigModal(false)}
        title="Configure Camera for FTS"
        size="lg"
      >
        {selectedCamera && (
          <div className="space-y-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Camera Details</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Type:</span> {selectedCamera.type}
                </div>
                <div>
                  <span className="text-gray-600">Source:</span> {selectedCamera.source}
                </div>
                <div>
                  <span className="text-gray-600">Resolution:</span> {selectedCamera.resolution}
                </div>
                <div>
                  <span className="text-gray-600">FPS:</span> {selectedCamera.fps}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Camera Name
                </label>
                <input
                  type="text"
                  value={configForm.camera_name}
                  onChange={(e) => setConfigForm(prev => ({ ...prev, camera_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={configForm.location}
                  onChange={(e) => setConfigForm(prev => ({ ...prev, location: e.target.value }))}
                  placeholder="e.g., Main Entrance, Office 101"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Camera Type
                </label>
                <select
                  value={configForm.camera_type}
                  onChange={(e) => setConfigForm(prev => ({ ...prev, camera_type: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="entry">Entry Point</option>
                  <option value="exit">Exit Point</option>
                  <option value="monitoring">General Monitoring</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enabled"
                  checked={configForm.enabled}
                  onChange={(e) => setConfigForm(prev => ({ ...prev, enabled: e.target.checked }))}
                  className="mr-2"
                />
                <label htmlFor="enabled" className="text-sm font-medium text-gray-700">
                  Enable camera for tracking
                </label>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Detection Zones (Tripwires)
                  </label>
                  <Button size="sm" onClick={addTripwire}>
                    Add Zone
                  </Button>
                </div>
                
                <div className="space-y-3">
                  {configForm.tripwires.map((tripwire, index) => (
                    <div key={index} className="border p-3 rounded-md">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Name</label>
                          <input
                            type="text"
                            value={tripwire.name}
                            onChange={(e) => updateTripwire(index, 'name', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Direction</label>
                          <select
                            value={tripwire.direction}
                            onChange={(e) => updateTripwire(index, 'direction', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                          >
                            <option value="horizontal">Horizontal</option>
                            <option value="vertical">Vertical</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Position (0-1)</label>
                          <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={tripwire.position}
                            onChange={(e) => updateTripwire(index, 'position', parseFloat(e.target.value))}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex items-end">
                          {configForm.tripwires.length > 1 && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeTripwire(index)}
                              className="text-red-600 border-red-300 hover:bg-red-50"
                            >
                              Remove
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowConfigModal(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={configureCamera}
                disabled={loading || !configForm.camera_name || !configForm.location}
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Configure Camera'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default CameraDetectionManagement;