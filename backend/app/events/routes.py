"""
Descrição: Expõe o fluxo SSE de inspeções e estados das estações.
Autor: Leôncio Ferreira
"""

import asyncio
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
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield format_sse(event)
                except TimeoutError:
                    yield ": ping\n\n"
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
