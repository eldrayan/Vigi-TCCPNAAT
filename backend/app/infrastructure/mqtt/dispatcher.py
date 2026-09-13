"""
Descrição: Despacha mensagens MQTT para handlers assíncronos com confirmação segura.
Autor: Leôncio Ferreira
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from concurrent.futures import Future
from typing import Any

MessageHandler = Callable[[bytes], Awaitable[None]]

logger = logging.getLogger(__name__)


class MQTTMessageDispatcher:
    def __init__(self, client: Any) -> None:
        self.client = client
        self.pending: set[Future[None]] = set()

    def dispatch(
        self,
        message: Any,
        handlers: list[MessageHandler],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        future = asyncio.run_coroutine_threadsafe(self.process(message, handlers), loop)
        self.pending.add(future)
        future.add_done_callback(self.pending.discard)
        future.add_done_callback(self._handle_processing_result)

    async def process(self, message: Any, handlers: list[MessageHandler]) -> None:
        while True:
            try:
                for handler in handlers:
                    await handler(message.payload)
            except Exception:
                logger.exception("Falha ao salvar mensagem; nova tentativa em 5s.")
                await asyncio.sleep(5)
            else:
                self.client.ack(message.mid, message.qos)
                return

    def cancel_pending(self) -> None:
        for future in tuple(self.pending):
            future.cancel()

    @staticmethod
    def _handle_processing_result(future: Future[None]) -> None:
        if future.cancelled():
            return

        exception = future.exception()
        if exception is not None:
            logger.error("Erro no handler MQTT.", exc_info=exception)
