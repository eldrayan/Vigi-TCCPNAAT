"""
Descrição: Verifica a distribuição assíncrona de eventos para o SSE.
Autor: Leôncio Ferreira
"""

import asyncio

from app.events.routes import format_sse
from app.infrastructure.events import EventBus


def test_event_bus_delivers_event_to_subscriber() -> None:
    async def scenario() -> None:
        bus = EventBus()
        subscriber = bus.subscribe()
        payload = {"inspection_id": 1, "result": "CONFORME"}

        await bus.publish("inspection.created", payload)
        event = await asyncio.wait_for(subscriber.get(), timeout=1)

        assert event == {"type": "inspection.created", "data": payload}
        bus.unsubscribe(subscriber)

    asyncio.run(scenario())


def test_format_sse_serializes_event_type_and_data() -> None:
    formatted = format_sse(
        {"type": "device.status", "data": {"connection": "ONLINE"}}
    )

    assert formatted == (
        'event: device.status\n'
        'data: {"connection": "ONLINE"}\n\n'
    )
