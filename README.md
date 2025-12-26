# DecisionTrace X-Ray

An X-Ray debugging system for multi-step, non-deterministic algorithmic pipelines.

## Overview

DecisionTrace X-Ray provides transparency into complex decision processes by capturing and visualizing the complete decision trail. Unlike traditional tracing tools that focus on performance, X-Ray answers the question: **"Why did the system make this decision?"**

### Key Features

- **X-Ray SDK**: Lightweight Python library for capturing decision context
- **Context Manager API**: Pythonic interface with automatic timing and error handling
- **Metadata-Based Design**: General-purpose system that works with any workflow
- **Pattern Detection**: Smart dashboard that renders specialized views for common patterns
- **REST API**: FastAPI backend for querying traces
- **Interactive Dashboard**: React-based UI for exploring decision trails

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Installation

#### 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Setup Frontend

```bash
cd frontend
npm install
```

### Running the Demo

#### 1. Generate Sample Traces

Run the demo pipeline to generate sample traces:

```bash
cd backend
python -m demo.pipeline
```

This will:
- Execute a 4-step competitor selection workflow
- Write trace data to `data/traces.db`
- Display results in the terminal

#### 2. Start the API Server

In a new terminal:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

API will be available at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

#### 3. Start the Dashboard

In a new terminal:

```bash
cd frontend
npm run dev
```

Dashboard will be available at `http://localhost:5173`

### First Look

1. Open `http://localhost:5173`
2. You'll see a list of traces
3. Click "View Details" on any trace to see:
   - Execution timeline
   - Step-by-step breakdown
   - Filter evaluations
   - Decision reasoning

## Architecture

### System Components

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
```

### Tech Stack

**Backend:**
- **Python 3.10+**: SDK and demo application
- **Pydantic 2.5**: Data validation and serialization
- **FastAPI 0.104**: REST API server
- **SQLite**: Data storage with WAL mode

**Frontend:**
- **React 18**: UI framework
- **TypeScript 5**: Type safety
- **Vite 5**: Build tool and dev server
- **Tailwind CSS 3**: Styling

## Using the SDK

### Basic Usage

```python
from decisiontrace import XRay

# Initialize SDK
xray = XRay()

# Create a trace
with xray.trace("my-workflow") as trace:

    # Step 1: Some decision
    with trace.step("keyword_generation") as step:
        step.set_input({"query": "water bottle"})

        # Your business logic here
        keywords = generate_keywords("water bottle")

        step.set_output({"keywords": keywords})
        step.set_reasoning("Extracted key product attributes")

    # Step 2: Another decision
    with trace.step("search_products") as step:
        step.set_input({"keyword": keywords[0]})

        results = search_api(keywords[0])

        step.set_output({"count": len(results)})
        step.set_reasoning(f"Found {len(results)} matching products")

# Close SDK
xray.close()
```

### Advanced Features

#### Using Metadata Helpers

```python
# For LLM calls
with trace.step("llm_generation") as step:
    step.set_input({"prompt": "..."})

    result = call_llm(prompt)

    step.add_llm_metadata(
        model="gpt-4",
        tokens_used=150,
        temperature=0.7
    )
    step.set_output({"result": result})

# For filter/evaluation steps
with trace.step("apply_filters") as step:
    for candidate in candidates:
        filters = [
            {"name": "price", "passed": check_price(candidate), "detail": "..."},
            {"name": "rating", "passed": check_rating(candidate), "detail": "..."}
        ]

        step.add_evaluation(
            item_id=candidate["id"],
            item_data=candidate,
            filters=filters,
            qualified=all(f["passed"] for f in filters),
            reasoning="All filters passed" if qualified else "Failed price check"
        )
```

#### Custom Metadata

```python
with trace.step("custom_step") as step:
    # Set any custom metadata
    step.set_metadata({
        "algorithm": "collaborative_filtering",
        "threshold": 0.85,
        "num_neighbors": 10
    })
```

### Error Handling

The SDK automatically captures exceptions:

```python
with xray.trace("my-workflow") as trace:
    with trace.step("risky_operation") as step:
        step.set_input({"data": data})

        # If this raises an exception:
        # - Step status → "failed"
        # - Error message captured in step.error
        # - Trace status → "failed"
        # - Exception propagates normally
        result = risky_function(data)
```

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "service": "DecisionTrace X-Ray API"
}
```

### GET /api/traces
List all traces

**Query Parameters:**
- `limit` (int, default=100): Maximum number of traces
- `status` (string, optional): Filter by status (running|completed|failed)

**Response:**
```json
[
  {
    "trace_id": "uuid",
    "name": "competitor-selection-pipeline",
    "status": "completed",
    "steps": [...],
    ...
  }
]
```

### GET /api/traces/{trace_id}
Get a specific trace with all steps

**Response:**
```json
{
  "trace_id": "uuid",
  "name": "competitor-selection-pipeline",
  "status": "completed",
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:30:02",
  "duration_ms": 2150,
  "steps": [
    {
      "step_id": "uuid",
      "name": "keyword_generation",
      "input": {...},
      "output": {...},
      "reasoning": "...",
      "metadata": {...},
      "duration_ms": 450,
      "status": "completed"
    }
  ]
}
```

## Dashboard Features

### Trace List View
- Table of all traces
- Status indicators (completed, failed, running)
- Duration and step count
- Quick navigation

### Trace Detail View
- Visual timeline of steps
- Click to select and inspect each step
- Status indicators and duration
- Step-by-step navigation

### Step Detail View

**Pattern Detection:**
1. **Filter Evaluations**: Renders table showing which items passed/failed filters
2. **LLM Metadata**: Shows model, tokens, temperature in dedicated view
3. **Ranked Candidates**: Displays ranking results with scores
4. **Generic Fallback**: JSON viewer for unknown patterns

**Always Shows:**
- Input/Output data
- Reasoning text
- Error messages (for failed steps)
- Execution duration

## Demo Application

The demo implements a competitor product selection workflow:

1. **Keyword Generation** (mock LLM)
   - Extracts search keywords from product title
   - Simulates GPT-4 with string manipulation

2. **Candidate Search** (mock API)
   - Searches product database
   - Returns scored results

3. **Apply Filters** (business logic)
   - Price range: 0.5x - 2x of reference
   - Rating: minimum 3.8 stars
   - Reviews: minimum 100

4. **Rank & Select** (ranking algorithm)
   - Scores by review count, rating, price proximity
   - Selects best competitor

### Demo Data

The demo uses 20 hardcoded products with varying attributes to test:
- Products that pass all filters
- Products that fail specific filters
- Edge cases (too expensive, too cheap, low reviews, accessories, etc.)

## Project Structure

```
decisiontraceX/
├── backend/
│   ├── decisiontrace/           # X-Ray SDK
│   │   ├── models.py            # Pydantic models
│   │   ├── xray.py              # Context managers
│   │   └── storage/
│   │       ├── base.py          # Abstract interface
│   │       └── sqlite.py        # SQLite implementation
│   │
│   ├── api/                     # FastAPI Server
│   │   └── main.py
│   │
│   ├── demo/                    # Demo Application
│   │   ├── data/products.py    # Dummy data
│   │   ├── steps/              # Pipeline steps
│   │   └── pipeline.py         # Main runner
│   │
│   └── requirements.txt
│
├── frontend/                    # React Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── TraceList.tsx
│   │   │   ├── TraceDetail.tsx
│   │   │   └── StepDetail.tsx
│   │   ├── types/trace.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   └── package.json
│
├── data/                        # SQLite database
│   └── traces.db
│
└── README.md
```

## Design Decisions

### 1. Context Manager Pattern
**Why:** Pythonic, automatic timing, graceful error handling

**Alternatives Considered:** Decorator pattern (less flexible)

### 2. Metadata-Based Extensibility
**Why:** SDK works with any workflow, zero domain assumptions

**Tradeoffs:**
- ✅ Fully general-purpose
- ✅ Easy integration
- ❌ No compile-time validation of metadata contents

**Mitigation:** Users can define Pydantic models for their metadata

### 3. SQLite Storage
**Why:** Zero-config, persistent, queryable

**Tradeoffs:**
- ✅ Easy for reviewers
- ✅ Perfect for demo
- ❌ Not distributed

**Production Alternative:** PostgreSQL, TimescaleDB, or ClickHouse

### 4. Dashboard Pattern Detection
**Why:** Smart rendering without hardcoding domain logic

**How It Works:**
- SDK helpers set standard metadata patterns (e.g., `metadata["evaluations"]`)
- Dashboard detects patterns and renders specialized views
- Falls back to JSON viewer for unknown patterns
- Users can create custom helpers for their domains

## Known Limitations

### Out of Scope (Demo)
- Authentication/authorization
- Real-time updates (must refresh)
- Trace comparison (side-by-side diff)
- Advanced querying (search by metadata, date range)
- Pagination (loads all traces)
- Distributed tracing

### Future Enhancements
1. **Distributed Tracing**: Integrate with OpenTelemetry
2. **Trace Comparison**: Side-by-side diff view
3. **Search & Filtering**: By metadata, date, duration
4. **Visualizations**: Sankey diagrams, heatmaps
5. **Performance Analytics**: Aggregate stats, anomaly detection
6. **Integration Helpers**: Langchain/LlamaIndex plugins
7. **Sampling**: Configurable trace sampling rates
8. **Remote Submission**: POST API for remote trace submission

## Development

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### No traces showing in dashboard

1. Make sure you ran the demo pipeline:
   ```bash
   python backend/demo/pipeline.py
   ```

2. Check that the database file exists:
   ```bash
   ls -la data/traces.db
   ```

3. Verify API is running:
   ```bash
   curl http://localhost:8000/health
   ```

### CORS errors

Make sure the API server is running on port 8000 and the frontend on port 5173 (default ports in configuration).

### Database locked errors

SQLite uses WAL mode for better concurrency, but if you see locking errors, close other connections to the database.

## License

This is a demo project created for evaluation purposes.

## Contributing

This is a demo project and not currently accepting contributions.

---

**Built with ❤️ using Python, FastAPI, React, and TypeScript**
