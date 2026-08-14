"""Verifica el recorrido del hito v0.0.1 (v0.3 S20) contra un PostgreSQL real:
PostgreSQL alcanzable + Audit Service persiste eventos correctamente."""

from audit.service import AuditService
from audit.writers.db_writer import DBAuditWriter
from database.repositories.audit_repository import AuditEventRepository
from database.session import make_session_factory


def test_database_is_reachable(db_engine):
    # Llegar aca implica que el fixture ya corrio check_database() sin excepciones.
    assert db_engine is not None


def test_audit_service_persists_boot_event(db_engine):
    session_factory = make_session_factory(db_engine)

    with session_factory() as session:
        before = AuditEventRepository(session).count()

    audit = AuditService(DBAuditWriter(session_factory))
    audit.record_system_event(
        actor="tony-core",
        category="boot",
        description="test: TONY Core bootstrap completado",
        payload={"env": "test"},
    )

    with session_factory() as session:
        after = AuditEventRepository(session).count()

    assert after == before + 1
