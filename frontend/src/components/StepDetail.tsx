import { Step, Evaluation, LLMMetadata } from '../types/trace'
import JSONViewer from './JSONViewer'

interface StepDetailProps {
  step: Step
}

function EvaluationTable({ evaluations }: { evaluations: Evaluation[] }) {
  const passedCount = evaluations.filter((e) => e.qualified).length
  const failedCount = evaluations.length - passedCount

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-gray-900 flex items-center">
          <span className="mr-2">🔍</span>
          Filter Evaluations
        </h4>
        <div className="flex gap-3 text-sm">
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-semibold">
            ✓ {passedCount} Passed
          </span>
          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-semibold">
            ✗ {failedCount} Failed
          </span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Item
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Filters
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Result
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {evaluations.map((evaluation, index) => (
              <tr key={index} className={`hover:bg-gray-50 transition-colors ${evaluation.qualified ? '' : 'bg-red-50/30'}`}>
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900 text-sm">
                    {evaluation.item_data.title || evaluation.item_id}
                  </div>
                  {evaluation.item_data.price !== undefined && (
                    <div className="text-xs text-gray-600 mt-1 flex gap-3">
                      <span>${evaluation.item_data.price}</span>
                      <span>{evaluation.item_data.rating}★</span>
                      <span>{evaluation.item_data.reviews?.toLocaleString()} reviews</span>
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1.5">
                    {evaluation.filters.map((filter, filterIndex) => (
                      <div key={filterIndex} className="flex items-start text-xs">
                        <span
                          className={`mr-2 font-bold ${
                            filter.passed ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {filter.passed ? '✓' : '✗'}
                        </span>
                        <span className={filter.passed ? 'text-gray-700' : 'text-red-700'}>
                          {filter.detail}
                        </span>
                      </div>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <span
                    className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      evaluation.qualified
                        ? 'bg-green-100 text-green-800 border border-green-300'
                        : 'bg-red-100 text-red-800 border border-red-300'
                    }`}
                  >
                    {evaluation.qualified ? '✓ Qualified' : '✗ Failed'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function LLMMetadataView({ llm }: { llm: LLMMetadata }) {
  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
        <span className="mr-2">🤖</span>
        LLM Call Details
      </h4>
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-5 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-3 border border-purple-200">
            <p className="text-xs text-purple-600 font-medium mb-1">Model</p>
            <p className="text-lg font-bold text-gray-900">{llm.model}</p>
          </div>
          {llm.tokens_used !== undefined && (
            <div className="bg-white rounded-lg p-3 border border-purple-200">
              <p className="text-xs text-purple-600 font-medium mb-1">Tokens Used</p>
              <p className="text-lg font-bold text-gray-900">{llm.tokens_used?.toLocaleString()}</p>
            </div>
          )}
          {llm.temperature !== undefined && (
            <div className="bg-white rounded-lg p-3 border border-purple-200">
              <p className="text-xs text-purple-600 font-medium mb-1">Temperature</p>
              <p className="text-lg font-bold text-gray-900">{llm.temperature}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function RankedCandidatesView({ candidates }: { candidates: any[] }) {
  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
        <span className="mr-2">🏆</span>
        Ranking Results
      </h4>
      <div className="space-y-3">
        {candidates.slice(0, 5).map((candidate: any, index: number) => (
          <div
            key={index}
            className={`bg-gradient-to-r rounded-lg p-4 border-2 transition-all hover:shadow-lg ${
              candidate.rank === 1
                ? 'from-yellow-50 to-amber-50 border-yellow-400'
                : 'from-gray-50 to-slate-50 border-gray-300'
            }`}
          >
            <div className="flex items-start gap-4">
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-md ${
                  candidate.rank === 1
                    ? 'bg-yellow-500'
                    : candidate.rank === 2
                    ? 'bg-gray-400'
                    : candidate.rank === 3
                    ? 'bg-amber-600'
                    : 'bg-gray-500'
                }`}
              >
                {candidate.rank === 1 && '🥇'}
                {candidate.rank === 2 && '🥈'}
                {candidate.rank === 3 && '🥉'}
                {candidate.rank > 3 && candidate.rank}
              </div>
              <div className="flex-grow">
                <div className="flex justify-between items-start mb-2">
                  <h5 className="font-semibold text-gray-900">{candidate.title}</h5>
                  <span className="text-sm font-bold text-blue-600 bg-blue-100 px-3 py-1 rounded-full">
                    Score: {candidate.score_breakdown?.total_score}
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  ${candidate.metrics?.price} • {candidate.metrics?.rating}★ •{' '}
                  {candidate.metrics?.reviews?.toLocaleString()} reviews
                </div>
                {candidate.score_breakdown && (
                  <div className="flex gap-2 text-xs">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Reviews: {candidate.score_breakdown.review_count_score}
                    </span>
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                      Rating: {candidate.score_breakdown.rating_score}
                    </span>
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      Price: {candidate.score_breakdown.price_proximity_score}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {candidates.length > 5 && (
          <p className="text-sm text-gray-500 text-center">
            +{candidates.length - 5} more candidates not shown
          </p>
        )}
      </div>
    </div>
  )
}

function StepDetail({ step }: StepDetailProps) {
  // Detect metadata patterns
  const hasEvaluations = step.metadata?.evaluations && Array.isArray(step.metadata.evaluations)
  const hasLLMMetadata = step.metadata?.llm
  const hasRankedCandidates =
    step.metadata?.ranked_candidates && Array.isArray(step.metadata.ranked_candidates)

  return (
    <div className="bg-white shadow-md rounded-lg border-2 border-gray-200 p-6">
      {/* Step Header */}
      <div className="border-b-2 border-gray-200 pb-5 mb-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div className="flex-grow">
            <h3 className="text-2xl font-bold text-gray-900 mb-2 capitalize">
              {step.name.replace(/_/g, ' ')}
            </h3>
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <span>Step ID:</span>
              <code className="bg-gray-100 px-2 py-1 rounded font-mono">
                {step.step_id.substring(0, 12)}...
              </code>
            </div>
          </div>
          <div className="flex flex-col gap-2 items-end">
            <span
              className={`px-4 py-2 inline-flex text-sm leading-5 font-semibold rounded-lg shadow-sm ${
                step.status === 'completed'
                  ? 'bg-green-100 text-green-800 border border-green-300'
                  : step.status === 'failed'
                  ? 'bg-red-100 text-red-800 border border-red-300'
                  : 'bg-blue-100 text-blue-800 border border-blue-300'
              }`}
            >
              {step.status.toUpperCase()}
            </span>
            {step.duration_ms !== undefined && (
              <span className="text-sm text-gray-600 font-mono">
                ⏱️ {step.duration_ms < 1000 ? `${step.duration_ms}ms` : `${(step.duration_ms / 1000).toFixed(2)}s`}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Reasoning */}
      {step.reasoning && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <span className="mr-2">💡</span>
            Reasoning
          </h4>
          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-4 shadow-sm">
            <p className="text-sm text-gray-800 leading-relaxed">{step.reasoning}</p>
          </div>
        </div>
      )}

      {/* Error */}
      {step.error && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-red-700 mb-3 flex items-center">
            <span className="mr-2">⚠️</span>
            Error
          </h4>
          <div className="bg-red-50 border border-red-300 rounded-lg p-4 shadow-sm">
            <p className="text-sm text-red-800 font-mono whitespace-pre-wrap">{step.error}</p>
          </div>
        </div>
      )}

      {/* Pattern Detection: Evaluations */}
      {hasEvaluations && <EvaluationTable evaluations={step.metadata.evaluations as Evaluation[]} />}

      {/* Pattern Detection: LLM Metadata */}
      {hasLLMMetadata && <LLMMetadataView llm={step.metadata.llm as LLMMetadata} />}

      {/* Pattern Detection: Ranked Candidates */}
      {hasRankedCandidates && (
        <RankedCandidatesView candidates={step.metadata.ranked_candidates} />
      )}

      {/* Input */}
      {step.input && Object.keys(step.input).length > 0 && (
        <JSONViewer data={step.input} title="📥 Input Data" />
      )}

      {/* Output */}
      {step.output && Object.keys(step.output).length > 0 && (
        <JSONViewer data={step.output} title="📤 Output Data" />
      )}

      {/* Additional Metadata (if not already displayed) */}
      {step.metadata &&
        Object.keys(step.metadata).length > 0 &&
        !hasEvaluations &&
        !hasLLMMetadata &&
        !hasRankedCandidates && <JSONViewer data={step.metadata} title="📊 Metadata" collapsed={true} />}
    </div>
  )
}

export default StepDetail
