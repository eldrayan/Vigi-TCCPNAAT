"""
Descrição: Gerencia conexão, reconexão e distribuição de mensagens do MQTT.
Autor: Leôncio Ferreira
"""

import logging

import paho.mqtt.client as mqtt

from app.config import Settings

from .connection import MQTTConnection
from .dispatcher import MQTTMessageDispatcher
from .subscriptions import MessageHandler, MQTTSubscriptions

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.connection = MQTTConnection(settings)
        self.client = self.connection.client
        self.subscriptions = MQTTSubscriptions()
        self.dispatcher = MQTTMessageDispatcher(
            self.client, max_retries=settings.mqtt_max_retries
        )
        self.loop = None
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def add_subscription(
        self,
        topic: str,
        handler: MessageHandler,
        qos: int,
    ) -> None:
        self.subscriptions.add(topic, handler, qos)

    def start(self) -> None:
        import asyncio

        self.loop = asyncio.get_running_loop()
        self.connection.start()

    def stop(self) -> None:
        self.dispatcher.cancel_pending()
        self.connection.stop()

    def is_connected(self) -> bool:
        return self.connection.is_connected()

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

        self.subscriptions.restore(client)

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

        handlers = self.subscriptions.matching_handlers(message.topic)
        self.dispatcher.dispatch(message, handlers, self.loop)

    async def _process(self, message, handlers: list[MessageHandler]) -> None:
        await self.dispatcher.process(message, handlers)
