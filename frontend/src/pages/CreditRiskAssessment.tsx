import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { creditRiskAPI, CreditRiskRequest, SubmittedApplication } from '../services/api'
import { Loader2, AlertCircle, CheckCircle, FileText, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import ApplicationSelector from '../components/ApplicationSelector'

const assessmentSchema = z.object({
  customer_id: z.string().min(1, 'Customer ID is required'),
  customer_name: z.string().min(1, 'Customer name is required'),
  business_type: z.string().min(1, 'Business type is required'),
  annual_revenue: z.number().min(0, 'Annual revenue must be positive'),
  credit_history_years: z.number().min(0, 'Credit history years must be positive'),
  requested_amount: z.number().min(0, 'Requested amount must be positive'),
  purpose: z.string().min(1, 'Purpose is required'),
})

type AssessmentFormData = z.infer<typeof assessmentSchema>

export default function CreditRiskAssessment() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedApplication, setSelectedApplication] = useState<SubmittedApplication | null>(null)
  const [useManualEntry, setUseManualEntry] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm<AssessmentFormData>({
    resolver: zodResolver(assessmentSchema),
  })

  const handleApplicationSelect = (application: SubmittedApplication) => {
    setSelectedApplication(application)
    const data = application.application_data
    
    // Pre-fill the form with application data
    setValue('customer_id', data.customer_id)
    setValue('customer_name', data.customer_name)
    setValue('business_type', data.business_type)
    setValue('annual_revenue', data.annual_revenue)
    setValue('credit_history_years', data.credit_history_years)
    setValue('requested_amount', data.requested_amount)
    setValue('purpose', data.purpose)
    
    setUseManualEntry(false)
  }

  const createAssessmentMutation = useMutation({
    mutationFn: creditRiskAPI.createAssessment,
    onSuccess: (data) => {
      toast.success('Credit risk assessment initiated successfully!')
      navigate(`/workflow/${data.request_id}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create assessment')
      setIsSubmitting(false)
    },
  })

  const onSubmit = async (data: AssessmentFormData) => {
    if (!selectedApplication && !useManualEntry) {
      toast.error('Please select a submitted loan application or enable manual entry')
      return
    }
    
    setIsSubmitting(true)
    try {
      const request: CreditRiskRequest = {
        ...data,
        additional_data: {},
      }
      await createAssessmentMutation.mutateAsync(request)
    } catch (error) {
      console.error('Assessment creation error:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">New Credit Risk Assessment</h1>
        <p className="mt-2 text-sm text-gray-600">
          Create a new credit risk assessment using our AI-powered Generator → Reflection → Refiner workflow.
        </p>
      </div>

      {/* Application Selection Mode */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-red-800">Application Selection</h2>
          <p className="mt-1 text-sm text-gray-600">
            Choose how you want to provide customer information for the credit risk assessment.
          </p>
        </div>
        <div className="card-content">
          <div className="flex space-x-4 mb-6">
            <button
              type="button"
              onClick={() => setUseManualEntry(false)}
              className={`btn ${!useManualEntry ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Users className="h-4 w-4 mr-2" />
              Select from Submitted Applications
            </button>
            <button
              type="button"
              onClick={() => setUseManualEntry(true)}
              className={`btn ${useManualEntry ? 'btn-primary' : 'btn-secondary'}`}
            >
              <FileText className="h-4 w-4 mr-2" />
              Manual Entry
            </button>
          </div>

          {!useManualEntry && (
            <div className="mb-6">
              <ApplicationSelector
                onApplicationSelect={handleApplicationSelect}
                selectedApplication={selectedApplication}
              />
            </div>
          )}

          {selectedApplication && !useManualEntry && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                <span className="text-green-800 font-medium">
                  Selected: {selectedApplication.application_data.customer_name} 
                  (ID: {selectedApplication.application_data.customer_id})
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Customer Information Form */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-red-800">
            {useManualEntry ? 'Customer Information' : 'Review & Edit Information'}
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            {useManualEntry 
              ? 'Provide the customer details for the credit risk assessment.'
              : 'Review and edit the information from the selected application if needed.'
            }
          </p>
        </div>
        <div className="card-content">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {/* Customer ID */}
              <div>
                <label htmlFor="customer_id" className="label">
                  Customer ID *
                </label>
                <input
                  type="text"
                  id="customer_id"
                  {...register('customer_id')}
                  className={`input mt-1 ${selectedApplication && !useManualEntry ? 'bg-gray-50' : ''}`}
                  placeholder="Enter customer ID"
                  readOnly={selectedApplication && !useManualEntry}
                />
                {errors.customer_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.customer_id.message}</p>
                )}
              </div>

              {/* Customer Name */}
              <div>
                <label htmlFor="customer_name" className="label">
                  Customer Name *
                </label>
                <input
                  type="text"
                  id="customer_name"
                  {...register('customer_name')}
                  className="input mt-1"
                  placeholder="Enter customer name"
                />
                {errors.customer_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.customer_name.message}</p>
                )}
              </div>

              {/* Business Type */}
              <div>
                <label htmlFor="business_type" className="label">
                  Business Type *
                </label>
                <select
                  id="business_type"
                  {...register('business_type')}
                  className="input mt-1"
                >
                  <option value="">Select business type</option>
                  <option value="Technology">Technology</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Retail">Retail</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Financial Services">Financial Services</option>
                  <option value="Real Estate">Real Estate</option>
                  <option value="Transportation">Transportation</option>
                  <option value="Energy">Energy</option>
                  <option value="Other">Other</option>
                </select>
                {errors.business_type && (
                  <p className="mt-1 text-sm text-red-600">{errors.business_type.message}</p>
                )}
              </div>

              {/* Annual Revenue */}
              <div>
                <label htmlFor="annual_revenue" className="label">
                  Annual Revenue (USD) *
                </label>
                <input
                  type="number"
                  id="annual_revenue"
                  {...register('annual_revenue', { valueAsNumber: true })}
                  className="input mt-1"
                  placeholder="Enter annual revenue"
                  min="0"
                  step="0.01"
                />
                {errors.annual_revenue && (
                  <p className="mt-1 text-sm text-red-600">{errors.annual_revenue.message}</p>
                )}
              </div>

              {/* Credit History Years */}
              <div>
                <label htmlFor="credit_history_years" className="label">
                  Credit History (Years) *
                </label>
                <input
                  type="number"
                  id="credit_history_years"
                  {...register('credit_history_years', { valueAsNumber: true })}
                  className="input mt-1"
                  placeholder="Enter credit history years"
                  min="0"
                  step="1"
                />
                {errors.credit_history_years && (
                  <p className="mt-1 text-sm text-red-600">{errors.credit_history_years.message}</p>
                )}
              </div>

              {/* Requested Amount */}
              <div>
                <label htmlFor="requested_amount" className="label">
                  Requested Amount (USD) *
                </label>
                <input
                  type="number"
                  id="requested_amount"
                  {...register('requested_amount', { valueAsNumber: true })}
                  className="input mt-1"
                  placeholder="Enter requested amount"
                  min="0"
                  step="0.01"
                />
                {errors.requested_amount && (
                  <p className="mt-1 text-sm text-red-600">{errors.requested_amount.message}</p>
                )}
              </div>
            </div>

            {/* Purpose */}
            <div>
              <label htmlFor="purpose" className="label">
                Purpose of Credit *
              </label>
              <textarea
                id="purpose"
                {...register('purpose')}
                className="input mt-1 min-h-[100px]"
                placeholder="Describe the purpose of the credit request..."
              />
              {errors.purpose && (
                <p className="mt-1 text-sm text-red-600">{errors.purpose.message}</p>
              )}
            </div>

            {/* Workflow Information */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-5 w-5 text-red-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    AI-Powered Workflow
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>This assessment will be processed through our advanced AI workflow:</p>
                    <ol className="mt-2 list-decimal list-inside space-y-1">
                      <li><strong>Generator Agent:</strong> Creates initial credit risk assessment report</li>
                      <li><strong>Reflection Agent:</strong> Evaluates report quality and provides critique</li>
                      <li><strong>Refiner Agent:</strong> Improves report based on feedback</li>
                      <li><strong>Loop:</strong> Continues until quality threshold is met</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => reset()}
                className="btn btn-secondary btn-md"
                disabled={isSubmitting}
              >
                Reset
              </button>
              <button
                type="submit"
                className="btn btn-primary btn-md"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Assessment...
                  </>
                ) : (
                  selectedApplication && !useManualEntry 
                    ? 'Start Assessment for Selected Application'
                    : 'Create Assessment'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
