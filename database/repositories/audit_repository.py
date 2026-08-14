"""Repositorio append-only de AuditEvent. Deliberadamente no expone update() ni delete().

Alcance de esta garantia en v0.0.1: es append-only a nivel Repository/API, no a nivel de
base de datos. El rol de PostgreSQL con el que corre TONY sigue siendo owner de la tabla
audit_events y conserva privilegios UPDATE/DELETE otorgados por PostgreSQL por defecto; nada
en el esquema actual se lo impide a nivel de motor. Cerrar esa brecha (revocar privilegios al
rol de runtime y/o encadenar checksums para detectar alteraciones) es responsabilidad de
audit/integrity/ y queda reservado para la fase de hardening (v0.3 S19 paso 19; v0.1 Fase 11),
tal como exige v0.3 S8.1: "audit events tendra politica distinta de la memoria conversacional".
"""

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
