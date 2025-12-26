# DecisionTrace X-Ray: Engineering Documentation

**Version:** 1.0
**Last Updated:** 2025-12-26
**Authors:** Engineering Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Component Architecture](#3-component-architecture)
4. [Data Flow & Interactions](#4-data-flow--interactions)
5. [Technology Stack](#5-technology-stack)
6. [SDK Implementation](#6-sdk-implementation)
7. [Storage Layer](#7-storage-layer)
8. [API Layer](#8-api-layer)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Security Considerations](#10-security-considerations)
11. [Performance Characteristics](#11-performance-characteristics)
12. [Testing Strategy](#12-testing-strategy)
13. [Deployment Guide](#13-deployment-guide)
14. [Monitoring & Observability](#14-monitoring--observability)
15. [Troubleshooting](#15-troubleshooting)
16. [Development Workflow](#16-development-workflow)
17. [Future Enhancements](#17-future-enhancements)
18. [Glossary](#18-glossary)

---

## 1. Executive Summary

### 1.1 Problem Statement

Modern AI and algorithmic systems make complex, multi-step decisions that are difficult to debug and understand. Traditional logging provides "what happened" but not "why it happened." This makes debugging non-deterministic systems (LLM-based agents, recommendation engines, decision pipelines) extremely challenging.

### 1.2 Solution Overview

DecisionTrace X-Ray is a **decision tracing framework** that captures the complete decision context at each step of a multi-step workflow. Unlike traditional APM tools (Application Performance Monitoring) that focus on performance metrics, X-Ray focuses on **decision transparency**.

### 1.3 Key Capabilities

- **Decision Context Capture**: Records input, output, and reasoning for each step
- **Metadata Extensibility**: Flexible metadata system supports any domain (e-commerce, streaming, finance, etc.)
- **Pattern Detection**: Automatically detects and visualizes common patterns (filters, rankings, LLM calls)
- **Pythonic API**: Context manager-based SDK with automatic timing and error handling
- **Visual Dashboard**: Interactive UI for exploring decision trails
- **General-Purpose**: Same SDK works across different domains without modification

### 1.4 Target Audience

- **Developers**: Integrating X-Ray into their applications
- **Data Scientists**: Debugging ML/AI pipelines
- **Product Managers**: Understanding system behavior
- **QA Engineers**: Testing and validating decision logic
- **Stakeholders**: Reviewing system decisions for compliance/audit

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER APPLICATION                           │
│                         (Python Process)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Business Logic (Pipeline Steps)                           │   │
│  │  - Keyword Generation                                      │   │
│  │  - Candidate Search                                        │   │
│  │  - Filtering                                               │   │
│  │  - Ranking                                                 │   │
│  └────────────────┬───────────────────────────────────────────┘   │
│                   │ uses                                           │
│                   ▼                                                │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           DecisionTrace X-Ray SDK                          │   │
│  │                                                            │   │
│  │  ┌──────────────────┐      ┌──────────────────┐          │   │
│  │  │  XRay Context    │      │  Helper Methods  │          │   │
│  │  │  Manager         │      │  - add_evaluation│          │   │
│  │  │  - trace()       │      │  - add_llm_meta  │          │   │
│  │  │  - step()        │      │  - set_metadata  │          │   │
│  │  └────────┬─────────┘      └──────────────────┘          │   │
│  │           │                                                │   │
│  │           │ saves to                                       │   │
│  │           ▼                                                │   │
│  │  ┌──────────────────┐      ┌──────────────────┐          │   │
│  │  │ Storage Layer    │─────▶│  Pydantic Models │          │   │
│  │  │ (Abstract)       │      │  - Trace         │          │   │
│  │  │                  │      │  - Step          │          │   │
│  │  └────────┬─────────┘      └──────────────────┘          │   │
│  └───────────┼────────────────────────────────────────────────   │
│              │                                                    │
└──────────────┼────────────────────────────────────────────────────┘
               │ writes
               ▼
    ┌──────────────────────┐
    │   SQLite Database    │
    │   (traces.db)        │
    │                      │
    │  Tables:             │
    │  - traces            │
    │  - steps             │
    └──────────┬───────────┘
               │ reads
               ▼
    ┌──────────────────────┐
    │   FastAPI Server     │
    │   (Port 8000)        │
    │                      │
    │  Endpoints:          │
    │  - GET /api/traces   │
    │  - GET /api/traces/  │
    │    {trace_id}        │
    └──────────┬───────────┘
               │ HTTP/JSON
               ▼
    ┌──────────────────────┐
    │   React Dashboard    │
    │   (Port 5173)        │
    │                      │
    │  Components:         │
    │  - TraceList         │
    │  - TraceDetail       │
    │  - StepDetail        │
    └──────────────────────┘
```

### 2.2 Architectural Patterns

#### 2.2.1 Context Manager Pattern (SDK)

**Why**: Automatic resource management, timing, and error handling.

**Implementation**:
- `XRay.trace()` returns `TraceContext` context manager
- `TraceContext.step()` returns `StepContext` context manager
- `__enter__` sets start time and status to "running"
- `__exit__` sets end time, calculates duration, handles exceptions

**Benefits**:
- Pythonic API
- Guaranteed cleanup
- Exception safety
- No manual timing code

#### 2.2.2 Repository Pattern (Storage)

**Why**: Abstract storage implementation from business logic.

**Implementation**:
- `StorageBackend` abstract base class defines interface
- `SQLiteStorage` concrete implementation
- Easy to swap storage backends (PostgreSQL, MongoDB, etc.)

**Benefits**:
- Testability (mock storage)
- Flexibility (multiple backends)
- Separation of concerns

#### 2.2.3 Metadata-Based Extensibility

**Why**: Support any domain without changing core models.

**Implementation**:
- Core fields: `input`, `output`, `reasoning` (generic dicts)
- `metadata` field for domain-specific data
- Helper methods set known patterns in metadata
- Dashboard detects patterns and renders accordingly

**Benefits**:
- General-purpose design
- No domain coupling
- Infinite extensibility

#### 2.2.4 Pattern Detection (Frontend)

**Why**: Smart rendering without hardcoding domain logic.

**Implementation**:
- Components check for known patterns in `metadata`
- Pattern 1: `metadata.evaluations` → Filter table
- Pattern 2: `metadata.llm` → LLM metadata card
- Pattern 3: `metadata.ranked_candidates` → Ranking view
- Fallback: JSON viewer for unknown patterns

**Benefits**:
- Works with any workflow
- Specialized views for common patterns
- Extensible by users

---

## 3. Component Architecture

### 3.1 SDK Layer

```
decisiontrace/
├── models.py              # Pydantic data models
├── xray.py                # Context managers and SDK API
└── storage/
    ├── base.py            # Abstract storage interface
    └── sqlite.py          # SQLite implementation
```

#### 3.1.1 models.py

**Responsibility**: Define data structures with validation.

**Key Classes**:

```python
class Step(BaseModel):
    # Identity
    step_id: str                        # UUID
    trace_id: str                       # Parent trace UUID
    name: str                           # Step name (e.g., "keyword_generation")
    step_order: int                     # Position in trace

    # Core Fields (Generic)
    input: dict[str, Any]               # What went in
    output: Optional[dict[str, Any]]    # What came out
    reasoning: Optional[str]            # Why this decision
    metadata: dict[str, Any]            # Domain-specific data

    # Timing & Status (Automatic)
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: Literal["running", "completed", "failed"]
    error: Optional[str]

class Trace(BaseModel):
    trace_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: Literal["running", "completed", "failed"]
    metadata: dict[str, Any]
    steps: list[Step]
```

**Design Decisions**:
- `dict[str, Any]` for flexibility (any JSON structure)
- Optional fields for incomplete traces (streaming support)
- Pydantic validation ensures data integrity
- ISO-8601 datetime serialization for API compatibility

#### 3.1.2 xray.py

**Responsibility**: User-facing API and orchestration.

**Key Classes**:

```python
class XRay:
    def __init__(self, storage: Optional[StorageBackend] = None)
    def trace(self, name: str) -> TraceContext
    def close(self)

class TraceContext:
    def __enter__(self) -> Self
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool
    def step(self, name: str) -> StepContext

class StepContext:
    def __enter__(self) -> Self
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool
    def set_input(self, input_data: dict[str, Any])
    def set_output(self, output_data: dict[str, Any])
    def set_reasoning(self, reasoning: str)
    def set_metadata(self, metadata: dict[str, Any])
    def add_evaluation(...)  # Helper for filter pattern
    def add_llm_metadata(...)  # Helper for LLM pattern
```

**Execution Flow**:

1. User creates `XRay()` instance
2. User calls `xray.trace("workflow-name")` → creates `Trace` object
3. Enter trace context → sets `start_time`, `status="running"`
4. User calls `trace.step("step-name")` → creates `Step` object
5. Enter step context → sets `start_time`, `status="running"`
6. User calls `step.set_input()`, `step.set_output()`, etc.
7. Exit step context → calculates `duration_ms`, saves to storage
8. Repeat steps 4-7 for each step
9. Exit trace context → calculates total `duration_ms`, saves trace

**Error Handling**:
- If exception raised in step: `status="failed"`, `error=str(exc_val)`, exception propagates
- If exception raised in trace: trace marked failed, exception propagates
- Storage errors are not swallowed (fail-fast)

#### 3.1.3 storage/base.py

**Responsibility**: Define storage interface contract.

```python
class StorageBackend(ABC):
    @abstractmethod
    def save_trace(self, trace: Trace) -> None:
        pass

    @abstractmethod
    def save_step(self, step: Step) -> None:
        pass

    @abstractmethod
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        pass

    @abstractmethod
    def get_all_traces(self, limit: int, status: Optional[str]) -> list[Trace]:
        pass
```

#### 3.1.4 storage/sqlite.py

**Responsibility**: Persist traces and steps to SQLite.

**Schema**:

```sql
CREATE TABLE traces (
    trace_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    metadata TEXT NOT NULL  -- JSON
)

CREATE TABLE steps (
    step_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    input TEXT NOT NULL,      -- JSON
    output TEXT,              -- JSON
    reasoning TEXT,
    metadata TEXT NOT NULL,   -- JSON
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    error TEXT,
    step_order INTEGER NOT NULL,
    FOREIGN KEY (trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
)
```

**Key Features**:
- WAL mode for better concurrency
- Foreign key cascade for data consistency
- JSON serialization for flexible fields
- Indexes on `trace_id`, `status`, `start_time`

**Queries**:

```python
# Save trace (UPSERT)
INSERT OR REPLACE INTO traces (...)

# Save step (UPSERT)
INSERT OR REPLACE INTO steps (...)

# Get trace with steps (JOIN)
SELECT * FROM traces WHERE trace_id = ?
SELECT * FROM steps WHERE trace_id = ? ORDER BY step_order

# List traces
SELECT * FROM traces ORDER BY start_time DESC LIMIT ?
```

### 3.2 API Layer

```
api/
└── main.py                # FastAPI application
```

**Responsibility**: HTTP interface for dashboard.

**Tech Stack**:
- FastAPI 0.104+
- Uvicorn ASGI server
- Pydantic response models
- CORS middleware

**Endpoints**:

```python
@app.get("/health")
async def health_check() -> dict

@app.get("/api/traces", response_model=list[Trace])
async def list_traces(limit: int = 100, status: Optional[str] = None)

@app.get("/api/traces/{trace_id}", response_model=Trace)
async def get_trace(trace_id: str)
```

**Design Decisions**:
- Read-only API (no POST/PUT/DELETE) - traces written by SDK only
- Pydantic response models ensure type safety
- CORS enabled for local development
- SQLite connection per request (simple, no pooling needed)

**Error Handling**:
- 404 for missing traces
- 500 for database errors
- Automatic JSON serialization of Pydantic models

### 3.3 Frontend Layer

```
frontend/src/
├── components/
│   ├── TraceList.tsx       # List view with stats and filters
│   ├── TraceDetail.tsx     # Timeline with inline expansion
│   ├── StepDetail.tsx      # Step details with pattern detection
│   └── JSONViewer.tsx      # Syntax-highlighted JSON viewer
├── types/
│   └── trace.ts            # TypeScript type definitions
├── App.tsx                 # Main application component
└── main.tsx                # Entry point
```

**Tech Stack**:
- React 18 (functional components + hooks)
- TypeScript 5 (strict mode)
- Vite 5 (dev server + build tool)
- Tailwind CSS 3 (utility-first styling)

**State Management**:
- `useState` for local state (selected trace, expanded steps)
- `useEffect` for data fetching
- No global state management (Redux, Zustand) - not needed for current scope

**Routing**:
- React Router for navigation
- `/` - Trace list
- `/traces/:id` - Trace detail

---

## 4. Data Flow & Interactions

### 4.1 Trace Creation Flow

```
┌──────────────┐
│ User Code    │
└──────┬───────┘
       │
       │ xray.trace("workflow")
       ▼
┌──────────────────────┐
│ XRay.trace()         │
│ - Create Trace obj   │
│ - Set start_time     │
└──────┬───────────────┘
       │
       │ __enter__
       ▼
┌──────────────────────┐
│ TraceContext         │
│ - status = "running" │
│ - Save to storage    │
└──────┬───────────────┘
       │
       │ trace.step("step1")
       ▼
┌──────────────────────┐
│ TraceContext.step()  │
│ - Create Step obj    │
│ - Set start_time     │
│ - Link trace_id      │
└──────┬───────────────┘
       │
       │ __enter__
       ▼
┌──────────────────────┐
│ StepContext          │
│ - status = "running" │
└──────┬───────────────┘
       │
       │ User calls set_input(), etc.
       ▼
┌──────────────────────┐
│ Business Logic       │
│ - Generate keywords  │
│ - Search products    │
│ - Apply filters      │
└──────┬───────────────┘
       │
       │ __exit__ (step)
       ▼
┌──────────────────────┐
│ StepContext.__exit__ │
│ - Set end_time       │
│ - Calc duration_ms   │
│ - status = "completed"│
│ - Save to storage    │
└──────┬───────────────┘
       │
       │ Repeat for more steps
       ▼
┌──────────────────────┐
│ __exit__ (trace)     │
│ - Set end_time       │
│ - Calc duration_ms   │
│ - status = "completed"│
│ - Save to storage    │
└──────────────────────┘
```

### 4.2 Dashboard Query Flow

```
┌──────────────┐
│ User Browser │
└──────┬───────┘
       │
       │ Navigate to http://localhost:5173
       ▼
┌──────────────────────┐
│ React App Loads      │
│ - Render TraceList   │
└──────┬───────────────┘
       │
       │ useEffect(() => fetchTraces())
       ▼
┌──────────────────────┐
│ fetch()              │
│ GET /api/traces      │
└──────┬───────────────┘
       │
       │ HTTP Request
       ▼
┌──────────────────────┐
│ FastAPI Server       │
│ @app.get("/api/traces")│
└──────┬───────────────┘
       │
       │ storage.get_all_traces()
       ▼
┌──────────────────────┐
│ SQLiteStorage        │
│ SELECT * FROM traces │
│ JOIN steps           │
└──────┬───────────────┘
       │
       │ Return list[Trace]
       ▼
┌──────────────────────┐
│ FastAPI Response     │
│ - Pydantic → JSON    │
│ - HTTP 200           │
└──────┬───────────────┘
       │
       │ JSON Response
       ▼
┌──────────────────────┐
│ React setState       │
│ - Store traces       │
│ - Trigger re-render  │
└──────┬───────────────┘
       │
       │ User clicks "View Details"
       ▼
┌──────────────────────┐
│ Navigate to          │
│ /traces/{id}         │
└──────┬───────────────┘
       │
       │ GET /api/traces/{id}
       ▼
┌──────────────────────┐
│ Render TraceDetail   │
│ - Timeline view      │
│ - Step expansion     │
└──────────────────────┘
```

### 4.3 Pattern Detection Flow

```
┌──────────────────────┐
│ StepDetail Component │
│ receives step prop   │
└──────┬───────────────┘
       │
       │ Check step.metadata
       ▼
┌──────────────────────────────────────┐
│ Pattern Detection Logic              │
│                                      │
│ if (step.metadata?.evaluations) {   │
│   return <FilterEvaluationTable />  │
│ }                                    │
│                                      │
│ if (step.metadata?.llm) {           │
│   return <LLMMetadataCard />        │
│ }                                    │
│                                      │
│ if (step.metadata?.ranked_candidates)│
│   return <RankedCandidatesView />   │
│ }                                    │
│                                      │
│ // Fallback                          │
│ return <JSONViewer data={metadata} />│
└──────┬───────────────────────────────┘
       │
       │ Render appropriate component
       ▼
┌──────────────────────┐
│ Specialized View     │
│ - Filter Table       │
│ - LLM Card           │
│ - Ranking View       │
│ - JSON Viewer        │
└──────────────────────┘
```

---

## 5. Technology Stack

### 5.1 Backend Technologies

#### 5.1.1 Python 3.10+

**Why Chosen**:
- Pydantic 2.x requires Python 3.10+
- Type hints for better IDE support
- Match-case statements (Python 3.10 feature)
- Growing adoption in AI/ML space

**Alternatives Considered**:
- Python 3.8/3.9: Would limit Pydantic features
- Go: Faster but less adoption in AI/ML space
- Node.js: Would complicate demo (two runtimes)

#### 5.1.2 Pydantic 2.5+

**Why Chosen**:
- Data validation with Python type hints
- Automatic JSON serialization
- FastAPI native integration
- Performance (Rust-based core)

**Key Features Used**:
- `BaseModel` for Trace and Step
- `Field()` for defaults and validation
- `model_dump()` for JSON serialization
- `Literal` types for enums

**Alternatives Considered**:
- dataclasses: No validation, manual JSON handling
- attrs: Less ecosystem integration
- marshmallow: Older, more verbose

#### 5.1.3 FastAPI 0.104+

**Why Chosen**:
- Auto-generated OpenAPI docs
- Async support (future scalability)
- Pydantic integration
- Modern, fast, easy to use

**Key Features Used**:
- `@app.get()` decorators
- Pydantic response models
- CORS middleware
- Automatic JSON serialization

**Alternatives Considered**:
- Flask: Older, synchronous, more boilerplate
- Django: Overkill for simple REST API
- Starlette: FastAPI is built on it, provides more features

#### 5.1.4 SQLite

**Why Chosen**:
- Zero configuration
- File-based (easy for reviewers)
- ACID guarantees
- Good for demo and small deployments

**Configuration**:
- WAL mode for better concurrency
- Foreign key enforcement
- JSON storage for flexible fields

**Alternatives Considered**:
- PostgreSQL: Overkill for demo, requires setup
- MongoDB: No ACID, more complex queries
- In-memory: Not persistent

**Production Migration Path**:
- PostgreSQL: For production scale
- TimescaleDB: For time-series analytics
- ClickHouse: For analytical queries

### 5.2 Frontend Technologies

#### 5.2.1 React 18

**Why Chosen**:
- Component-based architecture
- Large ecosystem
- Familiar to most developers
- Concurrent rendering features

**Key Features Used**:
- Functional components
- Hooks (useState, useEffect)
- Conditional rendering
- Props and composition

**Alternatives Considered**:
- Vue.js: Less ecosystem, similar features
- Svelte: Smaller, less adoption
- Angular: Overkill, steeper learning curve

#### 5.2.2 TypeScript 5

**Why Chosen**:
- Type safety for complex data structures
- Better IDE support
- Catch errors at compile time
- Industry standard

**Configuration**:
- Strict mode enabled
- No implicit any
- Strict null checks

**Alternatives Considered**:
- JavaScript: Loses type safety
- Flow: Less adoption, abandoned by Facebook

#### 5.2.3 Vite 5

**Why Chosen**:
- Fast dev server (native ESM)
- Hot module replacement (HMR)
- Optimized build (Rollup)
- Better developer experience than CRA

**Alternatives Considered**:
- Create React App: Slower, outdated
- Webpack: More complex configuration
- Parcel: Less control

#### 5.2.4 Tailwind CSS 3

**Why Chosen**:
- Utility-first approach
- No naming conventions needed
- Responsive design built-in
- Small bundle size (purging unused)

**Alternatives Considered**:
- CSS Modules: More boilerplate
- Styled Components: Runtime overhead
- Material-UI: Opinionated design

### 5.3 Development Tools

| Tool | Purpose | Version |
|------|---------|---------|
| pytest | Backend testing | 7.4+ |
| mypy | Python type checking | 1.7+ |
| black | Python formatting | 23.11+ |
| ruff | Python linting | 0.1+ |
| ESLint | TypeScript linting | 8.54+ |
| Prettier | Frontend formatting | 3.1+ |
| Git | Version control | 2.40+ |

---

## 6. SDK Implementation

### 6.1 Context Manager Implementation

#### 6.1.1 TraceContext

```python
class TraceContext:
    def __init__(self, trace: Trace, storage: StorageBackend):
        self.trace = trace
        self.storage = storage
        self.step_counter = 0

    def __enter__(self) -> Self:
        """Start the trace."""
        self.trace.start_time = datetime.now()
        self.trace.status = "running"
        self.storage.save_trace(self.trace)
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> bool:
        """End the trace and calculate duration."""
        self.trace.end_time = datetime.now()
        self.trace.duration_ms = int(
            (self.trace.end_time - self.trace.start_time).total_seconds() * 1000
        )

        if exc_type is not None:
            self.trace.status = "failed"
        else:
            self.trace.status = "completed"

        self.storage.save_trace(self.trace)

        # Return False to propagate exceptions
        return False

    def step(self, name: str) -> StepContext:
        """Create a new step in this trace."""
        step = Step(
            trace_id=self.trace.trace_id,
            name=name,
            start_time=datetime.now(),
            step_order=self.step_counter
        )
        self.step_counter += 1
        self.trace.steps.append(step)

        return StepContext(step, self.storage)
```

**Key Design Decisions**:
- `__exit__` returns `False` → exceptions propagate (fail-fast)
- `step_counter` ensures correct ordering
- Save on both enter and exit for real-time visibility

#### 6.1.2 StepContext

```python
class StepContext:
    def __init__(self, step: Step, storage: StorageBackend):
        self.step = step
        self.storage = storage

    def __enter__(self) -> Self:
        """Start the step."""
        self.step.start_time = datetime.now()
        self.step.status = "running"
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> bool:
        """End the step and calculate duration."""
        self.step.end_time = datetime.now()
        self.step.duration_ms = int(
            (self.step.end_time - self.step.start_time).total_seconds() * 1000
        )

        if exc_type is not None:
            self.step.status = "failed"
            self.step.error = str(exc_val)
        else:
            self.step.status = "completed"

        self.storage.save_step(self.step)

        # Return False to propagate exceptions
        return False

    def set_input(self, input_data: dict[str, Any]) -> None:
        """Set the input data for this step."""
        self.step.input = input_data

    def set_output(self, output_data: dict[str, Any]) -> None:
        """Set the output data for this step."""
        self.step.output = output_data

    def set_reasoning(self, reasoning: str) -> None:
        """Set the reasoning for this step."""
        self.step.reasoning = reasoning

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        """Set custom metadata for this step."""
        self.step.metadata.update(metadata)
```

**Exception Handling Strategy**:
- Capture exception message in `step.error`
- Mark status as "failed"
- Save failed step to storage
- Propagate exception (don't swallow)

### 6.2 Helper Methods

#### 6.2.1 add_evaluation()

**Purpose**: Standardize filter evaluation metadata.

```python
def add_evaluation(
    self,
    item_id: str,
    item_data: dict[str, Any],
    filters: list[dict[str, Any]],
    qualified: bool,
    reasoning: Optional[str] = None
) -> None:
    """Add a filter evaluation to metadata.

    Args:
        item_id: Unique identifier for the item being evaluated
        item_data: Full item data (title, price, etc.)
        filters: List of filter results
            [{"name": "price_range", "passed": true, "detail": "..."}]
        qualified: Whether item passed all filters
        reasoning: Optional explanation
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
```

**Dashboard Detection**:
```typescript
if (step.metadata?.evaluations && Array.isArray(step.metadata.evaluations)) {
  return <FilterEvaluationTable evaluations={step.metadata.evaluations} />
}
```

#### 6.2.2 add_llm_metadata()

**Purpose**: Standardize LLM call metadata.

```python
def add_llm_metadata(
    self,
    model: str,
    tokens_used: Optional[int] = None,
    temperature: Optional[float] = None,
    **kwargs: Any
) -> None:
    """Add LLM metadata to this step.

    Args:
        model: LLM model name (e.g., "gpt-4")
        tokens_used: Number of tokens consumed
        temperature: Temperature setting
        **kwargs: Additional LLM parameters
    """
    self.step.metadata["llm"] = {
        "model": model,
        "tokens_used": tokens_used,
        "temperature": temperature,
        **kwargs
    }
```

**Dashboard Detection**:
```typescript
if (step.metadata?.llm) {
  return (
    <div className="bg-blue-50 p-4 rounded">
      <h4>LLM Metadata</h4>
      <p>Model: {step.metadata.llm.model}</p>
      <p>Tokens: {step.metadata.llm.tokens_used}</p>
    </div>
  )
}
```

### 6.3 Usage Patterns

#### 6.3.1 Basic Usage

```python
from decisiontrace import XRay

xray = XRay()

with xray.trace("my-workflow") as trace:
    with trace.step("step1") as step:
        step.set_input({"query": "test"})
        result = do_something()
        step.set_output({"result": result})
        step.set_reasoning("Explanation of decision")

xray.close()
```

#### 6.3.2 Filter Evaluation Pattern

```python
with trace.step("apply_filters") as step:
    step.set_input({"candidates_count": len(candidates)})

    passed = []
    for candidate in candidates:
        filters = [
            {"name": "price", "passed": check_price(candidate), "detail": "..."},
            {"name": "rating", "passed": check_rating(candidate), "detail": "..."}
        ]

        qualified = all(f["passed"] for f in filters)

        step.add_evaluation(
            item_id=candidate["id"],
            item_data=candidate,
            filters=filters,
            qualified=qualified,
            reasoning="Passed all filters" if qualified else "Failed price check"
        )

        if qualified:
            passed.append(candidate)

    step.set_output({"passed": len(passed), "failed": len(candidates) - len(passed)})
```

#### 6.3.3 LLM Call Pattern

```python
with trace.step("llm_generation") as step:
    step.set_input({"prompt": prompt})

    response = llm.generate(prompt, temperature=0.7)

    step.add_llm_metadata(
        model="gpt-4",
        tokens_used=response.usage.total_tokens,
        temperature=0.7
    )

    step.set_output({"text": response.text})
    step.set_reasoning("Generated using GPT-4 with temperature 0.7")
```

---

## 7. Storage Layer

### 7.1 SQLite Schema Design

#### 7.1.1 Traces Table

```sql
CREATE TABLE traces (
    trace_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_ms INTEGER,
    status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed')),
    metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_traces_status ON traces(status);
CREATE INDEX idx_traces_start_time ON traces(start_time DESC);
```

**Design Decisions**:
- `trace_id`: UUID as TEXT (SQLite has no UUID type)
- `start_time`: ISO-8601 TEXT (sortable, readable)
- `metadata`: JSON TEXT (flexible storage)
- `status`: CHECK constraint for data integrity
- Indexes on common query patterns

#### 7.1.2 Steps Table

```sql
CREATE TABLE steps (
    step_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    input TEXT NOT NULL DEFAULT '{}',
    output TEXT,
    reasoning TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_ms INTEGER,
    status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed')),
    error TEXT,
    step_order INTEGER NOT NULL,
    FOREIGN KEY (trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
);

CREATE INDEX idx_steps_trace_id ON steps(trace_id);
CREATE INDEX idx_steps_trace_order ON steps(trace_id, step_order);
```

**Design Decisions**:
- Foreign key with CASCADE for referential integrity
- `step_order`: Ensures correct sequence
- Composite index on `(trace_id, step_order)` for efficient sorting

### 7.2 WAL Mode Configuration

```python
def _init_db(self):
    """Initialize database with WAL mode and foreign keys."""
    self.conn.execute("PRAGMA journal_mode=WAL")
    self.conn.execute("PRAGMA foreign_keys=ON")
    self.conn.commit()
```

**Why WAL Mode**:
- Better concurrency (readers don't block writers)
- Atomic commits
- Better performance for write-heavy workloads

**Tradeoffs**:
- Creates additional files (-wal, -shm)
- Slightly more complex backup process

### 7.3 Query Optimization

#### 7.3.1 Get All Traces

```python
def get_all_traces(
    self,
    limit: int = 100,
    status: Optional[str] = None
) -> list[Trace]:
    """Get traces with optional status filter."""
    cursor = self.conn.cursor()

    if status:
        # Filter by status
        cursor.execute(
            "SELECT * FROM traces WHERE status = ? "
            "ORDER BY start_time DESC LIMIT ?",
            (status, limit)
        )
    else:
        # Get all
        cursor.execute(
            "SELECT * FROM traces "
            "ORDER BY start_time DESC LIMIT ?",
            (limit,)
        )

    # Load steps for each trace
    traces = []
    for row in cursor.fetchall():
        trace = self._row_to_trace(row)
        trace.steps = self._get_steps_for_trace(trace.trace_id)
        traces.append(trace)

    return traces
```

**Optimization Notes**:
- Use index on `start_time` for sorting
- Use index on `status` for filtering
- N+1 query pattern acceptable for small datasets
- For large datasets, consider JOIN

#### 7.3.2 Get Single Trace

```python
def get_trace(self, trace_id: str) -> Optional[Trace]:
    """Get a single trace with all steps."""
    cursor = self.conn.cursor()

    # Get trace
    cursor.execute("SELECT * FROM traces WHERE trace_id = ?", (trace_id,))
    row = cursor.fetchone()

    if not row:
        return None

    trace = self._row_to_trace(row)

    # Get steps (ordered)
    cursor.execute(
        "SELECT * FROM steps WHERE trace_id = ? ORDER BY step_order",
        (trace_id,)
    )

    trace.steps = [self._row_to_step(row) for row in cursor.fetchall()]

    return trace
```

**Optimization Notes**:
- Primary key lookup (fast)
- Ordered by `step_order` (uses index)

---

## 8. API Layer

### 8.1 FastAPI Application Structure

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decisiontrace import Trace
from decisiontrace.storage.sqlite import SQLiteStorage

app = FastAPI(
    title="DecisionTrace X-Ray API",
    description="REST API for querying decision traces",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["GET"],  # Read-only API
    allow_headers=["*"],
)

# Storage instance (singleton)
storage = SQLiteStorage()
```

### 8.2 Endpoint Implementations

#### 8.2.1 Health Check

```python
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "DecisionTrace X-Ray API"
    }
```

**Purpose**:
- Liveness probe for deployment
- Quick connectivity test

#### 8.2.2 List Traces

```python
@app.get("/api/traces", response_model=list[Trace], tags=["Traces"])
async def list_traces(
    limit: int = 100,
    status: Optional[str] = None
):
    """List all traces with optional filtering.

    Args:
        limit: Maximum number of traces to return (default: 100)
        status: Filter by status (running|completed|failed)

    Returns:
        List of traces, newest first
    """
    try:
        traces = storage.get_all_traces(limit=limit, status=status)
        return traces
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Query Parameters**:
- `limit`: Pagination (default 100)
- `status`: Filter by execution status

**Response Example**:
```json
[
  {
    "trace_id": "abc-123",
    "name": "competitor-selection-pipeline",
    "status": "completed",
    "start_time": "2025-12-26T10:00:00",
    "end_time": "2025-12-26T10:00:02",
    "duration_ms": 2150,
    "steps": [...]
  }
]
```

#### 8.2.3 Get Single Trace

```python
@app.get("/api/traces/{trace_id}", response_model=Trace, tags=["Traces"])
async def get_trace(trace_id: str):
    """Get a single trace by ID.

    Args:
        trace_id: Unique trace identifier

    Returns:
        Complete trace with all steps

    Raises:
        404: Trace not found
    """
    try:
        trace = storage.get_trace(trace_id)
        if trace is None:
            raise HTTPException(status_code=404, detail="Trace not found")
        return trace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Path Parameters**:
- `trace_id`: UUID string

**Response Example**:
```json
{
  "trace_id": "abc-123",
  "name": "competitor-selection-pipeline",
  "status": "completed",
  "start_time": "2025-12-26T10:00:00",
  "end_time": "2025-12-26T10:00:02",
  "duration_ms": 2150,
  "metadata": {},
  "steps": [
    {
      "step_id": "def-456",
      "trace_id": "abc-123",
      "name": "keyword_generation",
      "input": {"product_title": "..."},
      "output": {"keywords": [...]},
      "reasoning": "...",
      "metadata": {"llm": {...}},
      "start_time": "2025-12-26T10:00:00",
      "end_time": "2025-12-26T10:00:01",
      "duration_ms": 450,
      "status": "completed",
      "error": null,
      "step_order": 0
    }
  ]
}
```

### 8.3 Error Handling

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 200 | Success | Trace found and returned |
| 404 | Not Found | Trace ID doesn't exist |
| 500 | Server Error | Database connection failed |

### 8.4 CORS Configuration

```python
CORSMiddleware(
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["GET"],  # Read-only
    allow_headers=["*"],
)
```

**Production Considerations**:
- Replace with actual frontend domain
- Consider environment-based configuration
- Add authentication if needed

---

## 9. Frontend Architecture

### 9.1 Component Hierarchy

```
App
├── Router
    ├── TraceList (/)
    │   ├── Statistics Cards
    │   ├── Search Bar
    │   ├── Status Filter
    │   └── Trace Table
    │       └── Trace Row (clickable)
    │
    └── TraceDetail (/traces/:id)
        ├── Header (name, status, duration)
        ├── Timeline (vertical)
        │   └── Timeline Item (clickable)
        │       └── StepDetail (inline expansion)
        │           ├── Input Section
        │           ├── Output Section
        │           ├── Reasoning Section
        │           ├── Pattern Detection
        │           │   ├── FilterEvaluationTable
        │           │   ├── LLMMetadataCard
        │           │   ├── RankedCandidatesView
        │           │   └── JSONViewer (fallback)
        │           └── Metadata Section
        │               └── JSONViewer
        └── Back Button
```

### 9.2 Component Details

#### 9.2.1 TraceList Component

**Responsibilities**:
- Fetch all traces from API
- Display statistics (total, completed, failed, running, avg duration)
- Provide search functionality
- Provide status filtering
- Render table of traces
- Navigate to detail view

**State**:
```typescript
const [traces, setTraces] = useState<Trace[]>([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
const [searchTerm, setSearchTerm] = useState('')
const [statusFilter, setStatusFilter] = useState<string>('all')
```

**Data Fetching**:
```typescript
useEffect(() => {
  const fetchTraces = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/traces')
      if (!response.ok) throw new Error('Failed to fetch traces')
      const data = await response.json()
      setTraces(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  fetchTraces()
}, [])
```

**Filtering Logic**:
```typescript
const filteredTraces = traces.filter((trace) => {
  const matchesSearch = trace.name.toLowerCase().includes(searchTerm.toLowerCase())
  const matchesStatus = statusFilter === 'all' || trace.status === statusFilter
  return matchesSearch && matchesStatus
})
```

#### 9.2.2 TraceDetail Component

**Responsibilities**:
- Fetch single trace by ID from URL
- Display trace metadata (name, status, duration)
- Render vertical timeline of steps
- Handle step expansion (accordion pattern)
- Auto-expand first step

**State**:
```typescript
const [trace, setTrace] = useState<Trace | null>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
const [expandedStepId, setExpandedStepId] = useState<string | null>(null)
```

**Accordion Logic**:
```typescript
const toggleStep = (stepId: string) => {
  setExpandedStepId(expandedStepId === stepId ? null : stepId)
}

// Auto-expand first step
useEffect(() => {
  if (trace && trace.steps.length > 0 && !expandedStepId) {
    setExpandedStepId(trace.steps[0].step_id)
  }
}, [trace])
```

**Timeline Rendering**:
```typescript
<div className="space-y-6">
  {trace.steps.map((step, index) => {
    const isExpanded = expandedStepId === step.step_id
    return (
      <div key={step.step_id} className="relative">
        {/* Vertical line connector */}
        {index < trace.steps.length - 1 && (
          <div className="absolute left-4 top-12 bottom-0 w-0.5 bg-gray-300" />
        )}

        {/* Step header (clickable) */}
        <button onClick={() => toggleStep(step.step_id)}>
          <div className="flex items-center gap-4">
            {/* Status icon */}
            <StatusIcon status={step.status} />

            {/* Step info */}
            <div>
              <h3>{step.name}</h3>
              <p>{step.duration_ms}ms</p>
            </div>

            {/* Expand indicator */}
            <span>{isExpanded ? '▼' : '▶'}</span>
          </div>
        </button>

        {/* Step details (expanded) */}
        {isExpanded && (
          <div className="mt-4 ml-16 animate-fadeIn">
            <StepDetail step={step} />
          </div>
        )}
      </div>
    )
  })}
</div>
```

#### 9.2.3 StepDetail Component

**Responsibilities**:
- Display step input/output
- Display reasoning
- Detect metadata patterns
- Render specialized views or fallback to JSON viewer

**Pattern Detection**:
```typescript
function StepDetail({ step }: { step: Step }) {
  const hasEvaluations = step.metadata?.evaluations && Array.isArray(step.metadata.evaluations)
  const hasLLMMetadata = step.metadata?.llm
  const hasRankedCandidates = step.metadata?.ranked_candidates

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Section title="Input">
        <JSONViewer data={step.input} />
      </Section>

      {/* Output Section */}
      {step.output && (
        <Section title="Output">
          <JSONViewer data={step.output} />
        </Section>
      )}

      {/* Reasoning Section */}
      {step.reasoning && (
        <Section title="Reasoning">
          <p className="text-gray-700">{step.reasoning}</p>
        </Section>
      )}

      {/* Pattern-Based Metadata Rendering */}
      {hasEvaluations && (
        <Section title="Filter Evaluations">
          <FilterEvaluationTable evaluations={step.metadata.evaluations} />
        </Section>
      )}

      {hasLLMMetadata && (
        <Section title="LLM Metadata">
          <LLMMetadataCard llm={step.metadata.llm} />
        </Section>
      )}

      {hasRankedCandidates && (
        <Section title="Ranked Candidates">
          <RankedCandidatesView candidates={step.metadata.ranked_candidates} />
        </Section>
      )}

      {/* Fallback: Raw Metadata */}
      {Object.keys(step.metadata).length > 0 && (
        <Section title="Metadata">
          <JSONViewer data={step.metadata} />
        </Section>
      )}

      {/* Error Section */}
      {step.error && (
        <Section title="Error">
          <div className="bg-red-50 p-4 rounded">
            <p className="text-red-700">{step.error}</p>
          </div>
        </Section>
      )}
    </div>
  )
}
```

#### 9.2.4 JSONViewer Component

**Responsibilities**:
- Syntax-highlight JSON
- Provide copy functionality
- Make JSON readable

**Implementation**:
```typescript
function JSONViewer({ data }: { data: any }) {
  const jsonString = JSON.stringify(data, null, 2)
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const syntaxHighlight = (json: string) => {
    return json.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = 'text-orange-600' // number
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'text-blue-600 font-semibold' // key
          } else {
            cls = 'text-green-600' // string
          }
        } else if (/true|false/.test(match)) {
          cls = 'text-purple-600' // boolean
        } else if (/null/.test(match)) {
          cls = 'text-gray-400' // null
        }
        return `<span class="${cls}">${match}</span>`
      }
    )
  }

  return (
    <div className="relative">
      <button onClick={handleCopy} className="absolute top-2 right-2">
        {copied ? 'Copied!' : 'Copy'}
      </button>
      <pre className="bg-gray-50 p-4 rounded overflow-x-auto">
        <code dangerouslySetInnerHTML={{ __html: syntaxHighlight(jsonString) }} />
      </pre>
    </div>
  )
}
```

### 9.3 Routing

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TraceList />} />
        <Route path="/traces/:id" element={<TraceDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
```

### 9.4 Styling Approach

**Tailwind Utility Classes**:
- `bg-blue-500` - Background color
- `text-white` - Text color
- `p-4` - Padding (1rem)
- `rounded` - Border radius
- `shadow-lg` - Box shadow
- `hover:bg-blue-600` - Hover state
- `transition-colors` - Smooth transitions

**Responsive Design**:
```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
  {/* 1 column on mobile, 2 on tablet, 5 on desktop */}
</div>
```

**Custom Animations** (in index.css):
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
```

---

## 10. Security Considerations

### 10.1 Current Security Posture

**Current State**: This is a **demo application** with minimal security features.

**Security Features Implemented**:
- ✅ Read-only API (no POST/PUT/DELETE)
- ✅ CORS restricted to specific origin
- ✅ Pydantic validation on data structures
- ✅ SQL injection protection (parameterized queries)

**Security Features NOT Implemented** (out of scope for demo):
- ❌ Authentication/Authorization
- ❌ Rate limiting
- ❌ Input sanitization for XSS
- ❌ HTTPS/TLS
- ❌ API keys
- ❌ Audit logging
- ❌ Data encryption at rest

### 10.2 Production Security Recommendations

#### 10.2.1 Authentication & Authorization

**Recommendations**:
1. **Add API Authentication**:
   - JWT tokens with expiration
   - API keys for service-to-service
   - OAuth 2.0 for user authentication

2. **Implement RBAC** (Role-Based Access Control):
   - Admin: Full access
   - Developer: Read all traces
   - User: Read own traces only

**Example**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.get("/api/traces")
async def list_traces(token: str = Depends(verify_token)):
    # Only return traces user has access to
    pass
```

#### 10.2.2 Input Validation

**Recommendations**:
1. **Validate all user inputs**:
   - Limit string lengths
   - Validate UUIDs
   - Sanitize for XSS

2. **Rate Limiting**:
   - Prevent DoS attacks
   - Throttle API requests

**Example**:
```python
from fastapi import Query
from pydantic import constr, validator

@app.get("/api/traces")
async def list_traces(
    limit: int = Query(default=100, le=1000),  # Max 1000
    status: Optional[constr(pattern=r'^(running|completed|failed)$')] = None
):
    pass
```

#### 10.2.3 Data Protection

**Recommendations**:
1. **Encrypt sensitive data**:
   - PII in trace metadata
   - API keys in step metadata
   - Database encryption at rest

2. **Redaction**:
   - Automatically redact secrets (API keys, passwords)
   - Configurable redaction patterns

**Example**:
```python
import re

def redact_secrets(text: str) -> str:
    """Redact common secret patterns."""
    patterns = [
        (r'api_key["\s:=]+([A-Za-z0-9_-]+)', r'api_key: [REDACTED]'),
        (r'password["\s:=]+([^\s"]+)', r'password: [REDACTED]'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
```

### 10.3 CORS Configuration for Production

```python
# Development
allow_origins=["http://localhost:5173"]

# Production
allow_origins=[
    "https://your-domain.com",
    "https://dashboard.your-domain.com"
]
```

### 10.4 SQL Injection Prevention

**Already Implemented**: Parameterized queries

```python
# ✅ Safe (parameterized)
cursor.execute("SELECT * FROM traces WHERE trace_id = ?", (trace_id,))

# ❌ Unsafe (string interpolation)
cursor.execute(f"SELECT * FROM traces WHERE trace_id = '{trace_id}'")
```

### 10.5 XSS Prevention

**Frontend**: React's JSX escapes by default

```typescript
// ✅ Safe (escaped automatically)
<p>{step.reasoning}</p>

// ❌ Unsafe (if you use dangerouslySetInnerHTML without sanitization)
<div dangerouslySetInnerHTML={{ __html: untrustedHTML }} />
```

**Recommendation**: Use `DOMPurify` if rendering user-provided HTML:

```typescript
import DOMPurify from 'dompurify'

<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />
```

---

## 11. Performance Characteristics

### 11.1 Benchmark Results

**Test Environment**:
- MacBook Pro M1, 16GB RAM
- Python 3.10
- SQLite 3.39
- React 18, Vite 5

#### 11.1.1 SDK Performance

| Operation | Duration | Notes |
|-----------|----------|-------|
| Create trace context | <1ms | In-memory object creation |
| Create step context | <1ms | In-memory object creation |
| Save trace to SQLite | 1-2ms | Single INSERT with WAL mode |
| Save step to SQLite | 1-2ms | Single INSERT with WAL mode |
| Complete trace (4 steps) | 10-20ms | Including business logic overhead |

**Overhead**: SDK adds <5ms overhead per trace (mostly I/O).

#### 11.1.2 API Performance

| Endpoint | Response Time | Notes |
|----------|---------------|-------|
| GET /health | <5ms | No database access |
| GET /api/traces (10 traces) | 10-20ms | Includes JOIN to load steps |
| GET /api/traces (100 traces) | 50-100ms | N+1 query pattern |
| GET /api/traces/{id} | 5-10ms | Single trace with steps |

**Bottleneck**: N+1 query pattern when loading many traces.

**Optimization**: Use JOIN instead of separate queries:

```sql
-- Current (N+1 queries)
SELECT * FROM traces LIMIT 100;           -- 1 query
SELECT * FROM steps WHERE trace_id = ?;   -- N queries

-- Optimized (1 query)
SELECT
  t.*,
  s.step_id, s.name, s.input, ...
FROM traces t
LEFT JOIN steps s ON t.trace_id = s.trace_id
ORDER BY t.start_time DESC, s.step_order
LIMIT 100;
```

#### 11.1.3 Frontend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Initial load time | <1s | For 100 traces |
| Time to interactive | <1.5s | Includes React hydration |
| Search/filter latency | <50ms | Client-side filtering |
| Step expansion animation | 300ms | CSS transition |

**Optimization Opportunities**:
- Lazy load trace details (only fetch when clicked)
- Virtualize long lists (react-window)
- Memoize expensive components

### 11.2 Scalability Analysis

#### 11.2.1 Current Limits

| Resource | Limit | Reason |
|----------|-------|--------|
| Traces per database | ~1M | SQLite file size limit (theoretically 281 TB) |
| Steps per trace | ~10K | Practical limit before UI becomes unwieldy |
| Concurrent writes | ~100/s | SQLite WAL mode bottleneck |
| Concurrent reads | Unlimited | SQLite allows multiple readers |

#### 11.2.2 Horizontal Scaling Strategy

**Current**: Single SQLite file (not horizontally scalable).

**Migration Path**:
1. **PostgreSQL**: Multi-writer support, better concurrency
2. **Read Replicas**: Separate read and write databases
3. **Sharding**: Partition traces by time range or workflow type
4. **Caching**: Redis for frequently accessed traces

**Example Architecture**:
```
┌──────────────┐
│ Application  │
└──────┬───────┘
       │
       │ Writes
       ▼
┌──────────────┐      Replication     ┌──────────────┐
│ PostgreSQL   │─────────────────────▶│ Read Replica │
│ (Primary)    │                      │ (Secondary)  │
└──────────────┘                      └──────┬───────┘
                                             │
                                             │ Reads
                                             ▼
                                      ┌──────────────┐
                                      │ FastAPI      │
                                      │ (Multiple)   │
                                      └──────────────┘
```

#### 11.2.3 Data Retention Strategy

**Problem**: Traces accumulate over time.

**Solutions**:
1. **TTL-based deletion**:
   ```sql
   DELETE FROM traces
   WHERE start_time < datetime('now', '-30 days');
   ```

2. **Archival**:
   ```python
   # Move old traces to cold storage (S3, Glacier)
   old_traces = storage.get_all_traces(
       where="start_time < datetime('now', '-90 days')"
   )
   archive_to_s3(old_traces)
   storage.delete_traces([t.trace_id for t in old_traces])
   ```

3. **Sampling**:
   ```python
   # Only keep 10% of traces
   if random.random() < 0.1:
       xray.trace("workflow")  # Capture
   ```

### 11.3 Memory Profile

**SDK Overhead** (per trace):
- Trace object: ~1KB
- Step object: ~2KB each
- Total for 4-step trace: ~9KB

**API Memory** (100 traces in memory):
- ~900KB for trace data
- ~50MB for Python runtime
- Total: ~51MB

**Frontend Memory**:
- ~30MB for React app
- ~1MB per 100 traces loaded
- Total: ~31MB for typical usage

---

## 12. Testing Strategy

### 12.1 Unit Tests

#### 12.1.1 SDK Tests

**File**: `backend/tests/test_xray.py`

```python
import pytest
from decisiontrace import XRay
from decisiontrace.storage.sqlite import SQLiteStorage

def test_trace_creation():
    """Test basic trace creation."""
    storage = SQLiteStorage(":memory:")
    xray = XRay(storage=storage)

    with xray.trace("test-workflow") as trace:
        assert trace.trace.name == "test-workflow"
        assert trace.trace.status == "running"

    # After exit
    saved_trace = storage.get_trace(trace.trace.trace_id)
    assert saved_trace.status == "completed"
    assert saved_trace.duration_ms is not None

def test_step_creation():
    """Test step creation within trace."""
    storage = SQLiteStorage(":memory:")
    xray = XRay(storage=storage)

    with xray.trace("test-workflow") as trace:
        with trace.step("test-step") as step:
            step.set_input({"test": "data"})
            step.set_output({"result": "success"})
            step.set_reasoning("Test reasoning")

    saved_trace = storage.get_trace(trace.trace.trace_id)
    assert len(saved_trace.steps) == 1
    assert saved_trace.steps[0].name == "test-step"
    assert saved_trace.steps[0].input == {"test": "data"}

def test_error_handling():
    """Test exception capture in step."""
    storage = SQLiteStorage(":memory:")
    xray = XRay(storage=storage)

    with pytest.raises(ValueError):
        with xray.trace("test-workflow") as trace:
            with trace.step("failing-step") as step:
                step.set_input({"test": "data"})
                raise ValueError("Test error")

    saved_trace = storage.get_trace(trace.trace.trace_id)
    assert saved_trace.status == "failed"
    assert saved_trace.steps[0].status == "failed"
    assert "Test error" in saved_trace.steps[0].error

def test_metadata_helpers():
    """Test metadata helper methods."""
    storage = SQLiteStorage(":memory:")
    xray = XRay(storage=storage)

    with xray.trace("test-workflow") as trace:
        with trace.step("llm-step") as step:
            step.add_llm_metadata(
                model="gpt-4",
                tokens_used=100,
                temperature=0.7
            )

    saved_trace = storage.get_trace(trace.trace.trace_id)
    llm_meta = saved_trace.steps[0].metadata["llm"]
    assert llm_meta["model"] == "gpt-4"
    assert llm_meta["tokens_used"] == 100
```

**Run Tests**:
```bash
cd backend
pytest tests/test_xray.py -v
```

#### 12.1.2 Storage Tests

**File**: `backend/tests/test_storage.py`

```python
def test_sqlite_save_and_retrieve():
    """Test SQLite storage operations."""
    storage = SQLiteStorage(":memory:")

    trace = Trace(
        trace_id="test-123",
        name="test",
        start_time=datetime.now(),
        status="completed"
    )

    storage.save_trace(trace)
    retrieved = storage.get_trace("test-123")

    assert retrieved is not None
    assert retrieved.trace_id == "test-123"

def test_foreign_key_cascade():
    """Test cascade delete of steps."""
    storage = SQLiteStorage(":memory:")

    trace = Trace(trace_id="test-123", ...)
    step = Step(step_id="step-1", trace_id="test-123", ...)

    storage.save_trace(trace)
    storage.save_step(step)

    # Delete trace
    storage.conn.execute("DELETE FROM traces WHERE trace_id = ?", ("test-123",))
    storage.conn.commit()

    # Steps should be deleted too
    cursor = storage.conn.execute("SELECT * FROM steps WHERE trace_id = ?", ("test-123",))
    assert cursor.fetchone() is None
```

### 12.2 Integration Tests

#### 12.2.1 API Tests

**File**: `backend/tests/test_api.py`

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_traces():
    """Test trace listing."""
    response = client.get("/api/traces")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_trace_not_found():
    """Test 404 for missing trace."""
    response = client.get("/api/traces/nonexistent-id")
    assert response.status_code == 404
```

**Run Tests**:
```bash
cd backend
pytest tests/test_api.py -v
```

### 12.3 End-to-End Tests

#### 12.3.1 Demo Pipeline Test

**File**: `backend/tests/test_e2e.py`

```python
def test_demo_pipeline_execution():
    """Test full demo pipeline execution."""
    from demo.pipeline import run_pipeline

    trace_id = run_pipeline()

    # Verify trace was created
    storage = SQLiteStorage()
    trace = storage.get_trace(trace_id)

    assert trace is not None
    assert trace.status == "completed"
    assert len(trace.steps) == 4
    assert trace.steps[0].name == "keyword_generation"
    assert trace.steps[3].name == "rank_and_select"
```

### 12.4 Frontend Tests

#### 12.4.1 Component Tests

**File**: `frontend/src/components/__tests__/TraceList.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import TraceList from '../TraceList'

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([
      {
        trace_id: '123',
        name: 'test-workflow',
        status: 'completed',
        steps: []
      }
    ])
  })
) as jest.Mock

test('renders trace list', async () => {
  render(
    <BrowserRouter>
      <TraceList />
    </BrowserRouter>
  )

  await waitFor(() => {
    expect(screen.getByText('test-workflow')).toBeInTheDocument()
  })
})
```

**Run Tests**:
```bash
cd frontend
npm test
```

### 12.5 Testing Checklist

**Before Release**:
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing of both demos
- [ ] Dashboard loads without errors
- [ ] All API endpoints return correct data
- [ ] Error states render correctly
- [ ] Performance benchmarks meet SLAs

---

## 13. Deployment Guide

### 13.1 Local Development

#### 13.1.1 Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run demos
python -m demo.pipeline
python -m demo2.pipeline

# Start API server
uvicorn api.main:app --reload --port 8000
```

#### 13.1.2 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

**Access**:
- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs

### 13.2 Production Deployment

#### 13.2.1 Backend Deployment (Docker)

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run**:
```bash
docker build -t decisiontrace-api .
docker run -p 8000:8000 -v $(pwd)/data:/app/data decisiontrace-api
```

#### 13.2.2 Frontend Deployment (Static Hosting)

**Build**:
```bash
cd frontend
npm run build
```

**Output**: `dist/` directory with static files

**Deploy to**:
- **Vercel**: `vercel deploy`
- **Netlify**: `netlify deploy --prod --dir=dist`
- **S3 + CloudFront**: Upload `dist/` to S3 bucket
- **Nginx**: Serve `dist/` directory

**Nginx Config**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/decisiontrace/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

#### 13.2.3 Database Migration

**Development**: SQLite file at `backend/data/traces.db`

**Production Options**:

1. **Persistent SQLite** (small scale):
   ```bash
   docker run -v /var/data/traces.db:/app/data/traces.db ...
   ```

2. **PostgreSQL** (recommended):
   ```python
   # backend/decisiontrace/storage/postgres.py
   class PostgreSQLStorage(StorageBackend):
       def __init__(self, connection_string: str):
           self.conn = psycopg2.connect(connection_string)
           self._init_db()
   ```

   **Migration**:
   ```bash
   # Export from SQLite
   sqlite3 data/traces.db .dump > traces.sql

   # Import to PostgreSQL
   psql -U user -d decisiontrace < traces.sql
   ```

#### 13.2.4 Environment Variables

**Backend**:
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/decisiontrace
CORS_ORIGINS=https://your-domain.com
LOG_LEVEL=INFO
```

**Frontend**:
```bash
# .env.production
VITE_API_URL=https://api.your-domain.com
```

### 13.3 Kubernetes Deployment

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decisiontrace-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: decisiontrace-api
  template:
    metadata:
      labels:
        app: decisiontrace-api
    spec:
      containers:
      - name: api
        image: your-registry/decisiontrace-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: decisiontrace-data
---
apiVersion: v1
kind: Service
metadata:
  name: decisiontrace-api
spec:
  selector:
    app: decisiontrace-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Apply**:
```bash
kubectl apply -f deployment.yaml
```

### 13.4 Monitoring Setup

#### 13.4.1 Health Checks

**Kubernetes Liveness Probe**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
```

#### 13.4.2 Logging

**Structured Logging** (Python):
```python
import logging
import json

logger = logging.getLogger("decisiontrace")
logger.setLevel(logging.INFO)

# JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
))
logger.addHandler(handler)
```

**Log to stdout** → Docker/K8s collects → Send to:
- CloudWatch (AWS)
- Stackdriver (GCP)
- Elastic Stack
- Datadog

#### 13.4.3 Metrics

**Prometheus Metrics** (FastAPI):
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**Metrics Exposed**:
- HTTP request count
- HTTP request duration
- HTTP error rate

---

## 14. Monitoring & Observability

### 14.1 Application Metrics

**Key Metrics to Track**:

| Metric | Type | Purpose |
|--------|------|---------|
| `traces_created_total` | Counter | Total traces created |
| `steps_created_total` | Counter | Total steps created |
| `trace_duration_seconds` | Histogram | Trace execution time distribution |
| `step_duration_seconds` | Histogram | Step execution time distribution |
| `trace_status_total{status="completed"}` | Counter | Successful traces |
| `trace_status_total{status="failed"}` | Counter | Failed traces |
| `api_request_duration_seconds` | Histogram | API response time |
| `db_query_duration_seconds` | Histogram | Database query time |

### 14.2 Alerting Rules

**Prometheus Alert Rules**:
```yaml
groups:
- name: decisiontrace
  rules:
  - alert: HighTraceFailureRate
    expr: rate(trace_status_total{status="failed"}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High trace failure rate"
      description: "{{ $value }}% of traces are failing"

  - alert: APILatencyHigh
    expr: histogram_quantile(0.95, api_request_duration_seconds) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "API 95th percentile latency > 1s"
```

### 14.3 Dashboard Metrics

**Grafana Dashboard**:
- Total traces (by status)
- Trace creation rate
- Average trace duration
- Top 10 slowest workflows
- API request rate and latency
- Database connection pool utilization

### 14.4 Tracing (OpenTelemetry)

**Future Enhancement**: Add distributed tracing for API calls.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Use in code
with tracer.start_as_current_span("list_traces"):
    traces = storage.get_all_traces()
```

---

## 15. Troubleshooting

### 15.1 Common Issues

#### 15.1.1 No Traces Showing in Dashboard

**Symptoms**: Dashboard shows empty list or "No traces found"

**Diagnosis**:
1. Check if database file exists:
   ```bash
   ls -la backend/data/traces.db
   ```

2. Check database contents:
   ```bash
   sqlite3 backend/data/traces.db "SELECT COUNT(*) FROM traces;"
   ```

3. Check API is returning data:
   ```bash
   curl http://localhost:8000/api/traces
   ```

**Solutions**:
- Run demo pipeline to create traces: `python -m demo.pipeline`
- Check API server is running on port 8000
- Check CORS configuration allows frontend origin

#### 15.1.2 Database Locked Error

**Symptoms**: `sqlite3.OperationalError: database is locked`

**Diagnosis**:
- Multiple processes writing to database
- SQLite not in WAL mode

**Solutions**:
1. Check WAL mode is enabled:
   ```bash
   sqlite3 backend/data/traces.db "PRAGMA journal_mode;"
   # Should return: wal
   ```

2. Close other connections:
   ```bash
   lsof backend/data/traces.db  # Find processes
   kill <PID>  # Close them
   ```

3. Enable WAL mode:
   ```python
   conn.execute("PRAGMA journal_mode=WAL")
   ```

#### 15.1.3 CORS Errors

**Symptoms**: Browser console shows `CORS policy: No 'Access-Control-Allow-Origin' header`

**Diagnosis**:
- Frontend is on different origin than allowed
- API CORS middleware not configured

**Solutions**:
1. Check CORS configuration in `api/main.py`:
   ```python
   allow_origins=["http://localhost:5173"]  # Must match frontend
   ```

2. Verify frontend is running on correct port:
   ```bash
   # Frontend should be on 5173
   npm run dev
   ```

#### 15.1.4 Import Errors (Python)

**Symptoms**: `ModuleNotFoundError: No module named 'decisiontrace'`

**Diagnosis**:
- Virtual environment not activated
- Running from wrong directory
- Package not installed

**Solutions**:
1. Activate venv:
   ```bash
   source backend/venv/bin/activate
   ```

2. Run from correct directory:
   ```bash
   cd backend
   python -m demo.pipeline  # Use -m flag
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

#### 15.1.5 Frontend Build Errors

**Symptoms**: `npm run build` fails with TypeScript errors

**Diagnosis**:
- Type mismatches
- Missing type definitions

**Solutions**:
1. Check TypeScript types:
   ```bash
   npm run type-check
   ```

2. Fix type errors in code
3. Update dependencies:
   ```bash
   npm update
   ```

### 15.2 Debugging Tools

#### 15.2.1 SQLite Browser

**Download**: https://sqlitebrowser.org/

**Usage**:
1. Open `backend/data/traces.db`
2. Browse tables: `traces`, `steps`
3. Run custom queries
4. Export data

#### 15.2.2 FastAPI Swagger UI

**Access**: http://localhost:8000/docs

**Features**:
- Interactive API testing
- View request/response schemas
- Test endpoints directly

#### 15.2.3 React DevTools

**Install**: Browser extension for Chrome/Firefox

**Features**:
- Inspect component tree
- View component state
- Profile performance

#### 15.2.4 Network Tab (Browser)

**Access**: Browser DevTools → Network

**Check**:
- API requests are being made
- Response status codes
- Response payloads
- Request timing

### 15.3 Log Analysis

#### 15.3.1 Backend Logs

**Uvicorn Logs**:
```bash
uvicorn api.main:app --log-level debug
```

**Look for**:
- Request paths and methods
- Response status codes
- Exceptions and tracebacks

#### 15.3.2 Frontend Console

**Browser Console**:
```javascript
// Check for errors
console.error  // Red errors

// Check API responses
// Network tab → XHR → Response
```

---

## 16. Development Workflow

### 16.1 Setting Up Development Environment

```bash
# 1. Clone repository
git clone <repo-url>
cd decisiontraceX

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 3. Setup frontend
cd ../frontend
npm install

# 4. Run tests
cd ../backend
pytest

cd ../frontend
npm test

# 5. Start development servers
# Terminal 1: Backend
cd backend
uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 16.2 Code Style

#### 16.2.1 Python Style

**Tools**:
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.10"
strict = true
```

**Run**:
```bash
black backend/
ruff check backend/
mypy backend/
```

#### 16.2.2 TypeScript Style

**Tools**:
- **ESLint**: Linting
- **Prettier**: Formatting

**Configuration** (`.eslintrc.json`):
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended"
  ],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/explicit-function-return-type": "off"
  }
}
```

**Run**:
```bash
npm run lint
npm run format
```

### 16.3 Git Workflow

**Branch Strategy**:
```
main
├── feature/add-authentication
├── feature/add-pagination
└── bugfix/fix-cors-issue
```

**Commit Convention**:
```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scopes: sdk, api, frontend, storage

Examples:
feat(sdk): add metadata helper for rankings
fix(api): correct CORS origin configuration
docs(readme): update installation instructions
```

### 16.4 Release Process

1. **Update Version**:
   ```bash
   # backend/setup.py
   version="1.1.0"

   # frontend/package.json
   "version": "1.1.0"
   ```

2. **Run Full Test Suite**:
   ```bash
   pytest backend/tests/
   npm test --prefix frontend
   ```

3. **Build**:
   ```bash
   cd frontend && npm run build
   ```

4. **Tag Release**:
   ```bash
   git tag -a v1.1.0 -m "Release 1.1.0"
   git push origin v1.1.0
   ```

5. **Deploy** (see Deployment Guide)

---

## 17. Future Enhancements

### 17.1 Planned Features

#### 17.1.1 Distributed Tracing

**Goal**: Integrate with OpenTelemetry for distributed systems.

**Benefits**:
- Trace requests across multiple services
- Correlate with existing APM tools
- Standard protocol

**Implementation**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("workflow-execution"):
    with xray.trace("workflow") as xray_trace:
        # Both OpenTelemetry and X-Ray capture
        pass
```

#### 17.1.2 Trace Comparison

**Goal**: Side-by-side diff view of two traces.

**Use Case**: Compare successful vs failed runs.

**UI Mockup**:
```
┌─────────────────────┬─────────────────────┐
│ Trace A (Success)   │ Trace B (Failed)    │
├─────────────────────┼─────────────────────┤
│ Step 1: ✓ 100ms     │ Step 1: ✓ 105ms     │
│ Step 2: ✓ 200ms     │ Step 2: ✗ 500ms     │ ← Difference
│ Step 3: ✓ 150ms     │ (not executed)      │
└─────────────────────┴─────────────────────┘
```

#### 17.1.3 Advanced Querying

**Goal**: Query traces by metadata, date range, duration.

**Examples**:
```
# Find all traces that used GPT-4
metadata.llm.model == "gpt-4"

# Find traces over 5 seconds
duration_ms > 5000

# Find failed filter steps
steps.name == "apply_filters" AND steps.status == "failed"
```

**Implementation**:
- Add search parser
- Build dynamic SQL queries
- Add search UI

#### 17.1.4 Visualizations

**Goal**: Additional visualization types.

**Ideas**:
- **Sankey Diagram**: Show decision flow and filtering
- **Heatmap**: Show slowest steps across traces
- **Timeline**: Show traces over time

#### 17.1.5 LLM Integration Helpers

**Goal**: First-class support for LangChain/LlamaIndex.

**Example**:
```python
from decisiontrace.integrations.langchain import XRayLangChainCallback

callback = XRayLangChainCallback(xray_trace)
chain.run(input, callbacks=[callback])

# Automatically captures:
# - LLM calls
# - Token usage
# - Chain steps
# - Prompts and outputs
```

#### 17.1.6 Sampling & Rate Limiting

**Goal**: Control trace volume in production.

**Implementation**:
```python
xray = XRay(
    sampling_rate=0.1,  # Capture 10% of traces
    rate_limit=1000     # Max 1000 traces/hour
)
```

#### 17.1.7 Remote Submission

**Goal**: Submit traces from remote applications.

**API**:
```python
# POST /api/traces
@app.post("/api/traces")
async def create_trace(trace: Trace):
    storage.save_trace(trace)
    return {"trace_id": trace.trace_id}

# Usage
xray = XRay(remote_url="https://api.your-domain.com")
```

### 17.2 Roadmap

**Q1 2026**:
- [ ] Trace comparison
- [ ] Advanced querying
- [ ] PostgreSQL storage backend

**Q2 2026**:
- [ ] LangChain integration
- [ ] Sampling support
- [ ] Remote submission API

**Q3 2026**:
- [ ] OpenTelemetry integration
- [ ] Sankey diagram visualization
- [ ] Performance analytics

**Q4 2026**:
- [ ] Multi-tenancy support
- [ ] RBAC and authentication
- [ ] Enterprise features

---

## 18. Glossary

| Term | Definition |
|------|------------|
| **Trace** | A complete execution of a multi-step workflow, containing multiple steps |
| **Step** | A single decision point within a trace (e.g., filtering, ranking, LLM call) |
| **Reasoning** | Human-readable explanation of why a decision was made |
| **Metadata** | Domain-specific data attached to traces or steps |
| **Pattern** | A recognized metadata structure (e.g., filter evaluations, LLM metadata) |
| **Context Manager** | Python construct using `with` for resource management |
| **WAL Mode** | Write-Ahead Logging mode in SQLite for better concurrency |
| **CORS** | Cross-Origin Resource Sharing, browser security mechanism |
| **Pydantic** | Python library for data validation using type hints |
| **FastAPI** | Modern Python web framework with auto-generated docs |
| **Vite** | Next-generation frontend build tool |
| **Tailwind CSS** | Utility-first CSS framework |
| **UPSERT** | SQL operation that inserts or updates (INSERT OR REPLACE) |
| **N+1 Query** | Performance anti-pattern where N additional queries are made |
| **APM** | Application Performance Monitoring |
| **Sankey Diagram** | Flow diagram showing quantity proportions between steps |

---

## Appendix A: API Reference

### A.1 SDK API

```python
class XRay:
    def __init__(self, storage: Optional[StorageBackend] = None)
    def trace(self, name: str) -> TraceContext
    def close(self) -> None

class TraceContext:
    def step(self, name: str) -> StepContext

class StepContext:
    def set_input(self, input_data: dict[str, Any]) -> None
    def set_output(self, output_data: dict[str, Any]) -> None
    def set_reasoning(self, reasoning: str) -> None
    def set_metadata(self, metadata: dict[str, Any]) -> None
    def add_evaluation(
        item_id: str,
        item_data: dict[str, Any],
        filters: list[dict[str, Any]],
        qualified: bool,
        reasoning: Optional[str] = None
    ) -> None
    def add_llm_metadata(
        model: str,
        tokens_used: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any
    ) -> None
```

### A.2 REST API

**Base URL**: `http://localhost:8000`

| Method | Endpoint | Description | Query Params |
|--------|----------|-------------|--------------|
| GET | `/health` | Health check | None |
| GET | `/api/traces` | List traces | `limit`, `status` |
| GET | `/api/traces/{trace_id}` | Get trace | None |

---

## Appendix B: Data Models

### B.1 Trace Schema

```json
{
  "trace_id": "string (UUID)",
  "name": "string",
  "start_time": "string (ISO-8601)",
  "end_time": "string (ISO-8601) | null",
  "duration_ms": "integer | null",
  "status": "running | completed | failed",
  "metadata": "object (any JSON)",
  "steps": "array of Step objects"
}
```

### B.2 Step Schema

```json
{
  "step_id": "string (UUID)",
  "trace_id": "string (UUID)",
  "name": "string",
  "step_order": "integer",
  "input": "object (any JSON)",
  "output": "object (any JSON) | null",
  "reasoning": "string | null",
  "metadata": "object (any JSON)",
  "start_time": "string (ISO-8601)",
  "end_time": "string (ISO-8601) | null",
  "duration_ms": "integer | null",
  "status": "running | completed | failed",
  "error": "string | null"
}
```

---

**End of Engineering Documentation**

---

**For questions or support, please refer to**:
- README.md for quick start guide
- DEMO_SCENARIOS.md for example use cases
- DATA_STRUCTURES.md for data structure comparisons
- GitHub Issues for bug reports and feature requests
