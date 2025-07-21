import { create } from 'zustand';
import { Camera, CameraCreate, Tripwire } from '../types';
import { apiService } from '../services/api';

interface CameraState {
  cameras: Camera[];
  selectedCamera: Camera | null;
  tripwires: Tripwire[];
  discoveredCameras: any[];
  isLoading: boolean;
  error: string | null;
}

interface CameraActions {
  fetchCameras: () => Promise<void>;
  createCamera: (cameraData: CameraCreate) => Promise<void>;
  updateCamera: (cameraId: number, updateData: Partial<CameraCreate>) => Promise<void>;
  deleteCamera: (cameraId: number) => Promise<void>;
  discoverCameras: () => Promise<void>;
  autoDetectCameras: () => Promise<void>;
  getDetectedCameras: () => Promise<any>;
  updateCameraSettings: (cameraId: number, settings: any) => Promise<void>;
  fetchTripwires: (cameraId: number) => Promise<void>;
  createTripwire: (cameraId: number, tripwireData: any) => Promise<void>;
  updateTripwire: (tripwireId: number, updateData: any) => Promise<void>;
  deleteTripwire: (tripwireId: number) => Promise<void>;
  setSelectedCamera: (camera: Camera | null) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useCameraStore = create<CameraState & CameraActions>()((set, get) => ({
  // State
  cameras: [],
  selectedCamera: null,
  tripwires: [],
  discoveredCameras: [],
  isLoading: false,
  error: null,

  // Actions
  fetchCameras: async () => {
    try {
      set({ isLoading: true, error: null });
      const cameras = await apiService.getCameras();
      set({ cameras, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch cameras',
        isLoading: false,
      });
    }
  },

  createCamera: async (cameraData: CameraCreate) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.createCamera(cameraData);
      
      // Refresh cameras list
      await get().fetchCameras();
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to create camera',
        isLoading: false,
      });
      throw error;
    }
  },

  updateCamera: async (cameraId: number, updateData: Partial<CameraCreate>) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.updateCamera(cameraId, updateData);
      
      // Refresh cameras list
      await get().fetchCameras();
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to update camera',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteCamera: async (cameraId: number) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.deleteCamera(cameraId);
      
      // Remove from local state
      const { cameras } = get();
      set({ 
        cameras: cameras.filter(camera => camera.id !== cameraId),
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to delete camera',
        isLoading: false,
      });
      throw error;
    }
  },

  discoverCameras: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiService.discoverCameras();
      set({ 
        discoveredCameras: response.cameras || [],
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to discover cameras',
        isLoading: false,
      });
    }
  },

  fetchTripwires: async (cameraId: number) => {
    try {
      set({ isLoading: true, error: null });
      const tripwires = await apiService.getCameraTripwires(cameraId);
      set({ tripwires, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch tripwires',
        isLoading: false,
      });
    }
  },

  createTripwire: async (cameraId: number, tripwireData: any) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.createTripwire(cameraId, tripwireData);
      
      // Refresh tripwires
      await get().fetchTripwires(cameraId);
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to create tripwire',
        isLoading: false,
      });
      throw error;
    }
  },

  updateTripwire: async (tripwireId: number, updateData: any) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.updateTripwire(tripwireId, updateData);
      
      // Refresh tripwires for the selected camera
      const { selectedCamera } = get();
      if (selectedCamera) {
        await get().fetchTripwires(selectedCamera.id);
      }
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to update tripwire',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteTripwire: async (tripwireId: number) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.deleteTripwire(tripwireId);
      
      // Remove from local state
      const { tripwires } = get();
      set({ 
        tripwires: tripwires.filter(tripwire => tripwire.id !== tripwireId),
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to delete tripwire',
        isLoading: false,
      });
      throw error;
    }
  },

  autoDetectCameras: async () => {
    try {
      set({ isLoading: true, error: null });
      await apiService.autoDetectCameras();
      // Refresh camera list after auto-detection
      await get().fetchCameras();
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to auto-detect cameras',
        isLoading: false,
      });
      throw error;
    }
  },

  getDetectedCameras: async () => {
    try {
      set({ isLoading: true, error: null });
      const result = await apiService.getDetectedCameras();
      set({ isLoading: false });
      return result;
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to get detected cameras',
        isLoading: false,
      });
      throw error;
    }
  },

  updateCameraSettings: async (cameraId: number, settings: any) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.updateCameraSettings(cameraId, settings);
      
      // Refresh camera list to get updated settings
      await get().fetchCameras();
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to update camera settings',
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedCamera: (camera: Camera | null) => set({ selectedCamera: camera }),
  clearError: () => set({ error: null }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
}));