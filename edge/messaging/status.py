"""Publica a disponibilidade operacional do dispositivo Edge no MQTT."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from .publisher import configure_mqtt_client, create_mqtt_client


class MQTTDeviceStatusPublisher:
    """Mantém no broker o último estado e o Last Will do dispositivo."""

    def __init__(
        self,
        host: str,
        device_id: str,
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.device_id = device_id
        self.topic = f"vigi/dispositivos/{device_id}/status"
        self._current_state: tuple[str, str, str, str] | None = None
        self.client = configure_mqtt_client(
            client or create_mqtt_client(client_id=f"vigi-status-{device_id}"),
            username,
            password,
        )
        self.client.on_connect = self._on_connect
        self.client.will_set(
            self.topic,
            json.dumps(self._payload("OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE")),
            qos=1,
            retain=True,
        )

    def start(
        self,
        *,
        camera: str,
        processing: str,
        sensor: str = "ONLINE",
    ) -> None:
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        self.publish(camera=camera, processing=processing, sensor=sensor)

    def publish(
        self,
        *,
        camera: str,
        processing: str,
        sensor: str = "ONLINE",
    ) -> None:
        self._current_state = ("ONLINE", camera, processing, sensor)
        publication = self.client.publish(
            self.topic,
            json.dumps(self._payload("ONLINE", camera, processing, sensor)),
            qos=1,
            retain=True,
        )
        publication.wait_for_publish(timeout=5)
        if not publication.is_published():
            raise TimeoutError("Tempo limite excedido ao publicar estado no MQTT.")

    def stop(self) -> None:
        self._current_state = ("OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE")
        publication = self.client.publish(
            self.topic,
            json.dumps(self._payload("OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE")),
            qos=1,
            retain=True,
        )
        publication.wait_for_publish(timeout=5)
        self.client.disconnect()
        self.client.loop_stop()

    def _on_connect(
        self,
        client: Any,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any = None,
    ) -> None:
        """Republica o último estado após a conexão ou reconexão ao broker."""
        del userdata, flags, properties
        if getattr(reason_code, "is_failure", False) or self._current_state is None:
            return

        connection, camera, processing, sensor = self._current_state
        client.publish(
            self.topic,
            json.dumps(self._payload(connection, camera, processing, sensor)),
            qos=1,
            retain=True,
        )

    def _payload(
        self,
        connection: str,
        camera: str,
        processing: str,
        sensor: str = "OFFLINE",
    ) -> dict[str, str]:
        return {
            "device_id": self.device_id,
            "connection": connection,
            "sensor": sensor,
            "camera": camera,
            "processing": processing,
            "timestamp": datetime.now(UTC).isoformat(),
        }
