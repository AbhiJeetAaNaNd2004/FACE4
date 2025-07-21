import { create } from 'zustand';
import { SystemStatus, Camera, DashboardStats } from '../types';
import { apiService } from '../services/api';

interface SystemState {
  systemStatus: SystemStatus | null;
  cameras: Camera[];
  logs: string[];
  dashboardStats: DashboardStats | null;
  isLoading: boolean;
  error: string | null;
}

interface SystemActions {
  fetchSystemStatus: () => Promise<void>;
  startSystem: () => Promise<void>;
  stopSystem: () => Promise<void>;
  fetchCameras: () => Promise<void>;
  fetchLogs: (limit?: number) => Promise<void>;
  fetchDashboardStats: () => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useSystemStore = create<SystemState & SystemActions>()((set, get) => ({
  // State
  systemStatus: null,
  cameras: [],
  logs: [],
  dashboardStats: null,
  isLoading: false,
  error: null,

  // Actions
  fetchSystemStatus: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiService.getSystemStatus();
      set({
        systemStatus: response.data || null,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch system status',
        isLoading: false,
      });
    }
  },

  startSystem: async () => {
    try {
      set({ isLoading: true, error: null });
      await apiService.startFaceDetection();
      // Refresh system status after starting
      await get().fetchSystemStatus();
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to start system',
        isLoading: false,
      });
      throw error;
    }
  },

  stopSystem: async () => {
    try {
      set({ isLoading: true, error: null });
      await apiService.stopFaceDetection();
      // Refresh system status after stopping
      await get().fetchSystemStatus();
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to stop system',
        isLoading: false,
      });
      throw error;
    }
  },

  fetchCameras: async () => {
    try {
      set({ isLoading: true, error: null });
      const cameras = await apiService.getCameras();
      set({
        cameras,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch cameras',
        isLoading: false,
      });
    }
  },

  fetchLogs: async (limit = 100) => {
    try {
      set({ isLoading: true, error: null });
      const logs = await apiService.getSystemLogs(limit);
      set({
        logs,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch logs',
        isLoading: false,
      });
    }
  },

  fetchDashboardStats: async () => {
    try {
      set({ isLoading: true, error: null });
      
      // Fetch data in parallel
      const [employees, presentEmployees, cameras, systemStatus] = await Promise.all([
        apiService.getEmployees(),
        apiService.getPresentEmployees(),
        apiService.getCameras(),
        apiService.getSystemStatus(),
      ]);

      const dashboardStats: DashboardStats = {
        totalEmployees: employees.length,
        presentEmployees: presentEmployees.total_count,
        totalCameras: cameras.length,
        activeCameras: cameras.filter(camera => camera.is_active).length,
        systemStatus: systemStatus.data?.is_running ? 'running' : 'stopped',
        todayAttendance: systemStatus.data?.attendance_count || 0,
      };

      set({
        dashboardStats,
        systemStatus: systemStatus.data || null,
        cameras,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch dashboard stats',
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
}));