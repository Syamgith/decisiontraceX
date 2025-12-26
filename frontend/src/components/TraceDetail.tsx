import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Trace, Step } from '../types/trace'
import StepDetail from './StepDetail'

function TraceDetail() {
  const { traceId } = useParams<{ traceId: string }>()
  const [trace, setTrace] = useState<Trace | null>(null)
  const [selectedStep, setSelectedStep] = useState<Step | null>(null)
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
      // Select first step by default
      if (data.steps.length > 0) {
        setSelectedStep(data.steps[0])
      }
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
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
        return 'border-green-500'
      case 'failed':
        return 'border-red-500'
      case 'running':
        return 'border-blue-500'
      default:
        return 'border-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">Loading trace...</div>
      </div>
    )
  }

  if (error || !trace) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error || 'Trace not found'}</p>
        <Link to="/" className="mt-2 text-sm text-blue-600 hover:text-blue-800 underline">
          Back to traces
        </Link>
      </div>
    )
  }

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="mb-4">
        <Link to="/" className="text-blue-600 hover:text-blue-800">
          ← Back to Traces
        </Link>
      </nav>

      {/* Trace Header */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{trace.name}</h2>
            <p className="text-sm text-gray-500 mt-1">
              Trace ID: {trace.trace_id}
            </p>
          </div>
          <span
            className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${
              trace.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : trace.status === 'failed'
                ? 'bg-red-100 text-red-800'
                : 'bg-blue-100 text-blue-800'
            }`}
          >
            {trace.status}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Steps</p>
            <p className="font-semibold text-gray-900">{trace.steps.length}</p>
          </div>
          <div>
            <p className="text-gray-500">Duration</p>
            <p className="font-semibold text-gray-900">
              {formatDuration(trace.duration_ms)}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Start Time</p>
            <p className="font-semibold text-gray-900">
              {new Date(trace.start_time).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Execution Timeline
        </h3>

        <div className="relative">
          {/* Timeline steps */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-4">
            {trace.steps.map((step, index) => (
              <div key={step.step_id} className="flex items-center flex-shrink-0">
                {/* Step node */}
                <button
                  onClick={() => setSelectedStep(step)}
                  className={`relative group ${
                    selectedStep?.step_id === step.step_id
                      ? 'transform scale-110'
                      : ''
                  }`}
                >
                  <div
                    className={`w-24 h-24 rounded-lg border-4 ${getStatusBorderColor(
                      step.status
                    )} bg-white p-2 hover:shadow-lg transition-all cursor-pointer ${
                      selectedStep?.step_id === step.step_id
                        ? 'shadow-lg'
                        : 'shadow-md'
                    }`}
                  >
                    <div className="text-xs font-medium text-gray-900 truncate">
                      {step.name.replace(/_/g, ' ')}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatDuration(step.duration_ms)}
                    </div>
                    <div className={`absolute top-0 right-0 w-3 h-3 rounded-full ${getStatusColor(step.status)}`} />
                  </div>

                  {/* Step number */}
                  <div className="absolute -top-2 -left-2 w-6 h-6 rounded-full bg-gray-700 text-white text-xs flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                </button>

                {/* Connector arrow */}
                {index < trace.steps.length - 1 && (
                  <div className="w-8 h-0.5 bg-gray-300 mx-1">
                    <div className="relative">
                      <div className="absolute right-0 -top-1 w-0 h-0 border-t-4 border-t-transparent border-b-4 border-b-transparent border-l-4 border-l-gray-300" />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Selected Step Detail */}
      {selectedStep && <StepDetail step={selectedStep} />}
    </div>
  )
}

export default TraceDetail
