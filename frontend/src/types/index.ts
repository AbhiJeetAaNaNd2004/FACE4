// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  role: UserRole;
  employee_id?: string;
  is_active: boolean;
}

export enum UserRole {
  EMPLOYEE = 'employee',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin'
}

// Employee types
export interface Employee {
  employee_id: string;
  name: string;
  department: string;
  role: string;
  date_joined: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  employee_id: string;
  name: string;
  department: string;
  role: string;
  date_joined: string;
  email?: string;
  phone?: string;
}

export interface EmployeeEnrollmentRequest {
  employee: EmployeeCreate;
  image_data: string;
}

// Attendance types
export interface AttendanceLog {
  id: number;
  employee_id: string;
  status: AttendanceStatus;
  timestamp: string;
  confidence_score?: number;
  notes?: string;
  created_at: string;
}

export enum AttendanceStatus {
  PRESENT = 'present',
  ABSENT = 'absent'
}

export interface AttendanceResponse {
  employee_id: string;
  employee_name: string;
  attendance_logs: AttendanceLog[];
}

export interface PresentEmployeesResponse {
  present_employees: Employee[];
  total_count: number;
}

// Camera types
export interface Camera {
  id: number;
  name: string;
  location: string;
  location_description?: string;
  stream_url: string;
  resolution_width?: number;
  resolution_height?: number;
  fps?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CameraCreate {
  name: string;
  location: string;
  stream_url: string;
  is_active?: boolean;
}

export interface Tripwire {
  id: number;
  camera_id: number;
  name: string;
  position: number;
  spacing: number;
  direction: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// System types
export interface SystemStatus {
  is_running: boolean;
  uptime: number;
  cam_count: number;
  faces_detected: number;
  attendance_count: number;
  load?: number;
}

// API Response types
export interface MessageResponse {
  message: string;
  success: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

// Dashboard types
export interface DashboardStats {
  totalEmployees: number;
  presentEmployees: number;
  totalCameras: number;
  activeCameras: number;
  systemStatus: 'running' | 'stopped';
  todayAttendance: number;
}

// UI Component types
export interface SidebarItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  current?: boolean;
  children?: SidebarItem[];
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  header: string;
  render?: (value: any, item: T) => React.ReactNode;
  sortable?: boolean;
}