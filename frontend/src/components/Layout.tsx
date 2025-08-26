import { Link, useLocation } from 'react-router-dom'
import { 
  BarChart3, 
  FileText, 
  Home, 
  Plus, 
  TrendingUp,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'New Assessment', href: '/assessment', icon: Plus },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Statistics', href: '/statistics', icon: BarChart3 },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-gray-50">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white shadow-2xl">
          <div className="flex h-16 items-center justify-between px-4 bg-gradient-to-r from-red-600 to-red-700">
            <h1 className="text-xl font-bold text-white">Credit Risk Assessment</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-white hover:text-red-200 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4 bg-white">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group nav-link ${
                    isActive ? 'nav-link-active' : 'nav-link-inactive'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? 'text-red-600' : 'text-gray-400 group-hover:text-red-500'
                    }`}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-red-200 shadow-lg">
          <div className="flex h-16 items-center px-4 bg-gradient-to-r from-red-600 to-red-700">
            <h1 className="text-xl font-bold text-white">Credit Risk Assessment</h1>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4 bg-white">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group nav-link ${
                    isActive ? 'nav-link-active' : 'nav-link-inactive'
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? 'text-red-600' : 'text-gray-400 group-hover:text-red-500'
                    }`}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-red-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden hover:text-red-600 transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <div className="flex items-center gap-x-2">
                <TrendingUp className="h-5 w-5 text-red-500" />
                <span className="text-sm text-gray-600 font-medium">AI-Powered Credit Risk Assessment</span>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
