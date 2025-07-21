import React, { useEffect, useState } from 'react';
import { useUserStore } from '../../store/userStore';
import { UserRole } from '../../types';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/Card';

interface CreateUserFormData {
  username: string;
  password: string;
  role: UserRole;
  employee_id: string;
}

export const UserManagement: React.FC = () => {
  const {
    users,
    isLoading,
    error,
    fetchUsers,
    createUser,
    updateUserRole,
    deleteUser,
    clearError
  } = useUserStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [newRole, setNewRole] = useState<UserRole>(UserRole.EMPLOYEE);
  const [createFormData, setCreateFormData] = useState<CreateUserFormData>({
    username: '',
    password: '',
    role: UserRole.EMPLOYEE,
    employee_id: ''
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const validateCreateForm = () => {
    const errors: Record<string, string> = {};

    if (!createFormData.username.trim()) {
      errors.username = 'Username is required';
    } else if (createFormData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }

    if (!createFormData.password) {
      errors.password = 'Password is required';
    } else if (createFormData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateUser = async () => {
    if (!validateCreateForm()) return;

    try {
      await createUser({
        username: createFormData.username,
        password: createFormData.password,
        role: createFormData.role,
        employee_id: createFormData.employee_id || undefined
      });
      
      setIsCreateModalOpen(false);
      setCreateFormData({
        username: '',
        password: '',
        role: UserRole.EMPLOYEE,
        employee_id: ''
      });
      setFormErrors({});
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleUpdateRole = async () => {
    if (!selectedUserId) return;

    try {
      await updateUserRole(selectedUserId, newRole);
      setIsEditModalOpen(false);
      setSelectedUserId(null);
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      try {
        await deleteUser(userId);
      } catch (error) {
        // Error is handled by store
      }
    }
  };

  const openEditModal = (userId: number, currentRole: UserRole) => {
    setSelectedUserId(userId);
    setNewRole(currentRole);
    setIsEditModalOpen(true);
  };

  const getRoleBadgeColor = (role: UserRole) => {
    switch (role) {
      case UserRole.SUPER_ADMIN:
        return 'bg-red-100 text-red-800';
      case UserRole.ADMIN:
        return 'bg-blue-100 text-blue-800';
      case UserRole.EMPLOYEE:
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const columns = [
    {
      key: 'username',
      header: 'Username',
      sortable: true,
    },
    {
      key: 'role',
      header: 'Role',
      sortable: true,
      render: (value: UserRole) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(value)}`}>
          {value.replace('_', ' ').toUpperCase()}
        </span>
      ),
    },
    {
      key: 'employee_id',
      header: 'Employee ID',
      render: (value: string | null) => value || 'N/A',
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (value: boolean) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {value ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'last_login',
      header: 'Last Login',
      render: (value: string | null) => {
        if (!value) return 'Never';
        return new Date(value).toLocaleDateString();
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (_: any, user: any) => (
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => openEditModal(user.id, user.role)}
          >
            Edit Role
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => handleDeleteUser(user.id)}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage system users and their roles</p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          Create User
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center justify-between">
            <p className="text-sm">{error}</p>
            <button onClick={clearError} className="text-red-500 hover:text-red-700">
              ×
            </button>
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {users.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {users.filter(user => user.is_active).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Admins</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {users.filter(user => user.role === UserRole.ADMIN || user.role === UserRole.SUPER_ADMIN).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <DataTable
        data={users}
        columns={columns}
        title="System Users"
        loading={isLoading}
        emptyMessage="No users found"
      />

      {/* Create User Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New User"
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateUser} loading={isLoading}>
              Create User
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Username"
            value={createFormData.username}
            onChange={(e) => setCreateFormData(prev => ({ ...prev, username: e.target.value }))}
            error={formErrors.username}
            placeholder="Enter username"
          />

          <Input
            label="Password"
            type="password"
            value={createFormData.password}
            onChange={(e) => setCreateFormData(prev => ({ ...prev, password: e.target.value }))}
            error={formErrors.password}
            placeholder="Enter password"
          />

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">Role</label>
            <select
              value={createFormData.role}
              onChange={(e) => setCreateFormData(prev => ({ ...prev, role: e.target.value as UserRole }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={UserRole.EMPLOYEE}>Employee</option>
              <option value={UserRole.ADMIN}>Admin</option>
              <option value={UserRole.SUPER_ADMIN}>Super Admin</option>
            </select>
          </div>

          <Input
            label="Employee ID (Optional)"
            value={createFormData.employee_id}
            onChange={(e) => setCreateFormData(prev => ({ ...prev, employee_id: e.target.value }))}
            placeholder="Link to employee record"
          />
        </div>
      </Modal>

      {/* Edit Role Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Update User Role"
        size="sm"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateRole} loading={isLoading}>
              Update Role
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">New Role</label>
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value as UserRole)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={UserRole.EMPLOYEE}>Employee</option>
              <option value={UserRole.ADMIN}>Admin</option>
              <option value={UserRole.SUPER_ADMIN}>Super Admin</option>
            </select>
          </div>
        </div>
      </Modal>
    </div>
  );
};