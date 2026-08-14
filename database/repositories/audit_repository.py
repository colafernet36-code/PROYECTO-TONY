"""Repositorio append-only de AuditEvent. Deliberadamente no expone update() ni delete()."""

from __future__ import annotations

from sqlalchemy.orm import Session

from contracts.audit import AuditEvent
from database.models.audit_event import AuditEventORM


class AuditEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event: AuditEvent) -> None:
        row = AuditEventORM(
            event_id=event.event_id,
            actor=event.actor,
            action_id=event.action_id,
            category=event.category,
            description=event.description,
            payload=event.payload,
        )
        self._session.add(row)
        self._session.commit()

    def count(self) -> int:
        from sqlalchemy import func, select

        return self._session.scalar(select(func.count()).select_from(AuditEventORM)) or 0
