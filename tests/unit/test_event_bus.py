import pytest

from contracts.events import SystemEvent
from core.event_bus import EventBus


@pytest.mark.asyncio
async def test_publish_delivers_to_matching_subscriber():
    bus = EventBus()
    received: list[SystemEvent] = []

    async def handler(event: SystemEvent) -> None:
        received.append(event)

    bus.subscribe("system.tony_ready", handler)
    await bus.publish(SystemEvent(type="system.tony_ready", source="test"))

    assert len(received) == 1
    assert received[0].type == "system.tony_ready"


@pytest.mark.asyncio
async def test_publish_ignores_non_matching_subscriber():
    bus = EventBus()
    received: list[SystemEvent] = []

    async def handler(event: SystemEvent) -> None:
        received.append(event)

    bus.subscribe("other.type", handler)
    await bus.publish(SystemEvent(type="system.tony_ready", source="test"))

    assert received == []


@pytest.mark.asyncio
async def test_wildcard_subscriber_receives_everything():
    bus = EventBus()
    received: list[str] = []

    async def handler(event: SystemEvent) -> None:
        received.append(event.type)

    bus.subscribe("*", handler)
    await bus.publish(SystemEvent(type="a.b", source="test"))
    await bus.publish(SystemEvent(type="c.d", source="test"))

    assert received == ["a.b", "c.d"]


@pytest.mark.asyncio
async def test_handler_exception_does_not_stop_other_handlers():
    bus = EventBus()
    received: list[SystemEvent] = []

    async def bad_handler(event: SystemEvent) -> None:
        raise RuntimeError("boom")

    async def good_handler(event: SystemEvent) -> None:
        received.append(event)

    bus.subscribe("x", bad_handler)
    bus.subscribe("x", good_handler)
    await bus.publish(SystemEvent(type="x", source="test"))

    assert len(received) == 1


@pytest.mark.asyncio
async def test_unsubscribe_stops_delivery():
    bus = EventBus()
    received: list[SystemEvent] = []

    async def handler(event: SystemEvent) -> None:
        received.append(event)

    bus.subscribe("x", handler)
    bus.unsubscribe("x", handler)
    await bus.publish(SystemEvent(type="x", source="test"))

    assert received == []
