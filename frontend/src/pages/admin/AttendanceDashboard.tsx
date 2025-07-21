import React, { useEffect } from 'react';
import { useEmployeeStore } from '../../store/employeeStore';
import { AttendanceStatus } from '../../types';
import { DataTable } from '../../components/ui/DataTable';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';

export const AttendanceDashboard: React.FC = () => {
  const {
    allAttendance,
    presentEmployees,
    employees,
    isLoading,
    error,
    fetchAllAttendance,
    fetchPresentEmployees,
    fetchEmployees,
    clearError
  } = useEmployeeStore();

  useEffect(() => {
    fetchAllAttendance();
    fetchPresentEmployees();
    fetchEmployees();
  }, [fetchAllAttendance, fetchPresentEmployees, fetchEmployees]);

  // Process attendance data for display
  const flattenedAttendance = allAttendance.flatMap(emp => 
    emp.attendance_logs.map(log => ({
      ...log,
      employee_name: emp.employee_name,
      employee_id: emp.employee_id
    }))
  ).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const getStatusBadge = (status: AttendanceStatus) => (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
      status === AttendanceStatus.PRESENT 
        ? 'bg-green-100 text-green-800' 
        : 'bg-red-100 text-red-800'
    }`}>
      {status.toUpperCase()}
    </span>
  );

  const getConfidenceBadge = (confidence?: number) => {
    if (!confidence) return 'N/A';
    
    const percentage = Math.round(confidence * 100);
    let colorClass = 'bg-gray-100 text-gray-800';
    
    if (percentage >= 90) colorClass = 'bg-green-100 text-green-800';
    else if (percentage >= 70) colorClass = 'bg-yellow-100 text-yellow-800';
    else colorClass = 'bg-red-100 text-red-800';
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colorClass}`}>
        {percentage}%
      </span>
    );
  };

  const attendanceColumns = [
    {
      key: 'employee_name',
      header: 'Employee',
      sortable: true,
    },
    {
      key: 'employee_id',
      header: 'Employee ID',
      sortable: true,
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: AttendanceStatus) => getStatusBadge(value),
    },
    {
      key: 'timestamp',
      header: 'Timestamp',
      sortable: true,
      render: (value: string) => new Date(value).toLocaleString(),
    },
    {
      key: 'confidence_score',
      header: 'Confidence',
      render: (value?: number) => getConfidenceBadge(value),
    },
    {
      key: 'notes',
      header: 'Notes',
      render: (value: string | null) => value || 'N/A',
    },
  ];

  const presentColumns = [
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
  ];

  // Calculate statistics
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  
  const todayAttendance = flattenedAttendance.filter(
    record => new Date(record.timestamp) >= todayStart
  );
  
  const uniqueTodayEmployees = new Set(
    todayAttendance
      .filter(record => record.status === AttendanceStatus.PRESENT)
      .map(record => record.employee_id)
  ).size;

  const averageConfidence = todayAttendance.length > 0
    ? todayAttendance
        .filter(record => record.confidence_score)
        .reduce((sum, record) => sum + (record.confidence_score || 0), 0) / 
      todayAttendance.filter(record => record.confidence_score).length
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Attendance Dashboard</h1>
        <p className="text-gray-600">Monitor and track employee attendance</p>
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
            <CardTitle className="text-lg">Currently Present</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {presentEmployees.length}
            </div>
            <p className="text-sm text-gray-600 mt-1">Active employees</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Today's Check-ins</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {uniqueTodayEmployees}
            </div>
            <p className="text-sm text-gray-600 mt-1">Unique employees</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Attendance Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {employees.length > 0 ? Math.round((presentEmployees.length / employees.length) * 100) : 0}%
            </div>
            <p className="text-sm text-gray-600 mt-1">Of total employees</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Avg. Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">
              {Math.round(averageConfidence * 100)}%
            </div>
            <p className="text-sm text-gray-600 mt-1">Recognition accuracy</p>
          </CardContent>
        </Card>
      </div>

      {/* Currently Present Employees */}
      <DataTable
        data={presentEmployees}
        columns={presentColumns}
        title="Currently Present Employees"
        loading={isLoading}
        emptyMessage="No employees currently present"
      />

      {/* All Attendance Records */}
      <DataTable
        data={flattenedAttendance}
        columns={attendanceColumns}
        title="Recent Attendance Records"
        loading={isLoading}
        emptyMessage="No attendance records found"
        searchPlaceholder="Search by employee name or ID..."
      />
    </div>
  );
};