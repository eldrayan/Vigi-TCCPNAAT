"""
Descrição: Distribui eventos transitórios para consumidores SSE conectados.
Autor: Leôncio Ferreira
"""

import asyncio
from typing import Any


class EventBus:
    """
    Descrição: Mantém filas isoladas para cada assinante de eventos.
    Autor: Leôncio Ferreira
    """

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._subscribers.discard(queue)

    async def publish(self, event_type: str, data: dict[str, Any]) -> None:
        event = {"type": event_type, "data": data}
        for queue in tuple(self._subscribers):
            await queue.put(event)
