"""
Descrição: Armazena e restaura as inscrições MQTT do backend.
Autor: Leôncio Ferreira
"""

from collections.abc import Awaitable, Callable

import paho.mqtt.client as mqtt

MessageHandler = Callable[[bytes], Awaitable[None]]


class MQTTSubscriptions:
    def __init__(self) -> None:
        self._items: dict[str, tuple[int, MessageHandler]] = {}

    def add(self, topic: str, handler: MessageHandler, qos: int) -> None:
        self._items[topic] = (qos, handler)

    def restore(self, client: mqtt.Client) -> None:
        for topic, (qos, _) in self._items.items():
            client.subscribe(topic, qos=qos)

    def matching_handlers(self, topic: str) -> list[MessageHandler]:
        return [
            handler
            for subscription, (_, handler) in self._items.items()
            if mqtt.topic_matches_sub(subscription, topic)
        ]
