import { useQuery } from '@tanstack/react-query'
import { creditRiskAPI } from '../services/api'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  TrendingUp, 
  FileText, 
  Activity, 
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'

export default function Statistics() {
  const { data: statistics, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: creditRiskAPI.getStatistics,
  })

  const { data: recentWorkflows } = useQuery({
    queryKey: ['recent-workflows'],
    queryFn: () => creditRiskAPI.getRecentWorkflows(50),
  })

  const statusData = recentWorkflows ? [
    { name: 'Completed', value: recentWorkflows.filter(w => w.status === 'completed').length, color: '#22c55e' },
    { name: 'In Progress', value: recentWorkflows.filter(w => w.status === 'in_progress').length, color: '#f59e0b' },
    { name: 'Error', value: recentWorkflows.filter(w => w.status === 'error').length, color: '#ef4444' },
  ] : []

  const iterationData = recentWorkflows ? recentWorkflows.map(workflow => ({
    requestId: workflow.request_id.slice(0, 8),
    iterations: workflow.iterations,
    duration: workflow.total_duration,
  })).slice(0, 10) : []

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-lg font-medium text-gray-900">Loading statistics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Statistics & Analytics</h1>
        <p className="mt-2 text-sm text-gray-600">
          Comprehensive analytics and metrics for the credit risk assessment system.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Reports</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {statistics?.total_reports || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Workflows</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {statistics?.total_workflows || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Success Rate</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {statistics?.success_rate?.toFixed(1) || 0}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Iterations</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {statistics?.average_iterations?.toFixed(1) || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Workflow Status Distribution */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">Workflow Status Distribution</h2>
          </div>
          <div className="card-content">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Iterations vs Duration */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">Iterations vs Duration</h2>
          </div>
          <div className="card-content">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={iterationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="requestId" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Bar yAxisId="left" dataKey="iterations" fill="#3b82f6" name="Iterations" />
                  <Bar yAxisId="right" dataKey="duration" fill="#10b981" name="Duration (s)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Detailed Statistics</h2>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Workflow Performance</h3>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Completed Workflows:</span>
                  <span className="font-medium">{statistics?.completed_workflows || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Error Workflows:</span>
                  <span className="font-medium">{statistics?.error_workflows || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Average Duration:</span>
                  <span className="font-medium">{statistics?.average_duration_seconds?.toFixed(2) || 0}s</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Quality Metrics</h3>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Success Rate:</span>
                  <span className="font-medium">{statistics?.success_rate?.toFixed(1) || 0}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Avg Iterations:</span>
                  <span className="font-medium">{statistics?.average_iterations?.toFixed(1) || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Total Reports:</span>
                  <span className="font-medium">{statistics?.total_reports || 0}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">System Health</h3>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Total Workflows:</span>
                  <span className="font-medium">{statistics?.total_workflows || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Error Rate:</span>
                  <span className="font-medium">
                    {statistics?.total_workflows 
                      ? ((statistics.error_workflows / statistics.total_workflows) * 100).toFixed(1)
                      : 0}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Efficiency Score:</span>
                  <span className="font-medium">
                    {statistics?.success_rate && statistics.average_iterations
                      ? ((statistics.success_rate / 100) * (1 / Math.max(statistics.average_iterations, 1)) * 100).toFixed(1)
                      : 0}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
