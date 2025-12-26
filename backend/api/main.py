"""
FastAPI server for DecisionTrace X-Ray system.

Provides REST API for querying traces and steps.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import decisiontrace
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decisiontrace import SQLiteStorage
from decisiontrace.models import Trace

# Initialize storage
storage = SQLiteStorage()

# Create FastAPI app
app = FastAPI(
    title="DecisionTrace X-Ray API",
    description="API for debugging multi-step decision processes",
    version="1.0.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "DecisionTrace X-Ray API"}


@app.get("/api/traces", response_model=list[Trace])
async def list_traces(
    limit: int = 100,
    status: Optional[str] = None
):
    """
    List all traces with optional filtering.

    - **limit**: Maximum number of traces to return (default 100)
    - **status**: Filter by status (running, completed, failed)
    """
    try:
        traces = storage.get_all_traces(limit=limit, status=status)
        return traces
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/traces/{trace_id}", response_model=Trace)
async def get_trace(trace_id: str):
    """
    Get a specific trace by ID with all its steps.
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


@app.on_event("shutdown")
def shutdown_event():
    """Close storage on shutdown."""
    storage.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
