import { create } from 'zustand';
import { User, UserRole } from '../types';
import { apiService } from '../services/api';

interface UserCreateData {
  username: string;
  password: string;
  role: UserRole;
  employee_id?: string;
}

interface UserState {
  users: User[];
  selectedUser: User | null;
  isLoading: boolean;
  error: string | null;
}

interface UserActions {
  fetchUsers: () => Promise<void>;
  createUser: (userData: UserCreateData) => Promise<void>;
  updateUserRole: (userId: number, role: UserRole) => Promise<void>;
  deleteUser: (userId: number) => Promise<void>;
  setSelectedUser: (user: User | null) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useUserStore = create<UserState & UserActions>()((set, get) => ({
  // State
  users: [],
  selectedUser: null,
  isLoading: false,
  error: null,

  // Actions
  fetchUsers: async () => {
    try {
      set({ isLoading: true, error: null });
      const users = await apiService.getUsers();
      set({ users, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to fetch users',
        isLoading: false,
      });
    }
  },

  createUser: async (userData: UserCreateData) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.createUser(userData);
      
      // Refresh users list
      await get().fetchUsers();
      
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to create user',
        isLoading: false,
      });
      throw error;
    }
  },

  updateUserRole: async (userId: number, role: UserRole) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.updateUserRole(userId, role);
      
      // Update local state
      const { users } = get();
      const updatedUsers = users.map(user => 
        user.id === userId ? { ...user, role } : user
      );
      
      set({ users: updatedUsers, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to update user role',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteUser: async (userId: number) => {
    try {
      set({ isLoading: true, error: null });
      await apiService.deleteUser(userId);
      
      // Remove from local state
      const { users } = get();
      set({ 
        users: users.filter(user => user.id !== userId),
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Failed to delete user',
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedUser: (user: User | null) => set({ selectedUser: user }),
  clearError: () => set({ error: null }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
}));