"""AuthorizationRequest / AuthorizationGrant para acciones CRITICAL (v0.3 S5, S7).

Invariante (v0.2 S4, v0.3 S7): ninguna accion CRITICAL puede ejecutarse sin un
AuthorizationGrant valido. No existe bypass de debug, LLM, terminal o UI.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AuthorizationRequest(BaseModel):
    """Solicitud de autorizacion reforzada ligada a una Action y a un dispositivo confiable."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    action_id: uuid.UUID
    trusted_device_id: uuid.UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime


class AuthorizationGrant(BaseModel):
    """Grant firmado y de un solo uso emitido por el dispositivo confiable (p. ej. tras Face ID).

    TONY no almacena la plantilla biometrica: solo esta prueba criptografica de que el
    dispositivo confiable autorizo la operacion (v0.1 S5, v0.3 S7).
    """

    grant_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    action_id: uuid.UUID
    device_id: uuid.UUID
    nonce: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    signature: str
    consumed: bool = False

    def is_valid(self, *, now: datetime | None = None) -> bool:
        """Un grant es valido si no fue consumido y no expiro. No implica verificar la firma."""
        current = now or datetime.now(timezone.utc)
        return not self.consumed and current < self.expires_at
