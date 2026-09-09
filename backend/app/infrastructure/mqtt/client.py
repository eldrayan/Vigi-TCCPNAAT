"""
Descrição: Gerencia conexão, reconexão e distribuição de mensagens do MQTT.
Autor: Leôncio Ferreira
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from concurrent.futures import Future

import paho.mqtt.client as mqtt

from app.config import Settings

MessageHandler = Callable[[bytes], Awaitable[None]]

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.loop: asyncio.AbstractEventLoop | None = None
        self.subscriptions: dict[str, tuple[int, MessageHandler]] = {}
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=settings.mqtt_client_id,
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    def add_subscription(
        self,
        topic: str,
        handler: MessageHandler,
        qos: int,
    ) -> None:
        self.subscriptions[topic] = (qos, handler)

    def start(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.client.connect_async(
            host=self.settings.mqtt_host,
            port=self.settings.mqtt_port,
        )
        self.client.loop_start()

    def stop(self) -> None:
        self.client.disconnect()
        self.client.loop_stop()

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata,
        flags,
        reason_code,
        properties,
    ) -> None:
        if reason_code != 0:
            logger.error("Falha ao conectar ao MQTT: %s", reason_code)
            return

        for topic, (qos, _) in self.subscriptions.items():
            client.subscribe(topic, qos=qos)

        logger.info("Cliente MQTT conectado e inscrições restauradas.")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata,
        message: mqtt.MQTTMessage,
    ) -> None:
        if self.loop is None:
            logger.error("Loop assíncrono indisponível para processar mensagem.")
            return

        handlers = [
            handler
            for topic, (_, handler) in self.subscriptions.items()
            if mqtt.topic_matches_sub(topic, message.topic)
        ]

        for handler in handlers:
            future = asyncio.run_coroutine_threadsafe(
                handler(message.payload),
                self.loop,
            )
            future.add_done_callback(self._handle_processing_result)

    @staticmethod
    def _handle_processing_result(future: Future[None]) -> None:
        if future.cancelled():
            return

        exception = future.exception()
        if exception is not None:
            logger.error("Erro no handler MQTT.", exc_info=exception)
