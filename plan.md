# DecisionTraceX - Implementation Plan

## Executive Summary

Build an X-Ray debugging system for multi-step, non-deterministic algorithmic pipelines. The system consists of:
1. **X-Ray SDK** - Lightweight library for capturing decision context
2. **Dashboard** - Web UI for visualizing decision trails
3. **Demo App** - Competitor product selection workflow

**Time Budget:** 4-6 hours

---

## Quick Start

```bash
# 1. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Run demo (generates sample traces)
python -m demo.pipeline

# 3. Start API server (new terminal)
cd backend
source venv/bin/activate
uvicorn api.main:app --reload

# 4. Start dashboard (new terminal)
cd frontend
npm install
npm run dev

# 5. Open http://localhost:5173
```

---

## Architecture Overview

### System Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐                                       │
│  │  Demo Application│                                       │
│  │  (Python)        │                                       │
│  └────────┬─────────┘                                       │
│           │ imports & uses                                  │
│           ▼                                                 │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   X-Ray SDK      │────────▶│  SQLite Database │         │
│  │   (Python)       │  writes │  (traces.db)     │         │
│  └──────────────────┘         └────────┬─────────┘         │
│                                        │                    │
│                                        │ reads              │
│                                        ▼                    │
│                               ┌──────────────────┐          │
│                               │  FastAPI Server  │          │
│                               │  (REST API)      │          │
│                               └────────┬─────────┘          │
│                                        │ HTTP GET           │
│                                        ▼                    │
│                               ┌──────────────────┐          │
│                               │ React Dashboard  │          │
│                               │ (Vite SPA)       │          │
│                               └──────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Data Flow:
1. Demo app uses SDK to record traces → Writes directly to SQLite
2. FastAPI server reads from SQLite → Exposes REST API (read-only)
3. React dashboard fetches from API → Displays trace visualization
```

**Key Design Decision:**
- Demo app writes directly to SQLite (simpler, faster for demo)
- API is read-only (GET endpoints only)
- No POST endpoints needed for this demo
- Production could add write API for remote trace submission

---

## Technology Stack

### Backend: Python + FastAPI

**Why FastAPI:**
- Pydantic models for validation + serialization
- Auto-generated Swagger docs at `/docs`
- Native async support
- Natural fit for AI/ML workflows (Python ecosystem)
- Shared models between SDK and API

### SDK: Python with Pydantic

**Why Python:**
- Context managers (`with` statement) perfect for trace lifecycle
- Target audience: AI/ML engineers building LLM pipelines
- Shared Pydantic models with backend (DRY principle)

### Frontend: React + TypeScript + Vite

**Why Vite over Next.js:**
- Simple SPA (no SSR needed for internal tool)
- Faster dev experience with instant HMR
- No SEO requirements
- Lighter weight

**UI Libraries:**
- **Tailwind CSS** - Rapid styling
- **shadcn/ui** - High-quality React components
- **Recharts** - Charts for timelines

### Data Storage: SQLite + In-Memory Cache

**Why SQLite:**
- Zero-config, persistent, queryable
- No external dependencies
- Perfect for demo and reviewers
- WAL mode for better concurrency

---

## Database Schema

### SQLite Schema Design

```sql
-- Traces table
CREATE TABLE traces (
    trace_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,      -- ISO 8601 format
    end_time TEXT,
    duration_ms INTEGER,
    metadata TEXT,                  -- JSON blob
    status TEXT CHECK(status IN ('running', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_traces_status ON traces(status);
CREATE INDEX idx_traces_created_at ON traces(created_at DESC);

-- Steps table
CREATE TABLE steps (
    step_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    input TEXT,                     -- JSON blob
    output TEXT,                    -- JSON blob
    reasoning TEXT,
    metadata TEXT,                  -- JSON blob (evaluations, llm, etc.)
    start_time TEXT NOT NULL,       -- ISO 8601 format
    end_time TEXT,
    duration_ms INTEGER,
    status TEXT CHECK(status IN ('running', 'completed', 'failed')),
    error TEXT,
    step_order INTEGER,             -- Position in trace (0-indexed)
    FOREIGN KEY (trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
);

CREATE INDEX idx_steps_trace_id ON steps(trace_id);
CREATE INDEX idx_steps_order ON steps(trace_id, step_order);

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;
```

**Design Notes:**
- JSON blobs for flexible schema (input, output, metadata)
- ISO 8601 timestamps for easy parsing
- Foreign key cascade deletes for data integrity
- Indexes on common query patterns

---

## SDK Design

### Core Concepts

1. **Trace:** A complete execution of a multi-step workflow
2. **Step:** A single decision point within a trace
3. **Metadata:** Flexible JSON field for domain-specific data

### API Design: Context Manager Pattern

**Chosen Approach:** Context Manager (Option 1)

```python
from decisiontrace import XRay

xray = XRay()

# Use context manager for trace lifecycle
with xray.trace("competitor-selection-123") as trace:

    # Step 1: Keyword Generation
    with trace.step("keyword_generation") as step:
        step.set_input({"product_title": "...", "category": "..."})

        keywords = generate_keywords(step.input)

        step.set_output({"keywords": keywords})
        step.set_reasoning("Extracted key attributes: material, capacity, feature")

    # Step 2: Candidate Search
    with trace.step("candidate_search") as step:
        step.set_input({"keyword": keywords[0], "limit": 50})

        results = search_products(step.input["keyword"])

        step.set_output({"candidates": results["candidates"], "total": results["total"]})
        step.set_reasoning(f"Fetched top 50 results; {results['total']} total matches")
```

**Why Context Manager:**
- ✅ Pythonic (native `with` statement)
- ✅ Automatic timing capture (enter/exit)
- ✅ Graceful error handling (exceptions → step.error)
- ✅ Clear step boundaries with indentation

**Alternative Considered:** Decorator pattern - cleaner syntax but less flexible for dynamic reasoning

### Pydantic Data Models

**Core Models (100% General-Purpose)**

```python
from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime
from uuid import uuid4

class Step(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str
    name: str
    input: dict[str, Any]
    output: Optional[dict[str, Any]] = None
    reasoning: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)  # ← Extensible
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Literal["running", "completed", "failed"] = "running"
    error: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Trace(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    steps: list[Step] = []
    metadata: dict[str, Any] = Field(default_factory=dict)  # ← Extensible
    status: Literal["running", "completed", "failed"] = "running"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
```

**Convenience Helpers (Optional)**

```python
class StepContext:
    """Context manager for recording a step"""

    def set_input(self, data: dict[str, Any]):
        self.step.input = data

    def set_output(self, data: dict[str, Any]):
        self.step.output = data

    def set_reasoning(self, text: str):
        self.step.reasoning = text

    def set_metadata(self, data: dict[str, Any]):
        """Set arbitrary metadata (fully flexible)"""
        self.step.metadata.update(data)

    # ─────────────────────────────────────────────────────
    # CONVENIENCE HELPERS for common patterns
    # ─────────────────────────────────────────────────────

    def add_evaluation(
        self,
        item_id: str,
        item_data: dict[str, Any],
        filters: list[dict[str, Any]],
        qualified: bool,
        reasoning: Optional[str] = None
    ):
        """
        Helper for filter/evaluation steps.
        Sets metadata["evaluations"] in standard format.
        """
        if "evaluations" not in self.step.metadata:
            self.step.metadata["evaluations"] = []

        self.step.metadata["evaluations"].append({
            "item_id": item_id,
            "item_data": item_data,
            "filters": filters,
            "qualified": qualified,
            "reasoning": reasoning
        })

    def add_llm_metadata(
        self,
        model: str,
        tokens_used: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """Helper for LLM call steps."""
        self.step.metadata["llm"] = {
            "model": model,
            "tokens_used": tokens_used,
            "temperature": temperature,
            **kwargs
        }
```

**Why This Design:**
- Core models have zero domain assumptions
- `metadata` field accepts any JSON-serializable data
- Helpers are optional convenience methods
- Users can extend with custom helpers
- Industry standard pattern (OpenTelemetry, Sentry, DataDog)

### Error Handling with Context Managers

```python
class StepContext:
    def __enter__(self):
        self.step.status = "running"
        self.step.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.step.end_time = datetime.now()
        self.step.duration_ms = int(
            (self.step.end_time - self.step.start_time).total_seconds() * 1000
        )

        if exc_type is not None:
            self.step.status = "failed"
            self.step.error = str(exc_val)
        else:
            self.step.status = "completed"

        # Save step to storage
        self.storage.save_step(self.step)

        # Return False to propagate exception
        return False
```

---

## FastAPI Server

### API Endpoints (Read-Only)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DecisionTrace X-Ray API",
    description="API for debugging multi-step decision processes",
    version="1.0.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/traces", response_model=list[Trace])
async def list_traces(
    limit: int = 100,
    status: Optional[str] = None
):
    """
    List all traces with optional filtering.

    - **limit**: Maximum number of traces to return (default 100)
    - **status**: Filter by status (running, completed, failed)
    """
    traces = storage.get_all_traces(limit=limit, status=status)
    return traces

@app.get("/traces/{trace_id}", response_model=Trace)
async def get_trace(trace_id: str):
    """
    Get a specific trace by ID with all its steps.
    """
    trace = storage.get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace
```

**Why Read-Only API:**
- Demo app writes directly to SQLite (simpler)
- API only needs to serve dashboard (GET endpoints)
- FastAPI auto-generates Swagger docs at `/docs`
- Production could add POST endpoints for remote submission

---

## Frontend Architecture

### TypeScript Type Definitions

```typescript
// frontend/src/types/trace.ts

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
```

### Dashboard Pattern Detection

```typescript
// frontend/src/components/StepDetail.tsx

function StepDetail({ step }: { step: Step }) {
  // Detect known metadata patterns
  if (step.metadata?.evaluations && Array.isArray(step.metadata.evaluations)) {
    return <FilterResultsTable evaluations={step.metadata.evaluations} />;
  }

  if (step.metadata?.llm) {
    return <LLMCallView llmMetadata={step.metadata.llm} step={step} />;
  }

  // Fallback: generic JSON viewer for unknown patterns
  return <GenericStepView step={step} />;
}
```

### Dashboard Pages

#### 1. Trace List View
- Table of all traces
- Columns: ID, Name, Status, Start Time, Duration, # Steps
- Failed traces highlighted
- Click to drill down

#### 2. Trace Detail View
- Horizontal timeline of steps
- Click step to see details
- Visual status indicators
- Duration waterfall

#### 3. Step Detail View
- Input/output JSON viewers
- Reasoning display
- Metadata pattern detection (evaluations, LLM, etc.)
- Error display for failed steps

---

## Demo Application

### 3-Step Competitor Selection Pipeline

1. **Keyword Generation** (Mock LLM)
   - Input: Product title + category
   - Output: Search keywords
   - Mock: String manipulation + patterns

2. **Candidate Search** (Mock API)
   - Input: Search keyword
   - Output: 50 products (hardcoded fixtures)

3. **Filter & Select** (Business Logic)
   - Apply filters: Price (0.5x-2x), Rating (>3.8), Reviews (>100)
   - Rank by review count
   - Output: Top competitor

**Dummy Data:**
- 10-15 hardcoded products with varying attributes
- Edge cases: products that fail all/some filters
- Randomization for different executions

---

## Project Structure

```
decisiontraceX/
├── backend/
│   ├── decisiontrace/           # X-Ray SDK
│   │   ├── __init__.py
│   │   ├── models.py            # Pydantic models
│   │   ├── xray.py              # Context managers
│   │   └── storage/
│   │       ├── base.py          # Abstract interface
│   │       ├── memory.py        # In-memory
│   │       └── sqlite.py        # SQLite
│   │
│   ├── api/                     # FastAPI Server
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── traces.py
│   │   └── dependencies.py
│   │
│   ├── demo/                    # Demo App
│   │   ├── data/products.py
│   │   ├── steps/
│   │   │   ├── keywords.py
│   │   │   ├── search.py
│   │   │   └── filter.py
│   │   └── pipeline.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                    # React Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── TraceList.tsx
│   │   │   ├── TraceDetail.tsx
│   │   │   ├── StepTimeline.tsx
│   │   │   ├── StepDetail.tsx
│   │   │   ├── FilterResults.tsx
│   │   │   └── JSONViewer.tsx
│   │   ├── types/trace.ts
│   │   ├── hooks/useTraces.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   └── traces.db                # SQLite database
│
├── README.md
├── plan.md
└── .gitignore
```

---

## Implementation Plan

### Phase 1: SDK Core (90 mins)
1. Pydantic models (Trace, Step)
2. XRay class with context managers
3. SQLite storage implementation
4. Basic tests

**Output:** Working SDK that records and retrieves traces

### Phase 2: Demo Application (60 mins)
1. Dummy product data
2. Keyword generation (mock)
3. Candidate search (mock)
4. Filter & select logic
5. SDK integration
6. CLI runner

**Output:** Demo app generating realistic traces

### Phase 3: FastAPI Server (30 mins)
1. FastAPI app setup
2. CORS middleware
3. GET endpoints (`/traces`, `/traces/{id}`, `/health`)
4. Dependency injection for storage
5. Test with Swagger UI

**Output:** REST API with auto-docs

### Phase 4: Dashboard UI (120 mins)
1. Vite + React + TypeScript setup
2. Tailwind + shadcn/ui
3. TraceList component
4. TraceDetail with timeline
5. StepDetail with pattern detection
6. FilterResults table
7. JSONViewer component
8. React Router setup

**Output:** Working dashboard

### Phase 5: Polish & Documentation (30 mins)
1. README with setup instructions
2. End-to-end testing
3. Screenshots
4. Known limitations

### Phase 6: Video Walkthrough Script (30 mins)

**Script Structure (5-10 minutes):**

1. **Introduction (30 sec)**
   - Problem: Multi-step decisions are hard to debug
   - Solution: X-Ray system for decision transparency

2. **Architecture Overview (1 min)**
   - Show component diagram
   - Explain data flow: Demo → SDK → SQLite → API → Dashboard
   - Highlight metadata-based design

3. **SDK Demo (2 min)**
   - Show demo app code using SDK
   - Highlight context manager pattern
   - Show convenience helpers (`add_evaluation()`)
   - Explain general-purpose design via metadata

4. **Dashboard Walkthrough (3 min)**
   - Show trace list view
   - Drill into trace detail
   - Show step timeline
   - Show filter results table (pattern detection)
   - Highlight reasoning visibility

5. **Design Decisions (2 min)**
   - Why Context Manager over Decorator?
   - Why metadata over hardcoded fields?
   - Why SQLite over PostgreSQL?
   - Dashboard pattern detection approach

6. **Limitations & Future Work (1 min)**
   - No auth, real-time updates, trace comparison
   - Future: Search/filtering, visualizations, distributed tracing

7. **Conclusion (30 sec)**
   - Recap: General-purpose SDK + smart dashboard
   - Metadata-based extensibility = works for any workflow

**Total Time:** ~5.5-6 hours

---

## Key Design Decisions & Tradeoffs

### 1. SDK API: Context Manager Pattern

**Decision:** Context Manager (not decorator or manual)

**Tradeoffs:**
- ✅ Pythonic and automatic timing
- ✅ Graceful error handling
- ✅ Clear step boundaries
- ❌ Requires indentation

### 2. Data Schema: Flexible Metadata

**Decision:** `dict[str, Any]` for input/output/metadata (no strict schema)

**Tradeoffs:**
- ✅ Works with any data structure
- ✅ Zero boilerplate
- ✅ Easy integration
- ❌ No type safety for contents
- ❌ Dashboard must handle unknowns

**Mitigation:** Users can define their own Pydantic models if they want validation

### 3. Storage: SQLite with WAL Mode

**Decision:** SQLite over PostgreSQL or pure in-memory

**Tradeoffs:**
- ✅ Persistent, queryable, zero-config
- ✅ Easy for reviewers
- ❌ Not distributed
- ❌ File locking (mitigated by WAL mode)

### 4. Metadata-Based Patterns

**Decision:** Core models are general-purpose; helpers set metadata patterns

**Tradeoffs:**
- ✅ SDK works for any workflow
- ✅ Helpers are optional
- ✅ Dashboard detects patterns
- ❌ Dashboard needs pattern detection logic

**Why This Works:**
- Core `Step` has no domain-specific fields
- `add_evaluation()` sets `metadata["evaluations"]`
- Dashboard renders specialized views for known patterns
- Falls back to JSON viewer for unknown patterns
- Users can create custom helpers

---

## Decisions Made

### 1. Step ID Generation
**Decision:** UUID v4 (unique, portable, simple)

### 2. Storage Location
**Decision:** `./data/traces.db` (configurable via env var)

### 3. Data Retention
**Decision:** Keep all for demo; add cleanup script for production

### 4. Concurrency
**Decision:** SQLite WAL mode (simple config, good concurrency)

---

## Known Limitations & Future Improvements

### Out of Scope for Demo

1. **No Authentication** - Dashboard is public
2. **No Real-time Updates** - Must refresh for new traces
3. **No Trace Comparison** - Can't compare executions side-by-side
4. **Limited Querying** - No search by metadata or date range
5. **No Pagination** - Loading all traces (fine for demo)
6. **Single-Machine** - SQLite not distributed

### Future Enhancements

1. **Distributed Tracing** - Integrate with OpenTelemetry
2. **Trace Comparison UI** - Side-by-side diff view
3. **Search & Filtering** - By metadata, date, duration
4. **Visualizations** - Sankey diagrams, heatmaps, time-series
5. **Performance Analytics** - Aggregate stats, percentiles, anomaly detection
6. **Integration Helpers** - Langchain/LlamaIndex plugins
7. **Metadata Pattern Ecosystem** - Registry of standard patterns, community helpers
8. **SDK Improvements** - Sampling, async recording, nested traces

---

## Success Criteria

### Must Have (MVP)
- ✅ SDK records traces with <5 lines per step
- ✅ Dashboard shows trace list and detail views
- ✅ Dashboard renders filter results clearly
- ✅ Demo generates realistic traces
- ✅ End-to-end flow works
- ✅ Clean, readable code

### Nice to Have (Stretch)
- Search/filter in dashboard
- Trace comparison
- Export to JSON
- More visualizations
- >80% test coverage

---

## Dependencies

### Backend (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
pytest==7.4.3
httpx==0.25.1
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

---

## Conclusion

**Core Design Principle:**
The SDK is truly general-purpose through metadata-based extensions:
- Core models have zero domain assumptions
- `metadata` field accepts any JSON data
- Helpers are optional conveniences
- Dashboard detects patterns, falls back gracefully
- Industry standard approach (OpenTelemetry, Sentry)

**Key Success Factors:**
1. Metadata-based design = works for any workflow
2. Context managers = Pythonic and automatic
3. Pattern detection = smart dashboard without hardcoding
4. Scope discipline = MVP focus
5. Quality over quantity = 3 solid steps > 5 half-done

**Ready to implement!** 🚀
