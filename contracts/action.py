"""Action: solicitud universal normalizada (v0.3 S5) y su maquina de estados (v0.3 S6)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    """Nivel de riesgo de una Action (v0.3 S5)."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    CRITICAL = "CRITICAL"


class ActionStatus(StrEnum):
    """Estados de una Action (v0.3 S6). CRITICAL pasa por WAITING_AUTH/AUTHORIZED antes de EXECUTING."""

    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    CLASSIFIED = "CLASSIFIED"
    WAITING_AUTH = "WAITING_AUTH"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Action(BaseModel):
    """Solicitud universal normalizada que circula entre Core, Policy Engine y agentes."""

    action_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    source: str
    """Origen de la accion: 'voice', 'text', 'ui', 'scheduler', etc."""
    intent: str
    parameters: dict = Field(default_factory=dict)
    target: str | None = None
    risk_level: RiskLevel = RiskLevel.NORMAL
    status: ActionStatus = ActionStatus.CREATED
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def with_status(self, status: ActionStatus) -> "Action":
        """Devuelve una copia con el nuevo estado y updated_at refrescado (Action es inmutable)."""
        return self.model_copy(update={"status": status, "updated_at": _utcnow()})
