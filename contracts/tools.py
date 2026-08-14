"""ToolCall / ToolResult: operacion concreta para un agente y su resultado (v0.3 S5, S12)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Operacion estructurada resuelta por el Intent Parser, previa a Risk Classifier + Policy Engine."""

    tool_call_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    action_id: uuid.UUID
    tool: str
    operation: str
    arguments: dict = Field(default_factory=dict)
    working_directory: str | None = None
    timeout_seconds: float = 30.0
    execution_policy: str = "standard"
    """P. ej. 'standard', 'dry_run', 'sandboxed' (security/sandbox, pendiente)."""


class ToolResult(BaseModel):
    """Resultado estructurado de una ToolCall, siempre acompanado de referencia de auditoria."""

    tool_call_id: uuid.UUID
    success: bool
    output: str | None = None
    error: str | None = None
    exit_code: int | None = None
    duration_ms: float | None = None
    audit_event_id: uuid.UUID | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
