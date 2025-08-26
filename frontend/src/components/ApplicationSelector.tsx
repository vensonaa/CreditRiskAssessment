import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { creditRiskAPI, SubmittedApplication } from '../services/api'
import { Loader2, AlertCircle, CheckCircle, FileText, Calendar, DollarSign, Building } from 'lucide-react'
import toast from 'react-hot-toast'

interface ApplicationSelectorProps {
  onApplicationSelect: (application: SubmittedApplication) => void
  selectedApplication?: SubmittedApplication | null
}

export default function ApplicationSelector({ onApplicationSelect, selectedApplication }: ApplicationSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('')

  const {
    data: applications,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['submitted-applications'],
    queryFn: creditRiskAPI.getSubmittedApplications,
    staleTime: 30000, // 30 seconds
  })

  const filteredApplications = applications?.filter(app => {
    const data = app?.application_data
    if (!data) return false
    
    const customerName = data.customer_name || ''
    const customerId = data.customer_id || ''
    const businessType = data.business_type || ''
    
    return customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
           customerId.toLowerCase().includes(searchTerm.toLowerCase()) ||
           businessType.toLowerCase().includes(searchTerm.toLowerCase())
  }) || []

  const handleApplicationSelect = (application: SubmittedApplication) => {
    onApplicationSelect(application)
    toast.success(`Selected application for ${application.application_data.customer_name}`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-red-600" />
        <span className="ml-2 text-gray-600">Loading submitted applications...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <AlertCircle className="h-8 w-8 text-red-600" />
        <span className="ml-2 text-red-600">Failed to load applications</span>
        <button
          onClick={() => refetch()}
          className="ml-4 btn btn-secondary"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!applications || applications.length === 0) {
    return (
      <div className="text-center p-8">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Submitted Applications</h3>
        <p className="text-gray-600 mb-4">
          There are currently no loan applications in submitted status.
        </p>
        <button
          onClick={() => refetch()}
          className="btn btn-primary"
        >
          Refresh
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <div>
        <label htmlFor="search" className="label">
          Search Applications
        </label>
        <input
          type="text"
          id="search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input"
          placeholder="Search by customer name, ID, or business type..."
        />
      </div>

      {/* Applications List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Submitted Applications ({filteredApplications.length})
          </h3>
          <button
            onClick={() => refetch()}
            className="btn btn-secondary btn-sm"
          >
            Refresh
          </button>
        </div>

        <div className="grid gap-4">
          {filteredApplications.map((application) => {
            const isSelected = selectedApplication?.customer_id === application.customer_id
            const data = application?.application_data

            // Skip rendering if data is missing
            if (!data) return null

            return (
              <div
                key={application.customer_id}
                className={`card cursor-pointer transition-all duration-200 hover:shadow-md ${
                  isSelected 
                    ? 'ring-2 ring-red-500 bg-red-50' 
                    : 'hover:bg-red-50'
                }`}
                onClick={() => handleApplicationSelect(application)}
              >
                <div className="card-content">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">
                          {data.customer_name || 'Unknown Customer'}
                        </h4>
                        {isSelected && (
                          <CheckCircle className="h-5 w-5 text-red-600" />
                        )}
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {data.application_status || 'Unknown Status'}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Building className="h-4 w-4" />
                          <span>{data.business_type || 'N/A'}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <DollarSign className="h-4 w-4" />
                          <span>${(data.loan_amount || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-4 w-4" />
                          <span>{data.application_date ? new Date(data.application_date).toLocaleDateString() : 'N/A'}</span>
                        </div>
                      </div>

                      <div className="mt-3 text-sm text-gray-500">
                        <p><strong>Purpose:</strong> {data.loan_purpose || 'N/A'}</p>
                        <p><strong>Collateral:</strong> {data.collateral_type || 'N/A'} (${(data.collateral_value || 0).toLocaleString()})</p>
                        <p><strong>Customer ID:</strong> {data.customer_id || 'N/A'}</p>
                      </div>
                    </div>

                    <div className="text-right text-sm text-gray-500">
                      <p>ID: {data.application_id || 'N/A'}</p>
                      <p>Term: {data.loan_term || 0} months</p>
                      <p>Rate: {data.interest_rate || 0}%</p>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {filteredApplications.length === 0 && searchTerm && (
          <div className="text-center py-8">
            <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">No applications found matching "{searchTerm}"</p>
          </div>
        )}
      </div>
    </div>
  )
}
