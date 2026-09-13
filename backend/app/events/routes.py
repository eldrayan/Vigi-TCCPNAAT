"""
Descrição: Expõe o fluxo SSE de inspeções e estados das estações.
Autor: Leôncio Ferreira
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.infrastructure.events import EventBus

router = APIRouter(prefix="/api/eventos", tags=["events"])


def format_sse(event: dict[str, Any]) -> str:
    return (
        f"event: {event['type']}\n"
        f"data: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
    )


@router.get("/stream")
async def stream_events(request: Request) -> StreamingResponse:
    bus: EventBus = request.app.state.event_bus
    queue = bus.subscribe()

    async def event_stream() -> AsyncIterator[str]:
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await queue.get()
                yield format_sse(event)
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
