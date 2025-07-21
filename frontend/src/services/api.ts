import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  LoginRequest, 
  Token, 
  User, 
  Employee, 
  EmployeeCreate, 
  EmployeeEnrollmentRequest,
  AttendanceResponse,
  PresentEmployeesResponse,
  Camera,
  CameraCreate,
  Tripwire,
  SystemStatus,
  MessageResponse,
  ApiResponse
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<Token> {
    const response = await this.api.post<Token>('/auth/login/json', credentials);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me');
    return response.data;
  }

  async logout(): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/auth/logout');
    return response.data;
  }

  async getUsers(): Promise<User[]> {
    const response = await this.api.get<User[]>('/auth/users');
    return response.data;
  }

  async createUser(userData: any): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/auth/users/create', userData);
    return response.data;
  }

  async deleteUser(userId: number): Promise<MessageResponse> {
    const response = await this.api.delete<MessageResponse>(`/auth/users/${userId}`);
    return response.data;
  }

  async updateUserRole(userId: number, role: string): Promise<MessageResponse> {
    const response = await this.api.patch<MessageResponse>(`/auth/users/${userId}/role`, { role });
    return response.data;
  }

  // Employee endpoints
  async getEmployees(): Promise<Employee[]> {
    const response = await this.api.get<Employee[]>('/employees/');
    return response.data;
  }

  async getEmployee(employeeId: string): Promise<Employee> {
    const response = await this.api.get<Employee>(`/employees/${employeeId}`);
    return response.data;
  }

  async enrollEmployee(enrollmentData: EmployeeEnrollmentRequest): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/employees/enroll', enrollmentData);
    return response.data;
  }

  async updateEmployee(employeeId: string, updateData: Partial<EmployeeCreate>): Promise<MessageResponse> {
    const response = await this.api.put<MessageResponse>(`/employees/${employeeId}`, updateData);
    return response.data;
  }

  async deleteEmployee(employeeId: string): Promise<MessageResponse> {
    const response = await this.api.delete<MessageResponse>(`/employees/${employeeId}`);
    return response.data;
  }

  async getPresentEmployees(): Promise<PresentEmployeesResponse> {
    const response = await this.api.get<PresentEmployeesResponse>('/employees/present/current');
    return response.data;
  }

  // Attendance endpoints
  async getMyAttendance(): Promise<AttendanceResponse> {
    const response = await this.api.get<AttendanceResponse>('/attendance/me');
    return response.data;
  }

  async getAllAttendance(): Promise<AttendanceResponse[]> {
    const response = await this.api.get<AttendanceResponse[]>('/attendance/all');
    return response.data;
  }

  async getEmployeeAttendance(employeeId: string): Promise<AttendanceResponse> {
    const response = await this.api.get<AttendanceResponse>(`/attendance/${employeeId}`);
    return response.data;
  }

  // Camera endpoints
  async getCameras(): Promise<Camera[]> {
    const response = await this.api.get<{ cameras: Camera[] }>('/cameras/');
    return response.data.cameras;
  }

  async getCamera(cameraId: number): Promise<Camera> {
    const response = await this.api.get<Camera>(`/cameras/${cameraId}`);
    return response.data;
  }

  async createCamera(cameraData: CameraCreate): Promise<Camera> {
    const response = await this.api.post<Camera>('/cameras/', cameraData);
    return response.data;
  }

  async updateCamera(cameraId: number, updateData: Partial<CameraCreate>): Promise<Camera> {
    const response = await this.api.put<Camera>(`/cameras/${cameraId}`, updateData);
    return response.data;
  }

  async deleteCamera(cameraId: number): Promise<MessageResponse> {
    const response = await this.api.delete<MessageResponse>(`/cameras/${cameraId}`);
    return response.data;
  }

  async discoverCameras(): Promise<any> {
    const response = await this.api.post('/cameras/discover');
    return response.data;
  }

  async getCameraTripwires(cameraId: number): Promise<Tripwire[]> {
    const response = await this.api.get<Tripwire[]>(`/cameras/${cameraId}/tripwires`);
    return response.data;
  }

  async createTripwire(cameraId: number, tripwireData: any): Promise<Tripwire> {
    const response = await this.api.post<Tripwire>(`/cameras/${cameraId}/tripwires`, tripwireData);
    return response.data;
  }

  async updateTripwire(tripwireId: number, updateData: any): Promise<Tripwire> {
    const response = await this.api.put<Tripwire>(`/cameras/tripwires/${tripwireId}`, updateData);
    return response.data;
  }

  async deleteTripwire(tripwireId: number): Promise<MessageResponse> {
    const response = await this.api.delete<MessageResponse>(`/cameras/tripwires/${tripwireId}`);
    return response.data;
  }

  async autoDetectCameras(): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/cameras/auto-detect');
    return response.data;
  }

  async getDetectedCameras(): Promise<any> {
    const response = await this.api.get<any>('/cameras/detected');
    return response.data;
  }

  async updateCameraSettings(cameraId: number, settings: any): Promise<MessageResponse> {
    const response = await this.api.put<MessageResponse>(`/cameras/${cameraId}/settings`, settings);
    return response.data;
  }

  async getSupportedResolutions(cameraId: number): Promise<any> {
    const response = await this.api.get<any>(`/cameras/${cameraId}/resolutions`);
    return response.data;
  }

  // Camera Detection and Configuration
  async detectAllCameras(): Promise<any> {
    const response = await this.api.post<any>('/cameras/detect-all');
    return response.data;
  }

  async configureCameraForFts(configData: any): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/cameras/configure-for-fts', configData);
    return response.data;
  }

  async removeCameraFromFts(databaseCameraId: number): Promise<MessageResponse> {
    const response = await this.api.delete<MessageResponse>(`/cameras/fts-configuration/${databaseCameraId}`);
    return response.data;
  }

  async getFtsConfiguredCameras(): Promise<any> {
    const response = await this.api.get<any>('/cameras/fts-configured');
    return response.data;
  }

  // System endpoints
  async startFaceDetection(): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/system/start');
    return response.data;
  }

  async stopFaceDetection(): Promise<MessageResponse> {
    const response = await this.api.post<MessageResponse>('/system/stop');
    return response.data;
  }

  async getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
    const response = await this.api.get<ApiResponse<SystemStatus>>('/system/status');
    return response.data;
  }

  async getSystemLogs(limit?: number): Promise<string[]> {
    const response = await this.api.get<string[]>('/system/logs', {
      params: limit ? { limit } : undefined
    });
    return response.data;
  }

  getCameraFeedUrl(cameraId: number): string {
    return `${API_BASE_URL}/system/camera-feed/${cameraId}`;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;