"""Servicio de auditoria usado por el Core y, mas adelante, por cada agente/Policy Engine."""

from __future__ import annotations

import logging
import uuid

from contracts.audit import AuditEvent
from audit.writers.db_writer import AuditWriter

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, writer: AuditWriter) -> None:
        self._writer = writer

    def record(self, event: AuditEvent) -> None:
        self._writer.write(event)
        logger.debug("audit event registrado: category=%s actor=%s", event.category, event.actor)

    def record_system_event(
        self,
        *,
        actor: str,
        category: str,
        description: str,
        payload: dict | None = None,
        action_id: uuid.UUID | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            actor=actor,
            action_id=action_id,
            category=category,
            description=description,
            payload=payload or {},
        )
        self.record(event)
        return event
