import React, { useEffect } from 'react';
import { useEmployeeStore } from '../../store/employeeStore';
import { useAuthStore } from '../../store/authStore';
import { AttendanceStatus } from '../../types';
import { DataTable } from '../../components/ui/DataTable';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';

export const EmployeeDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const {
    myAttendance,
    presentEmployees,
    isLoading,
    error,
    fetchMyAttendance,
    fetchPresentEmployees,
    clearError
  } = useEmployeeStore();

  useEffect(() => {
    fetchMyAttendance();
    fetchPresentEmployees();
  }, [fetchMyAttendance, fetchPresentEmployees]);

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

  // Calculate attendance statistics
  const attendanceLogs = myAttendance?.attendance_logs || [];
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  
  const todayLogs = attendanceLogs.filter(
    log => new Date(log.timestamp) >= todayStart
  );

  const thisWeekStart = new Date();
  thisWeekStart.setDate(thisWeekStart.getDate() - thisWeekStart.getDay());
  thisWeekStart.setHours(0, 0, 0, 0);
  
  const thisWeekLogs = attendanceLogs.filter(
    log => new Date(log.timestamp) >= thisWeekStart
  );

  const isCurrentlyPresent = todayLogs.length > 0 && 
    todayLogs[todayLogs.length - 1].status === AttendanceStatus.PRESENT;

  const lastCheckIn = attendanceLogs.find(log => log.status === AttendanceStatus.PRESENT);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Dashboard</h1>
        <p className="text-gray-600">Welcome back, {user?.username}!</p>
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

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Current Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              isCurrentlyPresent ? 'text-green-600' : 'text-red-600'
            }`}>
              {isCurrentlyPresent ? 'Present' : 'Not Present'}
            </div>
            <p className="text-sm text-gray-600 mt-1">Today's status</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Today's Check-ins</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {todayLogs.filter(log => log.status === AttendanceStatus.PRESENT).length}
            </div>
            <p className="text-sm text-gray-600 mt-1">Face recognitions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">This Week</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {new Set(
                thisWeekLogs
                  .filter(log => log.status === AttendanceStatus.PRESENT)
                  .map(log => new Date(log.timestamp).toDateString())
              ).size}
            </div>
            <p className="text-sm text-gray-600 mt-1">Days present</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Last Check-in</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-orange-600">
              {lastCheckIn 
                ? new Date(lastCheckIn.timestamp).toLocaleDateString()
                : 'Never'
              }
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {lastCheckIn 
                ? new Date(lastCheckIn.timestamp).toLocaleTimeString()
                : 'No records'
              }
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Info */}
      {myAttendance && (
        <Card>
          <CardHeader>
            <CardTitle>Employee Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Employee ID</label>
                <p className="text-lg font-semibold">{myAttendance.employee_id}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Name</label>
                <p className="text-lg font-semibold">{myAttendance.employee_name}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* My Attendance History */}
      <DataTable
        data={attendanceLogs}
        columns={attendanceColumns}
        title="My Attendance History"
        loading={isLoading}
        emptyMessage="No attendance records found"
        searchPlaceholder="Search attendance records..."
      />

      {/* Currently Present Colleagues */}
      <DataTable
        data={presentEmployees}
        columns={presentColumns}
        title="Currently Present Colleagues"
        loading={isLoading}
        emptyMessage="No colleagues currently present"
        searchPlaceholder="Search colleagues..."
      />
    </div>
  );
};