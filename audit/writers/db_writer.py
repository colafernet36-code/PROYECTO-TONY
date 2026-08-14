"""Writer de auditoria hacia PostgreSQL. Un writer alternativo (p. ej. a stdout/syslog) puede
implementar el mismo protocolo AuditWriter para degradacion segura si la base no responde."""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session, sessionmaker

from contracts.audit import AuditEvent
from database.repositories.audit_repository import AuditEventRepository


class AuditWriter(Protocol):
    def write(self, event: AuditEvent) -> None: ...


class DBAuditWriter:
    """Persiste cada AuditEvent en la tabla audit_events dentro de su propia sesion/transaccion."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def write(self, event: AuditEvent) -> None:
        with self._session_factory() as session:
            AuditEventRepository(session).add(event)
