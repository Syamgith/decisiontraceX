import { Step, Evaluation, LLMMetadata } from '../types/trace'

interface StepDetailProps {
  step: Step
}

function JSONViewer({ data, title }: { data: any; title: string }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>
      <pre className="bg-gray-50 border border-gray-200 rounded p-3 text-xs overflow-x-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}

function EvaluationTable({ evaluations }: { evaluations: Evaluation[] }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">
        Filter Evaluations ({evaluations.length} items)
      </h4>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Item
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Filters
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Result
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Reasoning
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {evaluations.map((evaluation, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">
                  <div className="font-medium text-gray-900">
                    {evaluation.item_data.title || evaluation.item_id}
                  </div>
                  {evaluation.item_data.price !== undefined && (
                    <div className="text-xs text-gray-500 mt-1">
                      ${evaluation.item_data.price} • {evaluation.item_data.rating}★ •{' '}
                      {evaluation.item_data.reviews?.toLocaleString()} reviews
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    {evaluation.filters.map((filter, filterIndex) => (
                      <div key={filterIndex} className="flex items-center text-xs">
                        <span
                          className={`mr-2 ${
                            filter.passed ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {filter.passed ? '✓' : '✗'}
                        </span>
                        <span className="text-gray-700">{filter.detail}</span>
                      </div>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span
                    className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      evaluation.qualified
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {evaluation.qualified ? 'Qualified' : 'Failed'}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-gray-600">
                  {evaluation.reasoning || 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="mt-3 text-sm text-gray-600">
        <span className="font-semibold text-green-600">
          {evaluations.filter((e) => e.qualified).length} passed
        </span>
        {' • '}
        <span className="font-semibold text-red-600">
          {evaluations.filter((e) => !e.qualified).length} failed
        </span>
      </div>
    </div>
  )
}

function LLMMetadataView({ llm }: { llm: LLMMetadata }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">LLM Call Details</h4>
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-purple-600 font-medium">Model</p>
            <p className="text-gray-900">{llm.model}</p>
          </div>
          {llm.tokens_used !== undefined && (
            <div>
              <p className="text-purple-600 font-medium">Tokens Used</p>
              <p className="text-gray-900">{llm.tokens_used?.toLocaleString()}</p>
            </div>
          )}
          {llm.temperature !== undefined && (
            <div>
              <p className="text-purple-600 font-medium">Temperature</p>
              <p className="text-gray-900">{llm.temperature}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StepDetail({ step }: StepDetailProps) {
  // Detect metadata patterns
  const hasEvaluations = step.metadata?.evaluations && Array.isArray(step.metadata.evaluations)
  const hasLLMMetadata = step.metadata?.llm
  const hasRankedCandidates = step.metadata?.ranked_candidates && Array.isArray(step.metadata.ranked_candidates)

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      {/* Step Header */}
      <div className="border-b border-gray-200 pb-4 mb-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              {step.name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Step ID: {step.step_id.substring(0, 8)}...
            </p>
          </div>
          <span
            className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${
              step.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : step.status === 'failed'
                ? 'bg-red-100 text-red-800'
                : 'bg-blue-100 text-blue-800'
            }`}
          >
            {step.status}
          </span>
        </div>

        {step.duration_ms !== undefined && (
          <p className="text-sm text-gray-600 mt-2">
            Duration: {step.duration_ms < 1000 ? `${step.duration_ms}ms` : `${(step.duration_ms / 1000).toFixed(2)}s`}
          </p>
        )}
      </div>

      {/* Reasoning */}
      {step.reasoning && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Reasoning</h4>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-gray-800">{step.reasoning}</p>
          </div>
        </div>
      )}

      {/* Error */}
      {step.error && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-red-700 mb-2">Error</h4>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800 font-mono">{step.error}</p>
          </div>
        </div>
      )}

      {/* Pattern Detection: Evaluations */}
      {hasEvaluations && <EvaluationTable evaluations={step.metadata.evaluations as Evaluation[]} />}

      {/* Pattern Detection: LLM Metadata */}
      {hasLLMMetadata && <LLMMetadataView llm={step.metadata.llm as LLMMetadata} />}

      {/* Pattern Detection: Ranked Candidates */}
      {hasRankedCandidates && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">
            Ranking Results ({step.metadata.ranked_candidates.length} candidates)
          </h4>
          <div className="space-y-2">
            {step.metadata.ranked_candidates.slice(0, 5).map((candidate: any, index: number) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold mr-2">
                      {candidate.rank}
                    </span>
                    <span className="font-medium text-gray-900">{candidate.title}</span>
                  </div>
                  <span className="text-sm font-semibold text-blue-600">
                    Score: {candidate.score_breakdown?.total_score}
                  </span>
                </div>
                <div className="text-xs text-gray-600 mt-2 ml-8">
                  ${candidate.metrics?.price} • {candidate.metrics?.rating}★ • {candidate.metrics?.reviews?.toLocaleString()} reviews
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      {step.input && Object.keys(step.input).length > 0 && <JSONViewer data={step.input} title="Input" />}

      {/* Output */}
      {step.output && <JSONViewer data={step.output} title="Output" />}

      {/* Additional Metadata (if not already displayed) */}
      {step.metadata && Object.keys(step.metadata).length > 0 && !hasEvaluations && !hasLLMMetadata && !hasRankedCandidates && (
        <JSONViewer data={step.metadata} title="Metadata" />
      )}
    </div>
  )
}

export default StepDetail
