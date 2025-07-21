import React, { useEffect, useState } from 'react';
import { useCameraStore } from '../../store/cameraStore';
import { useEmployeeStore } from '../../store/employeeStore';
import { LiveCameraFeed } from '../../components/camera/LiveCameraFeed';
import { CameraSwitcher } from '../../components/camera/CameraSwitcher';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useWebSocket } from '../../hooks/useWebSocket';

interface RealtimeActivity {
  id: string;
  timestamp: string;
  employee_id?: string;
  employee_name?: string;
  camera_id: number;
  camera_name: string;
  action: 'enter' | 'exit' | 'recognized' | 'unknown';
  confidence?: number;
}

export const LiveMonitor: React.FC = () => {
  const { cameras, fetchCameras } = useCameraStore();
  const { presentEmployees, fetchPresentEmployees } = useEmployeeStore();
  const [realtimeActivity, setRealtimeActivity] = useState<RealtimeActivity[]>([]);
  const [selectedCameras, setSelectedCameras] = useState<number[]>([]);
  const [showCameraSwitcher, setShowCameraSwitcher] = useState(false);

  // WebSocket for real-time activity updates
  const { isConnected } = useWebSocket({
    url: 'ws://localhost:8000/ws/activity',
    onMessage: (message) => {
      if (message.type === 'activity') {
        const activity: RealtimeActivity = {
          id: `${Date.now()}-${Math.random()}`,
          timestamp: message.timestamp,
          ...message.data
        };
        
        setRealtimeActivity(prev => [activity, ...prev.slice(0, 49)]); // Keep last 50 activities
      } else if (message.type === 'attendance_update') {
        // Refresh present employees when attendance changes
        fetchPresentEmployees();
      }
    }
  });

  useEffect(() => {
    fetchCameras();
    fetchPresentEmployees();
  }, [fetchCameras, fetchPresentEmployees]);

  // Auto-select first 4 active cameras
  useEffect(() => {
    if (cameras.length > 0 && selectedCameras.length === 0) {
      const activeCameras = cameras.filter(camera => camera.is_active).slice(0, 4);
      setSelectedCameras(activeCameras.map(camera => camera.id));
    }
  }, [cameras, selectedCameras.length]);

  const toggleCameraSelection = (cameraId: number) => {
    setSelectedCameras(prev => {
      if (prev.includes(cameraId)) {
        return prev.filter(id => id !== cameraId);
      } else if (prev.length < 4) {
        return [...prev, cameraId];
      } else {
        // Replace the first camera if already at max
        return [cameraId, ...prev.slice(0, 3)];
      }
    });
  };

  const getActivityIcon = (action: string) => {
    switch (action) {
      case 'enter':
        return '🚪➡️';
      case 'exit':
        return '🚪⬅️';
      case 'recognized':
        return '✅';
      case 'unknown':
        return '❓';
      default:
        return '📹';
    }
  };

  const getActivityColor = (action: string) => {
    switch (action) {
      case 'enter':
        return 'text-green-600';
      case 'exit':
        return 'text-orange-600';
      case 'recognized':
        return 'text-blue-600';
      case 'unknown':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const selectedCameraObjects = cameras.filter(camera => 
    selectedCameras.includes(camera.id)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Monitor</h1>
          <p className="text-gray-600">Real-time camera feeds and activity monitoring</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowCameraSwitcher(!showCameraSwitcher)}
          >
            📹 Switch Cameras
          </Button>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
            isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span>{isConnected ? 'Live' : 'Disconnected'}</span>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Active Cameras</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {cameras.filter(camera => camera.is_active).length}
            </div>
            <p className="text-sm text-gray-600 mt-1">of {cameras.length} total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Present Now</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {presentEmployees.length}
            </div>
            <p className="text-sm text-gray-600 mt-1">employees</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {realtimeActivity.length}
            </div>
            <p className="text-sm text-gray-600 mt-1">events logged</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Connection Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              isConnected ? 'text-green-600' : 'text-red-600'
            }`}>
              {isConnected ? 'Online' : 'Offline'}
            </div>
            <p className="text-sm text-gray-600 mt-1">Real-time updates</p>
          </CardContent>
        </Card>
      </div>

      {/* Camera Switcher Panel */}
      {showCameraSwitcher && (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <CameraSwitcher
              cameras={cameras}
              selectedCameras={selectedCameras}
              onCameraToggle={toggleCameraSelection}
              maxSelection={4}
            />
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera Feeds */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Live Camera Feeds</CardTitle>
                  <p className="text-sm text-gray-600">
                    Viewing {selectedCameraObjects.length} of {cameras.filter(c => c.is_active).length} active cameras
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowCameraSwitcher(!showCameraSwitcher)}
                >
                  {showCameraSwitcher ? 'Hide' : 'Show'} Camera Selector
                </Button>
              </div>
            </CardHeader>
            <CardContent>

              {/* Camera Grid */}
              <div className={`grid gap-4 ${
                selectedCameraObjects.length === 1 ? 'grid-cols-1' :
                selectedCameraObjects.length === 2 ? 'grid-cols-2' :
                selectedCameraObjects.length === 3 ? 'grid-cols-2' :
                'grid-cols-2'
              }`}>
                {selectedCameraObjects.map(camera => (
                  <div key={camera.id} className="aspect-video">
                    <LiveCameraFeed
                      camera={camera}
                      className="w-full h-full"
                      showControls={true}
                    />
                  </div>
                ))}
              </div>

              {selectedCameraObjects.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <div className="text-4xl mb-2">📹</div>
                  <p>Select cameras to start monitoring</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Activity Feed */}
        <div className="space-y-6">
          {/* Currently Present */}
          <Card>
            <CardHeader>
              <CardTitle>Currently Present</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {presentEmployees.length === 0 ? (
                  <p className="text-gray-500 text-sm">No employees present</p>
                ) : (
                  presentEmployees.map(employee => (
                    <div key={employee.employee_id} className="flex items-center space-x-2 text-sm">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="font-medium">{employee.name}</span>
                      <span className="text-gray-500">({employee.employee_id})</span>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Real-time Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Real-time Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {realtimeActivity.length === 0 ? (
                  <p className="text-gray-500 text-sm">No recent activity</p>
                ) : (
                  realtimeActivity.map(activity => (
                    <div key={activity.id} className="border-l-2 border-gray-200 pl-3 pb-3">
                      <div className="flex items-start space-x-2">
                        <span className="text-lg">{getActivityIcon(activity.action)}</span>
                        <div className="flex-1 min-w-0">
                          <div className={`font-medium text-sm ${getActivityColor(activity.action)}`}>
                            {activity.employee_name || 'Unknown Person'}
                          </div>
                          <div className="text-xs text-gray-500">
                            {activity.camera_name}
                          </div>
                          <div className="text-xs text-gray-400">
                            {new Date(activity.timestamp).toLocaleTimeString()}
                          </div>
                          {activity.confidence && (
                            <div className="text-xs text-gray-400">
                              Confidence: {Math.round(activity.confidence * 100)}%
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};