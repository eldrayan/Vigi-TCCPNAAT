"""Publicação de eventos de inspeção e alarmes no broker MQTT."""

from __future__ import annotations

import json
import logging
from typing import Any

from .event import InspectionEvent

logger = logging.getLogger(__name__)


def create_mqtt_client(client_id: str = "") -> Any:
    import paho.mqtt.client as mqtt

    return mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
    )


class MQTTInspectionPublisher:
    """Publicador MQTT para eventos de inspeção, alarmes e estado operacional.

    Atende ao RNF04:
    - Envio não-bloqueante nos tópicos vigi/esteira/inspecoes e vigi/esteira/alarmes.
    - Reconexão automática com intervalo inferior a 60 segundos.
    - Mensagem de Last Will and Testament (LWT) no tópico vigi/esteira/status.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        topic: str = "vigi/esteira/inspecoes",
        topic_alarms: str = "vigi/esteira/alarmes",
        topic_status: str = "vigi/esteira/status",
        client: Any | None = None,
        client_id: str = "vigi-edge-gateway",
    ) -> None:
        self.host = host
        self.port = port
        self.topic = topic
        self.topic_alarms = topic_alarms
        self.topic_status = topic_status
        self.client_id = client_id
        self.client = client or create_mqtt_client(client_id=client_id)
        self._persistent_session = False

    def start_session(self) -> None:
        """Inicia uma sessão persistente com LWT e reconexão automática."""
        lwt_payload = json.dumps(
            {
                "status": "OFFLINE",
                "device": self.client_id,
                "reason": "UNEXPECTED_DISCONNECT",
            },
            ensure_ascii=False,
        )

        if hasattr(self.client, "will_set"):
            self.client.will_set(
                topic=self.topic_status,
                payload=lwt_payload,
                qos=1,
                retain=True,
            )

        if hasattr(self.client, "reconnect_delay_set"):
            # Reconexão automática entre 1s e 60s (RNF04)
            self.client.reconnect_delay_set(min_delay=1, max_delay=60)

        self.client.connect(self.host, self.port)
        self.client.loop_start()
        self._persistent_session = True

        # Notifica status ONLINE no broker
        online_payload = json.dumps(
            {"status": "ONLINE", "device": self.client_id},
            ensure_ascii=False,
        )
        self.client.publish(
            self.topic_status,
            online_payload,
            qos=1,
            retain=True,
        )
        logger.info(
            "Sessão MQTT persistente iniciada em %s:%d (LWT ativo)",
            self.host,
            self.port,
        )

    def stop_session(self) -> None:
        """Encerra a sessão persistente com mensagem formal de encerramento."""
        if not self._persistent_session:
            return

        offline_payload = json.dumps(
            {
                "status": "OFFLINE",
                "device": self.client_id,
                "reason": "NORMAL_SHUTDOWN",
            },
            ensure_ascii=False,
        )
        try:
            pub = self.client.publish(
                self.topic_status,
                offline_payload,
                qos=1,
                retain=True,
            )
            if hasattr(pub, "wait_for_publish"):
                pub.wait_for_publish(timeout=2)
        except Exception as exc:
            logger.warning("Falha ao publicar status offline: %s", exc)

        try:
            self.client.disconnect()
            self.client.loop_stop()
        finally:
            self._persistent_session = False
        logger.info("Sessão MQTT encerrada.")

    def publish_inspection(self, event: InspectionEvent) -> Any:
        """Publica evento no tópico de inspeções vigi/esteira/inspecoes."""
        payload = json.dumps(event.as_dict(), ensure_ascii=False)
        return self.client.publish(
            self.topic,
            payload,
            qos=1,
            retain=False,
        )

    def publish_alarm(self, alarm_data: dict[str, Any]) -> Any:
        """Publica alarme operacional no tópico vigi/esteira/alarmes."""
        payload = json.dumps(alarm_data, ensure_ascii=False)
        return self.client.publish(
            self.topic_alarms,
            payload,
            qos=1,
            retain=False,
        )

    def publish(self, event: InspectionEvent) -> None:
        """Método de publicação compatível com chamadas one-shot e persistentes."""
        if self._persistent_session:
            self.publish_inspection(event)
            return

        # Modo one-shot (conecta -> publica -> desconecta)
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        try:
            publication = self.client.publish(
                self.topic,
                json.dumps(event.as_dict(), ensure_ascii=False),
                qos=1,
                retain=False,
            )
            if hasattr(publication, "wait_for_publish"):
                publication.wait_for_publish(timeout=5)
                if not publication.is_published():
                    raise TimeoutError("Tempo limite excedido ao publicar no MQTT.")
        finally:
            self.client.disconnect()
            self.client.loop_stop()
