import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Trace, Step } from '../types/trace'
import StepDetail from './StepDetail'

function TraceDetail() {
  const { traceId } = useParams<{ traceId: string }>()
  const [trace, setTrace] = useState<Trace | null>(null)
  const [expandedStepId, setExpandedStepId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (traceId) {
      fetchTrace(traceId)
    }
  }, [traceId])

  const fetchTrace = async (id: string) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/traces/${id}`)
      if (!response.ok) {
        throw new Error('Failed to fetch trace')
      }
      const data = await response.json()
      setTrace(data)
      // Expand first step by default
      if (data.steps.length > 0) {
        setExpandedStepId(data.steps[0].step_id)
      }
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const toggleStep = (stepId: string) => {
    setExpandedStepId(expandedStepId === stepId ? null : stepId)
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A'
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500'
      case 'failed':
        return 'bg-red-500'
      case 'running':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusBorderColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-500 shadow-green-200'
      case 'failed':
        return 'border-red-500 shadow-red-200'
      case 'running':
        return 'border-blue-500 shadow-blue-200'
      default:
        return 'border-gray-500 shadow-gray-200'
    }
  }

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50'
      case 'failed':
        return 'bg-red-50'
      case 'running':
        return 'bg-blue-50'
      default:
        return 'bg-gray-50'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-500">Loading trace...</p>
        </div>
      </div>
    )
  }

  if (error || !trace) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <span className="text-2xl mr-3">⚠️</span>
          <div>
            <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Trace</h3>
            <p className="text-red-700 mb-4">{error || 'Trace not found'}</p>
            <Link
              to="/"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              ← Back to Traces
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav>
        <Link
          to="/"
          className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
        >
          <span className="mr-2">←</span>
          Back to Traces
        </Link>
      </nav>

      {/* Trace Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">{trace.name}</h2>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">Trace ID:</span>
              <code className="text-sm bg-white px-2 py-1 rounded border border-gray-300 font-mono">
                {trace.trace_id}
              </code>
            </div>
          </div>
          <span
            className={`px-4 py-2 inline-flex text-sm leading-5 font-semibold rounded-lg shadow-sm ${
              trace.status === 'completed'
                ? 'bg-green-100 text-green-800 border border-green-300'
                : trace.status === 'failed'
                ? 'bg-red-100 text-red-800 border border-red-300'
                : 'bg-blue-100 text-blue-800 border border-blue-300'
            }`}
          >
            {trace.status.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Total Steps</p>
            <p className="text-2xl font-bold text-gray-900">{trace.steps.length}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Duration</p>
            <p className="text-2xl font-bold text-gray-900 font-mono">
              {formatDuration(trace.duration_ms)}
            </p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Start Time</p>
            <p className="text-sm font-semibold text-gray-900">
              {new Date(trace.start_time).toLocaleTimeString()}
            </p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">End Time</p>
            <p className="text-sm font-semibold text-gray-900">
              {trace.end_time ? new Date(trace.end_time).toLocaleTimeString() : 'Running...'}
            </p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <span className="mr-2">📊</span>
          Execution Timeline
          <span className="ml-3 text-sm font-normal text-gray-500">
            (Click on a step to expand/collapse details)
          </span>
        </h3>

        <div className="relative">
          {/* Vertical Timeline */}
          <div className="space-y-4">
            {trace.steps.map((step, index) => {
              const isExpanded = expandedStepId === step.step_id
              const isLast = index === trace.steps.length - 1

              return (
                <div key={step.step_id} className="relative">
                  {/* Connector Line */}
                  {!isLast && (
                    <div className="absolute left-6 top-16 bottom-0 w-0.5 bg-gray-300 -mb-4" />
                  )}

                  {/* Step Card */}
                  <div className={`transition-all ${isExpanded ? 'transform scale-[1.01]' : ''}`}>
                    <button
                      onClick={() => toggleStep(step.step_id)}
                      className="w-full text-left"
                    >
                      <div
                        className={`relative flex gap-4 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                          isExpanded
                            ? `${getStatusBorderColor(step.status)} shadow-lg ${getStatusBgColor(
                                step.status
                              )}`
                            : 'border-gray-200 hover:border-gray-300 bg-white hover:shadow-md'
                        }`}
                      >
                        {/* Step Number Circle */}
                        <div className="flex-shrink-0">
                          <div
                            className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white shadow-lg ${getStatusColor(
                              step.status
                            )}`}
                          >
                            {index + 1}
                          </div>
                        </div>

                        {/* Step Content */}
                        <div className="flex-grow min-w-0">
                          <div className="flex items-start justify-between gap-4 mb-2">
                            <div>
                              <h4 className="text-lg font-semibold text-gray-900 capitalize">
                                {step.name.replace(/_/g, ' ')}
                              </h4>
                              <p className="text-sm text-gray-500 font-mono">
                                {step.step_id.substring(0, 12)}...
                              </p>
                            </div>
                            <div className="flex flex-col items-end gap-1">
                              <span
                                className={`px-3 py-1 text-xs font-semibold rounded-full ${
                                  step.status === 'completed'
                                    ? 'bg-green-100 text-green-800'
                                    : step.status === 'failed'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-blue-100 text-blue-800'
                                }`}
                              >
                                {step.status}
                              </span>
                              <span className="text-xs text-gray-500 font-mono">
                                {formatDuration(step.duration_ms)}
                              </span>
                            </div>
                          </div>

                          {!isExpanded && step.reasoning && (
                            <p className="text-sm text-gray-700 line-clamp-2">{step.reasoning}</p>
                          )}

                          {/* Quick Stats */}
                          <div className="flex gap-4 mt-2 text-xs text-gray-600">
                            {step.input && Object.keys(step.input).length > 0 && (
                              <span>📥 {Object.keys(step.input).length} inputs</span>
                            )}
                            {step.output && Object.keys(step.output).length > 0 && (
                              <span>📤 {Object.keys(step.output).length} outputs</span>
                            )}
                            {step.metadata && Object.keys(step.metadata).length > 0 && (
                              <span>📊 {Object.keys(step.metadata).length} metadata</span>
                            )}
                          </div>
                        </div>

                        {/* Expand/Collapse Indicator */}
                        <div className="flex-shrink-0">
                          <div className="text-2xl transition-transform">
                            {isExpanded ? '▼' : '▶'}
                          </div>
                        </div>
                      </div>
                    </button>

                    {/* Expanded Step Details */}
                    {isExpanded && (
                      <div className="mt-4 ml-16 animate-fadeIn">
                        <StepDetail step={step} />
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TraceDetail
