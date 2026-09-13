"""Recupera do MQTT o contexto operacional configurado pelo dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from threading import Event
from typing import Any


@dataclass(frozen=True)
class OperationalContext:
    station_code: str
    batch_code: str

    @property
    def inspections_topic(self) -> str:
        return f"vigi/estacoes/{self.station_code}/inspecoes"


class MQTTOperationalContextReceiver:
    def __init__(
        self,
        host: str,
        port: int,
        device_id: str,
        client: Any | None = None,
    ) -> None:
        from .publisher import create_mqtt_client

        self.host = host
        self.port = port
        self.topic = f"vigi/dispositivos/{device_id}/configuracao"
        self.client = client or create_mqtt_client()

    def receive(self, timeout: float = 5) -> OperationalContext:
        received = Event()
        context: list[OperationalContext] = []

        def on_message(client, userdata, message) -> None:
            data = json.loads(message.payload)
            context.append(
                OperationalContext(
                    station_code=data["station_code"],
                    batch_code=data["batch_code"],
                )
            )
            received.set()

        self.client.on_message = on_message
        self.client.connect(self.host, self.port)
        self.client.subscribe(self.topic, qos=1)
        self.client.loop_start()
        try:
            if not received.wait(timeout):
                raise TimeoutError(
                    "Dispositivo sem estação e lote configurados no dashboard."
                )
            return context[0]
        finally:
            self.client.disconnect()
            self.client.loop_stop()
