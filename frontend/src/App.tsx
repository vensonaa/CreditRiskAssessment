import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CreditRiskAssessment from './pages/CreditRiskAssessment'
import WorkflowStatus from './pages/WorkflowStatus'
import Reports from './pages/Reports'
import Statistics from './pages/Statistics'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-gray-50">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assessment" element={<CreditRiskAssessment />} />
          <Route path="/workflow/:requestId" element={<WorkflowStatus />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/statistics" element={<Statistics />} />
        </Routes>
      </Layout>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#dc2626',
            color: '#fff',
            border: '2px solid #b91c1c',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)',
          },
          success: {
            style: {
              background: '#16a34a',
              border: '2px solid #15803d',
            },
          },
          error: {
            style: {
              background: '#dc2626',
              border: '2px solid #b91c1c',
            },
          },
        }}
      />
    </div>
  )
}

export default App
