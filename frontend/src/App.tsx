import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { UserRole } from './types';
import { LoginPage } from './pages/login/LoginPage';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { SuperAdminDashboard } from './pages/super-admin/SuperAdminDashboard';
import { UserManagement } from './pages/super-admin/UserManagement';
import CameraDetectionManagement from './pages/super-admin/CameraDetectionManagement';
import { EmployeeManagement } from './pages/admin/EmployeeManagement';
import { AttendanceDashboard } from './pages/admin/AttendanceDashboard';
import { CameraManagement } from './pages/admin/CameraManagement';
import { LiveMonitor } from './pages/admin/LiveMonitor';
import { EmployeeDashboard } from './pages/employee/EmployeeDashboard';

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { isAuthenticated, user, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole) {
    const roleHierarchy = {
      [UserRole.EMPLOYEE]: 1,
      [UserRole.ADMIN]: 2,
      [UserRole.SUPER_ADMIN]: 3,
    };

    if (roleHierarchy[user.role] < roleHierarchy[requiredRole]) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};



const Unauthorized: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="max-w-md w-full text-center">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
      <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
      <button
        onClick={() => window.history.back()}
        className="text-primary-600 hover:text-primary-500"
      >
        Go back
      </button>
    </div>
  </div>
);

function App() {
  const { loadUser, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Load user on app initialization
    loadUser();
  }, [loadUser]);

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Protected routes with dashboard layout */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            {/* Default redirect based on user role */}
            <Route
              index
              element={
                <Navigate
                  to={
                    isAuthenticated
                      ? useAuthStore.getState().user?.role === UserRole.SUPER_ADMIN
                        ? '/super-admin'
                        : useAuthStore.getState().user?.role === UserRole.ADMIN
                        ? '/admin'
                        : '/employee'
                      : '/login'
                  }
                  replace
                />
              }
            />

            {/* Super Admin routes */}
            <Route
              path="/super-admin"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <SuperAdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/super-admin/users"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <UserManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/super-admin/employees"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <EmployeeManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/super-admin/attendance"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <AttendanceDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/super-admin/cameras"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <CameraManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/super-admin/camera-detection"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <CameraDetectionManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/super-admin/monitor"
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <LiveMonitor />
                </ProtectedRoute>
              }
            />

            {/* Admin routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRole={UserRole.ADMIN}>
                  <AttendanceDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/employees"
              element={
                <ProtectedRoute requiredRole={UserRole.ADMIN}>
                  <EmployeeManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/attendance"
              element={
                <ProtectedRoute requiredRole={UserRole.ADMIN}>
                  <AttendanceDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/monitor"
              element={
                <ProtectedRoute requiredRole={UserRole.ADMIN}>
                  <LiveMonitor />
                </ProtectedRoute>
              }
            />

            {/* Employee routes */}
            <Route
              path="/employee"
              element={
                <ProtectedRoute requiredRole={UserRole.EMPLOYEE}>
                  <EmployeeDashboard />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
