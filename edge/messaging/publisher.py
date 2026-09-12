"""Publicação de eventos de inspeção no broker MQTT."""

from __future__ import annotations

import json
from typing import Any

from .event import InspectionEvent


def create_mqtt_client() -> Any:
    import paho.mqtt.client as mqtt

    return mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)


class MQTTInspectionPublisher:
    def __init__(
        self,
        host: str,
        port: int = 1883,
        topic: str = "vigi/esteira/inspecoes",
        client: Any | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.topic = topic
        self.client = client or create_mqtt_client()

    def publish(self, event: InspectionEvent) -> None:
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        try:
            publication = self.client.publish(
                self.topic,
                json.dumps(event.as_dict(), ensure_ascii=False),
                qos=1,
                retain=False,
            )
            publication.wait_for_publish(timeout=5)
            if not publication.is_published():
                raise TimeoutError("Tempo limite excedido ao publicar no MQTT.")
        finally:
            self.client.disconnect()
            self.client.loop_stop()
