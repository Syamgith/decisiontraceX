"""
XRay SDK for capturing decision traces.

Context manager pattern provides Pythonic API with automatic timing.
"""

from datetime import datetime
from typing import Any, Optional
from contextlib import contextmanager

from .models import Trace, Step
from .storage.base import StorageBackend
from .storage.sqlite import SQLiteStorage


class StepContext:
    """Context manager for recording a step."""

    def __init__(self, step: Step, storage: StorageBackend, trace: "TraceContext"):
        self.step = step
        self.storage = storage
        self.trace = trace

    def set_input(self, data: dict[str, Any]) -> None:
        """Set step input data."""
        self.step.input = data

    def set_output(self, data: dict[str, Any]) -> None:
        """Set step output data."""
        self.step.output = data

    def set_reasoning(self, text: str) -> None:
        """Set reasoning for this step's decision."""
        self.step.reasoning = text

    def set_metadata(self, data: dict[str, Any]) -> None:
        """Set arbitrary metadata (fully flexible)."""
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
    ) -> None:
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
    ) -> None:
        """Helper for LLM call steps."""
        self.step.metadata["llm"] = {
            "model": model,
            "tokens_used": tokens_used,
            "temperature": temperature,
            **kwargs
        }

    def __enter__(self):
        """Start step execution."""
        self.step.status = "running"
        self.step.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete step execution."""
        self.step.end_time = datetime.now()
        self.step.duration_ms = int(
            (self.step.end_time - self.step.start_time).total_seconds() * 1000
        )

        if exc_type is not None:
            self.step.status = "failed"
            self.step.error = str(exc_val)
            self.trace.trace.status = "failed"  # Mark trace as failed too
        else:
            self.step.status = "completed"

        # Save step to storage
        self.storage.save_step(self.step)

        # Update trace
        self.storage.save_trace(self.trace.trace)

        # Return False to propagate exception
        return False


class TraceContext:
    """Context manager for recording a trace."""

    def __init__(self, trace: Trace, storage: StorageBackend):
        self.trace = trace
        self.storage = storage
        self._step_counter = 0

    def step(self, name: str) -> StepContext:
        """Create a new step within this trace."""
        step = Step(
            trace_id=self.trace.trace_id,
            name=name,
            start_time=datetime.now(),
            step_order=self._step_counter
        )
        self._step_counter += 1
        self.trace.steps.append(step)
        return StepContext(step, self.storage, self)

    def __enter__(self):
        """Start trace execution."""
        self.trace.status = "running"
        self.trace.start_time = datetime.now()
        self.storage.save_trace(self.trace)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete trace execution."""
        self.trace.end_time = datetime.now()
        self.trace.duration_ms = int(
            (self.trace.end_time - self.trace.start_time).total_seconds() * 1000
        )

        if exc_type is not None:
            self.trace.status = "failed"
        else:
            self.trace.status = "completed"

        # Save final trace state
        self.storage.save_trace(self.trace)

        # Return False to propagate exception
        return False


class XRay:
    """Main SDK interface for creating traces."""

    def __init__(self, storage: Optional[StorageBackend] = None):
        """
        Initialize XRay SDK.

        Args:
            storage: Storage backend (defaults to SQLiteStorage)
        """
        self.storage = storage or SQLiteStorage()

    def trace(self, name: str, metadata: Optional[dict[str, Any]] = None) -> TraceContext:
        """
        Create a new trace.

        Args:
            name: Human-readable name for this trace
            metadata: Optional metadata for the trace

        Returns:
            TraceContext that can be used with 'with' statement
        """
        trace = Trace(
            name=name,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        return TraceContext(trace, self.storage)

    def close(self) -> None:
        """Close storage connection."""
        self.storage.close()
