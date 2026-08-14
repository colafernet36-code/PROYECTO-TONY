"""SystemEvent publicado en el Event Bus (v0.3 S5, S9)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class EventType:
    """Tipos de evento iniciales listados en v0.3 S9. Nuevos tipos se agregan aqui, no ad-hoc."""

    VOICE_WAKE_DETECTED = "voice.wake_detected"
    VOICE_TRANSCRIPTION_READY = "voice.transcription_ready"
    VOICE_SPEAKING = "voice.speaking"
    ACTION_CREATED = "action.created"
    ACTION_AUTHORIZED = "action.authorized"
    ACTION_REJECTED = "action.rejected"
    ACTION_EXECUTING = "action.executing"
    ACTION_COMPLETED = "action.completed"
    ACTION_FAILED = "action.failed"
    SECURITY_AUTHORIZATION_REQUIRED = "security.authorization_required"
    SECURITY_AUTHORIZATION_GRANTED = "security.authorization_granted"
    MEMORY_CREATED = "memory.created"
    MEMORY_RECALLED = "memory.recalled"
    AI_REQUESTED = "ai.requested"
    AI_COMPLETED = "ai.completed"
    SYSTEM_TONY_READY = "system.tony_ready"
    SYSTEM_DEGRADED = "system.degraded"


class SystemEvent(BaseModel):
    """Evento publicado en el Event Bus. La UI y otros componentes solo observan, no controlan."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    type: str
    source: str
    payload: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
