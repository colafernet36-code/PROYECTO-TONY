"""AIRequest/AIResponse: contrato neutral para que TONY no dependa de un proveedor (v0.3 S5, S10)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    """Peticion normalizada hacia el AI Router, independiente del proveedor final."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID | None = None
    task_type: str
    """P. ej. 'programming', 'reasoning', 'research', 'multimedia' (criterios de v0.3 S10)."""
    messages: list[dict] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)
    requires_tools: bool = False
    privacy_sensitive: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIResponse(BaseModel):
    """Respuesta normalizada del proveedor seleccionado por el AI Router."""

    response_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    request_id: uuid.UUID
    provider: str
    model: str
    content: str
    usage: dict = Field(default_factory=dict)
    latency_ms: float | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
