import React, { useEffect, useState } from 'react';
import { useSystemStore } from '../../store/systemStore';
import { useCameraStore } from '../../store/cameraStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { apiService } from '../../services/api';
import { useNavigate } from 'react-router-dom';

export const SuperAdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { 
    dashboardStats, 
    systemStatus, 
    fetchDashboardStats, 
    startSystem, 
    stopSystem, 
    isLoading, 
    error 
  } = useSystemStore();
  const { fetchCameras } = useCameraStore();
  
  const [showAutoDetectModal, setShowAutoDetectModal] = useState(false);
  const [autoDetectLoading, setAutoDetectLoading] = useState(false);
  const [autoDetectResult, setAutoDetectResult] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  const handleSystemControl = async (action: 'start' | 'stop') => {
    try {
      if (action === 'start') {
        await startSystem();
      } else {
        await stopSystem();
      }
      // Refresh dashboard stats after system control
      await fetchDashboardStats();
    } catch (error) {
      console.error('System control failed:', error);
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const handleAutoDetectCameras = async () => {
    try {
      setAutoDetectLoading(true);
      setAutoDetectResult(null);
      
      const response = await apiService.autoDetectCameras();
      setAutoDetectResult(response.message);
      
      // Refresh cameras and dashboard stats
      await fetchCameras();
      await fetchDashboardStats();
    } catch (error: any) {
      setAutoDetectResult(error.response?.data?.message || 'Failed to auto-detect cameras');
    } finally {
      setAutoDetectLoading(false);
    }
  };

  const quickActions = [
    {
      icon: '👥',
      label: 'Manage Users',
      action: () => navigate('/super-admin/users')
    },
    {
      icon: '📹',
      label: 'Camera Settings',
      action: () => navigate('/admin/cameras')
    },
    {
      icon: '🔍',
      label: 'Auto-Detect Cameras',
      action: () => setShowAutoDetectModal(true)
    },
    {
      icon: '📊',
      label: 'View Logs',
      action: () => navigate('/admin/attendance')
    },
    {
      icon: '📺',
      label: 'Live Monitor',
      action: () => navigate('/admin/live-monitor')
    },
    {
      icon: '⚙️',
      label: 'System Config',
      action: () => navigate('/admin/cameras')
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Super Admin Dashboard</h1>
        <p className="text-gray-600">System overview and master controls</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* System Status and Control */}
      <Card>
        <CardHeader>
          <CardTitle>Face Recognition System Control</CardTitle>
          <CardDescription>
            Monitor and control the core face recognition system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <div 
                  className={`h-3 w-3 rounded-full ${
                    systemStatus?.is_running ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
                <span className="font-medium">
                  Status: {systemStatus?.is_running ? 'Running' : 'Stopped'}
                </span>
              </div>
              {systemStatus?.is_running && systemStatus.uptime > 0 && (
                <p className="text-sm text-gray-600">
                  Uptime: {formatUptime(systemStatus.uptime)}
                </p>
              )}
            </div>
            <div className="space-x-2">
              <Button
                onClick={() => handleSystemControl('start')}
                disabled={isLoading || systemStatus?.is_running}
                loading={isLoading}
                variant="default"
              >
                Start System
              </Button>
              <Button
                onClick={() => handleSystemControl('stop')}
                disabled={isLoading || !systemStatus?.is_running}
                loading={isLoading}
                variant="destructive"
              >
                Stop System
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Metrics */}
      {dashboardStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Total Employees</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary-600">
                {dashboardStats.totalEmployees}
              </div>
              <p className="text-sm text-gray-600 mt-1">Registered in system</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Present Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {dashboardStats.presentEmployees}
              </div>
              <p className="text-sm text-gray-600 mt-1">Currently present</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Active Cameras</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {dashboardStats.activeCameras}/{dashboardStats.totalCameras}
              </div>
              <p className="text-sm text-gray-600 mt-1">Online cameras</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Today's Detections</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {dashboardStats.todayAttendance}
              </div>
              <p className="text-sm text-gray-600 mt-1">Face recognitions</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* System Information */}
      {systemStatus && (
        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Cameras Active</label>
                <p className="text-lg font-semibold">{systemStatus.cam_count}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Faces Detected</label>
                <p className="text-lg font-semibold">{systemStatus.faces_detected}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Attendance Count</label>
                <p className="text-lg font-semibold">{systemStatus.attendance_count}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Frequently used administrative tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action, index) => (
              <Button
                key={index}
                variant="outline"
                className="h-20 flex-col hover:bg-gray-50 transition-colors"
                onClick={action.action}
              >
                <span className="text-lg mb-1">{action.icon}</span>
                <span className="text-sm font-medium">{action.label}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Auto-detect Cameras Modal */}
      <Modal
        isOpen={showAutoDetectModal}
        onClose={() => {
          setShowAutoDetectModal(false);
          setAutoDetectResult(null);
        }}
        title="Auto-Detect Cameras"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            This will scan for all available cameras (USB, built-in, and network cameras) 
            and automatically configure them for the face recognition system.
          </p>
          
          {autoDetectResult && (
            <div className={`p-3 rounded-md ${
              autoDetectResult.includes('Failed') 
                ? 'bg-red-50 text-red-700 border border-red-200' 
                : 'bg-green-50 text-green-700 border border-green-200'
            }`}>
              {autoDetectResult}
            </div>
          )}
          
          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => {
                setShowAutoDetectModal(false);
                setAutoDetectResult(null);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAutoDetectCameras}
              loading={autoDetectLoading}
              disabled={autoDetectLoading}
            >
              {autoDetectLoading ? 'Detecting...' : 'Start Detection'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};