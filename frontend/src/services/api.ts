import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export interface CreditRiskRequest {
  customer_id: string
  customer_name: string
  business_type: string
  annual_revenue: number
  credit_history_years: number
  requested_amount: number
  purpose: string
  additional_data?: Record<string, any>
}

export interface WorkflowResponse {
  request_id: string
  status: string
  final_report?: any
  iterations: number
  total_duration: number
  agent_responses: Array<{
    agent_type: string
    content: string
    metadata?: any
    timestamp: string
  }>
}

export interface WorkflowStatus {
  request_id: string
  status: string
  iterations: number
  total_duration: number
  agent_responses: Array<{
    agent_type: string
    content: string
    metadata?: any
    timestamp: string
  }>
  final_report_id?: string
  created_at: string
  completed_at?: string
}

export interface CreditRiskReport {
  report_id: string
  customer_id: string
  generated_at: string
  sections: Array<{
    title: string
    content: string
    score?: number
  }>
  overall_score?: number
  risk_level?: string
  recommendations: string[]
}

export interface ReportListItem {
  report_id: string
  customer_id: string
  customer_name: string
  business_type: string
  annual_revenue: number
  requested_amount: number
  purpose: string
  created_at: string
  report_data: any
  risk_level?: string
  overall_score?: number
}

export interface SystemStatistics {
  total_reports: number
  total_workflows: number
  completed_workflows: number
  error_workflows: number
  success_rate: number
  average_iterations: number
  average_duration_seconds: number
}

export interface SubmittedApplication {
  customer_id: string
  application_data: {
    application_id: string
    customer_id: string
    customer_name: string
    application_date: string
    loan_amount: number
    loan_purpose: string
    loan_term: number
    interest_rate: number
    collateral_type: string
    collateral_value: number
    application_status: string
    business_type: string
    annual_revenue: number
    credit_history_years: number
    requested_amount: number
    purpose: string
  }
}

export interface ApplicationStatus {
  customer_id: string
  application_status: string
  is_submitted: boolean
}

export const creditRiskAPI = {
  // Create new credit risk assessment
  createAssessment: async (data: CreditRiskRequest): Promise<WorkflowResponse> => {
    const response = await api.post('/credit-risk-assessment', data)
    return response.data
  },

  // Get workflow status
  getWorkflowStatus: async (requestId: string): Promise<WorkflowStatus> => {
    const response = await api.get(`/workflow/${requestId}`)
    return response.data
  },

  // Get credit risk report
  getReport: async (reportId: string): Promise<CreditRiskReport> => {
    const response = await api.get(`/reports/${reportId}`)
    return response.data
  },

  // Delete credit risk report
  deleteReport: async (reportId: string): Promise<{ message: string; report_id: string; deleted_at: string }> => {
    const response = await api.delete(`/reports/${reportId}`)
    return response.data
  },

  // Get customer reports
  getCustomerReports: async (customerId: string): Promise<CreditRiskReport[]> => {
    const response = await api.get(`/reports/customer/${customerId}`)
    return response.data
  },

  // Get all reports
  getAllReports: async (): Promise<ReportListItem[]> => {
    const response = await api.get('/reports')
    return response.data
  },

  // Get recent workflows
  getRecentWorkflows: async (limit: number = 10): Promise<WorkflowStatus[]> => {
    const response = await api.get(`/workflows/recent?limit=${limit}`)
    return response.data
  },

  // Get system statistics
  getStatistics: async (): Promise<SystemStatistics> => {
    const response = await api.get('/statistics')
    return response.data
  },

  // Cancel workflow
  cancelWorkflow: async (requestId: string): Promise<{ message: string }> => {
    const response = await api.post(`/workflow/${requestId}/cancel`)
    return response.data
  },

  // Delete workflow execution
  deleteWorkflow: async (requestId: string): Promise<any> => {
    const response = await api.delete(`/workflow/${requestId}`)
    return response.data
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; service: string; timestamp: string }> => {
    const response = await api.get('/health')
    return response.data
  },

  // Get submitted applications
  getSubmittedApplications: async (): Promise<SubmittedApplication[]> => {
    const response = await api.get('/submitted-applications')
    return response.data
  },

  // Get application status
  getApplicationStatus: async (customerId: string): Promise<ApplicationStatus> => {
    const response = await api.get(`/application-status/${customerId}`)
    return response.data
  },
}

export default api
