"""
Abstract base class for storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models import Trace, Step


class StorageBackend(ABC):
    """Abstract interface for storing and retrieving traces."""

    @abstractmethod
    def save_trace(self, trace: Trace) -> None:
        """Save or update a trace."""
        pass

    @abstractmethod
    def save_step(self, step: Step) -> None:
        """Save or update a step."""
        pass

    @abstractmethod
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID with all its steps."""
        pass

    @abstractmethod
    def get_all_traces(self, limit: int = 100, status: Optional[str] = None) -> list[Trace]:
        """Get all traces with optional filtering."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the storage connection."""
        pass
