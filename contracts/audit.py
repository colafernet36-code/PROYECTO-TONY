"""AuditEvent: evento inmutable orientado a append para trazabilidad (v0.3 S5).

Distinto de MemoryItem y de logs tecnicos: un recuerdo editable no debe poder reescribir el
historial de auditoria (v0.3 S8.1).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Registro de auditoria: que se solicito, que componente actuo, con que permisos y resultado."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    actor: str
    """Componente o identidad que origina el evento, p. ej. 'tony-core', 'terminal-agent'."""
    action_id: uuid.UUID | None = None
    category: str
    """P. ej. 'boot', 'authorization', 'tool_execution', 'security'."""
    description: str
    payload: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
