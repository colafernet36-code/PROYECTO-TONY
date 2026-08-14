"""ErrorResponse: error normalizado entre modulos (v0.3 S5)."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Forma comun de reportar errores entre Core, agentes y clientes."""

    error_code: str
    message: str
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
