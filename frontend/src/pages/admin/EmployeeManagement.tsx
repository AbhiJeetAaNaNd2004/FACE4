import React, { useEffect, useState } from 'react';
import { useEmployeeStore } from '../../store/employeeStore';
import { Employee, EmployeeCreate } from '../../types';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { FileUpload } from '../../components/ui/FileUpload';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';

interface EnrollFormData extends EmployeeCreate {
  image_data: string;
}

export const EmployeeManagement: React.FC = () => {
  const {
    employees,
    presentEmployees,
    isLoading,
    error,
    fetchEmployees,
    fetchPresentEmployees,
    enrollEmployee,
    updateEmployee,
    deleteEmployee,
    clearError
  } = useEmployeeStore();

  const [isEnrollModalOpen, setIsEnrollModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [enrollFormData, setEnrollFormData] = useState<EnrollFormData>({
    employee_id: '',
    name: '',
    department: '',
    role: '',
    date_joined: new Date().toISOString().split('T')[0],
    email: '',
    phone: '',
    image_data: ''
  });
  const [editFormData, setEditFormData] = useState<Partial<EmployeeCreate>>({});
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchEmployees();
    fetchPresentEmployees();
  }, [fetchEmployees, fetchPresentEmployees]);

  const validateEnrollForm = () => {
    const errors: Record<string, string> = {};

    if (!enrollFormData.employee_id.trim()) {
      errors.employee_id = 'Employee ID is required';
    }

    if (!enrollFormData.name.trim()) {
      errors.name = 'Name is required';
    }

    if (!enrollFormData.department.trim()) {
      errors.department = 'Department is required';
    }

    if (!enrollFormData.role.trim()) {
      errors.role = 'Role is required';
    }

    if (!enrollFormData.date_joined) {
      errors.date_joined = 'Date joined is required';
    }

    if (!enrollFormData.image_data) {
      errors.image_data = 'Face image is required for enrollment';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleEnrollEmployee = async () => {
    if (!validateEnrollForm()) return;

    try {
      const { image_data, ...employeeData } = enrollFormData;
      await enrollEmployee({
        employee: employeeData,
        image_data
      });
      
      setIsEnrollModalOpen(false);
      setEnrollFormData({
        employee_id: '',
        name: '',
        department: '',
        role: '',
        date_joined: new Date().toISOString().split('T')[0],
        email: '',
        phone: '',
        image_data: ''
      });
      setFormErrors({});
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleUpdateEmployee = async () => {
    if (!selectedEmployee) return;

    try {
      await updateEmployee(selectedEmployee.employee_id, editFormData);
      setIsEditModalOpen(false);
      setSelectedEmployee(null);
      setEditFormData({});
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleDeleteEmployee = async (employeeId: string) => {
    if (window.confirm('Are you sure you want to delete this employee? This action cannot be undone.')) {
      try {
        await deleteEmployee(employeeId);
      } catch (error) {
        // Error is handled by store
      }
    }
  };

  const openEditModal = (employee: Employee) => {
    setSelectedEmployee(employee);
    setEditFormData({
      name: employee.name,
      department: employee.department,
      role: employee.role,
      email: employee.email,
      phone: employee.phone
    });
    setIsEditModalOpen(true);
  };

  const handleFileSelect = (file: File, base64: string) => {
    setEnrollFormData(prev => ({ ...prev, image_data: base64 }));
    setFormErrors(prev => ({ ...prev, image_data: '' }));
  };

  const getStatusBadge = (isActive: boolean) => (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
      isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    }`}>
      {isActive ? 'Active' : 'Inactive'}
    </span>
  );

  const columns = [
    {
      key: 'employee_id',
      header: 'Employee ID',
      sortable: true,
    },
    {
      key: 'name',
      header: 'Name',
      sortable: true,
    },
    {
      key: 'department',
      header: 'Department',
      sortable: true,
    },
    {
      key: 'role',
      header: 'Role',
      sortable: true,
    },
    {
      key: 'email',
      header: 'Email',
      render: (value: string | null) => value || 'N/A',
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (value: boolean) => getStatusBadge(value),
    },
    {
      key: 'date_joined',
      header: 'Date Joined',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (_: any, employee: Employee) => (
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => openEditModal(employee)}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => handleDeleteEmployee(employee.employee_id)}
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
          <h1 className="text-2xl font-bold text-gray-900">Employee Management</h1>
          <p className="text-gray-600">Manage employees and their enrollment</p>
        </div>
        <Button onClick={() => setIsEnrollModalOpen(true)}>
          Enroll Employee
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Total Employees</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {employees.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Active Employees</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {employees.filter(emp => emp.is_active).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Present Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {presentEmployees.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Departments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {new Set(employees.map(emp => emp.department)).size}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Employees Table */}
      <DataTable
        data={employees}
        columns={columns}
        title="Employees"
        loading={isLoading}
        emptyMessage="No employees found"
      />

      {/* Enroll Employee Modal */}
      <Modal
        isOpen={isEnrollModalOpen}
        onClose={() => setIsEnrollModalOpen(false)}
        title="Enroll New Employee"
        size="lg"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsEnrollModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEnrollEmployee} loading={isLoading}>
              Enroll Employee
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Employee ID"
              value={enrollFormData.employee_id}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, employee_id: e.target.value }))}
              error={formErrors.employee_id}
              placeholder="Enter employee ID"
            />

            <Input
              label="Full Name"
              value={enrollFormData.name}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, name: e.target.value }))}
              error={formErrors.name}
              placeholder="Enter full name"
            />

            <Input
              label="Department"
              value={enrollFormData.department}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, department: e.target.value }))}
              error={formErrors.department}
              placeholder="Enter department"
            />

            <Input
              label="Role/Position"
              value={enrollFormData.role}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, role: e.target.value }))}
              error={formErrors.role}
              placeholder="Enter role/position"
            />

            <Input
              label="Email"
              type="email"
              value={enrollFormData.email}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, email: e.target.value }))}
              placeholder="Enter email address"
            />

            <Input
              label="Phone"
              value={enrollFormData.phone}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, phone: e.target.value }))}
              placeholder="Enter phone number"
            />

            <Input
              label="Date Joined"
              type="date"
              value={enrollFormData.date_joined}
              onChange={(e) => setEnrollFormData(prev => ({ ...prev, date_joined: e.target.value }))}
              error={formErrors.date_joined}
            />
          </div>

          <div className="pt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Face Image *
            </label>
            <FileUpload
              onFileSelect={handleFileSelect}
              accept="image/*"
              maxSize={5 * 1024 * 1024} // 5MB
            />
            {formErrors.image_data && (
              <p className="text-sm text-red-600 mt-1">{formErrors.image_data}</p>
            )}
          </div>
        </div>
      </Modal>

      {/* Edit Employee Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Employee"
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateEmployee} loading={isLoading}>
              Update Employee
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Full Name"
            value={editFormData.name || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="Enter full name"
          />

          <Input
            label="Department"
            value={editFormData.department || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, department: e.target.value }))}
            placeholder="Enter department"
          />

          <Input
            label="Role/Position"
            value={editFormData.role || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, role: e.target.value }))}
            placeholder="Enter role/position"
          />

          <Input
            label="Email"
            type="email"
            value={editFormData.email || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, email: e.target.value }))}
            placeholder="Enter email address"
          />

          <Input
            label="Phone"
            value={editFormData.phone || ''}
            onChange={(e) => setEditFormData(prev => ({ ...prev, phone: e.target.value }))}
            placeholder="Enter phone number"
          />
        </div>
      </Modal>
    </div>
  );
};