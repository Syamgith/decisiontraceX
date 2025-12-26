import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import TraceList from './components/TraceList'
import TraceDetail from './components/TraceDetail'

function Header() {
  const location = useLocation()
  const isDetailPage = location.pathname.startsWith('/trace/')

  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg border-b-4 border-indigo-700">
      <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="text-4xl transition-transform group-hover:scale-110">🔍</div>
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                DecisionTrace X-Ray
              </h1>
              <p className="text-sm text-blue-100">
                Debug multi-step decision processes with transparency
              </p>
            </div>
          </Link>

          {!isDetailPage && (
            <div className="hidden md:flex items-center gap-4 bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
              <div className="text-white text-sm">
                <span className="font-semibold">API:</span>{' '}
                <code className="bg-black/20 px-2 py-1 rounded">localhost:8000</code>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Header />

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<TraceList />} />
            <Route path="/trace/:traceId" element={<TraceDetail />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="mt-12 py-6 bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-gray-500">
              Built with ❤️ using Python, FastAPI, React, and TypeScript •{' '}
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                API Docs
              </a>
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
