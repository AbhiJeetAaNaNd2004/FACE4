import { create } from 'zustand';
import { Employee, EmployeeCreate, EmployeeEnrollmentRequest, AttendanceResponse, PresentEmployeesResponse } from '../types';
import { apiService } from '../services/api';

interface EmployeeState {
  employees: Employee[];
  presentEmployees: Employee[];
  selectedEmployee: Employee | null;
  myAttendance: AttendanceResponse | null;
  allAttendance: AttendanceResponse[];
  isLoading: boolean;
  error: string | null;
}

interface EmployeeActions {
  fetchEmployees: () => Promise<void>;
  fetchPresentEmployees: () => Promise<void>;
  fetchMyAttendance: () => Promise<void>;
  fetchAllAttendance: () => Promise<void>;
  enrollEmployee: (enrollmentData: EmployeeEnrollmentRequest) => Promise<void>;
  updateEmployee: (employeeId: string, updateData: Partial<EmployeeCreate>) => Promise<void>;
  deleteEmployee: (employeeId: string) => Promise<void>;
  setSelectedEmployee: (employee: Employee | null) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useEmployeeStore = create<EmployeeState & EmployeeActions>()((set, get) => ({
  // State
  employees: [],
  presentEmployees: [],
  selectedEmployee: null,
  myAttendance: null,
  allAttendance: [],
  isLoading: false,
  error: null,

  // Actions
  fetchEmployees: async () => {
    try {
      set({ isLoading: true, error: null });
      const employees = await apiService.getEmployees();
      set({ employees, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch employees',
        isLoading: false,
      });
    }
  },

  fetchPresentEmployees: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiService.getPresentEmployees();
      set({ 
        presentEmployees: response.present_employees,
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch present employees',
        isLoading: false,
      });
    }
  },

  fetchMyAttendance: async () => {
    try {
      set({ isLoading: true, error: null });
      const attendance = await apiService.getMyAttendance();
      set({ myAttendance: attendance, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch attendance',
        isLoading: false,
      });
    }
  },

  fetchAllAttendance: async () => {
    try {
      set({ isLoading: true, error: null });
      const attendance = await apiService.getAllAttendance();
      set({ allAttendance: attendance, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch all attendance',
        isLoading: false,
      });
    }
  },

  enrollEmployee: async (enrollmentData: EmployeeEnrollmentRequest) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.enrollEmployee(enrollmentData);
      
      // Refresh employees list
      await get().fetchEmployees();
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to enroll employee',
        isLoading: false,
      });
      throw error;
    }
  },

  updateEmployee: async (employeeId: string, updateData: Partial<EmployeeCreate>) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.updateEmployee(employeeId, updateData);
      
      // Refresh employees list
      await get().fetchEmployees();
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to update employee',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteEmployee: async (employeeId: string) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.deleteEmployee(employeeId);
      
      // Remove from local state
      const { employees } = get();
      set({ 
        employees: employees.filter(emp => emp.employee_id !== employeeId),
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to delete employee',
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedEmployee: (employee: Employee | null) => set({ selectedEmployee: employee }),
  clearError: () => set({ error: null }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
}));