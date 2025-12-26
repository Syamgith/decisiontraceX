/**
 * TypeScript type definitions for DecisionTrace X-Ray system.
 *
 * These types mirror the Python Pydantic models.
 */

export interface Step {
  step_id: string;
  trace_id: string;
  name: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  reasoning?: string;
  metadata: Record<string, any>;
  start_time: string;  // ISO 8601
  end_time?: string;
  duration_ms?: number;
  status: 'running' | 'completed' | 'failed';
  error?: string;
  step_order: number;
}

export interface Trace {
  trace_id: string;
  name: string;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  steps: Step[];
  metadata: Record<string, any>;
  status: 'running' | 'completed' | 'failed';
}

// Metadata pattern types (known patterns)
export interface EvaluationFilter {
  name: string;
  passed: boolean;
  detail: string;
}

export interface Evaluation {
  item_id: string;
  item_data: Record<string, any>;
  filters: EvaluationFilter[];
  qualified: boolean;
  reasoning?: string;
}

export interface LLMMetadata {
  model: string;
  tokens_used?: number;
  temperature?: number;
  [key: string]: any;
}
