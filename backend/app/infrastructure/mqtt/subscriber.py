"""
Descrição: Registra handlers assíncronos para inscrição em tópicos MQTT.
Autor: Leôncio Ferreira
"""

from .client import MessageHandler, MQTTClient


class MQTTSubscriber:
    def __init__(self, client: MQTTClient) -> None:
        self.client = client

    def subscribe(
        self,
        topic: str,
        handler: MessageHandler,
        qos: int = 1,
    ) -> None:
        self.client.add_subscription(topic, handler, qos)
