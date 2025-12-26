import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Trace } from '../types/trace'

function TraceList() {
  const [traces, setTraces] = useState<Trace[]>([])
  const [filteredTraces, setFilteredTraces] = useState<Trace[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    fetchTraces()
  }, [])

  useEffect(() => {
    filterTraces()
  }, [traces, searchTerm, statusFilter])

  const fetchTraces = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/traces')
      if (!response.ok) {
        throw new Error('Failed to fetch traces')
      }
      const data = await response.json()
      setTraces(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const filterTraces = () => {
    let filtered = traces

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter((trace) => trace.status === statusFilter)
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (trace) =>
          trace.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          trace.trace_id.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredTraces(filtered)
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A'
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  // Calculate statistics
  const stats = {
    total: traces.length,
    completed: traces.filter((t) => t.status === 'completed').length,
    failed: traces.filter((t) => t.status === 'failed').length,
    running: traces.filter((t) => t.status === 'running').length,
    avgDuration:
      traces.length > 0
        ? traces.reduce((sum, t) => sum + (t.duration_ms || 0), 0) / traces.length
        : 0,
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-500">Loading traces...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <span className="text-2xl mr-3">⚠️</span>
          <div>
            <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Traces</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={fetchTraces}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (traces.length === 0) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">No Traces Yet</h3>
        <p className="text-gray-600 mb-6">
          Run the demo pipeline to generate your first traces
        </p>
        <div className="bg-white border border-gray-200 rounded-lg p-4 max-w-2xl mx-auto">
          <code className="text-sm text-gray-800 block mb-2">cd backend</code>
          <code className="text-sm text-gray-800 block">python -m demo.pipeline</code>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500 mb-1">Total Traces</p>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-green-50 rounded-lg shadow-sm border border-green-200 p-4">
          <p className="text-sm text-green-700 mb-1">Completed</p>
          <p className="text-3xl font-bold text-green-800">{stats.completed}</p>
        </div>
        <div className="bg-red-50 rounded-lg shadow-sm border border-red-200 p-4">
          <p className="text-sm text-red-700 mb-1">Failed</p>
          <p className="text-3xl font-bold text-red-800">{stats.failed}</p>
        </div>
        <div className="bg-blue-50 rounded-lg shadow-sm border border-blue-200 p-4">
          <p className="text-sm text-blue-700 mb-1">Running</p>
          <p className="text-3xl font-bold text-blue-800">{stats.running}</p>
        </div>
        <div className="bg-purple-50 rounded-lg shadow-sm border border-purple-200 p-4">
          <p className="text-sm text-purple-700 mb-1">Avg Duration</p>
          <p className="text-3xl font-bold text-purple-800">
            {formatDuration(stats.avgDuration)}
          </p>
        </div>
      </div>

      {/* Header with Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <h2 className="text-2xl font-bold text-gray-900">Execution Traces</h2>

          <div className="flex flex-col sm:flex-row gap-3">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search traces..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
            </select>

            {/* Refresh Button */}
            <button
              onClick={fetchTraces}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span>🔄</span>
              Refresh
            </button>
          </div>
        </div>

        {/* Results count */}
        {(searchTerm || statusFilter !== 'all') && (
          <p className="mt-3 text-sm text-gray-600">
            Showing {filteredTraces.length} of {traces.length} traces
          </p>
        )}
      </div>

      {/* Traces Table */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name & ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Steps
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTraces.map((trace) => (
                <tr key={trace.trace_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">
                      {trace.name}
                    </div>
                    <div className="text-xs text-gray-500 font-mono">
                      {trace.trace_id.substring(0, 8)}...
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusColor(
                        trace.status
                      )}`}
                    >
                      {trace.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-semibold text-gray-900 mr-1">
                        {trace.steps.length}
                      </span>
                      <span className="text-xs text-gray-500">steps</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900 font-mono">
                      {formatDuration(trace.duration_ms)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatTimestamp(trace.start_time)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <Link
                      to={`/trace/${trace.trace_id}`}
                      className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <span className="mr-1">👁️</span>
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredTraces.length === 0 && traces.length > 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-gray-500">No traces match your filters</p>
        </div>
      )}
    </div>
  )
}

export default TraceList
