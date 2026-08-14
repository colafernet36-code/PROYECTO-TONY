"""Event Bus interno en proceso (v0.3 S9): pub/sub asincrono para SystemEvent.

La UI y otros componentes observan eventos; no controlan la logica central (v0.3 S9).
Este bus es intra-proceso; si en el futuro TONY se separa en varios procesos, este modulo
es el punto de reemplazo por un broker real sin tocar a los publicadores/suscriptores.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Awaitable, Callable

from contracts.events import SystemEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[SystemEvent], Awaitable[None]]

WILDCARD = "*"


class EventBus:
    """Pub/sub asincrono en memoria. `subscribe(WILDCARD, handler)` recibe todos los eventos."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler)

    async def publish(self, event: SystemEvent) -> None:
        """Entrega el evento a los suscriptores de su tipo y a los de wildcard, en orden.

        Un handler que lanza una excepcion se registra y no interrumpe al resto: un
        suscriptor caido (p. ej. la UI) no puede tumbar al Core (v0.1 principio de
        degradacion segura).
        """
        handlers = list(self._subscribers.get(event.type, ())) + list(
            self._subscribers.get(WILDCARD, ())
        )
        if not handlers:
            logger.debug("evento %s publicado sin suscriptores", event.type)
            return
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.exception(
                    "handler de evento fallo para type=%s source=%s", event.type, event.source
                )
