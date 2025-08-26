import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { creditRiskAPI } from '../services/api'
import { FileText, Search, Calendar, User, Trash2, Eye, AlertCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { Link } from 'react-router-dom'

export default function Reports() {
  const queryClient = useQueryClient()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => creditRiskAPI.getAllReports(),
  })

  // Delete report mutation
  const deleteReportMutation = useMutation({
    mutationFn: (reportId: string) => creditRiskAPI.deleteReport(reportId),
    onSuccess: (data) => {
      toast.success('Report deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['statistics'] })
      setShowDeleteConfirm(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete report')
      setShowDeleteConfirm(null)
    }
  })

  const handleDeleteReport = (reportId: string) => {
    deleteReportMutation.mutate(reportId)
  }

  // Filter reports based on search term
  const filteredReports = reports?.filter(report => 
    report.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.business_type.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Credit Risk Reports</h1>
        <p className="mt-2 text-sm text-gray-600">
          View and manage credit risk assessment reports.
        </p>
      </div>

      {/* Search Bar */}
      <div className="card">
        <div className="card-content">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by customer name, ID, or business type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">All Reports</h2>
            <div className="text-sm text-gray-500">
              {filteredReports.length} of {reports?.length || 0} reports
            </div>
          </div>
        </div>
        <div className="card-content">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">Loading reports...</p>
            </div>
          ) : filteredReports.length > 0 ? (
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Business Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Requested Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Purpose
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
                  {filteredReports.map((report) => (
                    <tr key={report.report_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {report.customer_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {report.customer_id}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report.business_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${report.requested_amount.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          report.report_data?.risk_level === 'Low' 
                            ? 'text-green-600 bg-green-50' 
                            : report.report_data?.risk_level === 'High'
                            ? 'text-red-600 bg-red-50'
                            : 'text-yellow-600 bg-yellow-50'
                        }`}>
                          {report.report_data?.risk_level || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report.purpose}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(report.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <Link
                            to={`/workflow/${report.report_id}`}
                            className="text-red-600 hover:text-red-900 flex items-center space-x-1"
                          >
                            <Eye className="h-4 w-4" />
                            <span>View</span>
                          </Link>
                          <button
                            onClick={() => setShowDeleteConfirm(report.report_id)}
                            className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded-md transition-colors duration-200 flex items-center space-x-1"
                            disabled={deleteReportMutation.isPending}
                            title="Delete this report"
                          >
                            <Trash2 className="h-4 w-4" />
                            <span>Delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                {searchTerm ? 'No reports found' : 'No reports yet'}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm 
                  ? 'Try adjusting your search terms.'
                  : 'Create your first credit risk assessment to generate reports.'
                }
              </p>
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
                <h3 className="text-lg font-medium text-gray-900">Delete Report</h3>
                <p className="text-sm text-gray-500">This action cannot be undone.</p>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-gray-700">
                Are you sure you want to delete this credit risk assessment report? 
                This will permanently remove the report and all associated data.
              </p>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="btn btn-secondary btn-sm"
                disabled={deleteReportMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteReport(showDeleteConfirm)}
                className="btn btn-danger btn-sm"
                disabled={deleteReportMutation.isPending}
              >
                {deleteReportMutation.isPending ? 'Deleting...' : 'Delete Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
