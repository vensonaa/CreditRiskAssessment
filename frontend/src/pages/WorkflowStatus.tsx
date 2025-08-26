import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { creditRiskAPI } from '../services/api'
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Activity,
  FileText,
  RefreshCw,
  Eye,
  Trash2
} from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function WorkflowStatus() {
  const { requestId } = useParams<{ requestId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [pollingStartTime] = useState(Date.now())
  const [manualStop, setManualStop] = useState(false)
  const [shouldStopPolling, setShouldStopPolling] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const { data: workflow, isLoading, error } = useQuery({
    queryKey: ['workflow', requestId],
    queryFn: () => creditRiskAPI.getWorkflowStatus(requestId!),
    refetchInterval: (query) => {
      // Stop if manually stopped or should stop polling
      if (manualStop || shouldStopPolling) {
        console.log('Stopping polling - manually stopped or should stop')
        return false
      }
      
      const data = query.state.data
      
      // Debug logging
      console.log('Workflow status check:', data?.status, 'Elapsed time:', ((Date.now() - pollingStartTime) / 1000).toFixed(1) + 's')
      
      // Stop polling if workflow is in a final state
      const finalStatuses = [
        'completed', 
        'completed_with_fallback', 
        'max_iterations_reached', 
        'workflow_error', 
        'generator_error', 
        'reflection_error', 
        'refiner_error'
      ]
      
      if (data?.status && finalStatuses.includes(data.status)) {
        console.log('Stopping polling - workflow in final state:', data.status)
        setShouldStopPolling(true)
        return false
      }
      
      // Stop polling if workflow has been running for more than 10 minutes
      if (data?.created_at) {
        const workflowStartTime = new Date(data.created_at).getTime()
        const workflowElapsedTime = (Date.now() - workflowStartTime) / 1000
        if (workflowElapsedTime > 600) { // 10 minutes
          console.warn('Stopping polling - workflow running for more than 10 minutes')
          setShouldStopPolling(true)
          return false
        }
      }
      
      // Stop polling after 5 minutes (300 seconds) to prevent infinite polling
      const elapsedTime = (Date.now() - pollingStartTime) / 1000
      if (elapsedTime > 300) {
        console.warn('Stopping workflow polling after 5 minutes')
        setShouldStopPolling(true)
        return false
      }
      
      return 2000 // Poll every 2 seconds for active workflows
    },
    retry: 3, // Limit retries
    retryDelay: 1000, // Wait 1 second between retries
    enabled: !shouldStopPolling, // Disable query when should stop polling
    refetchOnWindowFocus: false, // Prevent refetch on window focus
    refetchOnMount: false, // Prevent refetch on mount if already fetched
    staleTime: 0, // Always consider data stale
  })

  // Decide which report id to fetch: prefer final_report_id; fallback to request_id when completed
  const reportIdToFetch = workflow?.final_report_id || (workflow?.status === 'completed' ? workflow?.request_id : undefined)

  // Fetch the actual credit risk report as soon as we have a report id
  const { data: creditReport, isLoading: reportLoading, error: reportError } = useQuery({
    queryKey: ['credit-report', reportIdToFetch],
    queryFn: () => creditRiskAPI.getReport(reportIdToFetch!),
    enabled: !!reportIdToFetch,
  })

  // Debug logging for credit report query
  useEffect(() => {
    if (workflow) {
      console.log('Credit report query debug:', {
        workflowStatus: workflow.status,
        finalReportId: workflow.final_report_id,
        reportIdToFetch: reportIdToFetch,
        queryEnabled: !!reportIdToFetch,
        creditReport: creditReport,
        reportLoading: reportLoading,
        reportError: reportError
      })
    }
  }, [workflow, creditReport, reportLoading, reportError])

  // Delete report mutation
  const deleteReportMutation = useMutation({
    mutationFn: (reportId: string) => creditRiskAPI.deleteReport(reportId),
    onSuccess: (data) => {
      toast.success('Report deleted successfully')
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries({ queryKey: ['workflow', requestId] })
      queryClient.invalidateQueries({ queryKey: ['credit-report', workflow?.final_report_id] })
      queryClient.invalidateQueries({ queryKey: ['statistics'] })
      // Navigate back to the main page
      navigate('/')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete report')
    }
  })

  const handleDeleteReport = () => {
    if (workflow?.final_report_id) {
      deleteReportMutation.mutate(workflow.final_report_id)
    }
  }

  // Effect to stop polling when workflow reaches final state
  useEffect(() => {
    if (workflow?.status) {
      const finalStatuses = [
        'completed', 
        'completed_with_fallback', 
        'max_iterations_reached', 
        'workflow_error', 
        'generator_error', 
        'reflection_error', 
        'refiner_error'
      ]
      
      if (finalStatuses.includes(workflow.status)) {
        console.log('Workflow reached final state, stopping polling:', workflow.status)
        setShouldStopPolling(true)
        // Force stop the query immediately
        return
      }
    }
  }, [workflow?.status])

  // Effect to stop polling after 5 minutes
  useEffect(() => {
    const timer = setTimeout(() => {
      console.log('Stopping polling after 5 minutes timeout')
      setShouldStopPolling(true)
    }, 300000) // 5 minutes

    return () => clearTimeout(timer)
  }, [])

  // Effect to immediately stop polling if workflow is already completed
  useEffect(() => {
    if (workflow?.status === 'completed') {
      console.log('Workflow already completed, stopping polling immediately')
      setShouldStopPolling(true)
    }
  }, [workflow?.status])

  // Debug effect for delete button
  useEffect(() => {
    if (workflow) {
      console.log('Workflow debug:', {
        status: workflow.status,
        final_report_id: workflow.final_report_id,
        shouldShowDelete: workflow.status === 'completed' && workflow.final_report_id
      })
    }
  }, [workflow])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-500" />
      case 'in_progress':
        return <Clock className="h-5 w-5 text-warning-500" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-danger-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-50 border-success-200'
      case 'in_progress':
        return 'text-warning-600 bg-warning-50 border-warning-200'
      case 'error':
        return 'text-danger-600 bg-danger-50 border-danger-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getAgentIcon = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'generator':
        return <FileText className="h-4 w-4" />
      case 'reflection':
        return <Eye className="h-4 w-4" />
      case 'refiner':
        return <RefreshCw className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const getAgentColor = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'generator':
        return 'bg-primary-100 text-primary-800 border-primary-200'
      case 'reflection':
        return 'bg-warning-100 text-warning-800 border-warning-200'
      case 'refiner':
        return 'bg-success-100 text-success-800 border-success-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-lg font-medium text-gray-900">Loading workflow status...</p>
          <p className="mt-2 text-sm text-gray-500">Retrieving workflow information</p>
        </div>
      </div>
    )
  }

  if (error || !workflow) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <AlertCircle className="mx-auto h-12 w-12 text-danger-500" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">Workflow not found</h3>
          <p className="mt-2 text-sm text-gray-500">
            The requested workflow could not be found or an error occurred.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Workflow Status</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitoring the Generator → Reflection → Refiner workflow execution.
        </p>
      </div>

      {/* Workflow Overview */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Workflow Overview</h2>
            <div className="flex items-center space-x-2">
              {getStatusIcon(workflow.status)}
              <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full border ${getStatusColor(workflow.status)}`}>
                {workflow.status.replace('_', ' ').toUpperCase()}
              </span>
              {!manualStop && !['completed', 'completed_with_fallback', 'max_iterations_reached', 'workflow_error', 'generator_error', 'reflection_error', 'refiner_error'].includes(workflow.status) && (
                <button
                  onClick={() => setManualStop(true)}
                  className="btn btn-secondary btn-sm"
                >
                  Stop Polling
                </button>
              )}
            </div>
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm font-medium text-gray-500">Request ID</p>
              <p className="text-sm text-gray-900 font-mono">{workflow.request_id}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Iterations</p>
              <p className="text-sm text-gray-900">{workflow.iterations}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Duration</p>
              <p className="text-sm text-gray-900">{workflow.total_duration.toFixed(2)}s</p>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-gray-500">Created</p>
              <p className="text-sm text-gray-900">
                {new Date(workflow.created_at).toLocaleString()}
              </p>
            </div>
            {workflow.completed_at && (
              <div>
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-sm text-gray-900">
                  {new Date(workflow.completed_at).toLocaleString()}
                </p>
              </div>
            )}
          </div>
          
          {/* Delete Report Button - Always visible when conditions are met */}
          {workflow.status === 'completed' && workflow.final_report_id && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Report Management</h3>
                  <p className="text-sm text-gray-500">Manage the completed credit risk assessment report</p>
                </div>
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="btn btn-danger btn-sm flex items-center space-x-2"
                  disabled={deleteReportMutation.isPending}
                >
                  <Trash2 className="h-4 w-4" />
                  <span>{deleteReportMutation.isPending ? 'Deleting...' : 'Delete Report'}</span>
                </button>
              </div>
            </div>
          )}
          
          {/* Debug info removed for cleaner UI */}
        </div>
      </div>

      {/* Debug Information card removed */}

      {/* Final Credit Risk Assessment - Always Displayed When Available */}
      {workflow.final_report_id && (
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-600" />
              <h2 className="text-lg font-semibold text-gray-900">Final Credit Risk Assessment</h2>
            </div>
            <p className="mt-1 text-sm text-gray-600">
              The completed credit risk assessment report.
            </p>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {/* Report Overview */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Report ID</p>
                    <p className="text-sm text-gray-900 font-medium">{workflow.final_report_id}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Status</p>
                    <p className="text-sm text-gray-900 font-medium">
                      {workflow.status === 'completed' ? 'Completed' : workflow.status}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Iterations</p>
                    <p className="text-sm text-gray-900 font-medium">
                      {workflow.iterations}
                    </p>
                  </div>
                </div>
              </div>

              {/* Report Details - Show when workflow is completed */}
              {workflow.status === 'completed' && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <h3 className="text-md font-semibold text-gray-900">Assessment Complete</h3>
                  </div>
                  <p className="text-sm text-gray-700 mt-2">
                    The credit risk assessment has been completed successfully. 
                    The final report is available with ID: <span className="font-mono font-medium">{workflow.final_report_id}</span>
                  </p>
                  <div className="mt-3">
                    <p className="text-sm text-gray-600">
                      <strong>Quality Score:</strong> The assessment met the quality threshold requirements.
                    </p>
                    <p className="text-sm text-gray-600">
                      <strong>Processing Time:</strong> {workflow.total_duration.toFixed(2)} seconds
                    </p>
                  </div>
                </div>
              )}

              {/* Assessment Summary - Display actual report content */}
              {workflow.status === 'completed' && creditReport && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Assessment Summary</h3>
                  
                  {/* Risk Level and Score */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      <div>
                        <p className="text-sm font-medium text-gray-500">Risk Level</p>
                        <p className="text-sm text-gray-900 font-medium">
                          {creditReport.risk_level || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Overall Score</p>
                        <p className="text-sm text-gray-900 font-medium">
                          {creditReport.overall_score ? `${(creditReport.overall_score * 100).toFixed(1)}%` : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Generated At</p>
                        <p className="text-sm text-gray-900 font-medium">
                          {new Date(creditReport.generated_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Assessment Sections */}
                  {creditReport.sections && creditReport.sections.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="text-md font-semibold text-gray-900">Assessment Details</h4>
                      {creditReport.sections.map((section, index) => (
                        <div
                          key={index}
                          className={`border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-white to-gray-50 border-l-4 ${[
                            'border-blue-500 bg-blue-50',
                            'border-green-500 bg-green-50',
                            'border-purple-500 bg-purple-50',
                            'border-amber-500 bg-amber-50',
                            'border-pink-500 bg-pink-50',
                          ][index % 5]}`}
                        >
                          <div className="flex items-center justify-between mb-3">
                            <h5 className="text-sm font-semibold text-gray-900">{section.title}</h5>
                            {section.score && (
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                                  section.score * 100 >= 80
                                    ? 'bg-green-50 text-green-700'
                                    : section.score * 100 >= 60
                                    ? 'bg-amber-50 text-amber-700'
                                    : 'bg-red-50 text-red-700'
                                }`}
                              >
                                Score {(section.score * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-800 space-y-2">
                            {String(section.content)
                              .split(/\n\n+/)
                              .map((para, i) => (
                                <p key={i}>{para}</p>
                              ))}
                          </div>
                          {/* Technical details toggle per section */}
                          <details className="mt-3">
                            <summary className="text-xs text-gray-600 cursor-pointer select-none hover:text-gray-800">
                              Show technical details
                            </summary>
                            <pre className="text-xs text-gray-700 mt-2 bg-white/70 backdrop-blur rounded border border-gray-200 p-2 overflow-auto">
{JSON.stringify(section, null, 2)}
                            </pre>
                          </details>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Recommendations */}
                  {creditReport.recommendations && creditReport.recommendations.length > 0 && (
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <h4 className="text-md font-semibold text-gray-900 mb-3">Recommendations</h4>
                      <ul className="space-y-2">
                        {creditReport.recommendations.map((recommendation, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <span className="text-yellow-600 mt-1">•</span>
                            <span className="text-sm text-gray-700">{recommendation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Loading state for report */}
              {workflow.status === 'completed' && reportLoading && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-500">Loading assessment report...</p>
                </div>
              )}

              {/* Workflow Progress Summary */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-md font-semibold text-gray-900 mb-3">Workflow Summary</h3>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Total Iterations</p>
                    <p className="text-sm text-gray-900 font-medium">
                      {workflow.iterations}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Processing Time</p>
                    <p className="text-sm text-gray-900 font-medium">
                      {workflow.total_duration.toFixed(2)}s
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Agent Responses</p>
                    <p className="text-sm text-gray-900 font-medium">
                      {workflow.agent_responses.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Final Status</p>
                    <p className="text-sm text-gray-900 font-medium">
                      {workflow.status.replace('_', ' ').toUpperCase()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Responses - Display on Demand */}
      {workflow.agent_responses && workflow.agent_responses.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Agent Responses</h2>
                <p className="mt-1 text-sm text-gray-600">
                  Click on any agent to view their detailed responses and analysis.
                </p>
              </div>
              <button
                onClick={() => setSelectedAgent(selectedAgent ? null : 'all')}
                className="btn btn-secondary btn-sm"
              >
                {selectedAgent ? 'Collapse All' : 'Expand All'}
              </button>
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {workflow.agent_responses.map((response, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedAgent === response.agent_type || selectedAgent === 'all'
                      ? 'border-primary-300 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedAgent(
                    selectedAgent === response.agent_type ? null : response.agent_type
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`flex items-center space-x-2 px-3 py-1 rounded-full border text-sm font-medium ${getAgentColor(response.agent_type)}`}>
                        {getAgentIcon(response.agent_type)}
                        <span>{response.agent_type}</span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(response.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {response.metadata?.status && (
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          response.metadata.status === 'success' 
                            ? 'text-success-600 bg-success-50' 
                            : 'text-danger-600 bg-danger-50'
                        }`}>
                          {response.metadata.status}
                        </span>
                      )}
                      <span className="text-gray-400">
                        {(selectedAgent === response.agent_type || selectedAgent === 'all') ? '▼' : '▶'}
                      </span>
                    </div>
                  </div>
                  
                  {(selectedAgent === response.agent_type || selectedAgent === 'all') && (
                    <div className="mt-4 space-y-3">
                      <div>
                        <p className="text-sm font-medium text-gray-700">Summary</p>
                        <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
                          {response.content}
                        </p>
                      </div>

                      {/* Friendly details for Reflection evaluation */}
                      {response.agent_type?.toLowerCase() === 'reflection' && response.metadata?.evaluation && (
                        <div className="bg-gray-50 border border-gray-200 rounded p-3">
                          <p className="text-sm font-medium text-gray-700 mb-2">Quality Evaluation</p>
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                            <div className="text-xs text-gray-700"><span className="font-medium">Overall:</span> {response.metadata.evaluation.overall_score?.toFixed?.(2) ?? response.metadata.evaluation.overall_score}</div>
                            <div className="text-xs text-gray-700"><span className="font-medium">Accuracy:</span> {response.metadata.evaluation.accuracy}</div>
                            <div className="text-xs text-gray-700"><span className="font-medium">Completeness:</span> {response.metadata.evaluation.completeness}</div>
                            <div className="text-xs text-gray-700"><span className="font-medium">Structure:</span> {response.metadata.evaluation.structure}</div>
                            <div className="text-xs text-gray-700"><span className="font-medium">Verbosity:</span> {response.metadata.evaluation.verbosity}</div>
                            <div className="text-xs text-gray-700"><span className="font-medium">Relevance:</span> {response.metadata.evaluation.relevance}</div>
                            <div className="text-xs text-gray-700"><span className="font-medium">Tone:</span> {response.metadata.evaluation.tone}</div>
                          </div>
                          {Array.isArray(response.metadata.evaluation.critique) && response.metadata.evaluation.critique.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-medium text-gray-700">Improvement suggestions</p>
                              <ul className="mt-1 list-disc list-inside space-y-1">
                                {response.metadata.evaluation.critique.map((item: string, idx: number) => (
                                  <li key={idx} className="text-xs text-gray-700">{item}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Minimal metadata toggle for advanced users */}
                      {response.metadata && Object.keys(response.metadata).length > 0 && (
                        <details className="mt-1">
                          <summary className="text-xs text-gray-500 cursor-pointer select-none">Show technical details</summary>
                          <pre className="text-xs text-gray-600 mt-1 bg-gray-50 p-2 rounded overflow-auto">
                            {JSON.stringify(response.metadata, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Workflow Visualization */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">Workflow Flow</h2>
        </div>
        <div className="card-content">
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                <FileText className="h-4 w-4 text-primary-600" />
              </div>
              <span className="text-sm font-medium">Generator</span>
            </div>
            <div className="text-gray-400">→</div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-warning-100 flex items-center justify-center">
                <Eye className="h-4 w-4 text-warning-600" />
              </div>
              <span className="text-sm font-medium">Reflection</span>
            </div>
            <div className="text-gray-400">→</div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center">
                <RefreshCw className="h-4 w-4 text-success-600" />
              </div>
              <span className="text-sm font-medium">Refiner</span>
            </div>
            <div className="text-gray-400">→</div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-gray-600" />
              </div>
              <span className="text-sm font-medium">Complete</span>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Current iteration: <span className="font-medium">{workflow.iterations}</span>
              {workflow.status === 'completed' && (
                <span className="ml-2 text-success-600 font-medium">
                  ✓ Quality threshold met
                </span>
              )}
            </p>
          </div>
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
                onClick={() => setShowDeleteConfirm(false)}
                className="btn btn-secondary btn-sm"
                disabled={deleteReportMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  handleDeleteReport()
                  setShowDeleteConfirm(false)
                }}
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
