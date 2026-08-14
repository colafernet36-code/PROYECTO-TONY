"""MemoryItem: recuerdo estructurado (v0.3 S5, S8.1). Implementacion completa en memory/ (paso 11)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """Recuerdo estructurado con fuente, importancia, confianza, relaciones y embedding opcional."""

    memory_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID | None = None
    content: str
    source: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    related_memory_ids: list[uuid.UUID] = Field(default_factory=list)
    embedding: list[float] | None = None
    """Vector pgvector; se completa cuando memory/embeddings este implementado."""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
