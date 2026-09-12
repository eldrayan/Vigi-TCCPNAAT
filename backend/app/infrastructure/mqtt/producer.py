"""
Descrição: Publica mensagens serializadas em tópicos MQTT configuráveis.
Autor: Leôncio Ferreira
"""

import json
from typing import Any

import paho.mqtt.client as mqtt
from pydantic import BaseModel

from .client import MQTTClient


class MQTTProducer:
    def __init__(self, client: MQTTClient) -> None:
        self.client = client

    def publish(
        self,
        topic: str,
        payload: BaseModel | dict[str, Any] | str | bytes,
        qos: int = 1,
        retain: bool = False,
    ) -> mqtt.MQTTMessageInfo:
        if isinstance(payload, BaseModel):
            serialized_payload: str | bytes = payload.model_dump_json()
        elif isinstance(payload, dict):
            serialized_payload = json.dumps(payload, default=str)
        else:
            serialized_payload = payload

        return self.client.client.publish(
            topic=topic,
            payload=serialized_payload,
            qos=qos,
            retain=retain,
        )
