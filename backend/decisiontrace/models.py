"""
Pydantic models for DecisionTrace X-Ray system.

These models are general-purpose and domain-agnostic.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime
from uuid import uuid4


class Step(BaseModel):
    """
    Represents a single decision point within a trace.

    Core fields are general-purpose; domain-specific data goes in metadata.
    """
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str
    name: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: Optional[dict[str, Any]] = None
    reasoning: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)  # Extensible
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Literal["running", "completed", "failed"] = "running"
    error: Optional[str] = None
    step_order: int = 0

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Trace(BaseModel):
    """
    Represents a complete execution of a multi-step workflow.
    """
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    steps: list[Step] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)  # Extensible
    status: Literal["running", "completed", "failed"] = "running"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
