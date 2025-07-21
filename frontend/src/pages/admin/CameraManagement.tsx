import React, { useEffect, useState } from 'react';
import { useCameraStore } from '../../store/cameraStore';
import { Camera, CameraCreate } from '../../types';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { CameraSettingsModal } from '../../components/camera/CameraSettingsModal';

export const CameraManagement: React.FC = () => {
  const {
    cameras,
    discoveredCameras,
    isLoading,
    error,
    fetchCameras,
    createCamera,
    updateCamera,
    deleteCamera,
    discoverCameras,
    updateCameraSettings,
    autoDetectCameras,
    clearError
  } = useCameraStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDiscoverModalOpen, setIsDiscoverModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [createFormData, setCreateFormData] = useState<CameraCreate>({
    name: '',
    location: '',
    stream_url: '',
    is_active: true
  });
  const [editFormData, setEditFormData] = useState<Partial<CameraCreate>>({});
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  const validateForm = (data: CameraCreate | Partial<CameraCreate>) => {
    const errors: Record<string, string> = {};

    if ('name' in data && !data.name?.trim()) {
      errors.name = 'Camera name is required';
    }

    if ('location' in data && !data.location?.trim()) {
      errors.location = 'Location is required';
    }

    if ('stream_url' in data && !data.stream_url?.trim()) {
      errors.stream_url = 'Stream URL is required';
    } else if ('stream_url' in data && data.stream_url && !isValidUrl(data.stream_url)) {
      errors.stream_url = 'Please enter a valid URL';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const isValidUrl = (string: string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  const handleCreateCamera = async () => {
    if (!validateForm(createFormData)) return;

    try {
      await createCamera(createFormData);
      setIsCreateModalOpen(false);
      setCreateFormData({
        name: '',
        location: '',
        stream_url: '',
        is_active: true
      });
      setFormErrors({});
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleUpdateCamera = async () => {
    if (!selectedCamera || !validateForm(editFormData)) return;

    try {
      await updateCamera(selectedCamera.id, editFormData);
      setIsEditModalOpen(false);
      setSelectedCamera(null);
      setEditFormData({});
      setFormErrors({});
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleDeleteCamera = async (cameraId: number) => {
    if (window.confirm('Are you sure you want to delete this camera? This action cannot be undone.')) {
      try {
        await deleteCamera(cameraId);
      } catch (error) {
        // Error is handled by store
      }
    }
  };

  const openEditModal = (camera: Camera) => {
    setSelectedCamera(camera);
    setEditFormData({
      name: camera.name,
      location: camera.location,
      stream_url: camera.stream_url,
      is_active: camera.is_active
    });
    setIsEditModalOpen(true);
  };

  const openSettingsModal = (camera: Camera) => {
    setSelectedCamera(camera);
    setIsSettingsModalOpen(true);
  };

  const handleUpdateCameraSettings = async (cameraId: number, settings: any) => {
    try {
      await updateCameraSettings(cameraId, settings);
      // Refresh the camera list
      await fetchCameras();
    } catch (error) {
      throw error; // Re-throw to let the modal handle the error
    }
  };

  const handleAutoDetectCameras = async () => {
    try {
      await autoDetectCameras();
      // Refresh the camera list after auto-detection
      await fetchCameras();
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleDiscoverCameras = async () => {
    await discoverCameras();
    setIsDiscoverModalOpen(true);
  };

  const addDiscoveredCamera = (discoveredCamera: any) => {
    setCreateFormData({
      name: `Camera ${discoveredCamera.name || discoveredCamera.ip}`,
      location: `Network Camera at ${discoveredCamera.ip}`,
      stream_url: discoveredCamera.rtsp_url || `rtsp://${discoveredCamera.ip}/stream`,
      is_active: true
    });
    setIsDiscoverModalOpen(false);
    setIsCreateModalOpen(true);
  };

  const getStatusBadge = (isActive: boolean) => (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
      isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    }`}>
      {isActive ? 'Active' : 'Inactive'}
    </span>
  );

  const columns = [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
    },
    {
      key: 'location',
      header: 'Location',
      sortable: true,
    },
    {
      key: 'stream_url',
      header: 'Stream URL',
      render: (value: string) => (
        <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
          {value.length > 40 ? `${value.substring(0, 40)}...` : value}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (value: boolean) => getStatusBadge(value),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (_: any, camera: Camera) => (
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => openSettingsModal(camera)}
            title="Camera Settings"
          >
            ⚙️ Settings
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => openEditModal(camera)}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => handleDeleteCamera(camera.id)}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  const discoveredColumns = [
    {
      key: 'ip',
      header: 'IP Address',
    },
    {
      key: 'name',
      header: 'Name',
      render: (value: string) => value || 'Unknown',
    },
    {
      key: 'manufacturer',
      header: 'Manufacturer',
      render: (value: string) => value || 'Unknown',
    },
    {
      key: 'model',
      header: 'Model',
      render: (value: string) => value || 'Unknown',
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (_: any, camera: any) => (
        <Button
          size="sm"
          onClick={() => addDiscoveredCamera(camera)}
        >
          Add Camera
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Camera Management</h1>
          <p className="text-gray-600">Manage cameras and monitoring settings</p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={handleAutoDetectCameras}
            disabled={isLoading}
          >
            🔍 Auto-Detect Cameras
          </Button>
          <Button variant="outline" onClick={handleDiscoverCameras}>
            Discover Network Cameras
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            Add Camera
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center justify-between">
            <p className="text-sm">{error}</p>
            <button onClick={clearError} className="text-red-500 hover:text-red-700">
              ×
            </button>
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Total Cameras</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {cameras.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Active Cameras</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {cameras.filter(camera => camera.is_active).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Monitoring Points</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {new Set(cameras.map(camera => camera.location)).size}
            </div>
            <p className="text-sm text-gray-600 mt-1">Unique locations</p>
          </CardContent>
        </Card>
      </div>

      {/* Cameras Table */}
      <DataTable
        data={cameras}
        columns={columns}
        title="Cameras"
        loading={isLoading}
        emptyMessage="No cameras found"
      />

      {/* Create Camera Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Add New Camera"
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateCamera} loading={isLoading}>
              Add Camera
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Camera Name"
            value={createFormData.name}
            onChange={(e) => setCreateFormData(prev => ({ ...prev, name: e.target.value }))}
            error={formErrors.name}
            placeholder="Enter camera name"
          />

          <Input
            label="Location"
            value={createFormData.location}
            onChange={(e) => setCreateFormData(prev => ({ ...prev, location: e.target.value }))}
            error={formErrors.location}
            placeholder="Enter camera location"
          />

          <Input
            label="Stream URL"
            value={createFormData.stream_url}
            onChange={(e) => setCreateFormData(prev => ({ ...prev, stream_url: e.target.value }))}
            error={formErrors.stream_url}
            placeholder="rtsp://camera-ip:port/stream"
            hint="RTSP, HTTP, or local device URL"
          />

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={createFormData.is_active}
              onChange={(e) => setCreateFormData(prev => ({ ...prev, is_active: e.target.checked }))}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label className="text-sm font-medium text-gray-700">
              Camera is active
            </label>
          </div>
        </div>
      </Modal>

      {/* Edit Camera Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Camera"
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateCamera} loading={isLoading}>
              Update Camera
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Camera Name"
            value={editFormData.name || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, name: e.target.value }))}
            error={formErrors.name}
            placeholder="Enter camera name"
          />

          <Input
            label="Location"
            value={editFormData.location || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, location: e.target.value }))}
            error={formErrors.location}
            placeholder="Enter camera location"
          />

          <Input
            label="Stream URL"
            value={editFormData.stream_url || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, stream_url: e.target.value }))}
            error={formErrors.stream_url}
            placeholder="rtsp://camera-ip:port/stream"
          />

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={editFormData.is_active ?? true}
              onChange={(e) => setEditFormData(prev => ({ ...prev, is_active: e.target.checked }))}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label className="text-sm font-medium text-gray-700">
              Camera is active
            </label>
          </div>
        </div>
      </Modal>

      {/* Discover Cameras Modal */}
      <Modal
        isOpen={isDiscoverModalOpen}
        onClose={() => setIsDiscoverModalOpen(false)}
        title="Discovered Cameras"
        size="lg"
        footer={
          <Button onClick={() => setIsDiscoverModalOpen(false)}>
            Close
          </Button>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            The following cameras were discovered on your network:
          </p>
          
          {discoveredCameras.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No cameras discovered. Make sure cameras are connected to the network.
            </div>
          ) : (
            <DataTable
              data={discoveredCameras}
              columns={discoveredColumns}
              searchable={false}
              emptyMessage="No cameras discovered"
            />
          )}
        </div>
      </Modal>

      {/* Camera Settings Modal */}
      <CameraSettingsModal
        camera={selectedCamera}
        isOpen={isSettingsModalOpen}
        onClose={() => {
          setIsSettingsModalOpen(false);
          setSelectedCamera(null);
        }}
        onSave={handleUpdateCameraSettings}
      />
    </div>
  );
};