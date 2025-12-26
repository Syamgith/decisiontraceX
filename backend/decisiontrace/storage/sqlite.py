"""
SQLite storage backend for DecisionTrace X-Ray system.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .base import StorageBackend
from ..models import Trace, Step


class SQLiteStorage(StorageBackend):
    """SQLite implementation of storage backend."""

    def __init__(self, db_path: str = "./data/traces.db"):
        """Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")

        # Create traces table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_ms INTEGER,
                metadata TEXT,
                status TEXT CHECK(status IN ('running', 'completed', 'failed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_traces_status ON traces(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_traces_created_at ON traces(created_at DESC)
        """)

        # Create steps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                step_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                input TEXT,
                output TEXT,
                reasoning TEXT,
                metadata TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_ms INTEGER,
                status TEXT CHECK(status IN ('running', 'completed', 'failed')),
                error TEXT,
                step_order INTEGER,
                FOREIGN KEY (trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_steps_trace_id ON steps(trace_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_steps_order ON steps(trace_id, step_order)
        """)

        self.conn.commit()

    def save_trace(self, trace: Trace) -> None:
        """Save or update a trace."""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO traces (
                trace_id, name, start_time, end_time, duration_ms, metadata, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            trace.trace_id,
            trace.name,
            trace.start_time.isoformat() if trace.start_time else None,
            trace.end_time.isoformat() if trace.end_time else None,
            trace.duration_ms,
            json.dumps(trace.metadata),
            trace.status
        ))

        self.conn.commit()

    def save_step(self, step: Step) -> None:
        """Save or update a step."""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO steps (
                step_id, trace_id, name, input, output, reasoning, metadata,
                start_time, end_time, duration_ms, status, error, step_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            step.step_id,
            step.trace_id,
            step.name,
            json.dumps(step.input),
            json.dumps(step.output) if step.output else None,
            step.reasoning,
            json.dumps(step.metadata),
            step.start_time.isoformat() if step.start_time else None,
            step.end_time.isoformat() if step.end_time else None,
            step.duration_ms,
            step.status,
            step.error,
            step.step_order
        ))

        self.conn.commit()

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID with all its steps."""
        cursor = self.conn.cursor()

        # Get trace
        cursor.execute("""
            SELECT * FROM traces WHERE trace_id = ?
        """, (trace_id,))

        trace_row = cursor.fetchone()
        if not trace_row:
            return None

        # Get steps for this trace
        cursor.execute("""
            SELECT * FROM steps WHERE trace_id = ? ORDER BY step_order ASC
        """, (trace_id,))

        step_rows = cursor.fetchall()

        # Convert rows to models
        trace = Trace(
            trace_id=trace_row["trace_id"],
            name=trace_row["name"],
            start_time=datetime.fromisoformat(trace_row["start_time"]),
            end_time=datetime.fromisoformat(trace_row["end_time"]) if trace_row["end_time"] else None,
            duration_ms=trace_row["duration_ms"],
            metadata=json.loads(trace_row["metadata"]) if trace_row["metadata"] else {},
            status=trace_row["status"],
            steps=[
                Step(
                    step_id=row["step_id"],
                    trace_id=row["trace_id"],
                    name=row["name"],
                    input=json.loads(row["input"]) if row["input"] else {},
                    output=json.loads(row["output"]) if row["output"] else None,
                    reasoning=row["reasoning"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                    duration_ms=row["duration_ms"],
                    status=row["status"],
                    error=row["error"],
                    step_order=row["step_order"]
                )
                for row in step_rows
            ]
        )

        return trace

    def get_all_traces(self, limit: int = 100, status: Optional[str] = None) -> list[Trace]:
        """Get all traces with optional filtering."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM traces"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        trace_rows = cursor.fetchall()

        # Load each trace with its steps
        traces = []
        for row in trace_rows:
            trace = self.get_trace(row["trace_id"])
            if trace:
                traces.append(trace)

        return traces

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
