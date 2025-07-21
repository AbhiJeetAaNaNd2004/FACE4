import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, UserRole } from '../types';
import { apiService } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: localStorage.getItem('access_token'),
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (username: string, password: string) => {
        try {
          set({ isLoading: true, error: null });
          
          const tokenResponse = await apiService.login({ username, password });
          localStorage.setItem('access_token', tokenResponse.access_token);
          
          const user = await apiService.getCurrentUser();
          
          set({
            user,
            token: tokenResponse.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
          });
          localStorage.removeItem('access_token');
          throw error;
        }
      },

      logout: async () => {
        try {
          // Call backend logout endpoint
          await apiService.logout();
        } catch (error) {
          // Continue with logout even if backend call fails
          console.warn('Backend logout failed:', error);
        } finally {
          // Always clear local state
          localStorage.removeItem('access_token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      loadUser: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        try {
          set({ isLoading: true });
          const user = await apiService.getCurrentUser();
          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          localStorage.removeItem('access_token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      clearError: () => set({ error: null }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Helper function to check user role
export const hasRole = (user: User | null, requiredRole: UserRole): boolean => {
  if (!user) return false;
  
  const roleHierarchy = {
    [UserRole.EMPLOYEE]: 1,
    [UserRole.ADMIN]: 2,
    [UserRole.SUPER_ADMIN]: 3,
  };
  
  return roleHierarchy[user.role] >= roleHierarchy[requiredRole];
};

// Helper function to get redirect path based on user role
export const getRoleRedirectPath = (role: UserRole): string => {
  switch (role) {
    case UserRole.SUPER_ADMIN:
      return '/super-admin';
    case UserRole.ADMIN:
      return '/admin';
    case UserRole.EMPLOYEE:
      return '/employee';
    default:
      return '/login';
  }
};