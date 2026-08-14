"""TONY Core Bootstrap: primer hito programable (v0.3 S20).

    Kali Linux -> systemd -> TONY Core Bootstrap -> PostgreSQL -> Event Bus
    -> Audit Service -> publish: system.tony_ready

Un fallo en cualquier componente no debe otorgar permisos adicionales ni omitir
autenticacion (v0.2 S11): ante un fallo de arranque se publica system.degraded, se
registra en auditoria cuando sea posible, y el proceso termina con codigo != 0 para
que systemd decida el reintento (ver systemd/units/tony.service, Restart=on-failure).

Este bootstrap deliberadamente NO incluye todavia: Policy Engine, AI Router, voz,
memoria semantica ni agentes. Esos se conectan en los pasos siguientes del orden
oficial de implementacion (v0.3 S19), una vez que este recorrido minimo esta
verificado y estable (regla de desarrollo, v0.3 portada).
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys

from audit.service import AuditService
from audit.writers.db_writer import DBAuditWriter
from config import get_settings
from contracts.events import EventType, SystemEvent
from core.event_bus import EventBus
from database.session import check_database, make_engine, make_session_factory

logger = logging.getLogger("tony.bootstrap")


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )


async def _log_event(event: SystemEvent) -> None:
    logger.info("event %s from=%s payload=%s", event.type, event.source, event.payload)


async def wait_for_shutdown() -> None:
    """Espera SIGTERM/SIGINT para permitir un apagado ordenado bajo systemd."""
    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    def _request_stop(*_args: object) -> None:
        if not stop.done():
            stop.set_result(None)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _request_stop)
        except NotImplementedError:
            # add_signal_handler no esta disponible en todas las plataformas (p. ej. Windows).
            signal.signal(sig, lambda *_a: _request_stop())

    await stop


async def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("TONY bootstrap iniciando (env=%s)", settings.tony_env)

    bus = EventBus()
    bus.subscribe("*", _log_event)

    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)
    audit = AuditService(DBAuditWriter(session_factory))

    try:
        check_database(engine)
    except Exception as exc:  # noqa: BLE001 - queremos degradar ante cualquier fallo de arranque
        logger.error("chequeo de PostgreSQL fallo: %s", exc)
        await bus.publish(
            SystemEvent(
                type=EventType.SYSTEM_DEGRADED,
                source="core.bootstrap",
                payload={"reason": "database_unreachable", "detail": str(exc)},
            )
        )
        raise SystemExit(1) from exc

    audit.record_system_event(
        actor="tony-core",
        category="boot",
        description="TONY Core bootstrap completado: PostgreSQL, Event Bus y Audit Service activos.",
        payload={"env": settings.tony_env},
    )

    await bus.publish(
        SystemEvent(type=EventType.SYSTEM_TONY_READY, source="core.bootstrap", payload={})
    )
    logger.info("TONY READY")

    await wait_for_shutdown()
    logger.info("TONY apagandose (senal de shutdown recibida)")


def main() -> None:
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        logger.info("TONY interrumpido por teclado")
    except Exception:  # noqa: BLE001 - ultimo recurso: log y salida no-cero para systemd
        logger.exception("fallo no controlado durante el bootstrap")
        sys.exit(1)


if __name__ == "__main__":
    main()
