import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { creditRiskAPI } from '../services/api'
import { 
  BarChart3, 
  FileText, 
  Plus, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Activity,
  Trash2
} from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function Dashboard() {
  const queryClient = useQueryClient()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)

  const { data: statistics, isLoading: statsLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: creditRiskAPI.getStatistics,
  })

  const { data: recentWorkflows, isLoading: workflowsLoading } = useQuery({
    queryKey: ['recent-workflows'],
    queryFn: () => creditRiskAPI.getRecentWorkflows(5),
  })

  // Delete workflow mutation
  const deleteWorkflowMutation = useMutation({
    mutationFn: (requestId: string) => creditRiskAPI.deleteWorkflow(requestId),
    onSuccess: (data) => {
      toast.success('Workflow deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['recent-workflows'] })
      queryClient.invalidateQueries({ queryKey: ['statistics'] })
      setShowDeleteConfirm(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete workflow')
      setShowDeleteConfirm(null)
    }
  })

  const handleDeleteWorkflow = (requestId: string) => {
    deleteWorkflowMutation.mutate(requestId)
  }

  const quickActions = [
    {
      name: 'New Assessment',
      description: 'Create a new credit risk assessment',
      href: '/assessment',
      icon: Plus,
      color: 'bg-primary-500',
    },
    {
      name: 'View Reports',
      description: 'Browse all credit risk reports',
      href: '/reports',
      icon: FileText,
      color: 'bg-success-500',
    },
    {
      name: 'Statistics',
      description: 'View system analytics and metrics',
      href: '/statistics',
      icon: BarChart3,
      color: 'bg-warning-500',
    },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-success-500" />
      case 'in_progress':
        return <Clock className="h-4 w-4 text-warning-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-danger-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-50'
      case 'in_progress':
        return 'text-warning-600 bg-warning-50'
      case 'error':
        return 'text-danger-600 bg-danger-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Welcome to the Credit Risk Assessment System. Monitor workflows and access key features.
        </p>
      </div>

      {/* Statistics Cards */}
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
                  {statsLoading ? '...' : statistics?.total_reports || 0}
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
                  {statsLoading ? '...' : statistics?.total_workflows || 0}
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
                  {statsLoading ? '...' : `${statistics?.success_rate?.toFixed(1) || 0}%`}
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
                  {statsLoading ? '...' : statistics?.average_iterations?.toFixed(1) || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.href}
                className="group relative rounded-lg border border-gray-200 bg-white p-6 hover:border-primary-300 hover:shadow-md transition-all"
              >
                <div className="flex items-center">
                  <div className={`flex-shrink-0 rounded-lg p-3 ${action.color}`}>
                    <action.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900 group-hover:text-primary-600">
                      {action.name}
                    </h3>
                    <p className="text-sm text-gray-500">{action.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Workflows */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Recent Workflows</h2>
        </div>
        <div className="card-content">
          {workflowsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">Loading recent workflows...</p>
            </div>
          ) : recentWorkflows && recentWorkflows.length > 0 ? (
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Request ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Iterations
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentWorkflows.map((workflow) => (
                    <tr key={workflow.request_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <Link
                          to={`/workflow/${workflow.request_id}`}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          {workflow.request_id.slice(0, 8)}...
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(workflow.status)}
                          <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(workflow.status)}`}>
                            {workflow.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {workflow.iterations}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {workflow.total_duration.toFixed(2)}s
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(workflow.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={() => setShowDeleteConfirm(workflow.request_id)}
                          className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded-md transition-colors duration-200"
                          disabled={deleteWorkflowMutation.isPending}
                          title="Delete this workflow"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No workflows yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first credit risk assessment.
              </p>
              <div className="mt-6">
                <Link
                  to="/assessment"
                  className="btn btn-primary btn-md"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Assessment
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="flex-shrink-0">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">Delete Workflow</h3>
                <p className="text-sm text-gray-500">This action cannot be undone.</p>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-gray-700">
                Are you sure you want to delete this workflow execution? 
                This will permanently remove the workflow and its associated report.
              </p>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="btn btn-secondary btn-sm"
                disabled={deleteWorkflowMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteWorkflow(showDeleteConfirm)}
                className="btn btn-danger btn-sm"
                disabled={deleteWorkflowMutation.isPending}
              >
                {deleteWorkflowMutation.isPending ? 'Deleting...' : 'Delete Workflow'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
