import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import TraceList from './components/TraceList'
import TraceDetail from './components/TraceDetail'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <Link to="/" className="flex items-center space-x-3">
                <div className="text-2xl">🔍</div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    DecisionTrace X-Ray
                  </h1>
                  <p className="text-sm text-gray-500">
                    Debug multi-step decision processes
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<TraceList />} />
            <Route path="/trace/:traceId" element={<TraceDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
